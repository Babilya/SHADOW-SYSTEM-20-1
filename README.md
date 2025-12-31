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

**Current Status (December 31, 2025):** Production Ready. Entry point: `bot.py`

**New in v2.0.2:**
- Structured Logging with categorized events (SECURITY, CAMPAIGN, DM, PARSER, FLOOD, SYSTEM)
- Flood Monitor with severity-based alerts (LOW/MEDIUM/HIGH/CRITICAL)
- Comprehensive Unit Test Suite (33 tests via pytest)
- API Reference Documentation (docs/API_REFERENCE.md)
- RBAC enforcement on all admin handlers

**v2.0.1:**
- Real-time System Stats (CPU/RAM/Disk via psutil)
- Health Dashboard with service monitoring
- In-memory Cache Service with TTL
- Enhanced REST API (OSINT, AI, System endpoints)
- 40+ improvement recommendations documented

---

## Table of Contents

1. [Key Features](#key-features)
2. [System Architecture](#system-architecture)
3. [Core Services](#core-services)
4. [Botnet Infrastructure](#botnet-infrastructure)
5. [Advanced Parsing & Monitoring](#advanced-parsing--monitoring)
6. [Forensics & Analysis Suite](#forensics--analysis-suite)
7. [Structured Logging & Monitoring](#structured-logging--monitoring)
8. [Security & Encryption](#security--encryption)
9. [Role-Based Access Control](#role-based-access-control)
10. [OSINT Capabilities](#osint-capabilities)
11. [Campaign Management](#campaign-management)
12. [Funnel System](#funnel-system)
13. [AI Integration](#ai-integration)
14. [Testing](#testing)
15. [Technology Stack](#technology-stack)

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
| **Anti-Detect Profiles** | 9 device profiles with 5 behavior patterns |
| **Flood Protection** | Automatic FloodWait handling with recovery |

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
├── bot.py                     # Main entry point (aiogram dispatcher)
├── config/                    # Application settings and configuration
│   ├── settings.py            # Global configuration
│   ├── constants.py           # System constants
│   └── limits.py              # Rate limits and thresholds
│
├── core/                      # Core Services (40+ modules)
│   ├── role_constants.py      # Unified role definitions (RBAC)
│   ├── states.py              # Centralized FSM states
│   ├── encryption.py          # AES-256-CBC encryption manager
│   ├── session_validator.py   # Multi-format session validation
│   ├── rate_limiter.py        # Token bucket rate limiting
│   ├── message_queue.py       # Async message queue (3 workers)
│   ├── audit_logger.py        # Comprehensive audit logging
│   ├── ui_components.py       # Paginator, ProgressBar, MenuBuilder
│   │
│   ├── # Campaign & Mailing
│   ├── advanced_campaign_manager.py
│   ├── mailing_engine.py
│   ├── mass_sender.py
│   ├── mailing_scheduler.py
│   │
│   ├── # Botnet Infrastructure
│   ├── botnet_manager.py      # Worker pool, bot selection, health monitoring
│   ├── antidetect.py          # 9 device profiles, 5 behavior patterns
│   ├── recovery_system.py     # 4-step auto-recovery, proxy rotation
│   ├── session_importer.py    # Multi-format import with 5-step validation
│   │
│   ├── # Advanced Parsing & Monitoring
│   ├── advanced_parser.py     # Deep chat parsing, threat analysis
│   ├── realtime_parser.py     # Real-time monitoring with configurable intervals
│   ├── osint_telethon.py      # Telethon integration for parsing
│   │
│   ├── # Forensics & Analysis Suite
│   ├── forensic_snapshot.py   # Media capture, SHA-256/512 hashing
│   ├── ai_sentiment.py        # OpenAI-powered sentiment analysis
│   ├── anti_ghost_recovery.py # Message capture before deletion
│   ├── xray_metadata.py       # Deep file analysis, EXIF extraction
│   ├── memory_indexer.py      # In-memory full-text search
│   ├── enhanced_monitoring.py # Target-based monitoring with triggers
│   │
│   ├── # OSINT Engine
│   ├── advanced_osint_engine.py
│   ├── rapid_osint.py
│   │
│   ├── # Advanced Tools (AI-Powered)
│   ├── ai_pattern_detection.py
│   ├── spam_analyzer.py
│   ├── drip_campaign.py
│   ├── behavior_profiler.py
│   ├── keyword_analyzer.py
│   └── enhanced_reports.py
│
├── database/
│   ├── models.py              # SQLAlchemy ORM models
│   ├── crud.py                # Database operations
│   └── migrations/            # Schema migrations
│
├── handlers/                  # Telegram Bot Handlers (25+ routers)
│   ├── start.py               # /start, welcome flow
│   ├── auth.py                # Authentication, SHADOW keys
│   ├── admin.py               # Admin panel operations
│   ├── funnels.py             # Funnel CRUD
│   ├── osint.py               # OSINT tools interface
│   ├── mailing.py             # Campaign management
│   ├── botnet.py              # Bot network control
│   ├── team.py                # Team management
│   ├── analytics.py           # Analytics dashboard
│   ├── templates.py           # Template CRUD
│   └── support.py             # Ticket system
│
├── keyboards/                 # Telegram Inline Keyboards
│   ├── role_menus.py          # Role-based menus
│   ├── admin_kb.py            # Admin keyboards
│   ├── funnel_kb.py           # Funnel keyboards
│   └── osint_kb.py            # OSINT keyboards
│
├── middlewares/               # Request Processing
│   ├── auth_middleware.py     # Authentication checks
│   ├── role_middleware.py     # Role verification
│   └── logging_middleware.py  # Request logging
│
├── services/                  # Business Logic Layer
│   ├── user_service.py        # User management
│   ├── funnel_service.py      # Funnel operations
│   ├── osint_service.py       # OSINT operations
│   └── mailing_service.py     # Mailing operations
│
└── utils/                     # Utilities
    ├── db.py                  # Database connection pool
    ├── helpers.py             # Common helpers
    └── formatters.py          # Text formatting
```

---

## Core Services

### 1. Role Management System
**File:** `core/role_constants.py`

```python
class UserRole:
    GUEST = 0      # View tariffs, submit applications
    MANAGER = 1    # Mailings, OSINT, botnet operation
    LEADER = 2     # Team management, license generation
    ADMIN = 3      # Full system control
    ROOT = 4       # Super admin (system level)
```

### 2. Unified Encryption Manager
**File:** `core/encryption.py`

| Feature | Specification |
|---------|---------------|
| Algorithm | AES-256-CBC |
| Key Derivation | HKDF (HMAC-based) |
| Key Types | Separate keys for sessions, proxies, data |
| Salt | Random 16-byte salt per encryption |

### 3. Session Validator
**File:** `core/session_validator.py`

Performs 5 validation tests:
1. **Connection Test** - Network connectivity
2. **Authorization Test** - Session auth status
3. **Rate Limit Test** - Flood wait detection
4. **Privacy Test** - Privacy settings access
5. **Functionality Test** - API operations

### 4. Rate Limiter
**File:** `core/rate_limiter.py`

| Limit Type | Value |
|------------|-------|
| Global Rate | 30 requests/second |
| Per-Bot Rate | 25 requests/second |
| Algorithm | Token Bucket |

### 5. Audit Logger
**File:** `core/audit_logger.py`

Logged events:
- User authentication (login/logout)
- Role changes
- Campaign operations
- OSINT queries
- Admin actions
- Security incidents

---

## Botnet Infrastructure

### BotnetManager
**File:** `core/botnet_manager.py`

| Feature | Description |
|---------|-------------|
| Worker Pool | Async task queue with configurable workers |
| Bot Selection | Round-robin, weighted, random, smart strategies |
| Health Monitoring | Automatic checks every 5 minutes |
| Daily Limits | Per-bot message limits with midnight reset |
| Auto Recovery | Automatic bot recovery after failures |
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

### AntiDetect System
**File:** `core/antidetect.py`

Device profiles (9 total):
- Samsung Galaxy (S21, A52)
- Xiaomi Redmi
- iPhone (13, 12)
- Pixel
- Desktop (Windows, macOS, Linux)

Behavior patterns (5 types):
- `casual_user` - Typical user, 9-12 & 18-23 online
- `active_user` - High activity, 8-24 online
- `business_user` - Office hours, formal communication
- `night_owl` - Late night activity, 20-04
- `early_bird` - Early morning, 5-10 & 19-22

Fingerprint components:
- Canvas hash, WebGL hash, Audio hash, Font hash
- Screen resolution, Device ID, Session ID

### Recovery System
**File:** `core/recovery_system.py`

4-step auto-recovery process:
1. Try reconnection
2. Rotate proxy and retry
3. Restore from backup
4. Mark as dead if all fail

Additional features:
- Proxy pool with rotation
- Session backup with versioning
- Batch recovery operations
- Proxy health monitoring

### Session Importer
**File:** `core/session_importer.py`

Supported formats:
| Format | Extension | Description |
|--------|-----------|-------------|
| Telethon Binary | `.session` | SQLite database format |
| Pyrogram JSON | `.json` | JSON with auth_key |
| String Session | `.txt` | Base64 encoded string |
| TData Archive | `.zip` | Telegram Desktop data |

Features:
- 5-step validation process
- Device fingerprint collection
- Import/validation report generation

---

## Advanced Parsing & Monitoring

### Advanced Parser
**File:** `core/advanced_parser.py`

Deep chat analysis with threat detection:

| Feature | Description |
|---------|-------------|
| Pattern Detection | Coordinates, crypto, phones, weapons, military terms |
| Threat Scoring | 0-100 risk score with configurable thresholds |
| User Risk Scoring | Key person identification and influence analysis |
| Interaction Graph | Network relationship mapping |
| Formatted Reports | Ukrainian-language threat analysis reports |

Detected patterns:
- **Coordinates**: Decimal (50.4501, 30.5234), DMS (50°27'00"N), MGRS
- **Phones**: UA (+380), RU (+7), BY (+375), PL (+48)
- **Crypto**: BTC, ETH, USDT (TRC-20/ERC-20)
- **Threat Keywords**: Explosives, weapons, military terminology

### RealTime Parser
**File:** `core/realtime_parser.py`

Real-time chat monitoring system:

| Setting | Default | Description |
|---------|---------|-------------|
| `check_interval` | 30s | Message check frequency |
| `threat_threshold` | 30 | Alert trigger threshold |
| `batch_size` | 100 | Messages per check |

Features:
- Threat level threshold alerts
- Message deduplication via hash cache
- Alert callbacks for notifications
- Dynamic settings (interval, threshold, batch size)
- Status reporting and control (start/stop)

### Telethon Integration
**File:** `core/osint_telethon.py`

Connects parsers to Telethon for real-time monitoring when API credentials available.

---

## Forensics & Analysis Suite

### Forensic Snapshot
**File:** `core/forensic_snapshot.py`

| Feature | Description |
|---------|-------------|
| Media Capture | Original metadata preservation |
| Hashing | SHA-256 and SHA-512 forensic hashing |
| File Analysis | Signature analysis and entropy calculation |
| Cache Recovery | Recover deleted media from local cache |
| Integrity Check | Tamper detection with verification |

### AI Sentiment Analyzer
**File:** `core/ai_sentiment.py`

OpenAI-powered analysis:

| Analysis Type | Output |
|---------------|--------|
| Sentiment | Positive/Negative/Neutral/Mixed |
| Toxicity | Probability score (0-100) |
| Spam | Spam probability score |
| Emotions | Joy, anger, sadness, fear, surprise |
| Intent | Question, statement, request, complaint |

Features:
- Keyword-based fallback when AI unavailable
- Configurable thresholds

### Anti-Ghost Recovery
**File:** `core/anti_ghost_recovery.py`

Recovery of deleted content:

| Feature | Description |
|---------|-------------|
| Message Capture | Automatic capture before deletion |
| Edit History | Tracking with timestamps |
| Search | Across captured content |
| Media Recovery | Reference to deleted text and media |
| Statistics | By chat and user |

### X-Ray Metadata
**File:** `core/xray_metadata.py`

Deep file analysis:

| Feature | Description |
|---------|-------------|
| Signature Detection | File type identification |
| EXIF Extraction | Camera, GPS, timestamps |
| Hidden Data | Embedded URLs, emails, strings |
| Anomaly Detection | High entropy, multi-signature, suspicious patterns |
| Risk Score | 0-100 risk assessment |

### Memory Indexer
**File:** `core/memory_indexer.py`

In-memory full-text search:

| Feature | Description |
|---------|-------------|
| Indexing | Inverted index with tokenization |
| Stop Words | Ukrainian and Russian filters |
| Multi-Type | Messages, users, media, channels |
| Scoring | Relevance with recency boost |
| Performance | Fast search with configurable limits |

### Enhanced Monitoring
**File:** `core/enhanced_monitoring.py`

Target-based monitoring:

| Feature | Description |
|---------|-------------|
| Targets | Channels, chats, users |
| Triggers | Keyword and regex patterns |
| Spam Detection | Pattern recognition |
| Alerts | Severity levels (low, medium, high) |
| Tracking | Event statistics and history |

---

## Structured Logging & Monitoring

### Structured Logger
**File:** `core/structured_logging.py`

Categorized logging with metrics and context:

| Category | Description |
|----------|-------------|
| `SECURITY` | Authentication, authorization events |
| `CAMPAIGN` | Campaign creation, execution |
| `DM` | Direct message operations |
| `PARSER` | Group parsing events |
| `FLOOD` | Telegram flood events |
| `SYSTEM` | System-level events |

Features:
- Contextual metadata (user_id, session_id, task_id, duration_ms)
- Automatic metrics tracking (total_logs, errors, warnings, flood_events)
- JSON export for analysis
- In-memory log storage with configurable limits

### Flood Monitor
**File:** `core/flood_monitor.py`

Real-time flood event monitoring:

| Severity | Threshold | Description |
|----------|-----------|-------------|
| `LOW` | < 3 floods | Minor flood events |
| `MEDIUM` | 3+ floods/session | Needs attention |
| `HIGH` | 300s+ wait | Significant delay |
| `CRITICAL` | 5+ floods/session | Immediate action required |

Configurable thresholds:
```python
{
    "floods_per_session_warn": 3,
    "floods_per_session_critical": 5,
    "floods_per_task_warn": 5,
    "floods_per_task_critical": 10,
    "wait_seconds_warn": 300,
    "wait_seconds_critical": 600,
    "window_minutes": 60
}
```

Features:
- Session/task flood tracking
- Automatic alert generation
- Pause recommendations
- Ukrainian-language reports
- Alert acknowledgement system

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

---

## Campaign Management

### Campaign Types

| Type | Description |
|------|-------------|
| **Broadcast** | One-time message to all users |
| **Targeted** | Segmented users based on criteria |
| **Drip** | Sequential messages over time |
| **Sequential** | Dependent on user actions |
| **A/B Testing** | Variant comparison with metrics |

### Scheduling System

Scheduling presets:
- **Interval**: 60 minutes, 240 minutes
- **Daily**: 1440 minutes (24 hours)
- **Weekly**: 10080 minutes (7 days)
- **Custom**: User-defined intervals

### Message Queue

| Parameter | Value |
|-----------|-------|
| Workers | 3 async workers |
| Queue Type | asyncio.Queue |
| Retry Logic | 3 retries with exponential backoff |
| Priority | Supports priority queuing |

---

## Funnel System

### Comprehensive Funnel Management

| Feature | Description |
|---------|-------------|
| **Full CRUD** | Create, read, update, delete funnels |
| **Template Integration** | Link with mailing templates |
| **Scheduling** | Time-based funnel automation |
| **OSINT Analysis** | Integrated threat assessment |
| **Monitoring** | Real-time performance tracking |
| **Trigger Transitions** | Conditional funnel state changes |

---

## AI Integration

### OpenAI Integration

**Replit AI Integration:** Seamless connection to OpenAI-compatible models (GPT-5 via Replit AI Integrations)

**API Keys (Configured):**
- `TELEGRAM_API_ID`: 20799080
- `TELEGRAM_API_HASH`: d6b90fc1e1d4fc023d5bab647069473b
- AI keys: Auto-configured via Replit AI Integrations

Features:
- AI Pattern Detection
- Sentiment Analysis
- Behavior Profiling
- Enhanced Report Generation
- Keyword Analysis
- Spam Detection

### Advanced Tools

#### 1. AI Pattern Detection
**File:** `core/ai_pattern_detection.py`

| Detection Type | Patterns |
|----------------|----------|
| **Coordinates** | Decimal, DMS, MGRS, Google Maps links |
| **Phones** | UA, RU, BY, PL formats |
| **Crypto** | BTC, ETH, USDT, LTC, XMR |
| **Threats** | 4 levels: Critical, High, Medium, Low |
| **Encoded Data** | Base64, Hex patterns |

Risk scoring: 0-100 with configurable thresholds.

#### 2. Spam Analyzer
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

#### 3. Drip Campaign Manager
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

#### 4. Behavior Profiler
**File:** `core/behavior_profiler.py`

User activity analysis:

| Analysis Type | Output |
|---------------|--------|
| Daily Rhythm | Morning/Afternoon/Evening/Night distribution |
| Sleep Schedule | Estimated sleep hours |
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

#### 5. Keyword Analyzer
**File:** `core/keyword_analyzer.py`

Text analysis capabilities:

| Feature | Description |
|---------|-------------|
| Word Frequency | Top N most common words |
| Sentiment | Positive/Negative/Neutral classification |
| Language Detection | Ukrainian, Russian, English |
| Readability Score | Flesch-Kincaid adapted for Cyrillic |
| Trending Words | Statistical outlier detection |

#### 6. Enhanced Report Generator
**File:** `core/enhanced_reports.py`

Professional PDF report generation:

| Report Type | Contents |
|-------------|----------|
| **OSINT Report** | Findings, threats, evidence, network graph |
| **Campaign Report** | Delivery stats, conversions, A/B results |
| **User Profile** | Behavior analysis, activity history, predictions |
| **Analytics Report** | Project overview, team metrics, trends |

Requires: ReportLab library

---

## Testing

### Unit Test Suite
**Directory:** `tests/`

The project includes a comprehensive test suite using pytest and pytest-asyncio:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=core
```

### Test Coverage

| Test File | Module | Tests |
|-----------|--------|-------|
| `test_dm_sender.py` | DMSenderService | 14 tests |
| `test_group_parser.py` | GroupParserService | 9 tests |
| `test_bot_session.py` | BotSession model | 12 tests |

### Test Categories

**DMSenderService Tests:**
- Service initialization
- Task creation with blacklist/cooldown filtering
- Task stop/start operations
- Flood protection (24h cooldown)
- Statistics tracking

**GroupParserService Tests:**
- User list storage
- ParsedUser dataclass
- ParseJob creation
- Filter enum values

**BotSession Tests:**
- Availability checks (status, flood wait, success rate)
- Statistics update
- Status constants

---

## Technology Stack

### Core Framework
- **aiogram 3.3+** - Telegram Bot API framework
- **asyncpg** - Asynchronous PostgreSQL driver
- **SQLAlchemy** - Object-Relational Mapper (ORM)

### Advanced Libraries
- **Telethon** - Telegram client library for OSINT
- **OpenAI API** - AI/GPT integration (via Replit AI)
- **ReportLab** - PDF report generation
- **Jinja2** - Template engine
- **cryptography** - AES-256-CBC encryption
- **dnspython** - DNS resolution
- **python-dotenv** - Environment configuration

### Python Version
- **Python 3.11+**

### Security
- AES-256-CBC encryption
- HKDF key derivation
- Argon2id password hashing
- Rate limiting (token bucket)
- Audit logging

---

## UI/UX Standards

- **Language:** Ukrainian throughout the interface
- **Dividers:** Exactly 15 single-line chars `───────────────` (mobile-optimized)
- **Progress bars:** Native style `●●●●○○○○ 50%`
- **Button layouts:** 1/2/3 per row, standardized
- **Rich formatting:** Bold, italic, code blocks in HTML
- **Tree structures:** List-like format with `├ └` characters
- **Design:** Clean minimal design, no frames/borders

---

## Deployment

**Type:** Reserved VM (Background Worker)
**Entry Point:** `python bot.py`
**Environment:** NixOS with Python 3.11+

---

## License

SHADOW LICENSE - Proprietary Ukrainian Software

---

**Last Updated:** December 31, 2025  
**Version:** 2.0.2
