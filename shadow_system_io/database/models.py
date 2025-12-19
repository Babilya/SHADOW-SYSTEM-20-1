import logging
from config.database import execute_query

logger = logging.getLogger(__name__)

async def init_db():
    """Ініціалізація таблиць бази даних"""
    try:
        # Таблиця користувачів (RBAC)
        await execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(100),
                role VARCHAR(20) NOT NULL DEFAULT 'manager',
                project_id VARCHAR(50),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            );
        """)

        # Таблиця проектів
        await execute_query("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id VARCHAR(50) PRIMARY KEY,
                admin_id BIGINT NOT NULL,
                name VARCHAR(100),
                description TEXT,
                status VARCHAR(20) DEFAULT 'active',
                settings JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(user_id)
            );
        """)

        # Таблиця ботів
        await execute_query("""
            CREATE TABLE IF NOT EXISTS bots (
                bot_id VARCHAR(50) PRIMARY KEY,
                project_id VARCHAR(50),
                phone_number VARCHAR(20),
                session_string TEXT,
                proxy_config JSONB,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            );
        """)

        # Таблиця кампаній
        await execute_query("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id VARCHAR(50) PRIMARY KEY,
                project_id VARCHAR(50),
                name VARCHAR(100),
                creator_id BIGINT,
                status VARCHAR(20),
                recipients JSONB,
                messages JSONB,
                schedule JSONB,
                settings JSONB,
                stats JSONB,
                created_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                error TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (creator_id) REFERENCES users(user_id)
            );
        """)
        
        # Таблиця логів доставки
        await execute_query("""
            CREATE TABLE IF NOT EXISTS delivery_logs (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(50),
                bot_id VARCHAR(50),
                recipient_type VARCHAR(20),
                recipient_value VARCHAR(100),
                message_id VARCHAR(50),
                success BOOLEAN,
                error TEXT,
                sent_at TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
                FOREIGN KEY (bot_id) REFERENCES bots(bot_id)
            );
        """)

        # Таблиця проксі
        await execute_query("""
            CREATE TABLE IF NOT EXISTS proxies (
                proxy_id VARCHAR(50) PRIMARY KEY,
                project_id VARCHAR(50),
                type VARCHAR(10),
                host VARCHAR(50),
                port INTEGER,
                username VARCHAR(50),
                password VARCHAR(50),
                added_at TIMESTAMP,
                expires_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            );
        """)
        
        # Таблиця результатів парсингу
        await execute_query("""
            CREATE TABLE IF NOT EXISTS parse_results (
                id SERIAL PRIMARY KEY,
                project_id VARCHAR(50),
                chat_id VARCHAR(50),
                chat_title VARCHAR(255),
                message_count INTEGER,
                users_count INTEGER,
                analysis_data JSONB,
                top_users JSONB,
                common_words JSONB,
                parsed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            );
        """)

        # Таблиця аудит-логів
        await execute_query("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                action VARCHAR(100),
                resource_type VARCHAR(50),
                resource_id VARCHAR(100),
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to init DB: {e}")
