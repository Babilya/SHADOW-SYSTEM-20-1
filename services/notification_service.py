import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.role_constants import UserRole

logger = logging.getLogger(__name__)

class NotificationService:
    """Сервіс сповіщень з таргетингом по ролям"""
    
    TYPES = {
        'info': {'name': 'Інформація', 'icon': 'ℹ️'},
        'warning': {'name': 'Попередження', 'icon': '⚠️'},
        'success': {'name': 'Успіх', 'icon': '✅'},
        'error': {'name': 'Помилка', 'icon': '❌'},
        'announcement': {'name': 'Оголошення', 'icon': '📢'},
        'update': {'name': 'Оновлення', 'icon': '🔄'},
        'maintenance': {'name': 'Техроботи', 'icon': '🔧'}
    }
    
    PRIORITIES = {
        'low': 1,
        'normal': 2,
        'high': 3,
        'urgent': 4
    }
    
    TARGET_TYPES = {
        'all': 'Всі користувачі',
        'role': 'За роллю',
        'multi_role': 'Декілька ролей',
        'personal': 'Персональні',
        'project': 'По проекту'
    }
    
    def __init__(self):
        self.send_callback: Optional[Callable] = None
    
    def set_send_callback(self, callback: Callable):
        """Встановлення callback для відправки повідомлень"""
        self.send_callback = callback
    
    async def create_notification(
        self,
        session: AsyncSession,
        sender_id: str,
        title: str,
        message: str,
        notification_type: str = 'info',
        target_type: str = 'all',
        target_roles: List[str] = None,
        target_user_ids: List[str] = None,
        priority: str = 'normal',
        expires_at: datetime = None
    ) -> Dict[str, Any]:
        """Створення сповіщення"""
        from database.models import SystemNotification
        
        notification = SystemNotification(
            sender_id=sender_id,
            title=title,
            message=message,
            notification_type=notification_type,
            target_type=target_type,
            target_roles=json.dumps(target_roles or []),
            target_user_ids=json.dumps(target_user_ids or []),
            priority=priority,
            expires_at=expires_at
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        logger.info(f"Created notification {notification.id}: {title}")
        
        return {
            'id': notification.id,
            'title': title,
            'type': notification_type,
            'target_type': target_type
        }
    
    async def send_notification(
        self,
        session: AsyncSession,
        notification_id: int
    ) -> Dict[str, Any]:
        """Відправка сповіщення"""
        from database.models import SystemNotification, User
        
        result = await session.execute(
            select(SystemNotification).where(SystemNotification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return {'success': False, 'error': 'Notification not found'}
        
        users_query = select(User).where(User.is_blocked == False)
        
        if notification.target_type == 'role':
            target_roles = json.loads(notification.target_roles)
            if target_roles:
                users_query = users_query.where(User.role.in_(target_roles))
        
        elif notification.target_type == 'multi_role':
            target_roles = json.loads(notification.target_roles)
            if target_roles:
                users_query = users_query.where(User.role.in_(target_roles))
        
        elif notification.target_type == 'personal':
            target_ids = json.loads(notification.target_user_ids)
            if target_ids:
                users_query = users_query.where(User.telegram_id.in_(target_ids))
        
        result = await session.execute(users_query)
        users = result.scalars().all()
        
        sent_count = 0
        failed_count = 0
        
        type_info = self.TYPES.get(notification.notification_type, {})
        icon = type_info.get('icon', 'ℹ️')
        
        formatted_message = f"""
{icon} <b>{notification.title}</b>

{notification.message}

<i>Системне сповіщення</i>
"""
        
        if self.send_callback:
            for user in users:
                try:
                    await self.send_callback(user.telegram_id, formatted_message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send notification to {user.telegram_id}: {e}")
                    failed_count += 1
        
        return {
            'success': True,
            'sent': sent_count,
            'failed': failed_count,
            'total': len(users)
        }
    
    async def get_notifications(
        self,
        session: AsyncSession,
        user_id: str = None,
        user_role: str = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Отримання сповіщень для користувача"""
        from database.models import SystemNotification
        
        query = select(SystemNotification)
        
        now = datetime.now()
        query = query.where(
            or_(
                SystemNotification.expires_at.is_(None),
                SystemNotification.expires_at > now
            )
        )
        
        query = query.order_by(
            SystemNotification.priority.desc(),
            SystemNotification.created_at.desc()
        ).limit(limit)
        
        result = await session.execute(query)
        notifications = result.scalars().all()
        
        user_notifications = []
        
        for n in notifications:
            target_roles = json.loads(n.target_roles) if n.target_roles else []
            target_user_ids = json.loads(n.target_user_ids) if n.target_user_ids else []
            read_by = json.loads(n.read_by) if n.read_by else []
            
            is_target = False
            if n.target_type == 'all':
                is_target = True
            elif n.target_type in ['role', 'multi_role'] and user_role in target_roles:
                is_target = True
            elif n.target_type == 'personal' and user_id in target_user_ids:
                is_target = True
            
            if not is_target:
                continue
            
            is_read = user_id in read_by
            
            if unread_only and is_read:
                continue
            
            type_info = self.TYPES.get(n.notification_type, {})
            
            user_notifications.append({
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'type_name': type_info.get('name', n.notification_type),
                'type_icon': type_info.get('icon', 'ℹ️'),
                'priority': n.priority,
                'is_read': is_read,
                'created_at': n.created_at.strftime('%d.%m.%Y %H:%M')
            })
        
        return user_notifications
    
    async def mark_as_read(
        self,
        session: AsyncSession,
        notification_id: int,
        user_id: str
    ) -> bool:
        """Позначити як прочитане"""
        from database.models import SystemNotification
        
        result = await session.execute(
            select(SystemNotification).where(SystemNotification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        read_by = json.loads(notification.read_by) if notification.read_by else []
        if user_id not in read_by:
            read_by.append(user_id)
            notification.read_by = json.dumps(read_by)
            await session.commit()
        
        return True
    
    async def delete_notification(self, session: AsyncSession, notification_id: int) -> bool:
        """Видалення сповіщення"""
        from database.models import SystemNotification
        
        await session.execute(
            delete(SystemNotification).where(SystemNotification.id == notification_id)
        )
        await session.commit()
        
        return True

class BanService:
    """Сервіс системи банів"""
    
    BAN_TYPES = {
        'temporary': 'Тимчасовий',
        'permanent': 'Постійний',
        'warning': 'Попередження'
    }
    
    async def ban_user(
        self,
        session: AsyncSession,
        user_id: str,
        banned_by: str,
        reason: str,
        ban_type: str = 'temporary',
        duration_hours: int = None,
        can_appeal: bool = True
    ) -> Dict[str, Any]:
        """Бан користувача"""
        from database.models import UserBan, User
        
        expires_at = None
        if ban_type == 'temporary' and duration_hours:
            expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        ban = UserBan(
            user_id=user_id,
            banned_by=banned_by,
            reason=reason,
            ban_type=ban_type,
            expires_at=expires_at,
            can_appeal=can_appeal
        )
        
        session.add(ban)
        
        await session.execute(
            update(User)
            .where(User.telegram_id == user_id)
            .values(is_blocked=True)
        )
        
        await session.commit()
        await session.refresh(ban)
        
        logger.warning(f"User {user_id} banned by {banned_by}: {reason}")
        
        return {
            'id': ban.id,
            'user_id': user_id,
            'ban_type': self.BAN_TYPES.get(ban_type, ban_type),
            'expires_at': expires_at.strftime('%d.%m.%Y %H:%M') if expires_at else 'Безстроково'
        }
    
    async def unban_user(
        self,
        session: AsyncSession,
        user_id: str
    ) -> bool:
        """Розбан користувача"""
        from database.models import UserBan, User
        
        await session.execute(
            update(UserBan)
            .where(
                UserBan.user_id == user_id,
                UserBan.is_active == True
            )
            .values(is_active=False)
        )
        
        await session.execute(
            update(User)
            .where(User.telegram_id == user_id)
            .values(is_blocked=False)
        )
        
        await session.commit()
        
        logger.info(f"User {user_id} unbanned")
        
        return True
    
    async def get_user_bans(
        self,
        session: AsyncSession,
        user_id: str,
        active_only: bool = True
    ) -> List[Dict]:
        """Отримання банів користувача"""
        from database.models import UserBan
        
        query = select(UserBan).where(UserBan.user_id == user_id)
        
        if active_only:
            query = query.where(UserBan.is_active == True)
        
        query = query.order_by(UserBan.created_at.desc())
        
        result = await session.execute(query)
        bans = result.scalars().all()
        
        return [
            {
                'id': b.id,
                'reason': b.reason,
                'ban_type': self.BAN_TYPES.get(b.ban_type, b.ban_type),
                'banned_by': b.banned_by,
                'expires_at': b.expires_at.strftime('%d.%m.%Y %H:%M') if b.expires_at else 'Безстроково',
                'is_active': b.is_active,
                'can_appeal': b.can_appeal,
                'created_at': b.created_at.strftime('%d.%m.%Y %H:%M')
            }
            for b in bans
        ]
    
    async def get_all_bans(
        self,
        session: AsyncSession,
        active_only: bool = True,
        limit: int = 100
    ) -> List[Dict]:
        """Отримання всіх банів"""
        from database.models import UserBan
        
        query = select(UserBan)
        
        if active_only:
            query = query.where(UserBan.is_active == True)
        
        query = query.order_by(UserBan.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        bans = result.scalars().all()
        
        return [
            {
                'id': b.id,
                'user_id': b.user_id,
                'reason': b.reason[:50] + '...' if len(b.reason) > 50 else b.reason,
                'ban_type': self.BAN_TYPES.get(b.ban_type, b.ban_type),
                'expires_at': b.expires_at.strftime('%d.%m.%Y') if b.expires_at else '∞',
                'created_at': b.created_at.strftime('%d.%m.%Y')
            }
            for b in bans
        ]
    
    async def submit_appeal(
        self,
        session: AsyncSession,
        ban_id: int,
        appeal_text: str
    ) -> bool:
        """Подання апеляції"""
        from database.models import UserBan
        
        result = await session.execute(
            select(UserBan).where(UserBan.id == ban_id)
        )
        ban = result.scalar_one_or_none()
        
        if not ban or not ban.can_appeal:
            return False
        
        ban.appeal_text = appeal_text
        await session.commit()
        
        return True
    
    async def check_expired_bans(self, session: AsyncSession) -> int:
        """Перевірка прострочених банів"""
        from database.models import UserBan, User
        
        now = datetime.now()
        
        result = await session.execute(
            select(UserBan)
            .where(
                UserBan.is_active == True,
                UserBan.expires_at.isnot(None),
                UserBan.expires_at <= now
            )
        )
        expired_bans = result.scalars().all()
        
        for ban in expired_bans:
            ban.is_active = False
            
            await session.execute(
                update(User)
                .where(User.telegram_id == ban.user_id)
                .values(is_blocked=False)
            )
        
        await session.commit()
        
        return len(expired_bans)

class ProjectStatsService:
    """Сервіс статистики проектів"""
    
    async def record_stat(
        self,
        session: AsyncSession,
        project_id: int,
        stat_type: str,
        value: int = 1
    ):
        """Запис статистики"""
        from database.models import ProjectStats
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await session.execute(
            select(ProjectStats)
            .where(
                ProjectStats.project_id == project_id,
                ProjectStats.date >= today
            )
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = ProjectStats(project_id=project_id, date=today)
            session.add(stats)
        
        current = getattr(stats, stat_type, 0)
        setattr(stats, stat_type, current + value)
        
        await session.commit()
    
    async def get_project_stats(
        self,
        session: AsyncSession,
        project_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """Отримання статистики проекту"""
        from database.models import ProjectStats, Project, Manager, Campaign
        from sqlalchemy import func
        
        project_result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            return None
        
        since = datetime.now() - timedelta(days=days)
        
        stats_result = await session.execute(
            select(ProjectStats)
            .where(
                ProjectStats.project_id == project_id,
                ProjectStats.date >= since
            )
            .order_by(ProjectStats.date)
        )
        daily_stats = stats_result.scalars().all()
        
        totals = {
            'messages_sent': sum(s.messages_sent for s in daily_stats),
            'messages_delivered': sum(s.messages_delivered for s in daily_stats),
            'messages_failed': sum(s.messages_failed for s in daily_stats),
            'new_users': sum(s.new_users for s in daily_stats),
            'campaigns_launched': sum(s.campaigns_launched for s in daily_stats),
            'osint_reports': sum(s.osint_reports for s in daily_stats)
        }
        
        managers_count = await session.execute(
            select(func.count(Manager.id))
            .where(Manager.project_id == project_id, Manager.is_active == True)
        )
        
        campaigns_count = await session.execute(
            select(func.count(Campaign.id))
            .where(Campaign.project_id == project_id)
        )
        
        delivery_rate = 0
        if totals['messages_sent'] > 0:
            delivery_rate = (totals['messages_delivered'] / totals['messages_sent']) * 100
        
        return {
            'project_id': project_id,
            'project_name': project.name,
            'period_days': days,
            'totals': totals,
            'delivery_rate': round(delivery_rate, 2),
            'managers_count': managers_count.scalar() or 0,
            'campaigns_count': campaigns_count.scalar() or 0,
            'bots_used': project.bots_used,
            'bots_limit': project.bots_limit,
            'daily_breakdown': [
                {
                    'date': s.date.strftime('%d.%m'),
                    'sent': s.messages_sent,
                    'delivered': s.messages_delivered
                }
                for s in daily_stats
            ]
        }

notification_service = NotificationService()
ban_service = BanService()
project_stats_service = ProjectStatsService()
