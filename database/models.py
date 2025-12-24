from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    first_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

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
