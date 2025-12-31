# Shadow System v2.0

## Overview
SHADOW SYSTEM iO v2.0 is a professional Ukrainian-language Telegram marketing automation platform. Its primary purpose is to provide comprehensive functionality for managing bot networks, mass mailings, OSINT reconnaissance, team collaboration, and AI-powered features. The system uses SHADOW license keys for authorization, emphasizing robust functionality over a payment/balance system. This platform aims to be a leading solution for advanced Telegram marketing and intelligence operations.

## User Preferences
- Concise, high-level summaries over granular details
- Focus on core architectural decisions
- Ukrainian interface with styled formatting (dividers, emoji, button layouts)
- Prefer simplicity over unnecessary complexity
- Do not include changelogs or date-wise entries

## System Architecture

### Core Architectural Decisions
The system employs a modular design with clear separation of concerns across dedicated folders (config, core, database, handlers, keyboards, middlewares, services, utils). It leverages `aiogram 3.3` and `asyncpg` with an optimized connection pool for high-performance asynchronous operations. Background tasks are managed via `core/background_tasks.py` for non-blocking and heavy operations. Security is paramount, with SHADOW keys, AES-256-CBC encryption, Telegram ID binding, comprehensive audit logging, rate limiting, anti-fraud measures, and session validation.

A unified `UserRole` class (ROOT/ADMIN, LEADER, MANAGER, GUEST) in `core/role_constants.py` enables Role-Based Access Control (RBAC), with all FSM states defined centrally in `core/states.py`. Reusable UI components like Paginator, ProgressBar, and MenuBuilder ensure a consistent user experience. The platform seamlessly integrates with OpenAI-compatible models (e.g., GPT-5) via Replit AI for various AI-powered features.

Advanced features include:
-   **Campaign Management:** Worker pool with async queues, weighted round-robin bot selection, adaptive delay calculation, and A/B testing.
-   **OSINT Engine:** Deep analysis, network graph building, threat assessment, pattern detection (phones, crypto, coordinates, emails), and evidence storage.
-   **Multi-Database OSINT:** Unified search across 10+ data sources (Telegram, GetContact, TrueCaller, NumVerify, HIBP, EmailRep, Hunter, social platforms) with auto-detection by query type, merged profiles, and risk scoring.
-   **Real-time Monitoring:** Telethon-based event listener for threat detection, pattern matching, and auto-actions, with dynamic alert thresholds.
-   **Bot Activity Tracking:** Comprehensive activity dashboard with conversation records, incoming/outgoing contact tracking, event timeline (messages, reactions, commands), and health scoring.
-   **Bot Commands System:** Reaction management (50+ emoji), user watching with change detection (username, name, photo, bio, status), alert notifications with read status.
-   **AI Communication Styles:** 8 default personas (friendly, professional, casual, sales, tech, crypto, support, mysterious), custom persona creation, training via examples, GPT-5 powered response generation.
-   **Geo Scanner:** Telethon-based GetLocatedRequest for finding nearby users/groups/channels, with caching, filtering, distance calculation, and result formatting.
-   **Comprehensive Funnel System:** Full CRUD for funnels, integrated with mailing templates, scheduling, and OSINT analysis, with trigger-based transitions.
-   **Group Parsing:** Telethon-based member extraction from groups/channels with filters (all, active recently, with username, premium only, no bots), saved lists management, and export to mailing.
-   **DM Sender:** Personal message campaigns with session rotation, personalization ({name}, {username}, {date}), blacklist management, 24h cooldown tracking, and proper flood protection (FloodWaitError, PeerFloodError, UserPrivacyRestrictedError handling with auto-pause).
-   **Advanced Tools:** AI Pattern Detection, Spam Analyzer, Drip Campaign Manager, Behavior Profiler, Enhanced Report Generator, Keyword Analyzer, Forensic Snapshotting, AI Sentiment Analysis, Anti-Ghost Recovery, X-Ray Metadata analysis, and an in-memory Memory Indexer for full-text search.
-   **User Profile System:** Profile management (display_name, email, project_name, project_goals) with optional session password (Argon2 hashed), configurable session timeout (1-24h), Leader-Manager linking (leader_id field). Tables: `user_profiles`, `user_sessions`.

### UI/UX Standards
The interface is entirely in Ukrainian. It uses mobile-optimized dividers (`───────────────`), native-style progress bars (`●●●●○○○○ 50%`), and standardized button layouts (1/2/3 per row). Rich HTML formatting (bold, italic, code) is supported, and hierarchical information uses tree-like list structures (`├ └`). Universal `◀️ Назад` buttons with standardized callback data are implemented. All role menus (Guest, Manager, Leader, Admin) are unified in `keyboards/role_menus.py` for consistent styling and simplified maintenance, avoiding frames or borders for a clean, minimal design. The application is designed for deployment on a reserved VM acting as a background worker.

### System Components
-   `api/`: FastAPI endpoints for system, OSINT, and AI.
-   `bot.py`: Main entry point with aiogram dispatcher.
-   `config/`: Application settings.
-   `core/`: Core services, business logic (e.g., `system_stats.py`, `cache_service.py`, `health_dashboard.py`).
-   `database/`: ORM models, migrations, CRUD.
-   `handlers/`: Telegram message handlers organized by core, features, moderation, and integrations.
-   `keyboards/`: Unified reply and inline keyboard builders in `role_menus.py`.
-   `middlewares/`: Request/response middleware.
-   `services/`: High-level business logic.
-   `utils/`: Helper functions.
-   `sessions/`: Bot session storage.
-   `data/`: Forensic snapshots and artifacts.
-   `attached_assets/`: User-uploaded files.

## External Dependencies
-   **aiogram 3.3:** Telegram Bot API interaction.
-   **SQLAlchemy + asyncpg:** ORM and asynchronous PostgreSQL driver.
-   **Telethon:** Telegram session management and interaction, used for real-time monitoring and OSINT.
-   **OpenAI (via Replit AI):** Provides AI capabilities for sentiment analysis, pattern detection, and other AI-powered features.
-   **ReportLab:** For generating professional PDF reports.
-   **Jinja2:** Templating engine for various text and HTML generation.
-   **psutil:** For real-time system resource monitoring.