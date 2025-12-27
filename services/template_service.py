import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class TemplateService:
    """Сервіс управління шаблонами розсилок"""
    
    CATEGORIES = {
        'welcome': 'Привітальні',
        'promo': 'Промо',
        'news': 'Новини',
        'reminder': 'Нагадування',
        'alert': 'Сповіщення',
        'general': 'Загальні'
    }
    
    async def create_template(
        self,
        session: AsyncSession,
        owner_id: str,
        name: str,
        content: str,
        category: str = 'general',
        project_id: int = None,
        media_file_id: str = None,
        media_type: str = None,
        buttons: List[Dict] = None,
        variables: List[str] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """Створення нового шаблону"""
        from database.models import MailingTemplate
        
        template = MailingTemplate(
            owner_id=owner_id,
            project_id=project_id,
            name=name,
            category=category,
            content=content,
            media_file_id=media_file_id,
            media_type=media_type,
            buttons_json=json.dumps(buttons or []),
            variables=json.dumps(variables or []),
            is_public=is_public
        )
        
        session.add(template)
        await session.commit()
        await session.refresh(template)
        
        logger.info(f"Created template {template.id}: {name}")
        
        return {
            'id': template.id,
            'name': template.name,
            'category': template.category,
            'content': template.content[:100] + '...' if len(template.content) > 100 else template.content
        }
    
    async def get_templates(
        self,
        session: AsyncSession,
        owner_id: str = None,
        project_id: int = None,
        category: str = None,
        include_public: bool = True
    ) -> List[Dict]:
        """Отримання списку шаблонів"""
        from database.models import MailingTemplate
        
        query = select(MailingTemplate)
        
        conditions = []
        if owner_id:
            if include_public:
                from sqlalchemy import or_
                conditions.append(
                    or_(MailingTemplate.owner_id == owner_id, MailingTemplate.is_public == True)
                )
            else:
                conditions.append(MailingTemplate.owner_id == owner_id)
        
        if project_id:
            conditions.append(MailingTemplate.project_id == project_id)
        
        if category:
            conditions.append(MailingTemplate.category == category)
        
        if conditions:
            query = query.where(*conditions)
        
        query = query.order_by(MailingTemplate.usage_count.desc())
        
        result = await session.execute(query)
        templates = result.scalars().all()
        
        return [
            {
                'id': t.id,
                'name': t.name,
                'category': t.category,
                'category_name': self.CATEGORIES.get(t.category, t.category),
                'content_preview': t.content[:80] + '...' if len(t.content) > 80 else t.content,
                'has_media': bool(t.media_file_id),
                'is_public': t.is_public,
                'usage_count': t.usage_count,
                'created_at': t.created_at.strftime('%d.%m.%Y')
            }
            for t in templates
        ]
    
    async def get_template(self, session: AsyncSession, template_id: int) -> Optional[Dict]:
        """Отримання шаблону за ID"""
        from database.models import MailingTemplate
        
        result = await session.execute(
            select(MailingTemplate).where(MailingTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            return None
        
        return {
            'id': template.id,
            'owner_id': template.owner_id,
            'project_id': template.project_id,
            'name': template.name,
            'category': template.category,
            'content': template.content,
            'media_file_id': template.media_file_id,
            'media_type': template.media_type,
            'buttons': json.loads(template.buttons_json) if template.buttons_json else [],
            'variables': json.loads(template.variables) if template.variables else [],
            'is_public': template.is_public,
            'usage_count': template.usage_count
        }
    
    async def update_template(
        self,
        session: AsyncSession,
        template_id: int,
        **updates
    ) -> bool:
        """Оновлення шаблону"""
        from database.models import MailingTemplate
        
        if 'buttons' in updates:
            updates['buttons_json'] = json.dumps(updates.pop('buttons'))
        if 'variables' in updates:
            updates['variables'] = json.dumps(updates.pop('variables'))
        
        updates['updated_at'] = datetime.now()
        
        await session.execute(
            update(MailingTemplate)
            .where(MailingTemplate.id == template_id)
            .values(**updates)
        )
        await session.commit()
        
        return True
    
    async def delete_template(self, session: AsyncSession, template_id: int) -> bool:
        """Видалення шаблону"""
        from database.models import MailingTemplate
        
        await session.execute(
            delete(MailingTemplate).where(MailingTemplate.id == template_id)
        )
        await session.commit()
        
        return True
    
    async def increment_usage(self, session: AsyncSession, template_id: int):
        """Збільшення лічильника використання"""
        from database.models import MailingTemplate
        
        await session.execute(
            update(MailingTemplate)
            .where(MailingTemplate.id == template_id)
            .values(usage_count=MailingTemplate.usage_count + 1)
        )
        await session.commit()
    
    def render_template(self, content: str, variables: Dict[str, str]) -> str:
        """Рендеринг шаблону зі змінними"""
        result = content
        for key, value in variables.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result

class SchedulerService:
    """Сервіс планування розсилок"""
    
    SCHEDULE_TYPES = {
        'once': 'Одноразово',
        'interval': 'За інтервалом',
        'daily': 'Щодня',
        'weekly': 'Щотижня',
        'monthly': 'Щомісяця'
    }
    
    async def create_scheduled_mailing(
        self,
        session: AsyncSession,
        template_id: int,
        owner_id: str,
        name: str,
        schedule_type: str = 'once',
        interval_minutes: int = None,
        target_roles: List[str] = None,
        target_user_ids: List[str] = None,
        next_run_at: datetime = None,
        max_runs: int = None,
        project_id: int = None,
        funnel_id: int = None
    ) -> Dict[str, Any]:
        """Створення запланованої розсилки"""
        from database.models import ScheduledMailing
        
        scheduled = ScheduledMailing(
            template_id=template_id,
            owner_id=owner_id,
            project_id=project_id,
            name=name,
            schedule_type=schedule_type,
            interval_minutes=interval_minutes,
            target_roles=json.dumps(target_roles or []),
            target_user_ids=json.dumps(target_user_ids or []),
            next_run_at=next_run_at or datetime.now(),
            max_runs=max_runs,
            status='active',
            funnel_id=funnel_id
        )
        
        session.add(scheduled)
        await session.commit()
        await session.refresh(scheduled)
        
        logger.info(f"Created scheduled mailing {scheduled.id}: {name}")
        
        return {
            'id': scheduled.id,
            'name': scheduled.name,
            'schedule_type': schedule_type,
            'next_run_at': scheduled.next_run_at.strftime('%d.%m.%Y %H:%M')
        }
    
    async def get_scheduled_mailings(
        self,
        session: AsyncSession,
        owner_id: str = None,
        status: str = None
    ) -> List[Dict]:
        """Отримання списку запланованих розсилок"""
        from database.models import ScheduledMailing
        
        query = select(ScheduledMailing)
        
        if owner_id:
            query = query.where(ScheduledMailing.owner_id == owner_id)
        if status:
            query = query.where(ScheduledMailing.status == status)
        
        query = query.order_by(ScheduledMailing.next_run_at)
        
        result = await session.execute(query)
        mailings = result.scalars().all()
        
        return [
            {
                'id': m.id,
                'name': m.name,
                'schedule_type': m.schedule_type,
                'schedule_type_name': self.SCHEDULE_TYPES.get(m.schedule_type, m.schedule_type),
                'interval_minutes': m.interval_minutes,
                'next_run_at': m.next_run_at.strftime('%d.%m.%Y %H:%M') if m.next_run_at else '-',
                'runs_count': m.runs_count,
                'max_runs': m.max_runs,
                'status': m.status,
                'target_roles': json.loads(m.target_roles) if m.target_roles else [],
                'funnel_id': getattr(m, 'funnel_id', None)
            }
            for m in mailings
        ]
    
    async def get_pending_mailings(self, session: AsyncSession) -> List[Dict]:
        """Отримання розсилок для виконання"""
        from database.models import ScheduledMailing
        
        now = datetime.now()
        
        result = await session.execute(
            select(ScheduledMailing)
            .where(
                ScheduledMailing.status == 'active',
                ScheduledMailing.next_run_at <= now
            )
        )
        
        return result.scalars().all()
    
    async def mark_executed(
        self,
        session: AsyncSession,
        mailing_id: int
    ):
        """Позначити розсилку як виконану"""
        from database.models import ScheduledMailing
        
        result = await session.execute(
            select(ScheduledMailing).where(ScheduledMailing.id == mailing_id)
        )
        mailing = result.scalar_one_or_none()
        
        if not mailing:
            return
        
        mailing.runs_count += 1
        mailing.last_run_at = datetime.now()
        
        if mailing.max_runs and mailing.runs_count >= mailing.max_runs:
            mailing.status = 'completed'
            mailing.next_run_at = None
        elif mailing.schedule_type == 'once':
            mailing.status = 'completed'
            mailing.next_run_at = None
        elif mailing.schedule_type == 'interval' and mailing.interval_minutes:
            mailing.next_run_at = datetime.now() + timedelta(minutes=mailing.interval_minutes)
        elif mailing.schedule_type == 'daily':
            mailing.next_run_at = datetime.now() + timedelta(days=1)
        elif mailing.schedule_type == 'weekly':
            mailing.next_run_at = datetime.now() + timedelta(weeks=1)
        elif mailing.schedule_type == 'monthly':
            mailing.next_run_at = datetime.now() + timedelta(days=30)
        
        await session.commit()
    
    async def toggle_status(self, session: AsyncSession, mailing_id: int) -> str:
        """Переключення статусу"""
        from database.models import ScheduledMailing
        
        result = await session.execute(
            select(ScheduledMailing).where(ScheduledMailing.id == mailing_id)
        )
        mailing = result.scalar_one_or_none()
        
        if not mailing:
            return None
        
        new_status = 'paused' if mailing.status == 'active' else 'active'
        mailing.status = new_status
        await session.commit()
        
        return new_status
    
    async def delete_scheduled(self, session: AsyncSession, mailing_id: int) -> bool:
        """Видалення запланованої розсилки"""
        from database.models import ScheduledMailing
        
        await session.execute(
            delete(ScheduledMailing).where(ScheduledMailing.id == mailing_id)
        )
        await session.commit()
        
        return True

template_service = TemplateService()
scheduler_service = SchedulerService()
