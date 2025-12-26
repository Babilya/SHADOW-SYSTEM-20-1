from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, and_, text
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from database.models import (
    User, Application, Key, Project, Manager, Campaign, Bot,
    Ticket, Log, Referral, Payment, SecurityBlock, MailingTask,
    MonitoringAlert, AuditLog, CMSConfig, UserRole
)
from utils.db import async_session, SessionLocal
import logging
import secrets

logger = logging.getLogger(__name__)

class UserCRUD:
    @staticmethod
    def get_or_create(db: Session, telegram_id: str, username: str, first_name: str):
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            db.add(user)
            db.commit()
        return user
    
    @staticmethod
    async def get_user(telegram_id: int) -> Optional[User]:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == str(telegram_id))
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(user_id: int, username: str = None) -> User:
        async with async_session() as session:
            user = User(
                telegram_id=str(user_id),
                username=username,
                referral_code=f"REF-{secrets.token_hex(4).upper()}"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_or_create_async(user_id: int, username: str = None) -> User:
        user = await UserCRUD.get_user(user_id)
        if not user:
            user = await UserCRUD.create_user(user_id, username)
        return user
    
    @staticmethod
    async def update_role(telegram_id: int, role: str) -> bool:
        async with async_session() as session:
            result = await session.execute(
                update(User).where(User.telegram_id == str(telegram_id)).values(role=role)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def block_user(telegram_id: int, blocked: bool = True) -> bool:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.telegram_id == str(telegram_id)).values(is_blocked=blocked)
            )
            await session.commit()
            return True

    @staticmethod
    async def kick_user(telegram_id: int, kicked: bool = True) -> bool:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.telegram_id == str(telegram_id)).values(is_kicked=kicked)
            )
            await session.commit()
            return True

    @staticmethod
    async def is_blocked(telegram_id: int) -> bool:
        user = await UserCRUD.get_user(telegram_id)
        return user.is_blocked if user else False

    @staticmethod
    async def is_kicked(telegram_id: int) -> bool:
        user = await UserCRUD.get_user(telegram_id)
        return user.is_kicked if user else False

class ApplicationCRUD:
    @staticmethod
    def create(db: Session, **kwargs):
        app = Application(**kwargs)
        db.add(app)
        db.commit()
        return app
    
    @staticmethod
    def get_by_id(db: Session, app_id: int):
        return db.query(Application).filter(Application.id == app_id).first()
    
    @staticmethod
    async def create_async(user_id: str, telegram_id: str, tariff: str, duration: int, name: str, purpose: str, contact: str, amount: int) -> Application:
        async with async_session() as session:
            app = Application(
                user_id=str(user_id),
                telegram_id=str(telegram_id),
                tariff=tariff,
                duration=duration,
                name=name,
                purpose=purpose,
                contact=contact,
                amount=amount
            )
            session.add(app)
            await session.commit()
            await session.refresh(app)
            return app
    
    @staticmethod
    async def get_new_applications() -> List[Application]:
        async with async_session() as session:
            result = await session.execute(
                select(Application).where(Application.status == "new")
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def update_status(app_id: int, status: str) -> bool:
        async with async_session() as session:
            await session.execute(
                update(Application).where(Application.id == app_id).values(status=status)
            )
            await session.commit()
            return True
    
    @staticmethod
    async def get_by_id_async(app_id: int) -> Optional[Application]:
        async with async_session() as session:
            result = await session.execute(
                select(Application).where(Application.id == app_id)
            )
            return result.scalar_one_or_none()

class KeyCRUD:
    @staticmethod
    def create(db: Session, code: str, tariff: str, key_type: str, expires_at: datetime):
        key = Key(code=code, tariff=tariff, expires_at=expires_at)
        db.add(key)
        db.commit()
        return key
    
    @staticmethod
    def get_by_code(db: Session, code: str):
        return db.query(Key).filter(Key.code == code).first()
    
    @staticmethod
    async def create_async(tariff: str, expires_at: datetime) -> Key:
        async with async_session() as session:
            code = f"SHADOW-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
            key = Key(code=code, tariff=tariff, expires_at=expires_at)
            session.add(key)
            await session.commit()
            await session.refresh(key)
            return key
    
    @staticmethod
    async def validate_key(code: str) -> Optional[Key]:
        async with async_session() as session:
            result = await session.execute(
                select(Key).where(and_(Key.code == code, Key.is_used == False))
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def use_key(code: str, user_id: str) -> bool:
        async with async_session() as session:
            await session.execute(
                update(Key).where(Key.code == code).values(is_used=True, user_id=str(user_id))
            )
            await session.commit()
            return True

class ProjectCRUD:
    @staticmethod
    def create(db: Session, **kwargs):
        project = Project(**kwargs)
        db.add(project)
        db.commit()
        return project
    
    @staticmethod
    def get_by_leader(db: Session, leader_id: str):
        return db.query(Project).filter(Project.leader_id == leader_id).first()
    
    @staticmethod
    async def create_async(leader_id: str, leader_username: str, key_id: int, name: str, tariff: str, bots_limit: int = 50, managers_limit: int = 5) -> bool:
        async with async_session() as session:
            project_id = f"PRJ-{secrets.token_hex(4).upper()}"
            await session.execute(
                text("""
                    INSERT INTO projects (project_id, leader_id, leader_username, key_id, name, tariff, bots_limit, managers_limit, is_active, created_at)
                    VALUES (:project_id, :leader_id, :leader_username, :key_id, :name, :tariff, :bots_limit, :managers_limit, true, NOW())
                """),
                {
                    "project_id": project_id,
                    "leader_id": str(leader_id),
                    "leader_username": leader_username,
                    "key_id": key_id,
                    "name": name,
                    "tariff": tariff,
                    "bots_limit": bots_limit,
                    "managers_limit": managers_limit
                }
            )
            await session.commit()
            return True

class SecurityCRUD:
    @staticmethod
    async def add_block(user_id: str, block_type: str, reason: str, blocked_by: str, legal_basis: str = None) -> SecurityBlock:
        async with async_session() as session:
            block = SecurityBlock(
                user_id=str(user_id),
                block_type=block_type,
                reason=reason,
                blocked_by=str(blocked_by),
                legal_basis=legal_basis
            )
            session.add(block)
            await session.commit()
            await session.refresh(block)
            return block
    
    @staticmethod
    async def get_active_blocks(user_id: str) -> List[SecurityBlock]:
        async with async_session() as session:
            result = await session.execute(
                select(SecurityBlock).where(
                    and_(SecurityBlock.user_id == str(user_id), SecurityBlock.is_active == True)
                )
            )
            return list(result.scalars().all())

class ReferralCRUD:
    @staticmethod
    async def create_referral(referrer_id: str, referred_id: str) -> Optional[Referral]:
        async with async_session() as session:
            existing = await session.execute(
                select(Referral).where(
                    and_(Referral.referrer_id == str(referrer_id), Referral.referred_id == str(referred_id))
                )
            )
            if existing.scalar_one_or_none():
                return None
            referral = Referral(referrer_id=str(referrer_id), referred_id=str(referred_id))
            session.add(referral)
            await session.commit()
            await session.refresh(referral)
            return referral
    
    @staticmethod
    async def get_referrals(referrer_id: str) -> List[Referral]:
        async with async_session() as session:
            result = await session.execute(
                select(Referral).where(Referral.referrer_id == str(referrer_id))
            )
            return list(result.scalars().all())

class PaymentCRUD:
    @staticmethod
    async def create_payment(user_id: str, amount: float, method: str) -> Payment:
        async with async_session() as session:
            payment = Payment(user_id=str(user_id), amount=amount, method=method)
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            return payment
    
    @staticmethod
    async def get_pending_payments() -> List[Payment]:
        async with async_session() as session:
            result = await session.execute(select(Payment).where(Payment.status == "pending"))
            return list(result.scalars().all())
    
    @staticmethod
    async def confirm_payment(payment_id: int, admin_id: str) -> bool:
        async with async_session() as session:
            await session.execute(
                update(Payment).where(Payment.id == payment_id).values(
                    status="confirmed", admin_id=str(admin_id), confirmed_at=datetime.now()
                )
            )
            await session.commit()
            return True

class TicketCRUD:
    @staticmethod
    async def create_ticket(user_id: str, subject: str, description: str) -> Ticket:
        async with async_session() as session:
            ticket_id = f"TKT-{secrets.token_hex(4).upper()}"
            ticket = Ticket(
                ticket_id=ticket_id, user_id=str(user_id), subject=subject, description=description
            )
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            return ticket
    
    @staticmethod
    async def get_open_tickets() -> List[Ticket]:
        async with async_session() as session:
            result = await session.execute(select(Ticket).where(Ticket.status == "open"))
            return list(result.scalars().all())
    
    @staticmethod
    async def close_ticket(ticket_id: str) -> bool:
        async with async_session() as session:
            await session.execute(
                update(Ticket).where(Ticket.ticket_id == ticket_id).values(status="closed", updated_at=datetime.now())
            )
            await session.commit()
            return True

class AuditCRUD:
    @staticmethod
    async def log_action(user_id: str, action: str, category: str, details: str = None, severity: str = "info") -> AuditLog:
        async with async_session() as session:
            log = AuditLog(
                user_id=str(user_id), action=action, category=category, severity=severity, details=details
            )
            session.add(log)
            await session.commit()
            return log
    
    @staticmethod
    async def get_logs(user_id: str = None, category: str = None, limit: int = 50) -> List[AuditLog]:
        async with async_session() as session:
            query = select(AuditLog)
            if user_id:
                query = query.where(AuditLog.user_id == str(user_id))
            if category:
                query = query.where(AuditLog.category == category)
            query = query.order_by(AuditLog.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

class MailingCRUD:
    @staticmethod
    async def create_task(project_id: int, name: str, message: str, audience_type: str) -> MailingTask:
        async with async_session() as session:
            task = MailingTask(project_id=project_id, name=name, message=message, audience_type=audience_type)
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task
    
    @staticmethod
    async def get_active_tasks(project_id: int) -> List[MailingTask]:
        async with async_session() as session:
            result = await session.execute(
                select(MailingTask).where(
                    and_(MailingTask.project_id == project_id, MailingTask.status.in_(["running", "paused"]))
                )
            )
            return list(result.scalars().all())

class StatsCRUD:
    @staticmethod
    async def get_user_stats() -> dict:
        async with async_session() as session:
            from sqlalchemy import func
            total = await session.execute(select(func.count(User.user_id)))
            leaders = await session.execute(select(func.count(User.user_id)).where(User.role == "leader"))
            managers = await session.execute(select(func.count(User.user_id)).where(User.role == "manager"))
            guests = await session.execute(select(func.count(User.user_id)).where(User.role == "guest"))
            blocked = await session.execute(select(func.count(User.user_id)).where(User.is_blocked == True))
            return {
                "total": total.scalar() or 0,
                "leaders": leaders.scalar() or 0,
                "managers": managers.scalar() or 0,
                "guests": guests.scalar() or 0,
                "blocked": blocked.scalar() or 0
            }
    
    @staticmethod
    async def get_app_stats() -> dict:
        async with async_session() as session:
            from sqlalchemy import func
            total = await session.execute(select(func.count(Application.id)))
            new = await session.execute(select(func.count(Application.id)).where(Application.status == "new"))
            confirmed = await session.execute(select(func.count(Application.id)).where(Application.status == "confirmed"))
            rejected = await session.execute(select(func.count(Application.id)).where(Application.status == "rejected"))
            return {
                "total": total.scalar() or 0,
                "new": new.scalar() or 0,
                "confirmed": confirmed.scalar() or 0,
                "rejected": rejected.scalar() or 0
            }
    
    @staticmethod
    async def get_key_stats() -> dict:
        async with async_session() as session:
            from sqlalchemy import func
            total = await session.execute(select(func.count(Key.id)))
            active = await session.execute(select(func.count(Key.id)).where(Key.is_used == False))
            used = await session.execute(select(func.count(Key.id)).where(Key.is_used == True))
            return {
                "total": total.scalar() or 0,
                "active": active.scalar() or 0,
                "used": used.scalar() or 0
            }
    
    @staticmethod
    async def get_campaign_stats() -> dict:
        async with async_session() as session:
            from sqlalchemy import func
            total = await session.execute(select(func.count(Campaign.id)))
            active = await session.execute(select(func.count(Campaign.id)).where(Campaign.status == "active"))
            draft = await session.execute(select(func.count(Campaign.id)).where(Campaign.status == "draft"))
            completed = await session.execute(select(func.count(Campaign.id)).where(Campaign.status == "completed"))
            return {
                "total": total.scalar() or 0,
                "active": active.scalar() or 0,
                "draft": draft.scalar() or 0,
                "completed": completed.scalar() or 0
            }

class ProxyCRUD:
    @staticmethod
    async def add_proxy(owner_id: int, url: str, ip: str = None, response_time: float = 0) -> "Proxy":
        from database.models import Proxy
        async with async_session() as session:
            proxy = Proxy(
                owner_id=owner_id,
                url=url,
                ip=ip,
                is_active=True,
                response_time=response_time
            )
            session.add(proxy)
            await session.commit()
            await session.refresh(proxy)
            return proxy
    
    @staticmethod
    async def get_user_proxies(owner_id: int) -> List:
        from database.models import Proxy
        async with async_session() as session:
            result = await session.execute(
                select(Proxy).where(Proxy.owner_id == owner_id)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def delete_proxy(proxy_id: int) -> bool:
        from database.models import Proxy
        async with async_session() as session:
            result = await session.execute(
                select(Proxy).where(Proxy.id == proxy_id)
            )
            proxy = result.scalar_one_or_none()
            if proxy:
                await session.delete(proxy)
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def update_proxy_status(proxy_id: int, is_active: bool, response_time: float = None) -> bool:
        from database.models import Proxy
        async with async_session() as session:
            values = {"is_active": is_active}
            if response_time is not None:
                values["response_time"] = response_time
            await session.execute(
                update(Proxy).where(Proxy.id == proxy_id).values(**values)
            )
            await session.commit()
            return True

class BotWarmingCRUD:
    @staticmethod
    async def start_warming(bot_id: int, project_id: int) -> "BotWarming":
        from database.models import BotWarming
        async with async_session() as session:
            warming = BotWarming(bot_id=bot_id, project_id=project_id, status="active")
            session.add(warming)
            await session.commit()
            await session.refresh(warming)
            return warming
    
    @staticmethod
    async def get_active_warmings(project_id: int) -> List:
        from database.models import BotWarming
        async with async_session() as session:
            result = await session.execute(
                select(BotWarming).where(
                    and_(BotWarming.project_id == project_id, BotWarming.status == "active")
                )
            )
            return list(result.scalars().all())

user_crud = UserCRUD()
security_crud = SecurityCRUD()
referral_crud = ReferralCRUD()
payment_crud = PaymentCRUD()
ticket_crud = TicketCRUD()
audit_crud = AuditCRUD()
key_crud = KeyCRUD()
mailing_crud = MailingCRUD()
application_crud = ApplicationCRUD()
stats_crud = StatsCRUD()
proxy_crud = ProxyCRUD()
bot_warming_crud = BotWarmingCRUD()
