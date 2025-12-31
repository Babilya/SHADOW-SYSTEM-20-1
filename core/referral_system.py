import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReferralTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class ReferralBonus:
    level: int
    percentage: float
    description: str


@dataclass
class ReferralUser:
    user_id: int
    referrer_id: Optional[int]
    referral_code: str
    tier: ReferralTier
    joined_at: datetime
    total_referrals: int = 0
    active_referrals: int = 0
    total_earnings: float = 0.0
    pending_earnings: float = 0.0
    withdrawn_earnings: float = 0.0
    bonus_days_earned: int = 0
    chain: List[int] = field(default_factory=list)


class MultiTierReferralSystem:
    TIER_THRESHOLDS = {
        ReferralTier.BRONZE: 0,
        ReferralTier.SILVER: 5,
        ReferralTier.GOLD: 15,
        ReferralTier.PLATINUM: 50,
        ReferralTier.DIAMOND: 100
    }
    
    TIER_BONUSES = {
        ReferralTier.BRONZE: {1: 10, 2: 5, 3: 2},
        ReferralTier.SILVER: {1: 12, 2: 6, 3: 3},
        ReferralTier.GOLD: {1: 15, 2: 8, 3: 4},
        ReferralTier.PLATINUM: {1: 18, 2: 10, 3: 5},
        ReferralTier.DIAMOND: {1: 20, 2: 12, 3: 6}
    }
    
    TIER_BONUS_DAYS = {
        ReferralTier.BRONZE: 3,
        ReferralTier.SILVER: 5,
        ReferralTier.GOLD: 7,
        ReferralTier.PLATINUM: 10,
        ReferralTier.DIAMOND: 14
    }
    
    ACHIEVEMENT_BONUSES = {
        1: {"days": 3, "description": "Перший реферал"},
        5: {"days": 7, "description": "5 рефералів"},
        10: {"days": 15, "description": "10 рефералів"},
        25: {"days": 30, "description": "25 рефералів"},
        50: {"days": 60, "description": "50 рефералів"},
        100: {"days": 120, "description": "100 рефералів"}
    }
    
    MIN_WITHDRAWAL = 100.0
    
    def __init__(self):
        self.users: Dict[int, ReferralUser] = {}
        self.codes: Dict[str, int] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.stats = {
            "total_users": 0,
            "total_referrals": 0,
            "total_paid": 0.0,
            "total_pending": 0.0
        }
    
    def generate_code(self, user_id: int) -> str:
        data = f"{user_id}_{datetime.now().timestamp()}_shadow"
        return hashlib.sha256(data.encode()).hexdigest()[:8].upper()
    
    def register_user(self, user_id: int, referrer_code: Optional[str] = None) -> ReferralUser:
        if user_id in self.users:
            return self.users[user_id]
        
        referrer_id = None
        chain = []
        
        if referrer_code and referrer_code in self.codes:
            referrer_id = self.codes[referrer_code]
            if referrer_id != user_id:
                referrer = self.users.get(referrer_id)
                if referrer:
                    chain = referrer.chain[-2:] + [referrer_id]
        
        code = self.generate_code(user_id)
        
        user = ReferralUser(
            user_id=user_id,
            referrer_id=referrer_id,
            referral_code=code,
            tier=ReferralTier.BRONZE,
            joined_at=datetime.now(),
            chain=chain
        )
        
        self.users[user_id] = user
        self.codes[code] = user_id
        self.stats["total_users"] += 1
        
        if referrer_id:
            self._process_new_referral(referrer_id, user_id)
        
        logger.info(f"Registered referral user {user_id} with code {code}")
        return user
    
    def _process_new_referral(self, referrer_id: int, new_user_id: int):
        referrer = self.users.get(referrer_id)
        if not referrer:
            return
        
        referrer.total_referrals += 1
        self.stats["total_referrals"] += 1
        
        self._update_tier(referrer)
        self._check_achievements(referrer)
        
        logger.info(f"Processed referral: {new_user_id} -> {referrer_id}")
    
    def _update_tier(self, user: ReferralUser):
        for tier in reversed(list(ReferralTier)):
            if user.total_referrals >= self.TIER_THRESHOLDS[tier]:
                if user.tier != tier:
                    old_tier = user.tier
                    user.tier = tier
                    logger.info(f"User {user.user_id} upgraded from {old_tier} to {tier}")
                break
    
    def _check_achievements(self, user: ReferralUser):
        for threshold, bonus in self.ACHIEVEMENT_BONUSES.items():
            if user.total_referrals == threshold:
                user.bonus_days_earned += bonus["days"]
                logger.info(f"User {user.user_id} earned achievement: {bonus['description']} (+{bonus['days']} days)")
    
    def process_payment(self, user_id: int, amount: float, is_first_payment: bool = False) -> Dict[str, Any]:
        user = self.users.get(user_id)
        if not user or not user.referrer_id:
            return {"distributed": 0, "levels": []}
        
        distributed = []
        chain = [user.referrer_id] + (user.chain if user.chain else [])
        
        for level, referrer_id in enumerate(chain[:3], 1):
            referrer = self.users.get(referrer_id)
            if not referrer:
                continue
            
            tier_bonuses = self.TIER_BONUSES.get(referrer.tier, self.TIER_BONUSES[ReferralTier.BRONZE])
            percentage = tier_bonuses.get(level, 0)
            
            if is_first_payment and level == 1:
                percentage = min(percentage + 5, 25)
            
            bonus = amount * (percentage / 100)
            referrer.pending_earnings += bonus
            referrer.total_earnings += bonus
            self.stats["total_pending"] += bonus
            
            distributed.append({
                "user_id": referrer_id,
                "level": level,
                "percentage": percentage,
                "amount": bonus,
                "tier": referrer.tier.value
            })
            
            self.transactions.append({
                "type": "referral_bonus",
                "from_user": user_id,
                "to_user": referrer_id,
                "level": level,
                "amount": bonus,
                "original_payment": amount,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "distributed": sum(d["amount"] for d in distributed),
            "levels": distributed
        }
    
    def request_withdrawal(self, user_id: int, amount: Optional[float] = None) -> Dict[str, Any]:
        user = self.users.get(user_id)
        if not user:
            return {"error": "Користувача не знайдено"}
        
        available = user.pending_earnings
        
        if available < self.MIN_WITHDRAWAL:
            return {"error": f"Мінімальна сума для виводу: {self.MIN_WITHDRAWAL} ₴"}
        
        withdraw_amount = min(amount or available, available)
        
        user.pending_earnings -= withdraw_amount
        user.withdrawn_earnings += withdraw_amount
        self.stats["total_pending"] -= withdraw_amount
        self.stats["total_paid"] += withdraw_amount
        
        self.transactions.append({
            "type": "withdrawal",
            "user_id": user_id,
            "amount": withdraw_amount,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "amount": withdraw_amount,
            "remaining": user.pending_earnings
        }
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        user = self.users.get(user_id)
        if not user:
            return {"error": "Користувача не знайдено"}
        
        tier_progress = 0
        next_tier = None
        for tier in ReferralTier:
            threshold = self.TIER_THRESHOLDS[tier]
            if user.total_referrals < threshold:
                next_tier = tier
                prev_threshold = self.TIER_THRESHOLDS[list(ReferralTier)[list(ReferralTier).index(tier) - 1]] if list(ReferralTier).index(tier) > 0 else 0
                tier_progress = int((user.total_referrals - prev_threshold) / (threshold - prev_threshold) * 100)
                break
        
        return {
            "user_id": user_id,
            "referral_code": user.referral_code,
            "tier": user.tier.value,
            "tier_name": self._get_tier_name(user.tier),
            "next_tier": next_tier.value if next_tier else None,
            "tier_progress": tier_progress,
            "total_referrals": user.total_referrals,
            "active_referrals": user.active_referrals,
            "total_earnings": user.total_earnings,
            "pending_earnings": user.pending_earnings,
            "withdrawn_earnings": user.withdrawn_earnings,
            "bonus_days_earned": user.bonus_days_earned,
            "bonuses": self.TIER_BONUSES[user.tier],
            "bonus_days_per_referral": self.TIER_BONUS_DAYS[user.tier]
        }
    
    def _get_tier_name(self, tier: ReferralTier) -> str:
        names = {
            ReferralTier.BRONZE: "🥉 Бронза",
            ReferralTier.SILVER: "🥈 Срібло",
            ReferralTier.GOLD: "🥇 Золото",
            ReferralTier.PLATINUM: "💎 Платина",
            ReferralTier.DIAMOND: "👑 Діамант"
        }
        return names.get(tier, "Бронза")
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        sorted_users = sorted(
            self.users.values(),
            key=lambda u: (u.total_referrals, u.total_earnings),
            reverse=True
        )[:limit]
        
        return [
            {
                "rank": i + 1,
                "user_id": u.user_id,
                "tier": self._get_tier_name(u.tier),
                "referrals": u.total_referrals,
                "earnings": u.total_earnings
            }
            for i, u in enumerate(sorted_users)
        ]
    
    def get_referral_tree(self, user_id: int, depth: int = 3) -> Dict[str, Any]:
        user = self.users.get(user_id)
        if not user:
            return {"error": "Користувача не знайдено"}
        
        def build_tree(uid: int, current_depth: int) -> Dict:
            if current_depth > depth:
                return {}
            
            children = [
                u for u in self.users.values()
                if u.referrer_id == uid
            ]
            
            return {
                "user_id": uid,
                "tier": self.users[uid].tier.value if uid in self.users else "unknown",
                "referrals": [
                    build_tree(c.user_id, current_depth + 1)
                    for c in children[:10]
                ]
            }
        
        return build_tree(user_id, 1)
    
    def format_stats_message(self, user_id: int) -> str:
        stats = self.get_user_stats(user_id)
        if "error" in stats:
            return stats["error"]
        
        bonuses = stats["bonuses"]
        
        return f"""📊 <b>РЕФЕРАЛЬНА СТАТИСТИКА</b>

<b>Ваш рівень:</b> {stats['tier_name']}
<b>Код:</b> <code>{stats['referral_code']}</code>

───────────────

<b>📈 Показники:</b>
├ Всього рефералів: {stats['total_referrals']}
├ Активних: {stats['active_referrals']}
├ Прогрес до {stats['next_tier'] or 'MAX'}: {stats['tier_progress']}%
└ Бонусних днів: +{stats['bonus_days_earned']}

<b>💰 Заробіток:</b>
├ Всього: {stats['total_earnings']:.2f} ₴
├ Доступно: {stats['pending_earnings']:.2f} ₴
└ Виведено: {stats['withdrawn_earnings']:.2f} ₴

<b>🎁 Ваші бонуси ({stats['tier_name']}):</b>
├ Рівень 1: {bonuses.get(1, 0)}% від оплат
├ Рівень 2: {bonuses.get(2, 0)}% від оплат
└ Рівень 3: {bonuses.get(3, 0)}% від оплат

<b>📅 Бонус днів:</b> +{stats['bonus_days_per_referral']} днів/реферал"""


referral_system = MultiTierReferralSystem()
