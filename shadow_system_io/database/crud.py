import json
from config.database import execute_query, fetchrow_query, fetch_query

async def create_bot(data: dict):
    query = """
        INSERT INTO bots (bot_id, phone_number, session_string, proxy_config, status, created_at)
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    await execute_query(query, data['bot_id'], data['phone_number'], 
                        data['session_string'], data['proxy_config'], 
                        data['status'], data['created_at'])

async def create_campaign(data: dict):
    query = """
        INSERT INTO campaigns (id, name, creator_id, project_id, status, recipients, messages, schedule, settings, stats, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """
    await execute_query(query, data['id'], data['name'], data['creator_id'], 
                        data.get('project_id'), data['status'], 
                        json.dumps(data['recipients']), json.dumps(data['messages']), 
                        json.dumps(data['schedule']), json.dumps(data['settings']), 
                        json.dumps(data['stats']), data['created_at'])

async def get_campaign(campaign_id: str):
    row = await fetchrow_query("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if row:
        data = dict(row)
        for field in ['recipients', 'messages', 'schedule', 'settings', 'stats']:
            if isinstance(data[field], str):
                data[field] = json.loads(data[field])
        return data
    return None

async def create_delivery_log(data: dict):
    query = """
        INSERT INTO delivery_logs (campaign_id, bot_id, recipient_type, recipient_value, message_id, success, error, sent_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """
    await execute_query(query, data['campaign_id'], data['bot_id'], 
                        data['recipient_type'], data['recipient_value'], 
                        data['message_id'], data['success'], 
                        data['error'], data['sent_at'])
