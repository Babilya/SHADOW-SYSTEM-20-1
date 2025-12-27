"""
Behavior Profiler - Аналіз поведінкових профілів
Виявлення патернів активності та аномалій
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UserActivity:
    timestamp: datetime
    action_type: str
    platform: str
    details: Optional[str] = None
    location: Optional[str] = None


class BehaviorProfiler:
    """Аналіз поведінкових профілів користувачів"""
    
    USER_TYPES = {
        'night_owl': 'Нічний користувач',
        'early_bird': 'Ранній користувач',
        'office_hours': 'Офісний графік',
        'irregular': 'Нерегулярна активність',
        'heavy_user': 'Активний користувач',
        'passive': 'Пасивний користувач'
    }
    
    def __init__(self):
        self.user_activities: Dict[int, List[UserActivity]] = defaultdict(list)
    
    def add_activity(
        self, 
        user_id: int, 
        action_type: str, 
        platform: str = 'telegram',
        details: str = None
    ):
        """Додавання активності користувача"""
        activity = UserActivity(
            timestamp=datetime.now(),
            action_type=action_type,
            platform=platform,
            details=details
        )
        self.user_activities[user_id].append(activity)
    
    def analyze_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Повний аналіз профілю користувача"""
        activities = self.user_activities.get(user_id, [])
        
        if not activities:
            return {
                'user_id': user_id,
                'status': 'insufficient_data',
                'message': 'Недостатньо даних для аналізу'
            }
        
        return {
            'user_id': user_id,
            'total_activities': len(activities),
            'first_seen': min(a.timestamp for a in activities).isoformat(),
            'last_seen': max(a.timestamp for a in activities).isoformat(),
            'patterns': {
                'daily_rhythm': self._analyze_daily_rhythm(activities),
                'sleep_schedule': self._estimate_sleep_schedule(activities),
                'peak_hours': self._find_peak_hours(activities),
                'activity_consistency': self._measure_consistency(activities),
                'platform_usage': self._analyze_platforms(activities)
            },
            'user_type': self._classify_user_type(activities),
            'anomalies': self._detect_anomalies(activities),
            'predictions': self._predict_activity(activities)
        }
    
    def _analyze_daily_rhythm(self, activities: List[UserActivity]) -> Dict:
        """Аналіз добового ритму"""
        hour_counts = Counter(a.timestamp.hour for a in activities)
        
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))
        
        total = morning + afternoon + evening + night
        if total == 0:
            return {'dominant_period': 'unknown'}
        
        periods = {
            'morning': morning / total,
            'afternoon': afternoon / total,
            'evening': evening / total,
            'night': night / total
        }
        
        dominant = max(periods, key=periods.get)
        
        return {
            'distribution': {k: round(v * 100, 1) for k, v in periods.items()},
            'dominant_period': dominant,
            'dominant_percentage': round(periods[dominant] * 100, 1)
        }
    
    def _estimate_sleep_schedule(self, activities: List[UserActivity]) -> Dict:
        """Оцінка графіку сну"""
        hour_counts = {h: 0 for h in range(24)}
        for a in activities:
            hour_counts[a.timestamp.hour] += 1
        
        min_activity_start = 0
        min_activity_count = float('inf')
        
        for start_hour in range(24):
            window_count = sum(hour_counts[(start_hour + i) % 24] for i in range(6))
            if window_count < min_activity_count:
                min_activity_count = window_count
                min_activity_start = start_hour
        
        sleep_start = min_activity_start
        sleep_end = (min_activity_start + 6) % 24
        
        total_activities = len(activities)
        if total_activities == 0:
            confidence = 0
        else:
            confidence = min(100, (total_activities / 50) * 100)
        
        return {
            'estimated_sleep_start': f"{sleep_start:02d}:00",
            'estimated_wake_time': f"{sleep_end:02d}:00",
            'confidence': round(confidence, 1)
        }
    
    def _find_peak_hours(self, activities: List[UserActivity]) -> List[int]:
        """Знаходження пікових годин активності"""
        hour_counts = Counter(a.timestamp.hour for a in activities)
        
        if not hour_counts:
            return []
        
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [h for h, c in sorted_hours[:3]]
        
        return peak_hours
    
    def _measure_consistency(self, activities: List[UserActivity]) -> Dict:
        """Вимірювання консистентності активності"""
        if len(activities) < 7:
            return {'status': 'insufficient_data'}
        
        day_counts = Counter(a.timestamp.date() for a in activities)
        
        if len(day_counts) < 2:
            return {'consistency_score': 100}
        
        counts = list(day_counts.values())
        avg = sum(counts) / len(counts)
        variance = sum((c - avg) ** 2 for c in counts) / len(counts)
        std_dev = variance ** 0.5
        
        cv = (std_dev / avg * 100) if avg > 0 else 0
        consistency = max(0, 100 - cv)
        
        return {
            'consistency_score': round(consistency, 1),
            'avg_daily_activities': round(avg, 1),
            'active_days': len(day_counts),
            'variability': 'low' if cv < 30 else 'medium' if cv < 60 else 'high'
        }
    
    def _analyze_platforms(self, activities: List[UserActivity]) -> Dict:
        """Аналіз використання платформ"""
        platform_counts = Counter(a.platform for a in activities)
        total = len(activities)
        
        return {
            platform: round(count / total * 100, 1)
            for platform, count in platform_counts.most_common()
        }
    
    def _classify_user_type(self, activities: List[UserActivity]) -> Dict:
        """Класифікація типу користувача"""
        if not activities:
            return {'type': 'unknown', 'label': 'Невідомий'}
        
        rhythm = self._analyze_daily_rhythm(activities)
        peak_hours = self._find_peak_hours(activities)
        
        daily_avg = len(activities) / max(1, len(set(a.timestamp.date() for a in activities)))
        
        if rhythm['dominant_period'] == 'night':
            user_type = 'night_owl'
        elif peak_hours and min(peak_hours) < 8:
            user_type = 'early_bird'
        elif all(9 <= h <= 18 for h in peak_hours[:2]) if peak_hours else False:
            user_type = 'office_hours'
        elif daily_avg > 20:
            user_type = 'heavy_user'
        elif daily_avg < 3:
            user_type = 'passive'
        else:
            user_type = 'irregular'
        
        return {
            'type': user_type,
            'label': self.USER_TYPES.get(user_type, 'Невідомий'),
            'avg_daily_activities': round(daily_avg, 1)
        }
    
    def _detect_anomalies(self, activities: List[UserActivity]) -> List[Dict]:
        """Виявлення аномалій у поведінці"""
        anomalies = []
        
        if len(activities) < 10:
            return anomalies
        
        hour_counts = Counter(a.timestamp.hour for a in activities)
        avg_hourly = len(activities) / 24
        
        for hour, count in hour_counts.items():
            if count > avg_hourly * 5:
                anomalies.append({
                    'type': 'activity_spike',
                    'hour': hour,
                    'count': count,
                    'description': f'Незвичайно висока активність о {hour}:00'
                })
        
        sorted_activities = sorted(activities, key=lambda a: a.timestamp)
        for i in range(1, len(sorted_activities)):
            gap = (sorted_activities[i].timestamp - sorted_activities[i-1].timestamp).days
            if gap > 7:
                anomalies.append({
                    'type': 'long_absence',
                    'days': gap,
                    'from': sorted_activities[i-1].timestamp.isoformat(),
                    'to': sorted_activities[i].timestamp.isoformat(),
                    'description': f'Відсутність {gap} днів'
                })
        
        return anomalies
    
    def _predict_activity(self, activities: List[UserActivity]) -> Dict:
        """Прогноз майбутньої активності"""
        if len(activities) < 5:
            return {'status': 'insufficient_data'}
        
        peak_hours = self._find_peak_hours(activities)
        rhythm = self._analyze_daily_rhythm(activities)
        
        now = datetime.now()
        best_hours = peak_hours[:3] if peak_hours else [12, 18, 20]
        
        predictions = []
        for hour in best_hours:
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            predictions.append(next_time.isoformat())
        
        return {
            'next_likely_active': predictions,
            'best_contact_time': f"{best_hours[0]:02d}:00" if best_hours else "12:00",
            'dominant_period': rhythm.get('dominant_period', 'unknown')
        }
    
    def format_profile_report(self, profile: Dict) -> str:
        """Форматування звіту профілю"""
        if profile.get('status') == 'insufficient_data':
            return "⚠️ Недостатньо даних для аналізу"
        
        patterns = profile.get('patterns', {})
        user_type = profile.get('user_type', {})
        predictions = profile.get('predictions', {})
        
        report = [
            "<b>👤 ПРОФІЛЬ КОРИСТУВАЧА</b>",
            "═══════════════════════",
            f"ID: <code>{profile['user_id']}</code>",
            f"Активностей: {profile['total_activities']}",
            f"Тип: {user_type.get('label', 'Невідомий')}",
            ""
        ]
        
        rhythm = patterns.get('daily_rhythm', {})
        if rhythm.get('distribution'):
            report.append("<b>📊 Добовий ритм:</b>")
            dist = rhythm['distribution']
            report.append(f"├ Ранок: {dist.get('morning', 0)}%")
            report.append(f"├ День: {dist.get('afternoon', 0)}%")
            report.append(f"├ Вечір: {dist.get('evening', 0)}%")
            report.append(f"└ Ніч: {dist.get('night', 0)}%")
            report.append("")
        
        sleep = patterns.get('sleep_schedule', {})
        if sleep.get('estimated_sleep_start'):
            report.append("<b>😴 Графік сну:</b>")
            report.append(f"├ Сон: ~{sleep['estimated_sleep_start']}")
            report.append(f"├ Підйом: ~{sleep['estimated_wake_time']}")
            report.append(f"└ Впевненість: {sleep.get('confidence', 0)}%")
            report.append("")
        
        if predictions.get('best_contact_time'):
            report.append("<b>📞 Рекомендації:</b>")
            report.append(f"├ Найкращий час: {predictions['best_contact_time']}")
            peak = patterns.get('peak_hours', [])
            if peak:
                report.append(f"└ Пікові години: {', '.join(f'{h}:00' for h in peak)}")
        
        anomalies = profile.get('anomalies', [])
        if anomalies:
            report.append("")
            report.append("<b>⚠️ Аномалії:</b>")
            for a in anomalies[:3]:
                report.append(f"├ {a.get('description', 'Невідома аномалія')}")
        
        return '\n'.join(report)


behavior_profiler = BehaviorProfiler()
