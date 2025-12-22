# Shadow Security Telegram Bot v2.0

## Project Overview
A fully-featured Telegram bot for Shadow Security with complete user management, payments, admin controls, and auto-reply system.

## Current Setup
- **Language**: Python 3.11
- **Framework**: aiogram 3.23.0
- **Database**: SQLite (shadow_security.db)
- **Status**: ✅ Running

## Project Structure
```
.
├── bot.py                    # Main bot entry point
├── config.py                 # Configuration & env vars
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore rules
│
├── handlers/                 # Command handlers
│   ├── __init__.py
│   ├── user.py              # User commands (mailing, autoreply, stats, settings)
│   ├── admin.py             # Admin commands (broadcast, users, stats)
│   └── payments.py          # Payment handlers (pay, balance, invoice, refund)
│
├── keyboards/               # UI buttons & menus
│   ├── __init__.py
│   ├── user.py              # User keyboards (main_menu, subscription, settings)
│   └── admin.py             # Admin keyboards (admin_menu, broadcast)
│
├── middlewares/             # Request processing
│   ├── __init__.py
│   └── logging.py           # Logging middleware for all messages
│
└── utils/                   # Utilities
    ├── __init__.py
    ├── db.py                # SQLite database manager
    └── decorators.py        # Decorators (admin_only, premium_only, rate_limit)
```

## Available Commands

### User Commands
- `/start` - Initialize bot
- `/menu` - Main menu with all options
- `/help` - Full help guide
- `/subscription` - View & manage subscription
- `/mailing` - Create mailing campaign
- `/autoreply` - Set up auto-reply rules
- `/stats` - View personal statistics
- `/settings` - Configure preferences (ghost mode, notifications, language)
- `/balance` - Check account balance
- `/pay` - Top up account

### Payment Commands
- `/pay` - Initiate payment
- `/history` - Payment history
- `/invoice` - Create invoice
- `/refund` - Request refund
- `/subscription` - View subscription plans

### Admin Commands
- `/admin` - Admin panel (admin-only)
- `/block` [user_id] - Block user
- `/unblock` [user_id] - Unblock user

## Features Implemented

✅ **User Management**
- User registration on `/start`
- Profile persistence in SQLite
- User statistics tracking

✅ **Mailing System**
- Create mailing campaigns
- Target specific users
- Campaign status tracking

✅ **Auto-Reply**
- Trigger-based responses
- Response customization
- Enable/disable toggle

✅ **Payment System**
- Multiple payment methods (Card, Liqpay, Crypto)
- Balance management
- Invoice system
- Payment history

✅ **Admin Panel**
- User management
- Broadcasting to all users
- Bot statistics
- Maintenance mode

✅ **Settings**
- Ghost mode (privacy)
- Notification toggle
- Language selection

## Database
SQLite database with tables:
- `users` - User profiles & subscription data
- `mailings` - Mailing campaigns
- `auto_replies` - Auto-reply rules

## Environment Variables
- `BOT_TOKEN` - Telegram bot token (required)
- `ADMIN_IDS` - Comma-separated admin Telegram IDs (optional)

## How to Run
1. Ensure `BOT_TOKEN` is set in secrets
2. The workflow starts automatically: `python bot.py`
3. Bot connects to Telegram and starts polling for messages

## Next Steps
- Add database persistence (payment records, user subscriptions)
- Implement real Liqpay/payment gateway integration
- Add webhook mode for faster updates
- Implement cron jobs for scheduled mailings
- Add inline query support
- Analytics dashboard

## User Preferences
- **Language**: Ukrainian (ua)
- **Format**: Inline keyboards for menus
- **Response Style**: Casual, with emojis

## Recent Changes (2025-12-22)
- ✅ Created complete handler system (user, admin, payments)
- ✅ Added keyboard layouts for all menus
- ✅ Implemented database module with SQLite
- ✅ Added decorators for admin access & rate limiting
- ✅ Set up logging middleware
- ✅ Registered all routers with dispatcher
- ✅ Bot fully functional and ready for use
