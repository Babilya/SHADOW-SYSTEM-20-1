from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from core.role_constants import UserRole

class BotStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class CampaignStatus:
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
PAUSED = "paused"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=True)
    username = Column(String)
    first_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.GUEST)
    project_id = Column(String, nullable=True)
    permissions = Column(String, nullable=True)
    status = Column(String, nullable=True)
    subscription_type = Column(String, nullable=True)
    subscription_expires = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    is_kicked = Column(Boolean, default=False)
    parent_leader_id = Column(String, nullable=True)
    referral_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, nullable=True)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    telegram_id = Column(String)
    tariff = Column(String)
    duration = Column(Integer)
    name = Column(String)
    purpose = Column(Text)
    contact = Column(String)
    status = Column(String, default="new")
    amount = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

class Key(Base):
    __tablename__ = "keys"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    tariff = Column(String)
    user_id = Column(String)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    leader_id = Column(String)
    leader_username = Column(String)
    key_id = Column(Integer)
    name = Column(String)
    tariff = Column(String)
    bots_limit = Column(Integer, default=50)
    managers_limit = Column(Integer, default=5)
    bots_used = Column(Integer, default=0)
    managers_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class Manager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    telegram_id = Column(String)
    username = Column(String)
    role = Column(String)
    manager_key = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    manager_id = Column(Integer)
    name = Column(String)
    status = Column(String, default="draft")
    messages_sent = Column(Integer, default=0)
    success_rate = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)

class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    session_hash = Column(String)
    phone = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)

class BotSessionStatus:
    """Статуси бот-сесій"""
    ACTIVE = "active"
    PAUSED = "paused"
    FLOODED = "flooded"
    BANNED = "banned"
    DEAD = "dead"
    TESTING = "testing"

class BotSession(Base):
    """Розширена модель бот-сесії згідно ТЗ"""
    __tablename__ = "bot_sessions"
    
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, nullable=True)
    
    phone = Column(String(20), nullable=True, index=True)
    session_string = Column(Text, nullable=True)
    session_data = Column(Text, nullable=True)
    api_id = Column(Integer, nullable=True)
    api_hash = Column(String(100), nullable=True)
    
    owner_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    tags = Column(Text, default="[]")
    
    status = Column(String(20), default=BotSessionStatus.ACTIVE)
    last_active = Column(DateTime, default=datetime.now)
    messages_sent = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    flood_wait_until = Column(DateTime, nullable=True)
    
    device_fingerprint = Column(Text, default="{}")
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    app_version = Column(String(50), nullable=True)
    
    proxy_id = Column(Integer, nullable=True)
    proxy_type = Column(String(20), nullable=True)
    proxy_config = Column(Text, default="{}")
    
    anti_detect_profile = Column(Text, default="{}")
    fingerprint_hash = Column(String(64), nullable=True)
    
    warming_phase = Column(Integer, default=0)
    warming_started_at = Column(DateTime, nullable=True)
    warming_profile = Column(String(20), default="standard")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def is_available(self) -> bool:
        """Перевірка доступності бота"""
        if self.status in [BotSessionStatus.BANNED, BotSessionStatus.DEAD]:
            return False
        
        if self.flood_wait_until and datetime.now() < self.flood_wait_until:
            return False
        
        if self.success_rate < 30.0:
            return False
            
        return self.is_active
    
    def update_statistics(self, success: bool):
        """Оновлення статистики"""
        self.messages_sent += 1
        if not success:
            self.messages_failed += 1
        
        total = self.messages_sent
        if total > 0:
            self.success_rate = ((total - self.messages_failed) / total) * 100
        
        self.last_active = datetime.now()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, unique=True)
    user_id = Column(String)
    subject = Column(String)
    description = Column(Text)
    status = Column(String, default="open")
    priority = Column(String, default="normal")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class AdminNotification(Base):
    __tablename__ = "admin_notifications"
    id = Column(Integer, primary_key=True)
    admin_id = Column(String)
    app_id = Column(Integer)
    status = Column(String, default="new")
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    referrer_id = Column(String)
    referred_id = Column(String)
    bonus_percent = Column(Float, default=10.0)
    total_earned = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    amount = Column(Float)
    method = Column(String)
    status = Column(String, default="pending")
    screenshot_file_id = Column(String, nullable=True)
    admin_id = Column(String, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class SecurityBlock(Base):
    __tablename__ = "security_blocks"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    block_type = Column(String)
    reason = Column(Text)
    legal_basis = Column(String, nullable=True)
    blocked_by = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class MailingTask(Base):
    __tablename__ = "mailing_tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    name = Column(String)
    message = Column(Text)
    audience_type = Column(String)
    target_ids = Column(Text, nullable=True)
    interval_min = Column(Integer, default=1)
    interval_max = Column(Integer, default=5)
    status = Column(String, default="draft")
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    alert_type = Column(String)
    keyword = Column(String, nullable=True)
    source_chat = Column(String)
    message_text = Column(Text)
    detected_at = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    category = Column(String)
    severity = Column(String, default="info")
    details = Column(Text)
    ip_address = Column(String, nullable=True)
    action_type = Column(String, nullable=True)
    actor_id = Column(Integer, nullable=True)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class CMSConfig(Base):
    __tablename__ = "cms_config"
    id = Column(Integer, primary_key=True)
    config_key = Column(String, unique=True)
    config_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)

class Proxy(Base):
    __tablename__ = "proxies"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer)
    url = Column(String)
    ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    proxy_type = Column(String, default="http")
    is_active = Column(Boolean, default=True)
    response_time = Column(Float, default=0)
    success_rate = Column(Float, default=100)
    failures_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    last_check = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class OSINTData(Base):
    __tablename__ = "osint_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)  # This will store telegram_id
    data_type = Column(String)
    filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Funnel(Base):
    __tablename__ = "funnels"
    id = Column(Integer, primary_key=True)
    owner_id = Column(String)
    name = Column(String)
    description = Column(Text, nullable=True)
    funnel_type = Column(String, default="onboarding")
    status = Column(String, default="draft")
    steps_count = Column(Integer, default=0)
    photo_file_id = Column(String, nullable=True)
    tariff_info = Column(Text, nullable=True)
    welcome_text = Column(Text, nullable=True)
    button_text = Column(String, default="Далі")
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class FunnelStep(Base):
    __tablename__ = "funnel_steps"
    id = Column(Integer, primary_key=True)
    funnel_id = Column(Integer)
    step_order = Column(Integer, default=1)
    title = Column(String, nullable=True)
    content = Column(Text)
    photo_file_id = Column(String, nullable=True)
    button_text = Column(String, default="Далі")
    action_type = Column(String, default="next")
    action_data = Column(String, nullable=True)
    delay_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

class MailingTemplate(Base):
    """Шаблони розсилок"""
    __tablename__ = "mailing_templates"
    id = Column(Integer, primary_key=True)
    owner_id = Column(String)
    project_id = Column(Integer, nullable=True)
    name = Column(String)
    category = Column(String, default="general")
    content = Column(Text)
    media_file_id = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    buttons_json = Column(Text, default="[]")
    variables = Column(Text, default="[]")
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class ScheduledMailing(Base):
    """Заплановані розсилки"""
    __tablename__ = "scheduled_mailings"
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, nullable=True)
    funnel_id = Column(Integer, nullable=True)
    owner_id = Column(String)
    project_id = Column(Integer, nullable=True)
    name = Column(String)
    schedule_type = Column(String, default="once")
    interval_minutes = Column(Integer, nullable=True)
    cron_expression = Column(String, nullable=True)
    target_roles = Column(Text, default="[]")
    target_user_ids = Column(Text, default="[]")
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    runs_count = Column(Integer, default=0)
    max_runs = Column(Integer, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)

class SupportTicket(Base):
    """Тікети підтримки"""
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True)
    ticket_code = Column(String, unique=True)
    user_id = Column(String)
    user_role = Column(String)
    assigned_admin_id = Column(String, nullable=True)
    subject = Column(String)
    category = Column(String, default="general")
    priority = Column(String, default="normal")
    status = Column(String, default="open")
    project_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    closed_at = Column(DateTime, nullable=True)
    rating = Column(Integer, nullable=True)

class TicketMessage(Base):
    """Повідомлення в тікетах"""
    __tablename__ = "ticket_messages"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer)
    sender_id = Column(String)
    sender_role = Column(String)
    message = Column(Text)
    attachments = Column(Text, default="[]")
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class UserBan(Base):
    """Система банів"""
    __tablename__ = "user_bans"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    banned_by = Column(String)
    reason = Column(Text)
    ban_type = Column(String, default="temporary")
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    can_appeal = Column(Boolean, default=True)
    appeal_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class SystemNotification(Base):
    """Системні сповіщення"""
    __tablename__ = "system_notifications"
    id = Column(Integer, primary_key=True)
    sender_id = Column(String)
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String, default="info")
    target_type = Column(String, default="all")
    target_roles = Column(Text, default="[]")
    target_user_ids = Column(Text, default="[]")
    priority = Column(String, default="normal")
    read_by = Column(Text, default="[]")
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class ProjectStats(Base):
    """Статистика проектів"""
    __tablename__ = "project_stats"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    date = Column(DateTime, default=datetime.now)
    messages_sent = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_bots = Column(Integer, default=0)
    campaigns_launched = Column(Integer, default=0)
    osint_reports = Column(Integer, default=0)

class UIConfig(Base):
    """Налаштування інтерфейсу"""
    __tablename__ = "ui_config"
    id = Column(Integer, primary_key=True)
    menu_key = Column(String(50), unique=True, index=True)
    title = Column(String(100))
    description = Column(Text)
    banner_text = Column(Text, nullable=True)
    divider_style = Column(String(50), default="double")
    is_active = Column(Boolean, default=True)
    updated_by = Column(String)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UIButton(Base):
    """Кнопки меню"""
    __tablename__ = "ui_buttons"
    id = Column(Integer, primary_key=True)
    menu_key = Column(String(50), index=True)
    text = Column(String(100))
    callback_data = Column(String(100))
    row_order = Column(Integer, default=0)
    col_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UIStyle(Base):
    """Глобальні стилі"""
    __tablename__ = "ui_styles"
    id = Column(Integer, primary_key=True)
    style_key = Column(String(50), unique=True, index=True)
    divider_char = Column(String(10), default="═")
    divider_length = Column(Integer, default=26)
    header_format = Column(String(200), default="{divider}\n{icon} <b>{title}</b>\n{divider}")
    tree_prefix = Column(String(10), default="├")
    tree_last = Column(String(10), default="└")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
