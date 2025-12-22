import sqlite3
from datetime import datetime
import json

class Database:
    """Простий SQLite DB для користувачів"""
    
    def __init__(self, db_path: str = "shadow_security.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Ініціалізувати БД"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця користувачів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    subscription_tier TEXT DEFAULT 'free',
                    balance INTEGER DEFAULT 0,
                    settings TEXT DEFAULT '{}',
                    stats TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблиця розсилок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mailings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT,
                    targets TEXT,
                    status TEXT DEFAULT 'draft',
                    sent_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
                )
            ''')
            
            # Таблиця автовідповідей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    trigger TEXT,
                    response TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, telegram_id: int, username: str, first_name: str):
        """Додати користувача"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (telegram_id, username, first_name))
            conn.commit()
    
    def get_user(self, telegram_id: int):
        """Отримати користувача"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
            return cursor.fetchone()
    
    def update_balance(self, telegram_id: int, amount: int):
        """Оновити баланс"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE telegram_id = ?
            ''', (amount, telegram_id))
            conn.commit()
    
    def get_all_users(self):
        """Отримати всіх користувачів"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()

# Глобальний екземпляр БД
db = Database()
