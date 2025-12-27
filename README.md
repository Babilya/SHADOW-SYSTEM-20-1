# SHADOW SYSTEM iO v2.0

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-SHADOW-red)
![Platform](https://img.shields.io/badge/platform-Telegram-0088cc)

**Professional Ukrainian Telegram Marketing Automation Platform**

*Професійна українськомовна платформа автоматизації маркетингу в Telegram*

</div>

---

## Overview

SHADOW SYSTEM iO v2.0 is a comprehensive Telegram marketing automation platform designed for Ukrainian-language operations. It provides advanced functionality for managing bot networks, mass messaging campaigns, OSINT intelligence gathering, team collaboration, and AI-powered features. The system uses SHADOW license keys for authorization and implements enterprise-grade security measures.

---

## Table of Contents

1. [Key Features](#key-features)
2. [System Architecture](#system-architecture)
3. [Core Modules](#core-modules)
4. [Advanced Tools](#advanced-tools)
5. [Security & Encryption](#security--encryption)
6. [Role-Based Access Control](#role-based-access-control)
7. [OSINT Capabilities](#osint-capabilities)
8. [Campaign Management](#campaign-management)
9. [Funnel System](#funnel-system)
10. [AI Integration](#ai-integration)
11. [Real-Time Monitoring](#real-time-monitoring)
12. [Installation & Setup](#installation--setup)
13. [API Reference](#api-reference)
14. [Technology Stack](#technology-stack)

---

## Key Features

### Bot Network Management
| Feature | Description |
|---------|-------------|
| **Session Import** | Support for Telethon .session, Pyrogram JSON, TData archives, StringSession |
| **Encrypted Storage** | AES-256-CBC encryption with HKDF key derivation |
| **Bot Warming** | 72-hour, 3-phase warming cycles with progress tracking |
| **Proxy Management** | SOCKS5/HTTP proxy rotation with health monitoring |
| **Mass Control** | Bulk operations on multiple bots simultaneously |
| **Anti-Detect Profiles** | Device fingerprinting and profile randomization |
| **Flood Protection** | Automatic FloodWait handling with retry logic |

### Campaign & Mailing System
| Feature | Description |
|---------|-------------|
| **Campaign Types** | Broadcast, targeted, drip, sequential, A/B testing |
| **Smart Scheduling** | Time-based presets (60min, 240min, daily, weekly) |
| **Rate Limiting** | 30 req/sec global, 25 req/sec per bot |
| **Async Workers** | Message queue with 3 concurrent async workers |
| **Adaptive Delays** | Dynamic delay calculation based on success rate |
| **Real-Time Stats** | Live delivery, open, and response tracking |
| **Template System** | Full CRUD for message templates with variables |

### Team Collaboration
| Feature | Description |
|---------|-------------|
| **CRM Integration** | Built-in CRM for manager operations |
| **Invite Codes** | INV code generation for team onboarding |
| **Activity Tracking** | Comprehensive activity logs per user |
| **Referral System** | Multi-tier referral bonuses |
| **Ticket Support** | Full ticket system with status tracking |
| **Role Hierarchy** | GUEST → MANAGER → LEADER → ADMIN |

### Analytics & Reporting
| Feature | Description |
|---------|-------------|
| **PDF Reports** | Professional PDF generation with ReportLab |
| **Data Export** | JSON, CSV, HTML export formats |
| **CRM Export** | Integration with Notion, Airtable, Google Sheets |
| **User Segmentation** | Automatic tagging (new_user, active, inactive, power_user, paying) |
| **Conversion Tracking** | Funnel-level conversion analytics |
| **Key Notifications** | License expiry alerts and reminders |

---

## System Architecture

```
shadow-system/
├── main.py                    # Application entry point
├── bot.py                     # Bot initialization
├── config/
│   ├── settings.py            # Global configuration
│   ├── constants.py           # System constants
│   └── limits.py              # Rate limits and thresholds
│
├── core/                      # Core Services (25+ modules)
│   ├── role_constants.py      # Unified role definitions (RBAC)
│   ├── states.py              # Centralized FSM states
│   ├── ai_service.py          # OpenAI/GPT integration
│   ├── encryption.py          # AES-256-CBC encryption manager
│   ├── session_validator.py   # Multi-format session validation
│   ├── rate_limiter.py        # Token bucket rate limiting
│   ├── message_queue.py       # Async message queue (3 workers)
│   ├── mailing_scheduler.py   # Campaign scheduling engine
│   ├── anti_fraud.py          # Behavioral fraud detection
│   ├── segmentation.py        # User segmentation engine
│   ├── audit_logger.py        # Comprehensive audit logging
│   ├── alerts.py              # Notification system
│   ├── alert_thresholds.py    # Dynamic rules engine
│   ├── ui_components.py       # Paginator, ProgressBar, MenuBuilder
│   ├── background_tasks.py    # Non-blocking heavy operations
│   │
│   ├── # Advanced Campaign System
│   ├── advanced_campaign_manager.py  # Worker pool with async queues
│   ├── mailing_engine.py             # Core mailing logic
│   ├── mass_sender.py                # Mass messaging with FloodWait handling
│   ├── psyops_campaign.py            # PsyOps message templates
│   │
│   ├── # OSINT Engine
│   ├── advanced_osint_engine.py      # Deep analysis system
│   ├── rapid_osint.py                # Fast channel scanning
│   ├── realtime_monitor.py           # Telethon event listener
│   │
│   ├── # Advanced Tools (AI-Powered)
│   ├── ai_pattern_detection.py       # GPT threat analysis
│   ├── spam_analyzer.py              # Pre-send spam checking
│   ├── drip_campaign.py              # Cascading campaigns
│   ├── behavior_profiler.py          # User pattern analysis
│   ├── keyword_analyzer.py           # Text/keyword analysis
│   └── enhanced_reports.py           # PDF report generator
│
├── database/
│   ├── models.py              # SQLAlchemy ORM models (20+ tables)
│   ├── crud.py                # Database operations
│   └── migrations/            # Schema migrations
│
├── handlers/                  # Telegram Bot Handlers (25+ routers)
│   ├── start.py               # /start, welcome flow
│   ├── auth.py                # Authentication, SHADOW keys
│   ├── admin.py               # Admin panel operations
│   ├── funnels.py             # Funnel CRUD
│   ├── osint.py               # OSINT tools interface
│   ├── osint_handlers.py      # OSINT callback handlers
│   ├── mailing.py             # Campaign management
│   ├── botnet.py              # Bot network control
│   ├── campaigns.py           # Campaign center
│   ├── team.py                # Team management
│   ├── analytics.py           # Analytics dashboard
│   ├── warming.py             # Bot warming cycles
│   ├── proxy.py               # Proxy management
│   ├── geo.py                 # Geo Scanner
│   ├── templates.py           # Template CRUD
│   ├── support.py             # Ticket system
│   ├── notifications.py       # Notifications, bans, stats
│   ├── advanced_tools.py      # AI-powered tools
│   └── missing.py             # Fallback handler
│
├── keyboards/                 # Telegram Inline Keyboards
│   ├── role_menus.py          # Role-based menus
│   ├── admin_kb.py            # Admin keyboards
│   ├── funnel_kb.py           # Funnel keyboards
│   ├── osint_kb.py            # OSINT keyboards
│   ├── advanced_kb.py         # Advanced tools keyboards
│   └── ...                    # Other keyboard modules
│
├── middlewares/               # Request Processing
│   ├── auth_middleware.py     # Authentication checks
│   ├── role_middleware.py     # Role verification
│   ├── rate_limit_middleware.py  # Rate limiting
│   └── logging_middleware.py  # Request logging
│
├── services/                  # Business Logic Layer
│   ├── user_service.py        # User management
│   ├── funnel_service.py      # Funnel operations
│   ├── osint_service.py       # OSINT operations
│   ├── mailing_service.py     # Mailing operations
│   └── key_service.py         # License key management
│
└── utils/                     # Utilities
    ├── db.py                  # Database connection pool
    ├── helpers.py             # Common helpers
    ├── formatters.py          # Text formatting
    └── validators.py          # Input validation
```

---

## Core Modules

### 1. Role Management System
**File:** `core/role_constants.py`

```python
class UserRole:
    GUEST = 0      # View tariffs, submit applications
    MANAGER = 1    # Mailings, OSINT, botnet operation
    LEADER = 2     # Team management, license generation, funnels
    ADMIN = 3      # Full system control, emergency access
    ROOT = 4       # Super admin (system level)
```

### 2. Encryption Manager
**File:** `core/encryption.py`

| Feature | Specification |
|---------|---------------|
| Algorithm | AES-256-CBC |
| Key Derivation | HKDF (HMAC-based) |
| Key Types | Separate keys for sessions, proxies, data |
| Fallback | XOR encryption when cryptography unavailable |
| Salt | Random 16-byte salt per encryption |

### 3. Session Validator
**File:** `core/session_validator.py`

Performs 5 validation tests on imported sessions:
1. **Connection Test** - Verifies network connectivity
2. **Authorization Test** - Checks session authorization status
3. **Rate Limit Test** - Detects flood wait states
4. **Privacy Test** - Verifies privacy settings access
5. **Functionality Test** - Tests basic API operations

Supported formats:
- Telethon `.session` files
- Pyrogram JSON sessions
- TData archives
- StringSession format

### 4. Rate Limiter
**File:** `core/rate_limiter.py`

| Limit Type | Value |
|------------|-------|
| Global Rate | 30 requests/second |
| Per-Bot Rate | 25 requests/second |
| Burst Capacity | 50 requests |
| Algorithm | Token Bucket |

### 5. Message Queue
**File:** `core/message_queue.py`

| Parameter | Value |
|-----------|-------|
| Workers | 3 async workers |
| Queue Type | asyncio.Queue |
| Retry Logic | 3 retries with exponential backoff |
| Priority | Supports priority queuing |

### 6. Mailing Scheduler
**File:** `core/mailing_scheduler.py`

Scheduling presets:
- **Interval**: 60 minutes, 240 minutes
- **Daily**: 1440 minutes (24 hours)
- **Weekly**: 10080 minutes (7 days)
- **Custom**: User-defined intervals

### 7. Anti-Fraud System
**File:** `core/anti_fraud.py`

Detection methods:
- Behavioral pattern analysis
- Velocity checks (action frequency)
- Device fingerprint verification
- Session anomaly detection
- Geographic inconsistency detection

### 8. User Segmentation
**File:** `core/segmentation.py`

Automatic segments:
| Segment | Criteria |
|---------|----------|
| `new_user` | Registered < 7 days |
| `active` | Activity in last 24 hours |
| `inactive` | No activity > 30 days |
| `power_user` | > 100 actions/week |
| `paying` | Active subscription |

### 9. Audit Logger
**File:** `core/audit_logger.py`

Logged events:
- User authentication (login/logout)
- Role changes
- Campaign operations
- OSINT queries
- Admin actions
- Security incidents

### 10. UI Components
**File:** `core/ui_components.py`

| Component | Description |
|-----------|-------------|
| `Paginator` | Infinite scroll pagination for lists |
| `ProgressBar` | Visual progress indicators |
| `MenuBuilder` | Dynamic keyboard construction |

---

## Advanced Tools

### 1. AI Pattern Detection
**File:** `core/ai_pattern_detection.py`

GPT-powered threat analysis system:

| Detection Type | Patterns |
|----------------|----------|
| **Coordinates** | Decimal (50.4501, 30.5234), DMS (50°27'00"N), MGRS (36U XC 12345), Google Maps links |
| **Phones** | UA (+380), RU (+7), BY (+375), PL (+48) |
| **Crypto** | BTC (1A1zP1...), ETH (0x...), USDT TRC-20 (T...) |
| **Threats** | 4 levels: Critical, High, Medium, Low |
| **Encoded Data** | Base64, Hex patterns |

Risk scoring: 0-100 with configurable thresholds.

### 2. Spam Analyzer
**File:** `core/spam_analyzer.py`

Pre-send analysis metrics:

| Metric | Weight |
|--------|--------|
| Caps Ratio | 15% |
| Link Density | 20% |
| Keyword Density | 25% |
| Emoji Count | 10% |
| Special Characters | 10% |
| Message Length | 10% |
| Readability | 10% |

Risk levels: `LOW` (0-30), `MEDIUM` (31-60), `HIGH` (61-100)

### 3. Drip Campaign Manager
**File:** `core/drip_campaign.py`

Sequential campaign automation:

| Trigger Type | Description |
|--------------|-------------|
| `TIME` | Delay-based progression |
| `MESSAGE_OPENED` | On message read |
| `LINK_CLICKED` | On link interaction |
| `REPLY_RECEIVED` | On user response |

Conditional transitions:
- `has_replied` - User responded
- `no_replies` - No response after X time
- `link_clicked` - Specific link interaction

### 4. Behavior Profiler
**File:** `core/behavior_profiler.py`

User activity analysis:

| Analysis Type | Output |
|---------------|--------|
| Daily Rhythm | Morning/Afternoon/Evening/Night distribution |
| Sleep Schedule | Estimated sleep hours (e.g., 23:00-07:00) |
| Peak Hours | Top 3 most active hours |
| Consistency | Activity regularity score (0-100%) |
| User Type | Classification (see below) |

User type classifications:
- `night_owl` - Primary activity 22:00-04:00
- `early_bird` - Primary activity 05:00-09:00
- `office_hours` - Primary activity 09:00-18:00
- `heavy_user` - > 50 daily actions
- `passive` - < 5 daily actions
- `irregular` - No consistent pattern

Anomaly detection:
- Activity spikes (> 3σ deviation)
- Long absences (> 7 days)
- Pattern changes (sudden behavior shift)

### 5. Enhanced Report Generator
**File:** `core/enhanced_reports.py`

Professional PDF report generation:

| Report Type | Contents |
|-------------|----------|
| **OSINT Report** | Findings, threats, evidence, network graph |
| **Campaign Report** | Delivery stats, conversions, A/B results |
| **User Profile** | Behavior analysis, activity history, predictions |
| **Analytics Report** | Project overview, team metrics, trends |

Requires: ReportLab library

### 6. Keyword Analyzer
**File:** `core/keyword_analyzer.py`

Text analysis capabilities:

| Feature | Description |
|---------|-------------|
| Word Frequency | Top N most common words |
| Sentiment | Positive/Negative/Neutral classification |
| Language Detection | Ukrainian, Russian, English |
| Readability Score | Flesch-Kincaid adapted for Cyrillic |
| Trending Words | Statistical outlier detection |

Stop words: Ukrainian (200+), Russian (200+) built-in lists

### 7. Botnet Manager
**File:** `core/botnet_manager.py`

Enterprise botnet management system:

| Feature | Description |
|---------|-------------|
| Worker Pool | Async task queue with configurable workers |
| Bot Selection | Round-robin, weighted, smart, geolocation strategies |
| Health Monitoring | Automatic health checks every 5 minutes |
| Auto Recovery | Automatic bot recovery after failures |
| Daily Limits | Per-bot message limits with midnight reset |
| Statistics | Real-time success rate, health score tracking |

Bot statuses:
- `ACTIVE` - Ready for tasks
- `PAUSED` - Manually paused
- `BUSY` - Executing task
- `FLOOD_WAIT` - Telegram rate limited
- `BANNED` - Account banned
- `DEAD` - Session expired
- `WARMING` - In warming phase
- `COOLING` - In cooldown period

### 8. AntiDetect System
**File:** `core/antidetect.py`

Device masking and behavior emulation:

| Device Profiles | Description |
|-----------------|-------------|
| `android_samsung_s21` | Samsung Galaxy S21, Android 12 |
| `android_samsung_a52` | Samsung Galaxy A52, Android 11 |
| `android_xiaomi` | Redmi Note 10, Android 11 |
| `android_pixel` | Pixel 6, Android 13 |
| `iphone_13` | iPhone 13 Pro, iOS 16.2 |
| `iphone_12` | iPhone 12, iOS 15.6 |
| `desktop_windows` | Windows 10 Desktop |
| `desktop_macos` | MacBook Pro, macOS 13.1 |
| `desktop_linux` | Ubuntu 22.04 Desktop |

Behavior patterns:
- `casual_user` - Typical user, 9-12 & 18-23 online
- `active_user` - High activity, 8-24 online
- `business_user` - Office hours, formal communication
- `night_owl` - Late night activity, 20-04
- `early_bird` - Early morning, 5-10 & 19-22

Fingerprint components:
- Canvas hash, WebGL hash, Audio hash, Font hash
- Screen resolution, Device ID, Session ID
- Unique fingerprint hash per bot

### 9. Recovery System
**File:** `core/recovery_system.py`

Automatic recovery and failover:

| Feature | Description |
|---------|-------------|
| Auto Recovery | 5-step recovery process |
| Proxy Rotation | Automatic proxy switching on failure |
| Backup System | Session backups with versioning |
| Health Checks | Proxy pool health monitoring |
| Batch Recovery | Mass bot recovery operations |

Recovery process:
1. Try reconnection
2. Rotate proxy and retry
3. Restore from backup
4. Mark as dead if all fail

### 10. Session Importer
**File:** `core/session_importer.py`

Multi-format session import:

| Format | Extension | Description |
|--------|-----------|-------------|
| Telethon Binary | `.session` | SQLite database format |
| Pyrogram JSON | `.json` | JSON with auth_key |
| String Session | `.txt` | Base64 encoded string |
| TData Archive | `.zip` | Telegram Desktop data |

Validation tests:
1. Connection test
2. Authorization test
3. Rate limit test
4. Privacy test
5. Functionality test

---

## Security & Encryption

### SHADOW Key System

License key format: `SHADOW-XXXX-XXXX-XXXX-XXXX`

| Key Type | Duration | Capabilities |
|----------|----------|--------------|
| Trial | 7 days | Limited features |
| Standard | 30 days | Full manager access |
| Premium | 90 days | Leader capabilities |
| Enterprise | 365 days | Full admin access |

Key features:
- One-time activation
- Telegram ID binding
- Hardware fingerprint optional
- Revocation support

### Encryption Standards

| Data Type | Algorithm | Key Size |
|-----------|-----------|----------|
| Sessions | AES-256-CBC | 256-bit |
| Proxies | AES-256-CBC | 256-bit |
| User Data | AES-256-GCM | 256-bit |
| Passwords | Argon2id | N/A |

### Security Measures

1. **IP Whitelisting** - Admin access restricted by IP
2. **Rate Limiting** - Token bucket algorithm
3. **Flood Protection** - Automatic FloodWait handling
4. **Session Validation** - 5-step verification
5. **Audit Logging** - All actions recorded
6. **Anti-Fraud** - Behavioral analysis
7. **Emergency Router** - Critical system control

---

## Role-Based Access Control

### Permission Matrix

| Feature | GUEST | MANAGER | LEADER | ADMIN |
|---------|:-----:|:-------:|:------:|:-----:|
| View Tariffs | ✓ | ✓ | ✓ | ✓ |
| Submit Applications | ✓ | ✓ | ✓ | ✓ |
| Basic Mailings | | ✓ | ✓ | ✓ |
| OSINT Tools | | ✓ | ✓ | ✓ |
| Botnet Operation | | ✓ | ✓ | ✓ |
| Template Management | | ✓ | ✓ | ✓ |
| Team Management | | | ✓ | ✓ |
| License Generation | | | ✓ | ✓ |
| Funnel Management | | | ✓ | ✓ |
| Advanced Tools | | | ✓ | ✓ |
| User Bans | | | | ✓ |
| System Configuration | | | | ✓ |
| Emergency Control | | | | ✓ |
| Audit Access | | | | ✓ |

---

## OSINT Capabilities

### Available Tools

| Tool | Description | Output |
|------|-------------|--------|
| **DNS Lookup** | Domain DNS records | A, AAAA, MX, TXT, NS records |
| **WHOIS** | Domain registration info | Registrar, dates, contacts |
| **GeoIP** | IP geolocation | Country, city, ISP, coordinates |
| **Email Verify** | Email validation | Syntax, MX, deliverability |
| **User Analysis** | Telegram profile deep scan | Activity, groups, connections |
| **Chat Analysis** | Channel/group parsing | Members, messages, patterns |
| **Contact Export** | Member extraction | JSON/CSV with metadata |

### Advanced OSINT Engine
**File:** `core/advanced_osint_engine.py`

| Feature | Description |
|---------|-------------|
| Network Graph | Relationship mapping with influence scores |
| Threat Assessment | Risk scoring based on keywords and patterns |
| Pattern Detection | Phones, crypto, coordinates, emails |
| Evidence Storage | Hash-verified evidence with timestamps |
| Keyword Detection | UK/RU/EN suspicious keyword lists |

### Rapid OSINT Parser
**File:** `core/rapid_osint.py`

Fast channel scanning:
- Multi-channel parallel scanning
- Pattern extraction in real-time
- Threat scoring system
- JSON report generation
- User lookup functionality

### Real-Time Monitor
**File:** `core/realtime_monitor.py`

Telethon-based event listener:

| Event Type | Handler |
|------------|---------|
| NewMessage | Content analysis, pattern matching |
| ChatAction | Join/leave, admin changes |
| MessageEdited | Change tracking |

Auto-actions:
- `block_user` - Automatic blocking
- `log_evidence` - Evidence capture
- `alert_admins` - Admin notifications
- `escalate` - Priority escalation

---

## Campaign Management

### Campaign Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Broadcast** | One-time mass message | Announcements |
| **Targeted** | Segmented audience | Personalization |
| **Drip** | Sequential messages | Onboarding |
| **A/B Test** | Split testing | Optimization |
| **Scheduled** | Time-based delivery | Planning |

### Advanced Campaign Manager
**File:** `core/advanced_campaign_manager.py`

| Feature | Description |
|---------|-------------|
| Worker Pool | Async queue-based workers |
| Bot Selection | Weighted round-robin algorithm |
| Delay Calculation | Adaptive based on success rate |
| Statistics | Lock-safe real-time updates |
| A/B Testing | Built-in variant support |

### Mass Sender
**File:** `core/mass_sender.py`

| Parameter | Value |
|-----------|-------|
| Batch Size | 30 messages |
| Base Delay | 3 seconds |
| Max Delay | 60 seconds |
| Retry Count | 3 attempts |
| FloodWait Handling | Automatic pause + retry |

---

## Funnel System

### Funnel Features

| Feature | Description |
|---------|-------------|
| Multi-Step | Unlimited steps per funnel |
| Photo Support | Images in funnel messages |
| Tariff Config | Per-funnel pricing |
| Conversion Tracking | Step-by-step analytics |
| AI Generation | GPT-powered step creation |
| Template Integration | Use templates as steps |
| Scheduling | Time-based step triggers |

### Funnel Integrations

| Integration | Callback Pattern |
|-------------|------------------|
| Templates | `funnel_templates_{funnel_id}` |
| Scheduling | `funnel_schedule_{funnel_id}` |
| Mailings | `funnel_mailing:{funnel_id}:menu` |
| OSINT | `funnel_osint:{funnel_id}:menu` |
| Monitoring | `funnel_monitor:{funnel_id}:menu` |

### Trigger Types

| Trigger | Description |
|---------|-------------|
| `message` | On message delivery |
| `button` | On button click |
| `time` | After time delay |
| `keyword` | On keyword match |
| `reply` | On user reply |

---

## AI Integration

### AI Service
**File:** `core/ai_service.py`

Powered by OpenAI via Replit AI Integrations.

### Available AI Features

| Feature | Description | Model |
|---------|-------------|-------|
| Campaign Text Generation | 4 styles (formal, casual, urgent, friendly) | GPT-4 |
| Sentiment Analysis | Positive/Negative/Neutral detection | GPT-4 |
| OSINT Report Generation | Automated threat reports | GPT-4 |
| Message Rewriting | 5 tones available | GPT-4 |
| Funnel Step Generation | AI-suggested funnel steps | GPT-4 |
| Chat History Analysis | Conversation summarization | GPT-4 |
| Response Templates | Auto-generated replies | GPT-4 |
| Audience Analysis | Demographic insights | GPT-4 |
| Threat Detection | Real-time content analysis | GPT-4 |

---

## Real-Time Monitoring

### Alert Thresholds System
**File:** `core/alert_thresholds.py`

Dynamic rules engine:

| Rule Type | Description |
|-----------|-------------|
| `MESSAGE_FREQUENCY` | Messages per time window |
| `KEYWORD_DETECTION` | Suspicious keyword matches |
| `COORDINATE_LEAK` | Location data exposure |
| `CRYPTO_ADDRESS` | Cryptocurrency patterns |
| `PHONE_EXPOSURE` | Phone number detection |
| `THREAT_LEVEL` | Combined risk score |

Actions:
- `LOG` - Record to audit log
- `ALERT` - Send notification
- `BLOCK_USER` - Automatic ban
- `NOTIFY_ADMIN` - Admin alert
- `ESCALATE` - Priority escalation

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Telegram Bot Token
- Telegram API Credentials (API_ID, API_HASH)
- OpenAI API Key (optional, for AI features)

### Environment Variables

```bash
# Required
BOT_TOKEN=your_telegram_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
DATABASE_URL=postgresql://user:password@host:5432/database

# Optional
OPENAI_API_KEY=your_openai_key
ENCRYPTION_KEY=your_32_byte_key
ADMIN_IDS=123456789,987654321
DEBUG=false
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-org/shadow-system.git
cd shadow-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python -c "from utils.db import init_db; import asyncio; asyncio.run(init_db())"

# 4. Run the bot
python main.py
```

### First-Time Setup

1. Start the bot with `/start`
2. As the first user, you'll be assigned ROOT role
3. Generate SHADOW keys for team members
4. Create INV codes for manager onboarding

---

## API Reference

### Database Models

| Model | Fields | Description |
|-------|--------|-------------|
| `User` | id, telegram_id, role, created_at, ... | User accounts |
| `ShadowKey` | key, user_id, expires_at, is_active | License keys |
| `Campaign` | id, name, type, status, stats, ... | Marketing campaigns |
| `Funnel` | id, name, steps, conversions, ... | Sales funnels |
| `BotSession` | id, session_data, proxy_config, ... | Bot sessions (20+ fields) |
| `Template` | id, name, content, variables, ... | Message templates |
| `Ticket` | id, user_id, status, messages, ... | Support tickets |
| `AuditLog` | id, user_id, action, details, ... | Audit records |

### BotSession Extended Fields

| Field | Type | Description |
|-------|------|-------------|
| `device_fingerprint` | JSON | Device identification |
| `anti_detect_profile` | JSON | Browser profile |
| `proxy_type` | Enum | SOCKS5/HTTP/None |
| `proxy_config` | JSON | Proxy settings |
| `warming_phase` | Integer | Current warming phase (1-3) |
| `flood_wait_until` | DateTime | FloodWait expiry |
| `success_rate` | Float | Delivery success percentage |
| `messages_sent` | Integer | Total messages sent |
| `tags` | Array | Filtering tags |

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Bot Framework** | aiogram | 3.3+ |
| **Database** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Async Driver** | asyncpg | Latest |
| **Sessions** | Telethon | Latest |
| **AI/LLM** | OpenAI API | GPT-4 |
| **Encryption** | cryptography | Latest |
| **PDF Reports** | ReportLab | Latest |
| **Templating** | Jinja2 | Latest |
| **HTTP Client** | aiohttp | Latest |

---

## Active Services (25+)

| # | Service | Description |
|---|---------|-------------|
| 1 | RateLimiter | Token bucket rate limiting |
| 2 | MessageQueue | 3 async workers |
| 3 | MailingScheduler | Campaign scheduling |
| 4 | AntiFraud | Behavioral analysis |
| 5 | Segmentation | Automatic user tagging |
| 6 | KeyNotifications | License expiry alerts |
| 7 | SecurityCache | Fast user blocking |
| 8 | AuditLogger | Action tracking |
| 9 | EncryptionManager | AES-256 encryption |
| 10 | AIService | GPT integration |
| 11 | SessionValidator | Session verification |
| 12 | AdvancedCampaignManager | Async campaign execution |
| 13 | AdvancedOSINTEngine | Deep OSINT analysis |
| 14 | RealTimeMonitor | Event-based monitoring |
| 15 | AlertThresholds | Dynamic rules engine |
| 16 | AIPatternDetector | Threat detection |
| 17 | SpamAnalyzer | Pre-send analysis |
| 18 | DripCampaignManager | Sequential campaigns |
| 19 | BehaviorProfiler | User profiling |
| 20 | KeywordAnalyzer | Text analysis |
| 21 | EnhancedReportGenerator | PDF generation |
| 22 | MassSender | Bulk messaging |
| 23 | RapidOSINTParser | Fast scanning |
| 24 | FunnelService | Funnel operations |
| 25 | TicketService | Support system |

---

## Registered Handlers (25+)

```python
# Main routers in registration order
start_router          # /start, welcome flow
auth_router           # Authentication
subs_router           # Subscriptions
tickets_router        # Ticket handling
admin_router          # Admin panel
osint_router          # OSINT tools
botnet_router         # Bot network
campaigns_router      # Campaigns
team_router           # Team management
analytics_router      # Analytics
config_router         # Configuration
help_router           # Help system
funnels_router        # Funnels
warming_router        # Bot warming
mailing_router        # Mailings
geo_router            # Geo Scanner
proxy_router          # Proxy management
advanced_router       # Advanced features
osint_handler_router  # OSINT callbacks
texting_router        # Texting
scheduler_router      # Scheduling
templates_router      # Templates
support_router        # Support
notifications_router  # Notifications
advanced_tools_router # AI-powered tools
missing_router        # Fallback handler
```

---

## UI/UX Standards

- **Language**: Ukrainian throughout
- **Dividers**: `═══════════════════════`
- **Button Layout**: 1/2/3 buttons per row
- **Formatting**: HTML (bold, italic, code)
- **Lists**: Tree structure (`├ └`)
- **Emojis**: Standardized per feature type

---

## License

This software is proprietary and requires a valid SHADOW license key for operation.

---

## Support

For technical support, use the built-in ticket system or contact your administrator.

---

<div align="center">

**SHADOW SYSTEM iO v2.0**

*Built for Ukrainian Marketing Professionals*

</div>
