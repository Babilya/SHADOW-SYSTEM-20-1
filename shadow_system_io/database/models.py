import logging
from config.database import execute_query

logger = logging.getLogger(__name__)

async def init_db():
    """Ініціалізація таблиць бази даних"""
    try:
        await execute_query("""
            CREATE TABLE IF NOT EXISTS bots (
                bot_id VARCHAR(50) PRIMARY KEY,
                phone_number VARCHAR(20) NOT NULL,
                session_string TEXT,
                proxy_config JSONB,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            );
        """)

        await execute_query("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                creator_id VARCHAR(50),
                project_id VARCHAR(50),
                status VARCHAR(20),
                recipients JSONB,
                messages JSONB,
                schedule JSONB,
                settings JSONB,
                stats JSONB,
                created_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                error TEXT
            );
        """)
        
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
                sent_at TIMESTAMP
            );
        """)

        await execute_query("""
            CREATE TABLE IF NOT EXISTS proxies (
                proxy_id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(10),
                host VARCHAR(50),
                port INTEGER,
                username VARCHAR(50),
                password VARCHAR(50),
                added_at TIMESTAMP,
                expires_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            );
        """)
        
        await execute_query("""
            CREATE TABLE IF NOT EXISTS parse_results (
                id SERIAL PRIMARY KEY,
                chat_id VARCHAR(50),
                chat_title VARCHAR(255),
                message_count INTEGER,
                users_count INTEGER,
                analysis_data JSONB,
                top_users JSONB,
                common_words JSONB,
                parsed_at TIMESTAMP
            );
        """)

        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to init DB: {e}")
