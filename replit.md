# Shadow System v2.0

## Overview
SHADOW SYSTEM iO v2.0 is a professional Ukrainian-language Telegram marketing automation platform. It provides comprehensive functionality for managing bot networks, mass mailings, OSINT reconnaissance, team collaboration, and AI-powered features. The system uses SHADOW license keys for authorization, focusing on robust functionality over a payment/balance system.

## User Preferences
- Concise, high-level summaries over granular details
- No changelogs or date-wise entries
- Focus on core architectural decisions
- Ukrainian interface with styled formatting (dividers, emoji, button layouts)

## System Architecture

### Core Architectural Decisions
- **Unified Role System:** Single `UserRole` class in `core/role_constants.py` imported by all modules, supporting RBAC (ROOT/ADMIN, LEADER, MANAGER, GUEST).
- **Centralized FSM States:** All FSM states defined in `core/states.py` for consistent state management.
- **Modular Design:** Clear separation of concerns with dedicated folders for configuration, core services, database, handlers, keyboards, middlewares, and utilities.
- **Asynchronous Operations:** Utilizes `aiogram 3.3` and `asyncpg` with an optimized connection pool for high performance.
- **Background Task Processing:** `core/background_tasks.py` handles non-blocking and heavy operations like OSINT.
- **Security-First Approach:** Implements SHADOW keys, AES-256-CBC encryption, Telegram ID binding, and comprehensive audit logging. Includes rate limiting, anti-fraud, and session validation.
- **Reusable UI Components:** Paginator, ProgressBar, and MenuBuilder in `core/ui_components.py` for consistent user experience.
- **AI Integration:** Seamless integration with OpenAI-compatible models (e.g., GPT-5) via Replit AI for various AI-powered features.
- **Advanced Campaign Management:** Features a worker pool with async queues, weighted round-robin bot selection, adaptive delay calculation, and A/B testing.
- **Enhanced OSINT Engine:** Deep analysis capabilities including network graph building, threat assessment, pattern detection (phones, crypto, coordinates, emails), and evidence storage.
- **Real-time Monitoring:** Telethon-based event listener for real-time threat detection, pattern matching, and auto-actions.
- **Dynamic Alert Thresholds:** Configurable rules engine for various events with actions like logging, alerting, and escalation.
- **Comprehensive Funnel System:** Full CRUD for funnels, integration with mailing templates, scheduling, OSINT analysis, and monitoring with trigger-based transitions.
- **Advanced Tools:** Includes AI Pattern Detection, Spam Analyzer, Drip Campaign Manager, Behavior Profiler, Enhanced Report Generator, and Keyword Analyzer.

### UI/UX Standards
- Ukrainian language throughout the interface.
- Dividers: exactly 15 single-line chars `───────────────` (mobile-optimized).
- Progress bars: native collab style `●●●●○○○○ 50%`.
- Standardized button layouts (1/2/3 per row).
- Rich HTML formatting (bold, italic, code) for messages.
- Tree-like list structures (e.g., `├ └`).
- No frames/borders - clean minimal design.
- Deployment: Reserved VM (Background Worker).

## External Dependencies
- **aiogram 3.3:** Telegram Bot API interaction.
- **SQLAlchemy + asyncpg:** Object Relational Mapper (ORM) and asynchronous PostgreSQL driver.
- **Telethon:** For Telegram session management and interaction.
- **OpenAI (via Replit AI):** Provides AI capabilities.
- **ReportLab:** For generating professional PDF reports.
- **Jinja2:** Templating engine for various text and HTML generation needs.
## Botnet Infrastructure (December 2025)

### BotnetManager (core/botnet_manager.py)
- Worker pool with async task queue
- Bot selection strategies: round_robin, weighted, random, smart
- Health monitoring loop (every 5 min)
- Daily limit reset at midnight
- Auto-recovery for flooded bots
- Statistics: success_rate, health_score, usage_count

### AntiDetect System (core/antidetect.py)
- 9 device profiles (Samsung, Xiaomi, iPhone, Desktop)
- 5 behavior patterns (casual, active, business, night_owl, early_bird)
- Unique fingerprint generation per bot
- Typing/thinking/pause emulation
- Canvas/WebGL/Audio/Font hash generation

### Recovery System (core/recovery_system.py)
- 4-step auto-recovery process
- Proxy pool with rotation
- Session backup storage with versioning
- Batch recovery operations
- Proxy health monitoring

### Session Importer (core/session_importer.py)
- Multi-format import: Telethon, Pyrogram, StringSession, TData
- 5-step validation process
- Device fingerprint collection
- Import/validation report generation

## Advanced Parsing & Monitoring (December 2025)

### Advanced Parser (core/advanced_parser.py)
- Deep chat parsing with threat analysis
- Coordinate/crypto/phone pattern detection
- User risk scoring and key person identification
- Interaction graph building
- Threat assessment with recommendations
- Formatted analysis reports

### RealTime Parser (core/realtime_parser.py)
- Real-time chat monitoring with configurable intervals
- Threat level threshold alerts
- Message deduplication via hash cache
- Alert callbacks for notifications
- Dynamic settings (interval, threshold, batch size)
- Status reporting and control (start/stop)

### Integration with OSINT
- handlers/osint.py: New buttons for "🔬 ГЛИБОКИЙ АНАЛІЗ" and "📡 РЕАЛТАЙМ"
- keyboards/role_menus.py: Updated Leader/Admin menus with direct access
- Parsers connect to Telethon via core/osint_telethon.py when API credentials available
