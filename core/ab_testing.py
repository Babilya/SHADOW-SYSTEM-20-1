import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger(__name__)


class TestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MetricType(str, Enum):
    CONVERSION = "conversion"
    CLICK_RATE = "click_rate"
    RESPONSE_RATE = "response_rate"
    REVENUE = "revenue"


@dataclass
class Variant:
    id: str
    name: str
    content: str
    weight: float = 0.5
    impressions: int = 0
    conversions: int = 0
    clicks: int = 0
    responses: int = 0
    revenue: float = 0.0
    
    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.impressions if self.impressions > 0 else 0.0
    
    @property
    def click_rate(self) -> float:
        return self.clicks / self.impressions if self.impressions > 0 else 0.0
    
    @property
    def response_rate(self) -> float:
        return self.responses / self.impressions if self.impressions > 0 else 0.0


@dataclass
class ABTest:
    id: str
    name: str
    description: str
    variants: List[Variant]
    primary_metric: MetricType
    status: TestStatus = TestStatus.DRAFT
    min_sample_size: int = 100
    confidence_level: float = 0.95
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    winner_id: Optional[str] = None
    
    def get_variant(self, variant_id: str) -> Optional[Variant]:
        for v in self.variants:
            if v.id == variant_id:
                return v
        return None


class StatisticalCalculator:
    @staticmethod
    def z_score(confidence_level: float) -> float:
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        return z_scores.get(confidence_level, 1.96)
    
    @staticmethod
    def standard_error(rate: float, n: int) -> float:
        if n == 0:
            return 0
        return math.sqrt(rate * (1 - rate) / n)
    
    @staticmethod
    def pooled_standard_error(rate_a: float, n_a: int, rate_b: float, n_b: int) -> float:
        if n_a == 0 or n_b == 0:
            return 0
        pooled_rate = (rate_a * n_a + rate_b * n_b) / (n_a + n_b)
        return math.sqrt(pooled_rate * (1 - pooled_rate) * (1/n_a + 1/n_b))
    
    @staticmethod
    def calculate_z_stat(rate_a: float, rate_b: float, pooled_se: float) -> float:
        if pooled_se == 0:
            return 0
        return (rate_b - rate_a) / pooled_se
    
    @staticmethod
    def p_value_from_z(z_stat: float) -> float:
        return 2 * (1 - StatisticalCalculator._normal_cdf(abs(z_stat)))
    
    @staticmethod
    def _normal_cdf(x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    @staticmethod
    def confidence_interval(rate: float, n: int, confidence: float = 0.95) -> tuple:
        if n == 0:
            return (0, 0)
        z = StatisticalCalculator.z_score(confidence)
        se = StatisticalCalculator.standard_error(rate, n)
        margin = z * se
        return (max(0, rate - margin), min(1, rate + margin))
    
    @staticmethod
    def minimum_sample_size(
        baseline_rate: float,
        minimum_detectable_effect: float,
        power: float = 0.8,
        significance: float = 0.05
    ) -> int:
        z_alpha = StatisticalCalculator.z_score(1 - significance)
        z_beta = 0.84 if power == 0.8 else 1.28
        
        p1 = baseline_rate
        p2 = baseline_rate * (1 + minimum_detectable_effect)
        
        numerator = (z_alpha * math.sqrt(2 * p1 * (1 - p1)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2
        
        if denominator == 0:
            return 1000
        
        return int(math.ceil(numerator / denominator))
    
    @staticmethod
    def lift(control_rate: float, treatment_rate: float) -> float:
        if control_rate == 0:
            return 0
        return (treatment_rate - control_rate) / control_rate * 100


class ABTestingService:
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
        self.user_assignments: Dict[str, Dict[int, str]] = {}
        self.calculator = StatisticalCalculator()
        self._counter = 0
    
    def _generate_id(self) -> str:
        self._counter += 1
        return f"ABT-{datetime.now().strftime('%Y%m%d')}-{self._counter:04d}"
    
    def create_test(
        self,
        name: str,
        description: str,
        variant_a_content: str,
        variant_b_content: str,
        primary_metric: MetricType = MetricType.CONVERSION,
        min_sample_size: int = 100,
        confidence_level: float = 0.95,
        variant_a_weight: float = 0.5
    ) -> ABTest:
        test_id = self._generate_id()
        
        variants = [
            Variant(id="A", name="Контроль", content=variant_a_content, weight=variant_a_weight),
            Variant(id="B", name="Тест", content=variant_b_content, weight=1 - variant_a_weight)
        ]
        
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            variants=variants,
            primary_metric=primary_metric,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level
        )
        
        self.tests[test_id] = test
        self.user_assignments[test_id] = {}
        
        logger.info(f"Created A/B test: {test_id} - {name}")
        return test
    
    def start_test(self, test_id: str) -> bool:
        test = self.tests.get(test_id)
        if not test:
            return False
        
        if test.status != TestStatus.DRAFT:
            return False
        
        test.status = TestStatus.RUNNING
        test.started_at = datetime.now()
        
        logger.info(f"Started A/B test: {test_id}")
        return True
    
    def pause_test(self, test_id: str) -> bool:
        test = self.tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return False
        
        test.status = TestStatus.PAUSED
        logger.info(f"Paused A/B test: {test_id}")
        return True
    
    def resume_test(self, test_id: str) -> bool:
        test = self.tests.get(test_id)
        if not test or test.status != TestStatus.PAUSED:
            return False
        
        test.status = TestStatus.RUNNING
        logger.info(f"Resumed A/B test: {test_id}")
        return True
    
    def complete_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        test = self.tests.get(test_id)
        if not test:
            return None
        
        test.status = TestStatus.COMPLETED
        test.completed_at = datetime.now()
        
        results = self.analyze_test(test_id)
        if results and results.get("winner"):
            test.winner_id = results["winner"]["id"]
        
        logger.info(f"Completed A/B test: {test_id}, winner: {test.winner_id}")
        return results
    
    def assign_variant(self, test_id: str, user_id: int) -> Optional[Variant]:
        test = self.tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return None
        
        if user_id in self.user_assignments.get(test_id, {}):
            variant_id = self.user_assignments[test_id][user_id]
            return test.get_variant(variant_id)
        
        rand = random.random()
        cumulative = 0
        selected_variant = test.variants[0]
        
        for variant in test.variants:
            cumulative += variant.weight
            if rand <= cumulative:
                selected_variant = variant
                break
        
        self.user_assignments[test_id][user_id] = selected_variant.id
        selected_variant.impressions += 1
        
        return selected_variant
    
    def record_conversion(
        self,
        test_id: str,
        user_id: int,
        metric: MetricType = MetricType.CONVERSION,
        value: float = 1.0
    ) -> bool:
        test = self.tests.get(test_id)
        if not test:
            return False
        
        variant_id = self.user_assignments.get(test_id, {}).get(user_id)
        if not variant_id:
            return False
        
        variant = test.get_variant(variant_id)
        if not variant:
            return False
        
        if metric == MetricType.CONVERSION:
            variant.conversions += 1
        elif metric == MetricType.CLICK_RATE:
            variant.clicks += 1
        elif metric == MetricType.RESPONSE_RATE:
            variant.responses += 1
        elif metric == MetricType.REVENUE:
            variant.revenue += value
            variant.conversions += 1
        
        return True
    
    def analyze_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        test = self.tests.get(test_id)
        if not test or len(test.variants) < 2:
            return None
        
        control = test.variants[0]
        treatment = test.variants[1]
        
        if test.primary_metric == MetricType.CONVERSION:
            rate_a = control.conversion_rate
            rate_b = treatment.conversion_rate
        elif test.primary_metric == MetricType.CLICK_RATE:
            rate_a = control.click_rate
            rate_b = treatment.click_rate
        elif test.primary_metric == MetricType.RESPONSE_RATE:
            rate_a = control.response_rate
            rate_b = treatment.response_rate
        else:
            rate_a = control.conversion_rate
            rate_b = treatment.conversion_rate
        
        pooled_se = self.calculator.pooled_standard_error(
            rate_a, control.impressions,
            rate_b, treatment.impressions
        )
        
        z_stat = self.calculator.calculate_z_stat(rate_a, rate_b, pooled_se)
        p_value = self.calculator.p_value_from_z(z_stat)
        
        is_significant = p_value < (1 - test.confidence_level)
        lift = self.calculator.lift(rate_a, rate_b)
        
        ci_a = self.calculator.confidence_interval(rate_a, control.impressions, test.confidence_level)
        ci_b = self.calculator.confidence_interval(rate_b, treatment.impressions, test.confidence_level)
        
        total_impressions = control.impressions + treatment.impressions
        has_enough_data = total_impressions >= test.min_sample_size * 2
        
        winner = None
        if is_significant and has_enough_data:
            winner = treatment if rate_b > rate_a else control
        
        return {
            "test_id": test_id,
            "test_name": test.name,
            "status": test.status.value,
            "primary_metric": test.primary_metric.value,
            "control": {
                "id": control.id,
                "name": control.name,
                "impressions": control.impressions,
                "conversions": control.conversions,
                "rate": round(rate_a * 100, 2),
                "confidence_interval": (round(ci_a[0] * 100, 2), round(ci_a[1] * 100, 2))
            },
            "treatment": {
                "id": treatment.id,
                "name": treatment.name,
                "impressions": treatment.impressions,
                "conversions": treatment.conversions,
                "rate": round(rate_b * 100, 2),
                "confidence_interval": (round(ci_b[0] * 100, 2), round(ci_b[1] * 100, 2))
            },
            "statistics": {
                "z_statistic": round(z_stat, 4),
                "p_value": round(p_value, 4),
                "lift_percent": round(lift, 2),
                "is_significant": is_significant,
                "confidence_level": test.confidence_level,
                "has_enough_data": has_enough_data,
                "total_sample_size": total_impressions,
                "required_sample_size": test.min_sample_size * 2
            },
            "winner": {
                "id": winner.id,
                "name": winner.name,
                "rate": round((rate_b if winner == treatment else rate_a) * 100, 2)
            } if winner else None,
            "recommendation": self._get_recommendation(is_significant, has_enough_data, lift, winner)
        }
    
    def _get_recommendation(
        self,
        is_significant: bool,
        has_enough_data: bool,
        lift: float,
        winner: Optional[Variant]
    ) -> str:
        if not has_enough_data:
            return "⏳ Продовжуйте тест. Недостатньо даних для статистично значущого висновку."
        
        if not is_significant:
            return "📊 Результати не є статистично значущими. Різниця може бути випадковою."
        
        if winner:
            if winner.id == "B":
                if lift > 20:
                    return f"🎉 Варіант B переміг! Значне покращення ({lift:.1f}%). Рекомендуємо впровадити."
                else:
                    return f"✅ Варіант B показав кращий результат ({lift:.1f}%). Рекомендуємо впровадити."
            else:
                return "⚠️ Контрольний варіант A кращий. Залиште поточну версію."
        
        return "❓ Результати неоднозначні. Потрібен додатковий аналіз."
    
    def format_results_message(self, test_id: str) -> str:
        results = self.analyze_test(test_id)
        if not results:
            return "❌ Тест не знайдено"
        
        stats = results["statistics"]
        control = results["control"]
        treatment = results["treatment"]
        
        significant_icon = "✅" if stats["is_significant"] else "❌"
        
        return f"""📊 <b>A/B ТЕСТ: {results['test_name']}</b>

<b>Статус:</b> {results['status'].upper()}
<b>Метрика:</b> {results['primary_metric']}

───────────────

<b>📈 ВАРІАНТ A (Контроль):</b>
├ Показів: {control['impressions']}
├ Конверсій: {control['conversions']}
├ Конверсія: {control['rate']}%
└ CI: ({control['confidence_interval'][0]}% - {control['confidence_interval'][1]}%)

<b>📈 ВАРІАНТ B (Тест):</b>
├ Показів: {treatment['impressions']}
├ Конверсій: {treatment['conversions']}
├ Конверсія: {treatment['rate']}%
└ CI: ({treatment['confidence_interval'][0]}% - {treatment['confidence_interval'][1]}%)

───────────────

<b>📉 СТАТИСТИКА:</b>
├ Z-статистика: {stats['z_statistic']}
├ P-value: {stats['p_value']}
├ Lift: {stats['lift_percent']:+.1f}%
├ {significant_icon} Значущість: {'Так' if stats['is_significant'] else 'Ні'}
└ Вибірка: {stats['total_sample_size']}/{stats['required_sample_size']}

<b>🏆 РЕЗУЛЬТАТ:</b>
{results['winner']['name'] + ' переміг!' if results['winner'] else 'Переможець не визначено'}

<b>💡 РЕКОМЕНДАЦІЯ:</b>
{results['recommendation']}"""
    
    def get_all_tests(self, status: Optional[TestStatus] = None) -> List[Dict[str, Any]]:
        tests = list(self.tests.values())
        if status:
            tests = [t for t in tests if t.status == status]
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "status": t.status.value,
                "impressions": sum(v.impressions for v in t.variants),
                "created_at": t.created_at.isoformat(),
                "winner_id": t.winner_id
            }
            for t in sorted(tests, key=lambda x: x.created_at, reverse=True)
        ]


ab_testing_service = ABTestingService()
