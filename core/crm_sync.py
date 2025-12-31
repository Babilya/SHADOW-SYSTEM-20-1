import logging
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    PAUSED = "paused"


class SyncDirection(str, Enum):
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncResult:
    success: bool
    records_pushed: int = 0
    records_pulled: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CRMConnection:
    name: str
    adapter_type: str
    status: SyncStatus = SyncStatus.IDLE
    last_sync: Optional[datetime] = None
    sync_interval_minutes: int = 30
    auto_sync: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)
    sync_history: List[SyncResult] = field(default_factory=list)


class CRMSyncAdapter(ABC):
    @abstractmethod
    async def push_records(self, records: List[Dict]) -> SyncResult:
        pass
    
    @abstractmethod
    async def pull_records(self, since: Optional[datetime] = None) -> tuple:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


class NotionSyncAdapter(CRMSyncAdapter):
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def get_name(self) -> str:
        return "Notion"
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/databases/{self.database_id}",
                    headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Notion connection test failed: {e}")
            return False
    
    async def push_records(self, records: List[Dict]) -> SyncResult:
        start_time = datetime.now()
        pushed = 0
        errors = []
        
        async with aiohttp.ClientSession() as session:
            for record in records:
                try:
                    page_data = self._format_record(record)
                    async with session.post(
                        f"{self.base_url}/pages",
                        headers=self.headers,
                        json=page_data
                    ) as response:
                        if response.status in (200, 201):
                            pushed += 1
                        else:
                            errors.append(f"Record {record.get('id')}: {response.status}")
                except Exception as e:
                    errors.append(str(e))
        
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SyncResult(
            success=len(errors) == 0,
            records_pushed=pushed,
            errors=errors,
            duration_ms=duration
        )
    
    async def pull_records(self, since: Optional[datetime] = None) -> tuple:
        records = []
        errors = []
        
        try:
            async with aiohttp.ClientSession() as session:
                filter_data = {}
                if since:
                    filter_data = {
                        "filter": {
                            "property": "Last edited time",
                            "date": {"after": since.isoformat()}
                        }
                    }
                
                async with session.post(
                    f"{self.base_url}/databases/{self.database_id}/query",
                    headers=self.headers,
                    json=filter_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for page in data.get("results", []):
                            records.append(self._parse_page(page))
                    else:
                        errors.append(f"Query failed: {response.status}")
        except Exception as e:
            errors.append(str(e))
        
        return records, errors
    
    def _format_record(self, record: Dict) -> Dict:
        return {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": record.get("name", "Unknown")}}]},
                "Telegram ID": {"number": record.get("user_id", 0)},
                "Username": {"rich_text": [{"text": {"content": record.get("username", "")}}]},
                "Status": {"select": {"name": record.get("status", "New")}},
                "Source": {"rich_text": [{"text": {"content": "SHADOW SYSTEM"}}]}
            }
        }
    
    def _parse_page(self, page: Dict) -> Dict:
        props = page.get("properties", {})
        return {
            "id": page.get("id"),
            "name": self._get_title(props.get("Name", {})),
            "user_id": props.get("Telegram ID", {}).get("number"),
            "username": self._get_text(props.get("Username", {})),
            "status": self._get_select(props.get("Status", {})),
            "updated_at": page.get("last_edited_time")
        }
    
    def _get_title(self, prop: Dict) -> str:
        titles = prop.get("title", [])
        return titles[0].get("text", {}).get("content", "") if titles else ""
    
    def _get_text(self, prop: Dict) -> str:
        texts = prop.get("rich_text", [])
        return texts[0].get("text", {}).get("content", "") if texts else ""
    
    def _get_select(self, prop: Dict) -> str:
        select = prop.get("select")
        return select.get("name", "") if select else ""


class AirtableSyncAdapter(CRMSyncAdapter):
    def __init__(self, api_key: str, base_id: str, table_name: str):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_name(self) -> str:
        return "Airtable"
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}?maxRecords=1",
                    headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Airtable connection test failed: {e}")
            return False
    
    async def push_records(self, records: List[Dict]) -> SyncResult:
        start_time = datetime.now()
        pushed = 0
        errors = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(records), 10):
                batch = records[i:i+10]
                airtable_records = [
                    {
                        "fields": {
                            "Name": r.get("name", "Unknown"),
                            "Telegram ID": str(r.get("user_id", "")),
                            "Username": r.get("username", ""),
                            "Status": r.get("status", "New"),
                            "Source": "SHADOW SYSTEM"
                        }
                    }
                    for r in batch
                ]
                
                try:
                    async with session.post(
                        self.base_url,
                        headers=self.headers,
                        json={"records": airtable_records}
                    ) as response:
                        if response.status == 200:
                            pushed += len(batch)
                        else:
                            errors.append(f"Batch failed: {response.status}")
                except Exception as e:
                    errors.append(str(e))
        
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SyncResult(
            success=len(errors) == 0,
            records_pushed=pushed,
            errors=errors,
            duration_ms=duration
        )
    
    async def pull_records(self, since: Optional[datetime] = None) -> tuple:
        records = []
        errors = []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = self.base_url
                if since:
                    formula = f"IS_AFTER({{Last Modified}}, '{since.isoformat()}')"
                    url += f"?filterByFormula={formula}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for record in data.get("records", []):
                            fields = record.get("fields", {})
                            records.append({
                                "id": record.get("id"),
                                "name": fields.get("Name", ""),
                                "user_id": fields.get("Telegram ID"),
                                "username": fields.get("Username", ""),
                                "status": fields.get("Status", "")
                            })
                    else:
                        errors.append(f"Query failed: {response.status}")
        except Exception as e:
            errors.append(str(e))
        
        return records, errors


class WebhookSyncAdapter(CRMSyncAdapter):
    def __init__(self, push_url: str, pull_url: Optional[str] = None, headers: Optional[Dict] = None):
        self.push_url = push_url
        self.pull_url = pull_url
        self.custom_headers = headers or {}
    
    def get_name(self) -> str:
        return "Webhook"
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    self.push_url,
                    headers=self.custom_headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status < 500
        except Exception:
            return True
    
    async def push_records(self, records: List[Dict]) -> SyncResult:
        start_time = datetime.now()
        errors = []
        
        payload = {
            "source": "shadow_system",
            "timestamp": datetime.now().isoformat(),
            "records": records,
            "count": len(records)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json", **self.custom_headers}
                async with session.post(
                    self.push_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status not in (200, 201, 202, 204):
                        errors.append(f"Webhook returned {response.status}")
        except Exception as e:
            errors.append(str(e))
        
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SyncResult(
            success=len(errors) == 0,
            records_pushed=len(records) if not errors else 0,
            errors=errors,
            duration_ms=duration
        )
    
    async def pull_records(self, since: Optional[datetime] = None) -> tuple:
        if not self.pull_url:
            return [], ["Pull URL not configured"]
        
        records = []
        errors = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {}
                if since:
                    params["since"] = since.isoformat()
                
                async with session.get(
                    self.pull_url,
                    headers=self.custom_headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        records = data.get("records", [])
                    else:
                        errors.append(f"Pull failed: {response.status}")
        except Exception as e:
            errors.append(str(e))
        
        return records, errors


class CRMSyncService:
    def __init__(self):
        self.connections: Dict[str, CRMConnection] = {}
        self.adapters: Dict[str, CRMSyncAdapter] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self.data_providers: Dict[str, Callable] = {}
        self.data_handlers: Dict[str, Callable] = {}
        self.stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "records_pushed": 0,
            "records_pulled": 0
        }
    
    def register_data_provider(self, name: str, provider: Callable):
        self.data_providers[name] = provider
    
    def register_data_handler(self, name: str, handler: Callable):
        self.data_handlers[name] = handler
    
    async def add_connection(
        self,
        name: str,
        adapter: CRMSyncAdapter,
        sync_interval_minutes: int = 30,
        auto_sync: bool = False
    ) -> bool:
        if not await adapter.test_connection():
            logger.error(f"Failed to connect to {adapter.get_name()}")
            return False
        
        connection = CRMConnection(
            name=name,
            adapter_type=adapter.get_name(),
            sync_interval_minutes=sync_interval_minutes,
            auto_sync=auto_sync
        )
        
        self.connections[name] = connection
        self.adapters[name] = adapter
        
        if auto_sync:
            self._start_auto_sync(name)
        
        logger.info(f"CRM connection added: {name} ({adapter.get_name()})")
        return True
    
    def _start_auto_sync(self, connection_name: str):
        if connection_name in self.sync_tasks:
            self.sync_tasks[connection_name].cancel()
        
        task = asyncio.create_task(self._auto_sync_loop(connection_name))
        self.sync_tasks[connection_name] = task
    
    async def _auto_sync_loop(self, connection_name: str):
        connection = self.connections.get(connection_name)
        if not connection:
            return
        
        while connection.auto_sync:
            try:
                await self.sync(connection_name, SyncDirection.PUSH)
                await asyncio.sleep(connection.sync_interval_minutes * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-sync error for {connection_name}: {e}")
                await asyncio.sleep(60)
    
    async def sync(
        self,
        connection_name: str,
        direction: SyncDirection = SyncDirection.PUSH,
        records: Optional[List[Dict]] = None
    ) -> SyncResult:
        connection = self.connections.get(connection_name)
        adapter = self.adapters.get(connection_name)
        
        if not connection or not adapter:
            return SyncResult(success=False, errors=["Connection not found"])
        
        connection.status = SyncStatus.SYNCING
        self.stats["total_syncs"] += 1
        
        result = SyncResult(success=True)
        start_time = datetime.now()
        
        try:
            if direction in (SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL):
                if records is None:
                    provider = self.data_providers.get("default")
                    if provider:
                        records = await provider() if asyncio.iscoroutinefunction(provider) else provider()
                    else:
                        records = []
                
                if records:
                    push_result = await adapter.push_records(records)
                    result.records_pushed = push_result.records_pushed
                    result.errors.extend(push_result.errors)
                    self.stats["records_pushed"] += push_result.records_pushed
            
            if direction in (SyncDirection.PULL, SyncDirection.BIDIRECTIONAL):
                pulled_records, pull_errors = await adapter.pull_records(connection.last_sync)
                result.records_pulled = len(pulled_records)
                result.errors.extend(pull_errors)
                self.stats["records_pulled"] += len(pulled_records)
                
                handler = self.data_handlers.get("default")
                if handler and pulled_records:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(pulled_records)
                    else:
                        handler(pulled_records)
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        result.duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        connection.status = SyncStatus.IDLE if result.success else SyncStatus.ERROR
        connection.last_sync = datetime.now()
        connection.sync_history.append(result)
        
        if len(connection.sync_history) > 100:
            connection.sync_history = connection.sync_history[-100:]
        
        if result.success:
            self.stats["successful_syncs"] += 1
        else:
            self.stats["failed_syncs"] += 1
        
        logger.info(f"Sync completed for {connection_name}: pushed={result.records_pushed}, pulled={result.records_pulled}")
        
        return result
    
    def pause_sync(self, connection_name: str):
        connection = self.connections.get(connection_name)
        if connection:
            connection.auto_sync = False
            connection.status = SyncStatus.PAUSED
            if connection_name in self.sync_tasks:
                self.sync_tasks[connection_name].cancel()
    
    def resume_sync(self, connection_name: str):
        connection = self.connections.get(connection_name)
        if connection:
            connection.auto_sync = True
            self._start_auto_sync(connection_name)
    
    def get_connection_status(self, connection_name: str) -> Optional[Dict[str, Any]]:
        connection = self.connections.get(connection_name)
        if not connection:
            return None
        
        recent_syncs = connection.sync_history[-5:] if connection.sync_history else []
        
        return {
            "name": connection.name,
            "adapter": connection.adapter_type,
            "status": connection.status.value,
            "auto_sync": connection.auto_sync,
            "sync_interval": connection.sync_interval_minutes,
            "last_sync": connection.last_sync.isoformat() if connection.last_sync else None,
            "recent_syncs": [
                {
                    "success": s.success,
                    "pushed": s.records_pushed,
                    "pulled": s.records_pulled,
                    "errors": len(s.errors),
                    "duration_ms": s.duration_ms,
                    "timestamp": s.timestamp.isoformat()
                }
                for s in recent_syncs
            ]
        }
    
    def get_all_connections(self) -> List[Dict[str, Any]]:
        return [
            self.get_connection_status(name)
            for name in self.connections
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "active_connections": len(self.connections),
            "auto_sync_active": sum(1 for c in self.connections.values() if c.auto_sync)
        }
    
    def format_status_message(self) -> str:
        connections = self.get_all_connections()
        
        if not connections:
            return "❌ Немає налаштованих CRM підключень"
        
        status_icons = {
            "idle": "🟢",
            "syncing": "🔄",
            "error": "🔴",
            "paused": "⏸️"
        }
        
        conn_lines = []
        for conn in connections:
            icon = status_icons.get(conn["status"], "⚪")
            last_sync = conn["last_sync"][:16] if conn["last_sync"] else "Ніколи"
            conn_lines.append(
                f"{icon} <b>{conn['name']}</b> ({conn['adapter']})\n"
                f"   └ Остання синхронізація: {last_sync}"
            )
        
        stats = self.get_stats()
        
        return f"""🔄 <b>CRM СИНХРОНІЗАЦІЯ</b>

<b>Підключення:</b>
{chr(10).join(conn_lines)}

───────────────

<b>📊 Статистика:</b>
├ Всього синхронізацій: {stats['total_syncs']}
├ Успішних: {stats['successful_syncs']}
├ Помилок: {stats['failed_syncs']}
├ Записів відправлено: {stats['records_pushed']}
└ Записів отримано: {stats['records_pulled']}"""


crm_sync_service = CRMSyncService()
