import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_session
from database.repositories.user_repository import UserRepository
from database.repositories.campaign_repository import CampaignRepository
from database.repositories.payment_repository import PaymentRepository
from database.repositories.bot_session_repository import BotSessionRepository

logger = logging.getLogger(__name__)

app = FastAPI(title="Shadow System V2.0 API", version="2.0.0")


# ============ USERS ROUTES ============

@app.get("/api/users/{telegram_id}")
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Get user profile"""
    try:
        repo = UserRepository(session)
        user = await repo.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "role": user.role.value,
            "plan": user.plan.value if user.plan else "free",
            "statistics": user.statistics
        }
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/stats/{telegram_id}")
async def get_user_stats(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Get user statistics"""
    try:
        repo = UserRepository(session)
        user = await repo.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "telegram_id": user.telegram_id,
            "statistics": user.statistics,
            "settings": user.settings
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CAMPAIGNS ROUTES ============

@app.get("/api/campaigns/{user_id}")
async def get_user_campaigns(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user campaigns"""
    try:
        repo = CampaignRepository(session)
        campaigns = await repo.get_user_campaigns(user_id)
        return {
            "count": len(campaigns),
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status.value,
                    "sent_count": c.sent_count,
                    "success_count": c.success_count,
                    "total_targets": c.total_targets,
                    "created_at": c.created_at.isoformat()
                }
                for c in campaigns
            ]
        }
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns/running")
async def get_running_campaigns(session: AsyncSession = Depends(get_session)):
    """Get all running campaigns"""
    try:
        repo = CampaignRepository(session)
        campaigns = await repo.get_running_campaigns()
        return {
            "count": len(campaigns),
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "progress": (c.sent_count / c.total_targets * 100) if c.total_targets > 0 else 0,
                    "sent_count": c.sent_count,
                    "total_targets": c.total_targets
                }
                for c in campaigns
            ]
        }
    except Exception as e:
        logger.error(f"Error getting running campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ PAYMENTS ROUTES ============

@app.get("/api/payments/{user_id}")
async def get_user_payments(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user payments"""
    try:
        repo = PaymentRepository(session)
        payments = await repo.get_user_payments(user_id, limit=50)
        return {
            "count": len(payments),
            "payments": [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                }
                for p in payments
            ]
        }
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/payments/revenue")
async def get_total_revenue(session: AsyncSession = Depends(get_session)):
    """Get total revenue"""
    try:
        repo = PaymentRepository(session)
        revenue = await repo.get_total_revenue()
        return {"total_revenue": revenue}
    except Exception as e:
        logger.error(f"Error calculating revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ BOTS ROUTES ============

@app.get("/api/bots/{user_id}")
async def get_user_bots(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user bots"""
    try:
        repo = BotSessionRepository(session)
        bots = await repo.get_active_bots_for_user(user_id)
        return {
            "count": len(bots),
            "bots": [
                {
                    "id": b.id,
                    "phone": b.phone,
                    "status": b.status.value,
                    "messages_sent": b.messages_sent,
                    "success_rate": b.success_rate
                }
                for b in bots
            ]
        }
    except Exception as e:
        logger.error(f"Error getting bots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        from core.system_stats import system_stats
        from core.health_dashboard import health_dashboard
        stats = system_stats.get_all_stats()
        await health_dashboard.check_all()
        health_summary = health_dashboard.get_summary()
        return {
            "status": health_summary["overall"],
            "service": "Shadow System V2.0",
            "version": "2.0.0",
            "uptime": stats["uptime"]["formatted"],
            "cpu_percent": stats["cpu"]["usage_percent"],
            "memory_percent": stats["memory"]["percent"],
            "services": health_summary["services"]
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "ok", "service": "Shadow System V2.0", "version": "2.0.0"}


@app.get("/api/system/stats")
async def get_system_stats():
    """Get detailed system statistics"""
    try:
        from core.system_stats import system_stats
        return system_stats.get_all_stats()
    except Exception as e:
        logger.error(f"System stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/cache")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        from core.cache_service import cache_service
        return cache_service.get_stats()
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/cache/clear")
async def clear_cache():
    """Clear all cache"""
    try:
        from core.cache_service import cache_service
        cleared = await cache_service.clear()
        return {"cleared": cleared, "message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/osint/dns/{domain}")
async def osint_dns_lookup(domain: str):
    """Perform DNS lookup"""
    try:
        from core.osint_service import osint_service
        result = await osint_service.dns_lookup(domain)
        return result
    except Exception as e:
        logger.error(f"DNS lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/osint/whois/{domain}")
async def osint_whois_lookup(domain: str):
    """Perform WHOIS lookup"""
    try:
        from core.osint_service import osint_service
        result = await osint_service.whois_lookup(domain)
        return result
    except Exception as e:
        logger.error(f"WHOIS lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/osint/geoip/{ip}")
async def osint_geoip_lookup(ip: str):
    """Perform GeoIP lookup"""
    try:
        from core.osint_service import osint_service
        result = await osint_service.ip_geolocation(ip)
        return result
    except Exception as e:
        logger.error(f"GeoIP lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/sentiment")
async def ai_sentiment_analysis(text: str):
    """Analyze text sentiment using AI"""
    try:
        from core.ai_service import ai_service
        result = await ai_service.analyze_sentiment(text)
        return result
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/generate")
async def ai_generate_text(topic: str, style: str = "professional"):
    """Generate marketing text using AI"""
    try:
        from core.ai_service import ai_service
        result = await ai_service.generate_campaign_text(topic, style)
        return {"topic": topic, "style": style, "generated_text": result}
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
