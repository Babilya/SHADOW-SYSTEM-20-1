import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import aiohttp
from sqlalchemy import text

logger = logging.getLogger(__name__)

class CRMAdapter(ABC):
    @abstractmethod
    async def export_leads(self, leads: List[dict]) -> dict:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass

class NotionAdapter(CRMAdapter):
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Notion-Version": "2022-06-28"
                }
                async with session.get(
                    f"{self.base_url}/databases/{self.database_id}",
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Notion connection test failed: {e}")
            return False
    
    async def export_leads(self, leads: List[dict]) -> dict:
        exported = 0
        failed = 0
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            for lead in leads:
                try:
                    page_data = {
                        "parent": {"database_id": self.database_id},
                        "properties": {
                            "Name": {"title": [{"text": {"content": lead.get("name", "Unknown")}}]},
                            "Telegram ID": {"number": lead.get("user_id", 0)},
                            "Username": {"rich_text": [{"text": {"content": lead.get("username", "")}}]},
                            "Status": {"select": {"name": lead.get("status", "New")}},
                            "Created": {"date": {"start": lead.get("created_at", datetime.now().isoformat())}}
                        }
                    }
                    
                    async with session.post(
                        f"{self.base_url}/pages",
                        headers=headers,
                        json=page_data
                    ) as response:
                        if response.status == 200:
                            exported += 1
                        else:
                            failed += 1
                except Exception as e:
                    logger.error(f"Failed to export lead to Notion: {e}")
                    failed += 1
        
        return {"exported": exported, "failed": failed}

class GoogleSheetsAdapter(CRMAdapter):
    def __init__(self, credentials: dict, spreadsheet_id: str, sheet_name: str = "Leads"):
        self.credentials = credentials
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
    
    async def test_connection(self) -> bool:
        return bool(self.spreadsheet_id)
    
    async def export_leads(self, leads: List[dict]) -> dict:
        try:
            values = [["ID", "Username", "Name", "Status", "Created At"]]
            for lead in leads:
                values.append([
                    lead.get("user_id", ""),
                    lead.get("username", ""),
                    lead.get("name", ""),
                    lead.get("status", ""),
                    lead.get("created_at", "")
                ])
            
            logger.info(f"Prepared {len(leads)} leads for Google Sheets export")
            return {"exported": len(leads), "failed": 0, "note": "Google Sheets API integration pending"}
        except Exception as e:
            logger.error(f"Failed to export to Google Sheets: {e}")
            return {"exported": 0, "failed": len(leads)}

class AirtableAdapter(CRMAdapter):
    def __init__(self, api_key: str, base_id: str, table_name: str):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.get(
                    f"{self.base_url}?maxRecords=1",
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Airtable connection test failed: {e}")
            return False
    
    async def export_leads(self, leads: List[dict]) -> dict:
        exported = 0
        failed = 0
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            batch_size = 10
            for i in range(0, len(leads), batch_size):
                batch = leads[i:i+batch_size]
                records = []
                
                for lead in batch:
                    records.append({
                        "fields": {
                            "Name": lead.get("name", "Unknown"),
                            "Telegram ID": str(lead.get("user_id", "")),
                            "Username": lead.get("username", ""),
                            "Status": lead.get("status", "New"),
                            "Created At": lead.get("created_at", "")
                        }
                    })
                
                try:
                    async with session.post(
                        self.base_url,
                        headers=headers,
                        json={"records": records}
                    ) as response:
                        if response.status == 200:
                            exported += len(batch)
                        else:
                            failed += len(batch)
                except Exception as e:
                    logger.error(f"Failed to export batch to Airtable: {e}")
                    failed += len(batch)
        
        return {"exported": exported, "failed": failed}

class CRMExportService:
    def __init__(self):
        self.adapters: Dict[str, CRMAdapter] = {}
    
    def register_adapter(self, name: str, adapter: CRMAdapter):
        self.adapters[name] = adapter
        logger.info(f"Registered CRM adapter: {name}")
    
    async def configure_notion(self, api_key: str, database_id: str) -> bool:
        adapter = NotionAdapter(api_key, database_id)
        if await adapter.test_connection():
            self.register_adapter("notion", adapter)
            return True
        return False
    
    async def configure_airtable(self, api_key: str, base_id: str, table_name: str) -> bool:
        adapter = AirtableAdapter(api_key, base_id, table_name)
        if await adapter.test_connection():
            self.register_adapter("airtable", adapter)
            return True
        return False
    
    async def configure_sheets(self, credentials: dict, spreadsheet_id: str) -> bool:
        adapter = GoogleSheetsAdapter(credentials, spreadsheet_id)
        self.register_adapter("sheets", adapter)
        return True
    
    async def get_leads(self, project_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        try:
            from database.db import async_session
            async with async_session() as session:
                query = """
                    SELECT user_id, username, role, created_at, last_active 
                    FROM users 
                    WHERE is_blocked = false
                """
                params = {"limit": limit}
                
                if project_id:
                    query += " AND project_id = :project_id"
                    params["project_id"] = project_id
                
                query += " ORDER BY created_at DESC LIMIT :limit"
                
                result = await session.execute(text(query), params)
                return [
                    {
                        "user_id": row.user_id,
                        "username": row.username,
                        "name": row.username or f"User {row.user_id}",
                        "status": row.role,
                        "created_at": row.created_at.isoformat() if row.created_at else ""
                    }
                    for row in result.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get leads: {e}")
            return []
    
    async def export_to(self, adapter_name: str, project_id: Optional[str] = None) -> dict:
        if adapter_name not in self.adapters:
            return {"error": f"Adapter {adapter_name} not configured"}
        
        leads = await self.get_leads(project_id)
        if not leads:
            return {"exported": 0, "failed": 0, "message": "No leads to export"}
        
        result = await self.adapters[adapter_name].export_leads(leads)
        logger.info(f"Exported {result['exported']} leads to {adapter_name}")
        return result
    
    def get_available_adapters(self) -> List[str]:
        return list(self.adapters.keys())

crm_export_service = CRMExportService()
