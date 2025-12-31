import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CommunicationStyle(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    FLIRTY = "flirty"
    CASUAL = "casual"
    FORMAL = "formal"
    HUMOROUS = "humorous"
    SUPPORTIVE = "supportive"
    SALES = "sales"
    INFORMATIVE = "informative"
    MYSTERIOUS = "mysterious"


class ConversationTopic(str, Enum):
    GENERAL = "general"
    BUSINESS = "business"
    DATING = "dating"
    TECH = "tech"
    CRYPTO = "crypto"
    MARKETING = "marketing"
    SUPPORT = "support"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    CUSTOM = "custom"


@dataclass
class PersonaProfile:
    persona_id: str
    name: str
    style: CommunicationStyle
    topic: ConversationTopic
    description: str
    system_prompt: str
    example_messages: List[str] = field(default_factory=list)
    emoji_usage: str = "moderate"
    response_length: str = "medium"
    formality_level: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    is_custom: bool = False


@dataclass
class ConversationContext:
    user_id: int
    user_name: Optional[str]
    messages_history: List[Dict[str, str]] = field(default_factory=list)
    detected_mood: str = "neutral"
    topics_discussed: List[str] = field(default_factory=list)


class AICommunicationStyleService:
    def __init__(self):
        self.personas: Dict[str, PersonaProfile] = {}
        self.active_personas: Dict[str, str] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.custom_training_examples: Dict[str, List[Dict[str, str]]] = {}
        self._init_default_personas()
    
    def _init_default_personas(self):
        default_personas = [
            PersonaProfile(
                persona_id="friendly_helper",
                name="Дружній помічник",
                style=CommunicationStyle.FRIENDLY,
                topic=ConversationTopic.GENERAL,
                description="Привітний та дружелюбний стиль спілкування",
                system_prompt="""Ти дружній помічник, який спілкується українською мовою. 
Використовуй теплий, привітний тон. Будь емпатичним та підтримуючим.
Відповідай стисло, але з душею. Використовуй емодзі помірно.""",
                example_messages=[
                    "Привіт! Радий тебе бачити 😊",
                    "Як справи? Чим можу допомогти?",
                    "Без проблем, завжди радий допомогти!"
                ],
                emoji_usage="moderate",
                response_length="medium",
                formality_level=3
            ),
            PersonaProfile(
                persona_id="professional_manager",
                name="Професійний менеджер",
                style=CommunicationStyle.PROFESSIONAL,
                topic=ConversationTopic.BUSINESS,
                description="Діловий та професійний стиль для бізнес-комунікації",
                system_prompt="""Ти професійний менеджер, який спілкується українською мовою.
Використовуй ввічливий, діловий тон. Будь конкретним та структурованим.
Пропонуй рішення та варіанти. Мінімум емодзі, максимум користі.""",
                example_messages=[
                    "Доброго дня! Дякую за звернення.",
                    "Дозвольте уточнити деталі вашого запиту.",
                    "Підготую для вас комерційну пропозицію."
                ],
                emoji_usage="minimal",
                response_length="medium",
                formality_level=8
            ),
            PersonaProfile(
                persona_id="casual_friend",
                name="Свій в дошку",
                style=CommunicationStyle.CASUAL,
                topic=ConversationTopic.GENERAL,
                description="Неформальний, розслаблений стиль як з другом",
                system_prompt="""Ти хороший друг, який спілкується українською мовою.
Використовуй неформальний стиль, можеш жартувати. Будь природнім.
Відповідай як реальна людина, без формальностей.""",
                example_messages=[
                    "Йоу! Як воно? 👋",
                    "Та не парся, все норм буде",
                    "О, круто! Расскажи більше"
                ],
                emoji_usage="high",
                response_length="short",
                formality_level=1
            ),
            PersonaProfile(
                persona_id="sales_expert",
                name="Експерт продажів",
                style=CommunicationStyle.SALES,
                topic=ConversationTopic.MARKETING,
                description="Стиль для продажів та залучення клієнтів",
                system_prompt="""Ти експерт з продажів, який спілкується українською мовою.
Використовуй переконливий, але не нав'язливий тон. Підкреслюй вигоди.
Ставши питання, щоб виявити потреби. Веди до покупки м'яко.""",
                example_messages=[
                    "Цікаво! А який результат ви хочете отримати?",
                    "У нас є рішення, яке ідеально підходить для ваших цілей",
                    "Можу показати, як це працює на практиці?"
                ],
                emoji_usage="moderate",
                response_length="medium",
                formality_level=5
            ),
            PersonaProfile(
                persona_id="tech_guru",
                name="Технічний гуру",
                style=CommunicationStyle.INFORMATIVE,
                topic=ConversationTopic.TECH,
                description="Стиль для технічних консультацій",
                system_prompt="""Ти технічний експерт, який спілкується українською мовою.
Пояснюй складні речі простими словами. Будь точним та корисним.
Давай конкретні рекомендації та поради.""",
                example_messages=[
                    "Це працює так: спершу потрібно...",
                    "Рекомендую спробувати цей підхід",
                    "Щоб це налаштувати, виконай ці кроки"
                ],
                emoji_usage="minimal",
                response_length="long",
                formality_level=6
            ),
            PersonaProfile(
                persona_id="crypto_trader",
                name="Крипто трейдер",
                style=CommunicationStyle.CASUAL,
                topic=ConversationTopic.CRYPTO,
                description="Стиль для крипто-спільноти",
                system_prompt="""Ти досвідчений крипто-трейдер, який спілкується українською.
Використовуй крипто-сленг природно. Будь в курсі трендів.
Давай аналітику, але не фінансові поради.""",
                example_messages=[
                    "BTC тримає рівень, виглядає бичачо 📈",
                    "DYOR, але цей проєкт цікавий",
                    "Не FOMO, ринок завжди дає нові можливості"
                ],
                emoji_usage="high",
                response_length="short",
                formality_level=2
            ),
            PersonaProfile(
                persona_id="support_agent",
                name="Агент підтримки",
                style=CommunicationStyle.SUPPORTIVE,
                topic=ConversationTopic.SUPPORT,
                description="Стиль для клієнтської підтримки",
                system_prompt="""Ти агент підтримки клієнтів, який спілкується українською.
Будь терплячим та розуміючим. Вислухай проблему уважно.
Запропонуй рішення кроками. Переконайся, що клієнт задоволений.""",
                example_messages=[
                    "Розумію вашу ситуацію. Давайте разом розберемось.",
                    "Дякую за терпіння! Ось що можемо зробити:",
                    "Чи є ще питання, з якими можу допомогти?"
                ],
                emoji_usage="minimal",
                response_length="medium",
                formality_level=7
            ),
            PersonaProfile(
                persona_id="mysterious_stranger",
                name="Загадкова особа",
                style=CommunicationStyle.MYSTERIOUS,
                topic=ConversationTopic.GENERAL,
                description="Загадковий, інтригуючий стиль",
                system_prompt="""Ти загадкова особа, яка спілкується українською.
Будь інтригуючим, не розкривай все одразу. Створюй цікавість.
Відповідай загадково, але не збивай з пантелику.""",
                example_messages=[
                    "Цікаво... Але головне ще попереду.",
                    "Не все так просто, як здається на перший погляд",
                    "Є речі, про які не варто говорити відкрито..."
                ],
                emoji_usage="minimal",
                response_length="short",
                formality_level=5
            )
        ]
        
        for persona in default_personas:
            self.personas[persona.persona_id] = persona
    
    def get_persona(self, persona_id: str) -> Optional[PersonaProfile]:
        return self.personas.get(persona_id)
    
    def get_all_personas(self) -> List[PersonaProfile]:
        return list(self.personas.values())
    
    def get_personas_by_style(self, style: CommunicationStyle) -> List[PersonaProfile]:
        return [p for p in self.personas.values() if p.style == style]
    
    def get_personas_by_topic(self, topic: ConversationTopic) -> List[PersonaProfile]:
        return [p for p in self.personas.values() if p.topic == topic]
    
    def set_active_persona(self, bot_id: str, persona_id: str) -> bool:
        if persona_id in self.personas:
            self.active_personas[bot_id] = persona_id
            return True
        return False
    
    def get_active_persona(self, bot_id: str) -> Optional[PersonaProfile]:
        persona_id = self.active_personas.get(bot_id)
        if persona_id:
            return self.personas.get(persona_id)
        return None
    
    def create_custom_persona(
        self,
        name: str,
        style: CommunicationStyle,
        topic: ConversationTopic,
        description: str,
        custom_prompt: str,
        examples: List[str] = None
    ) -> PersonaProfile:
        persona_id = f"custom_{len([p for p in self.personas.values() if p.is_custom]) + 1}"
        
        persona = PersonaProfile(
            persona_id=persona_id,
            name=name,
            style=style,
            topic=topic,
            description=description,
            system_prompt=custom_prompt,
            example_messages=examples or [],
            is_custom=True
        )
        
        self.personas[persona_id] = persona
        return persona
    
    def add_training_example(
        self,
        persona_id: str,
        user_message: str,
        ideal_response: str
    ):
        if persona_id not in self.custom_training_examples:
            self.custom_training_examples[persona_id] = []
        
        self.custom_training_examples[persona_id].append({
            "user": user_message,
            "assistant": ideal_response,
            "added_at": datetime.now().isoformat()
        })
    
    def get_training_examples(self, persona_id: str) -> List[Dict[str, str]]:
        return self.custom_training_examples.get(persona_id, [])
    
    async def generate_response(
        self,
        bot_id: str,
        user_message: str,
        context: ConversationContext = None
    ) -> str:
        persona = self.get_active_persona(bot_id)
        if not persona:
            persona = self.personas.get("friendly_helper")
        
        try:
            from core.ai_service import ai_service
            
            if not ai_service.is_available:
                return self._generate_fallback_response(persona, user_message)
            
            system_prompt = persona.system_prompt
            
            training_examples = self.get_training_examples(persona.persona_id)
            messages = [{"role": "system", "content": system_prompt}]
            
            for example in training_examples[-3:]:
                messages.append({"role": "user", "content": example["user"]})
                messages.append({"role": "assistant", "content": example["assistant"]})
            
            if context and context.messages_history:
                for msg in context.messages_history[-5:]:
                    messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            response = ai_service.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return self._generate_fallback_response(persona, user_message)
    
    def _generate_fallback_response(self, persona: PersonaProfile, user_message: str) -> str:
        if persona.example_messages:
            import random
            return random.choice(persona.example_messages)
        
        fallback_responses = {
            CommunicationStyle.FRIENDLY: "Привіт! Радий тебе бачити! 😊",
            CommunicationStyle.PROFESSIONAL: "Доброго дня! Дякую за звернення.",
            CommunicationStyle.CASUAL: "Йоу! Як справи?",
            CommunicationStyle.SALES: "Цікаво! Розкажіть більше про ваші потреби.",
            CommunicationStyle.SUPPORTIVE: "Розумію вас. Давайте разом розберемось."
        }
        
        return fallback_responses.get(persona.style, "Привіт!")
    
    def format_persona_info(self, persona: PersonaProfile) -> str:
        lines = []
        lines.append(f"<b>{persona.name}</b>")
        lines.append(f"═══════════════════════")
        lines.append(f"<b>Стиль:</b> {persona.style.value}")
        lines.append(f"<b>Тема:</b> {persona.topic.value}")
        lines.append(f"<b>Опис:</b> {persona.description}")
        lines.append("")
        lines.append(f"<b>Налаштування:</b>")
        lines.append(f"├ Емодзі: {persona.emoji_usage}")
        lines.append(f"├ Довжина: {persona.response_length}")
        lines.append(f"└ Формальність: {persona.formality_level}/10")
        
        if persona.example_messages:
            lines.append("")
            lines.append("<b>Приклади:</b>")
            for i, msg in enumerate(persona.example_messages[:3], 1):
                lines.append(f"  {i}. <i>{msg}</i>")
        
        return "\n".join(lines)
    
    def format_personas_list(self) -> str:
        lines = []
        lines.append("<b>🎭 СТИЛІ КОМУНІКАЦІЇ</b>")
        lines.append("═══════════════════════")
        lines.append("")
        
        for persona in self.personas.values():
            custom_badge = " [custom]" if persona.is_custom else ""
            lines.append(f"<b>{persona.name}</b>{custom_badge}")
            lines.append(f"  └ {persona.description}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_personas": len(self.personas),
            "custom_personas": len([p for p in self.personas.values() if p.is_custom]),
            "active_assignments": len(self.active_personas),
            "training_examples": sum(len(e) for e in self.custom_training_examples.values()),
            "timestamp": datetime.now().isoformat()
        }


ai_communication_styles = AICommunicationStyleService()
