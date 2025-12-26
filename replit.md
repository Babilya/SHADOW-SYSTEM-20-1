# Shadow System v2.0

## Overview
Shadow System is a professional platform designed for automating Telegram marketing. It provides comprehensive functionality for managing botnets, mass mailings, OSINT (Open-Source Intelligence) reconnaissance, and team collaboration. Its purpose is to control over 1000 Telegram bots simultaneously, offer a CRM system for teams, provide advanced OSINT tools, implement a robust tariff and authorization system, and ensure complete isolation of user projects.

## User Preferences
The user prefers a concise and streamlined approach to project information. They prioritize clear, high-level summaries over granular implementation details. The user prefers that all changelogs and date-wise entries be removed to avoid context pollution. When interacting with the codebase, the user wants the agent to focus on core architectural decisions and consolidate redundant information. The user expects the agent to remove all update logs.

## System Architecture
The system is built around a modular architecture with distinct components for configuration, database interactions, Telegram handlers, core functionalities, middlewares, and services.

### Core Architectural Decisions:
- **Role-Based Access Control (RBAC):** A sophisticated role system (ROOT/ADMIN, LEADER, MANAGER, GUEST) dictates access and functionalities, ensuring secure and segmented operations.
- **Project Isolation:** Each leader's project is isolated, managing its own bots, managers, and campaigns, ensuring data integrity and security.
- **State Management:** Utilizes FSM (Finite State Machine) for managing user interactions, particularly for registration, application processing, and manager authorization.
- **Asynchronous Operations:** Built with `aiogram 3.3` and `asyncpg` for efficient, non-blocking operations, crucial for managing a large number of Telegram bots.
- **Security-First Design:** Features unique access keys, Telegram ID binding, project isolation, comprehensive audit logging, rate limiting, and an Emergency Router for critical system control.
- **Dynamic Configuration:** A CMS Configurator allows dynamic modification of UI elements, welcome texts, and banners via an admin panel.

### UI/UX Decisions:
- **Intuitive Telegram Bot Interface:** All interactions are handled within Telegram, leveraging keyboards and menus for navigation.
- **Role-Specific Menus:** Different menus are presented based on the user's role to provide a tailored experience and prevent unauthorized access.

### Feature Specifications:
- **Botnet Management:** Control and operation of numerous Telegram bots for various marketing activities.
- **Campaign Management:** Creation and execution of different types of mailing campaigns (broadcast, targeted, drip, sequential) with status tracking and statistics.
- **OSINT Tools:** Integrated modules for Telegram analysis, DNS/WHOIS lookups, image metadata analysis, and social media reconnaissance, with an aggregator for comprehensive reports.
- **CRM for Teams:** Features for managing managers, generating invite codes, and tracking team activities.
- **Tariffing and Authorization:** A multi-tiered tariff system with unique SHADOW keys for leaders and INV codes for managers, managed through an admin panel.
- **Alerting System:** Critical, operational, financial, and emergency alerts to notify the team of important events.
- **Audit Logging:** Detailed logging of all user actions with categorization and severity levels for accountability and security.
- **Session Management:** Secure import, encryption, and binding of Telegram sessions to specific projects.
- **Evidence Export:** Tools to export OSINT findings into structured JSON and HTML reports.
- **Security Center:** A dedicated module for user blocking, FSM state resets, and security monitoring.
- **Referral System:** Mechanism for generating unique referral links, tracking referrals, and awarding bonuses.
- **Ticket System:** Allows unregistered users to create support tickets and communicate with administrators.
- **Bot Warming System:** 72-hour warming cycles with 3 phases for new bots.
- **Campaign Scheduler:** Schedule campaigns for future execution with time presets.
- **Geo Scanner:** Search for Telegram chats by city/coordinates with radius selection.

## Advanced Features (v2.0)
- **Rate Limiter:** Token bucket algorithm (30 req/sec global, 25 req/sec per bot, 1 req/sec per user)
- **Message Queue:** Async queue system with 3 workers for reliable message delivery
- **Mailing Scheduler:** Schedule mailings for future dates/times with database persistence
- **A/B Testing:** Support for split testing in campaigns
- **Anti-Fraud Service:** Behavioral analysis and automatic blocking of suspicious users
- **Login Tracker:** IP-based login tracking with geolocation
- **IP Whitelist:** Admin IP whitelisting for enhanced security
- **Encrypted Backups:** AES-256 Fernet encryption for backup data (falls back to basic mode if cryptography not available)
- **Auto-Responder:** Keyword-based automatic responses (exact/contains/regex matching)
- **Segmentation Service:** Automatic user tagging (new_user, active, inactive, power_user, paying, leader, manager)
- **CRM Export:** Export leads to Notion, Airtable, Google Sheets
- **PDF Export:** Generate analytics and audit log reports
- **Key Expiration Notifications:** Automatic alerts 3/7 days before key expiry
- **Pagination:** Utilities for handling large datasets in Telegram messages

## External Dependencies
- **Telegram Bot API:** Interacted with via `aiogram 3.3` for all bot functionalities.
- **PostgreSQL:** Used as the primary database for storing system data, managed through `SQLAlchemy` and `asyncpg`.
- **Telethon/Pyrogram:** Session formats supported for importing Telegram bot sessions.
- **Payment Gateways (Manual Confirmation):** The system supports manual confirmation of payments, implying integration with various payment methods (Telegram Stars, Liqpay, Card) without direct API automation for balance top-ups.
- **Replit AI Integrations:** OpenAI integration for AI-powered text generation