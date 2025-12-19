import logging
from database.crud import (
    get_user, get_project, get_all_projects, get_admin_projects
)

logger = logging.getLogger(__name__)

class RBACManager:
    """Role-Based Access Control Manager"""
    
    ROLES = {
        "superadmin": {"level": 3, "permissions": ["*"]},
        "admin": {"level": 2, "permissions": ["manage_project", "manage_bots", "manage_campaigns", "view_stats"]},
        "manager": {"level": 1, "permissions": ["manage_bots", "send_messages", "view_stats"]},
    }
    
    @staticmethod
    async def can_access(user_id: int, action: str) -> bool:
        """Check if user can perform action"""
        user = await get_user(user_id)
        if not user:
            return False
        
        role = user.get("role", "manager")
        role_info = RBACManager.ROLES.get(role, {})
        permissions = role_info.get("permissions", [])
        
        return "*" in permissions or action in permissions
    
    @staticmethod
    async def can_manage_project(user_id: int, project_id: str) -> bool:
        """Check if user can manage specific project"""
        user = await get_user(user_id)
        if not user:
            return False
        
        role = user.get("role", "manager")
        
        # Superadmin can manage all
        if role == "superadmin":
            return True
        
        # Admin can only manage own project
        if role == "admin":
            project = await get_project(project_id)
            return project and project.get("admin_id") == user_id
        
        # Manager can only manage assigned project
        return user.get("project_id") == project_id
    
    @staticmethod
    async def get_user_projects(user_id: int):
        """Get projects visible to user"""
        user = await get_user(user_id)
        if not user:
            return []
        
        role = user.get("role", "manager")
        
        # Superadmin sees all
        if role == "superadmin":
            return await get_all_projects()
        
        # Admin sees own
        if role == "admin":
            return await get_admin_projects(user_id)
        
        # Manager sees assigned
        project_id = user.get("project_id")
        if project_id:
            project = await get_project(project_id)
            return [project] if project else []
        return []

rbac = RBACManager()
