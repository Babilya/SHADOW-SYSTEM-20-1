# Shadow System v2.0

## Overview
SHADOW SYSTEM iO v2.0 is a professional Ukrainian-language Telegram marketing automation platform. It provides comprehensive functionality for managing bot networks, mass mailings, OSINT reconnaissance, team collaboration, and AI-powered features. The system uses SHADOW license keys for authorization, focusing on robust functionality over a payment/balance system.

## Project Structure (Reorganized - December 31, 2025)

**Handler Reorganization:**
- `handlers/core/` - Authentication, start, help, user, security handlers
- `handlers/features/` - Campaigns, botnet, osint, mailing, funnels, etc.
- `handlers/moderation/` - Support, tickets, notifications handlers  
- `handlers/integrations/` - Templates, scheduler, export, geo handlers

**UI Components:**
- `core/ui_builder.py` - MenuMessage, MessageBuilder, UniversalPaginator classes
- `core/ui_components.py` - StatusIndicator, Paginator, ProgressBar classes
- `keyboards/user.py` - Compatibility wrapper for role_menus imports

**Active Entry Point:** `bot.py` - Uses single main_router from handlers/__init__.py

**Backups:** `keyboards/*.py.bak` files for reference

### Root Directory Organization
- **api/** - API endpoints (FastAPI/minimal)
- **bot.py** - Main entry point (aiogram dispatcher setup)
- **config/** - Application settings and configuration
- **core/** - Core services and business logic
- **database/** - ORM models, migrations, CRUD operations
- **docs/** - API and user guides
- **handlers/** - Telegram message handlers and command routers
- **keyboards/** - Reply and inline keyboard builders
- **middlewares/** - Request/response middleware (auth, roles, logging)
- **services/** - High-level business logic services
- **utils/** - Helper functions and utilities
- **logs/** - Log files storage
- **evidence/** - Forensic evidence storage
- **intel_reports/** - Intelligence report generation
- **sessions/** - Bot session storage
- **data/** - Forensic snapshots and data artifacts
- **attached_assets/** - User-uploaded files and media

## User Preferences
- Concise, high-level summaries over granular details
- No changelogs or date-wise entries
- Focus on core architectural decisions
- Ukrainian interface with styled formatting (dividers, emoji, button layouts)
- Prefer simplicity over unnecessary complexity

## Feature Status (December 31, 2025)
- **Baseline Functionality:** 100% Complete (All initial ТЗ implemented)
- **v2.0 Additions:** 16+ advanced modules (Forensics, AI tools, Real-time monitoring)
- **UI/UX Refactor:** ✅ Complete - Unified menu system across all roles
- **AI Integration:** ✅ Replit AI Integrations (GPT-5) - fully connected
- **See:** `FEATURE_MATRIX.md` for detailed comparison
- **See:** `docs/PROJECT_ANALYSIS_2025.md` for comprehensive analysis + 40 improvements

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

### UI/UX Standards (December 31, 2025 - UNIFIED)
- Ukrainian language throughout the interface.
- **Dividers:** exactly 15 single-line chars `───────────────` (mobile-optimized).
- **Progress bars:** native collab style `●●●●○○○○ 50%`.
- **Standardized button layouts:** 1/2/3 per row with consistent spacing.
- **Rich HTML formatting:** bold, italic, code formatting for messages.
- **Tree-like list structures:** e.g., `├ └` for hierarchical info.
- **Back buttons:** Universal `◀️ Назад` with callback_data standardization.
- **Menu consolidation:** All role menus unified in `keyboards/role_menus.py`
  - Guest, Manager, Leader, Admin menus with consistent styling
  - Unified descriptions with role-based information sections
  - Back buttons using shared `back_button()` utility function
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

## Forensics & Analysis Suite (December 2025)

### Forensic Snapshot (core/forensic_snapshot.py)
- Media file capture with original metadata preservation
- SHA-256 and SHA-512 forensic hashing
- File signature analysis and entropy calculation
- Recovery of deleted media from local cache
- Integrity verification with tamper detection

### AI Sentiment Analyzer (core/ai_sentiment.py)
- OpenAI-powered sentiment analysis (positive/negative/neutral/mixed)
- Toxicity and spam probability scoring
- Emotion extraction (joy, anger, sadness, fear, surprise)
- Intent classification (question/statement/request/complaint)
- Keyword-based fallback when AI unavailable

### Anti-Ghost Recovery (core/anti_ghost_recovery.py)
- Automatic message capture before deletion
- Edit history tracking with timestamps
- Message search across captured content
- Recovery of deleted text and media references
- Statistics by chat and user

### X-Ray Metadata (core/xray_metadata.py)
- Deep file analysis with signature detection
- EXIF extraction for images (camera, GPS, timestamps)
- Hidden data discovery (embedded URLs, emails, strings)
- Anomaly detection (high entropy, multi-signature, suspicious patterns)
- Risk score calculation

### Memory Indexer (core/memory_indexer.py)
- In-memory full-text search with inverted index
- Tokenization with stop-word filtering
- Multi-type indexing (messages, users, media, channels)
- Relevance scoring with recency boost
- Fast search with configurable limits

### Enhanced Monitoring (core/enhanced_monitoring.py)
- Target-based monitoring (channels, chats, users)
- Keyword and regex triggers
- Spam pattern detection
- Alert system with severity levels
- Event tracking and statistics

## UI System Refactor (December 31, 2025)

### Consolidation Summary
**Problem:** 2 different styling systems for funnels/buttons across roles, especially in back navigation
**Solution:** Unified keyboard system in `keyboards/role_menus.py`

### Key Changes
1. **Centralized All Menus:**
   - Guest menu, Manager menu, Leader menu, Admin menu
   - License, Subscription, Settings menus
   - Broadcast and confirmation menus
   - All previously scattered across `admin.py`, `user.py`, `admin_kb.py`

2. **Consistent Styling:**
   - `DIVIDER = "───────────────"` constant used everywhere
   - `back_button()` utility function for universal back buttons
   - All descriptions use same structure: `<b>Title</b> <i>subtitle</i> DIVIDER content`
   - Tree structures with `├ └` symbols throughout

3. **Role-Based Dispatchers:**
   - `get_menu_by_role(role: str)` - Returns appropriate menu
   - `get_description_by_role(role: str)` - Returns consistent role description
   - All callback_data normalized to standard patterns

4. **Handler Updates:**
   - `handlers/user.py` now imports from `keyboards.role_menus`
   - `main_menu()` function added for universal main menu access
   - All menu functions available in single import source

### Architecture Benefit
- **No Function Loss:** All previous functionality preserved
- **Single Source of Truth:** One file for all menu definitions
- **Easy Maintenance:** Changes to UI styling affect all roles uniformly
- **Extensibility:** New menus added to one place, instantly available to all handlers

## Keyboard System Consolidation (December 31, 2025 - COMPLETE)

### Full Consolidation Status
✅ **100% Complete** - All 8 specialized keyboard files merged into `keyboards/role_menus.py`

#### Files Consolidated:
1. **keyboards/advanced_kb.py** → 8 functions (AI analysis, spam check, drip campaigns, behavior, keywords, reports)
2. **keyboards/notifications_kb.py** → 14 functions (notifications, bans management, project stats)
3. **keyboards/forensics_kb.py** → 13 functions (forensics, monitoring, sentiment analysis, metadata)
4. **keyboards/templates_kb.py** → 10 functions (templates, scheduling)
5. **keyboards/support_kb.py** → 7 functions (support tickets, categories, ratings)
6. **keyboards/application_kb.py** → 1 function (application duration)
7. **keyboards/guest_kb.py** → 2 functions (guest menu, tariffs)
8. **keyboards/user_kb.py** → 1 function (user main menu)

**Total: 56 functions consolidated into single file**

#### Handler Updates:
✅ All 6 handlers updated to import from `keyboards.role_menus`:
- `handlers/advanced_tools.py`
- `handlers/forensics.py`
- `handlers/guest_flow.py`
- `handlers/notifications_handler.py`
- `handlers/support_handler.py`
- `handlers/templates_handler.py`

#### Backup Created:
All original files backed up with `.bak` extension in `keyboards/` directory

#### Benefits Achieved:
1. **Single Source of Truth** - All 431 keyboard buttons in one file
2. **Consistent Styling** - All menus use same dividers, back buttons, formatting
3. **Easier Maintenance** - Changes to UI style affect all roles uniformly
4. **No Function Loss** - All 56 functions preserved with identical functionality
5. **Clear Organization** - Menus grouped by functional area (Advanced Tools, Notifications, Forensics, etc.)

#### Architecture:
```
keyboards/role_menus.py
├─ Universal Components (back_button, DIVIDER)
├─ Role-Based Menus (Guest, Manager, Leader, Admin)
├─ Additional Menus (License, Subscription, Settings, Broadcast)
├─ Advanced Tools (8 functions)
├─ Notifications & Bans (14 functions)
├─ Forensics (13 functions)
├─ Templates & Scheduling (10 functions)
├─ Support (7 functions)
└─ Misc Keyboards (3 functions)
```

#### System Status:
- ✅ Bot running successfully
- ✅ All services initialized
- ✅ Database connected
- ✅ Imports working correctly
