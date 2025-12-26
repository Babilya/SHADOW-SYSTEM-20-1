from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserRole:
    GUEST = "guest"
    LEADER = "leader"
    MANAGER = "manager"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    role = Column(String, default=UserRole.GUEST)
    project_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
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
    created_at = Column(DateTime, default=datetime.now)

class CMSConfig(Base):
    __tablename__ = "cms_config"
    id = Column(Integer, primary_key=True)
    config_key = Column(String, unique=True)
    config_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)
