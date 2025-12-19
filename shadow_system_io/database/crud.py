import json
from datetime import datetime
from config.database import execute_query, fetchrow_query, fetch_query

# ============ USERS (RBAC) ============
async def create_user(user_id: int, username: str, role: str = "manager", project_id: str = None):
    query = """
        INSERT INTO users (user_id, username, role, project_id, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO NOTHING
    """
    await execute_query(query, user_id, username, role, project_id, datetime.now())

async def get_user(user_id: int):
    row = await fetchrow_query("SELECT * FROM users WHERE user_id = $1", user_id)
    return dict(row) if row else None

async def update_user_role(user_id: int, role: str):
    query = "UPDATE users SET role = $1 WHERE user_id = $2"
    await execute_query(query, role, user_id)

async def get_users_by_role(role: str):
    query = "SELECT * FROM users WHERE role = $1"
    rows = await fetch_query(query, role)
    return [dict(row) for row in rows] if rows else []

# ============ PROJECTS ============
async def create_project(project_id: str, admin_id: int, name: str, description: str = ""):
    query = """
        INSERT INTO projects (project_id, admin_id, name, description, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (project_id) DO NOTHING
    """
    await execute_query(query, project_id, admin_id, name, description, datetime.now())

async def get_project(project_id: str):
    row = await fetchrow_query("SELECT * FROM projects WHERE project_id = $1", project_id)
    return dict(row) if row else None

async def get_admin_projects(admin_id: int):
    query = "SELECT * FROM projects WHERE admin_id = $1"
    rows = await fetch_query(query, admin_id)
    return [dict(row) for row in rows] if rows else []

async def get_all_projects():
    query = "SELECT * FROM projects"
    rows = await fetch_query(query)
    return [dict(row) for row in rows] if rows else []

# ============ BOTS ============
async def create_bot(bot_id: str, project_id: str, phone_number: str = None, session_string: str = None):
    query = """
        INSERT INTO bots (bot_id, project_id, phone_number, session_string, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (bot_id) DO NOTHING
    """
    await execute_query(query, bot_id, project_id, phone_number, session_string, datetime.now())

async def get_bot(bot_id: str):
    row = await fetchrow_query("SELECT * FROM bots WHERE bot_id = $1", bot_id)
    return dict(row) if row else None

async def get_project_bots(project_id: str):
    query = "SELECT * FROM bots WHERE project_id = $1"
    rows = await fetch_query(query, project_id)
    return [dict(row) for row in rows] if rows else []

async def update_bot_status(bot_id: str, status: str):
    query = "UPDATE bots SET status = $1, last_active = $2 WHERE bot_id = $3"
    await execute_query(query, status, datetime.now(), bot_id)

# ============ CAMPAIGNS ============
async def create_campaign(campaign_id: str, project_id: str, name: str, creator_id: int, 
                         recipients: dict, messages: dict, schedule: dict = None):
    query = """
        INSERT INTO campaigns 
        (id, project_id, name, creator_id, status, recipients, messages, schedule, stats, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    """
    await execute_query(query, campaign_id, project_id, name, creator_id, 'pending',
                       json.dumps(recipients), json.dumps(messages), 
                       json.dumps(schedule or {}), json.dumps({"sent": 0, "delivered": 0, "failed": 0}),
                       datetime.now())

async def get_campaign(campaign_id: str):
    row = await fetchrow_query("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if row:
        data = dict(row)
        for field in ['recipients', 'messages', 'schedule', 'stats']:
            if isinstance(data.get(field), str):
                data[field] = json.loads(data[field])
        return data
    return None

async def update_campaign_status(campaign_id: str, status: str):
    query = "UPDATE campaigns SET status = $1 WHERE id = $2"
    await execute_query(query, status, campaign_id)

# ============ DELIVERY LOGS ============
async def create_delivery_log(campaign_id: str, bot_id: str, recipient_type: str, 
                             recipient_value: str, success: bool, error: str = None):
    query = """
        INSERT INTO delivery_logs 
        (campaign_id, bot_id, recipient_type, recipient_value, success, error, sent_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await execute_query(query, campaign_id, bot_id, recipient_type, recipient_value, 
                       success, error, datetime.now())

async def get_campaign_stats(campaign_id: str):
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE success = true) as delivered,
            COUNT(*) FILTER (WHERE success = false) as failed
        FROM delivery_logs 
        WHERE campaign_id = $1
    """
    row = await fetchrow_query(query, campaign_id)
    return dict(row) if row else {"total": 0, "delivered": 0, "failed": 0}

# ============ AUDIT LOGS ============
async def create_audit_log(user_id: int, action: str, resource_type: str, 
                          resource_id: str, details: dict = None):
    query = """
        INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, created_at)
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    await execute_query(query, user_id, action, resource_type, resource_id, 
                       json.dumps(details or {}), datetime.now())
