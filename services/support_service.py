import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class SupportService:
    """Сервіс системи підтримки"""
    
    CATEGORIES = {
        'technical': 'Технічна підтримка',
        'billing': 'Питання оплати',
        'account': 'Акаунт та доступ',
        'feature': 'Запит функції',
        'bug': 'Повідомлення про баг',
        'general': 'Загальне питання'
    }
    
    PRIORITIES = {
        'low': {'name': 'Низький', 'icon': '🟢'},
        'normal': {'name': 'Звичайний', 'icon': '🟡'},
        'high': {'name': 'Високий', 'icon': '🟠'},
        'urgent': {'name': 'Терміновий', 'icon': '🔴'}
    }
    
    STATUSES = {
        'open': {'name': 'Відкритий', 'icon': '📂'},
        'in_progress': {'name': 'В роботі', 'icon': '🔄'},
        'waiting': {'name': 'Очікує відповіді', 'icon': '⏳'},
        'resolved': {'name': 'Вирішено', 'icon': '✅'},
        'closed': {'name': 'Закритий', 'icon': '📁'}
    }
    
    def _generate_ticket_code(self) -> str:
        """Генерація коду тікета"""
        return f"TKT-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    async def create_ticket(
        self,
        session: AsyncSession,
        user_id: str,
        user_role: str,
        subject: str,
        message: str,
        category: str = 'general',
        priority: str = 'normal',
        project_id: int = None
    ) -> Dict[str, Any]:
        """Створення нового тікета"""
        from database.models import SupportTicket, TicketMessage
        
        ticket_code = self._generate_ticket_code()
        
        ticket = SupportTicket(
            ticket_code=ticket_code,
            user_id=user_id,
            user_role=user_role,
            subject=subject,
            category=category,
            priority=priority,
            project_id=project_id,
            status='open'
        )
        
        session.add(ticket)
        await session.flush()
        
        first_message = TicketMessage(
            ticket_id=ticket.id,
            sender_id=user_id,
            sender_role=user_role,
            message=message
        )
        
        session.add(first_message)
        await session.commit()
        await session.refresh(ticket)
        
        logger.info(f"Created ticket {ticket_code} from user {user_id}")
        
        return {
            'id': ticket.id,
            'ticket_code': ticket_code,
            'subject': subject,
            'category': self.CATEGORIES.get(category, category),
            'priority': self.PRIORITIES.get(priority, {}).get('name', priority),
            'status': 'open'
        }
    
    async def get_tickets(
        self,
        session: AsyncSession,
        user_id: str = None,
        admin_id: str = None,
        status: str = None,
        project_id: int = None,
        limit: int = 50
    ) -> List[Dict]:
        """Отримання списку тікетів"""
        from database.models import SupportTicket
        
        query = select(SupportTicket)
        
        if user_id:
            query = query.where(SupportTicket.user_id == user_id)
        if admin_id:
            query = query.where(SupportTicket.assigned_admin_id == admin_id)
        if status:
            query = query.where(SupportTicket.status == status)
        if project_id:
            query = query.where(SupportTicket.project_id == project_id)
        
        query = query.order_by(SupportTicket.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        tickets = result.scalars().all()
        
        return [
            {
                'id': t.id,
                'ticket_code': t.ticket_code,
                'subject': t.subject,
                'category': self.CATEGORIES.get(t.category, t.category),
                'priority': self.PRIORITIES.get(t.priority, {}).get('name', t.priority),
                'priority_icon': self.PRIORITIES.get(t.priority, {}).get('icon', ''),
                'status': self.STATUSES.get(t.status, {}).get('name', t.status),
                'status_icon': self.STATUSES.get(t.status, {}).get('icon', ''),
                'user_role': t.user_role,
                'assigned_admin_id': t.assigned_admin_id,
                'created_at': t.created_at.strftime('%d.%m.%Y %H:%M'),
                'updated_at': t.updated_at.strftime('%d.%m.%Y %H:%M')
            }
            for t in tickets
        ]
    
    async def get_ticket(self, session: AsyncSession, ticket_id: int) -> Optional[Dict]:
        """Отримання тікета за ID"""
        from database.models import SupportTicket
        
        result = await session.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            return None
        
        messages = await self.get_ticket_messages(session, ticket_id)
        
        return {
            'id': ticket.id,
            'ticket_code': ticket.ticket_code,
            'user_id': ticket.user_id,
            'user_role': ticket.user_role,
            'assigned_admin_id': ticket.assigned_admin_id,
            'subject': ticket.subject,
            'category': ticket.category,
            'category_name': self.CATEGORIES.get(ticket.category, ticket.category),
            'priority': ticket.priority,
            'priority_name': self.PRIORITIES.get(ticket.priority, {}).get('name', ticket.priority),
            'status': ticket.status,
            'status_name': self.STATUSES.get(ticket.status, {}).get('name', ticket.status),
            'project_id': ticket.project_id,
            'rating': ticket.rating,
            'created_at': ticket.created_at.strftime('%d.%m.%Y %H:%M'),
            'closed_at': ticket.closed_at.strftime('%d.%m.%Y %H:%M') if ticket.closed_at else None,
            'messages': messages
        }
    
    async def get_ticket_messages(self, session: AsyncSession, ticket_id: int) -> List[Dict]:
        """Отримання повідомлень тікета"""
        from database.models import TicketMessage
        
        result = await session.execute(
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at)
        )
        messages = result.scalars().all()
        
        return [
            {
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_role': m.sender_role,
                'message': m.message,
                'attachments': json.loads(m.attachments) if m.attachments else [],
                'is_internal': m.is_internal,
                'created_at': m.created_at.strftime('%d.%m.%Y %H:%M')
            }
            for m in messages
        ]
    
    async def add_message(
        self,
        session: AsyncSession,
        ticket_id: int,
        sender_id: str,
        sender_role: str,
        message: str,
        attachments: List[str] = None,
        is_internal: bool = False
    ) -> Dict:
        """Додавання повідомлення до тікета"""
        from database.models import SupportTicket, TicketMessage
        
        ticket_msg = TicketMessage(
            ticket_id=ticket_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message=message,
            attachments=json.dumps(attachments or []),
            is_internal=is_internal
        )
        
        session.add(ticket_msg)
        
        await session.execute(
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .values(updated_at=datetime.now())
        )
        
        await session.commit()
        await session.refresh(ticket_msg)
        
        return {
            'id': ticket_msg.id,
            'sender_role': sender_role,
            'created_at': ticket_msg.created_at.strftime('%d.%m.%Y %H:%M')
        }
    
    async def assign_ticket(
        self,
        session: AsyncSession,
        ticket_id: int,
        admin_id: str
    ) -> bool:
        """Призначення тікета адміністратору"""
        from database.models import SupportTicket
        
        await session.execute(
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .values(
                assigned_admin_id=admin_id,
                status='in_progress',
                updated_at=datetime.now()
            )
        )
        await session.commit()
        
        return True
    
    async def update_status(
        self,
        session: AsyncSession,
        ticket_id: int,
        status: str
    ) -> bool:
        """Оновлення статусу тікета"""
        from database.models import SupportTicket
        
        values = {
            'status': status,
            'updated_at': datetime.now()
        }
        
        if status in ['resolved', 'closed']:
            values['closed_at'] = datetime.now()
        
        await session.execute(
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .values(**values)
        )
        await session.commit()
        
        return True
    
    async def rate_ticket(
        self,
        session: AsyncSession,
        ticket_id: int,
        rating: int
    ) -> bool:
        """Оцінка тікета"""
        from database.models import SupportTicket
        
        await session.execute(
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .values(rating=rating)
        )
        await session.commit()
        
        return True
    
    async def get_stats(self, session: AsyncSession, admin_id: str = None) -> Dict:
        """Статистика тікетів"""
        from database.models import SupportTicket
        
        query = select(
            SupportTicket.status,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.status)
        
        if admin_id:
            query = query.where(SupportTicket.assigned_admin_id == admin_id)
        
        result = await session.execute(query)
        status_counts = dict(result.all())
        
        return {
            'open': status_counts.get('open', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'waiting': status_counts.get('waiting', 0),
            'resolved': status_counts.get('resolved', 0),
            'closed': status_counts.get('closed', 0),
            'total': sum(status_counts.values())
        }

support_service = SupportService()
