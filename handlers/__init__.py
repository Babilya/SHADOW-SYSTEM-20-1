"""
Handlers module - Organized by functionality

Structure:
├─ admin/           - Admin panel handlers
├─ core/            - Core handlers (auth, start, help, user, security)
├─ features/        - Feature handlers (campaigns, botnet, osint, mailing, etc.)
├─ moderation/      - Moderation handlers (bans, notifications, support)
└─ integrations/    - Integration handlers (templates, scheduler, export, geo)
"""
from aiogram import Router

main_router = Router()

try:
    from handlers.core import start_router, user_router, help_router, security_router, auth_router
    main_router.include_router(start_router)
    main_router.include_router(user_router)
    main_router.include_router(help_router)
    main_router.include_router(security_router)
    main_router.include_router(auth_router)
except ImportError as e:
    print(f"Warning: Could not import core handlers: {e}")

try:
    from handlers.features import (
        botnet_router, funnels_router, analytics_router, warming_router,
        mailing_router, osint_router, subscriptions_router, team_router,
        advanced_router, tools_router, forensics_router, bots_router,
        campaigns_router, osint_handler_router, proxy_router, referral_router,
        profile_router
    )
    main_router.include_router(botnet_router)
    main_router.include_router(funnels_router)
    main_router.include_router(analytics_router)
    main_router.include_router(warming_router)
    main_router.include_router(mailing_router)
    main_router.include_router(osint_router)
    main_router.include_router(subscriptions_router)
    main_router.include_router(team_router)
    main_router.include_router(advanced_router)
    main_router.include_router(tools_router)
    main_router.include_router(forensics_router)
    main_router.include_router(bots_router)
    main_router.include_router(campaigns_router)
    main_router.include_router(osint_handler_router)
    main_router.include_router(proxy_router)
    main_router.include_router(referral_router)
    main_router.include_router(profile_router)
except ImportError as e:
    print(f"Warning: Could not import feature handlers: {e}")

try:
    from handlers.moderation import (
        notifications_router, support_router, tickets_router, 
        admin_notifications_router, users_router
    )
    main_router.include_router(notifications_router)
    main_router.include_router(support_router)
    main_router.include_router(tickets_router)
    main_router.include_router(admin_notifications_router)
    main_router.include_router(users_router)
except ImportError as e:
    print(f"Warning: Could not import moderation handlers: {e}")

try:
    from handlers.integrations import (
        templates_router, scheduler_router, export_router, geo_router,
        texting_router, configurator_router
    )
    main_router.include_router(templates_router)
    main_router.include_router(scheduler_router)
    main_router.include_router(export_router)
    main_router.include_router(geo_router)
    main_router.include_router(texting_router)
    main_router.include_router(configurator_router)
except ImportError as e:
    print(f"Warning: Could not import integration handlers: {e}")

try:
    from handlers.admin import admin_router
    main_router.include_router(admin_router)
except ImportError as e:
    print(f"Warning: Could not import admin handlers: {e}")

try:
    from handlers.applications import applications_router
    main_router.include_router(applications_router)
except ImportError as e:
    pass

try:
    from handlers.guest_flow import router as guest_router
    main_router.include_router(guest_router)
except ImportError as e:
    pass

try:
    from handlers.missing_handlers import missing_router
    main_router.include_router(missing_router)
except ImportError as e:
    pass

__all__ = ["main_router"]
