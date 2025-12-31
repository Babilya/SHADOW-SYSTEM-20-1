"""
UI Builder - Unified system for building consistent UI messages and menus

Provides:
- MenuMessage class for standardized menu construction
- MessageBuilder for complex multi-section messages
- Consistent styling across all roles and features
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from core.roles import UserRole

DIVIDER = "───────────────"
DIVIDER_DOUBLE = "═══════════════"

ROLE_EMOJIS = {
    "guest": "🌐",
    "manager": "👤",
    "leader": "👑",
    "admin": "🛡️",
}

ROLE_NAMES = {
    "guest": "Гість",
    "manager": "Менеджер",
    "leader": "Лідер",
    "admin": "Адміністратор",
}

SECTION_EMOJIS = {
    "botnet": "🤖",
    "osint": "🔍",
    "campaigns": "🚀",
    "analytics": "📊",
    "team": "👥",
    "settings": "⚙️",
    "support": "💬",
    "license": "🔑",
    "profile": "👤",
    "help": "📖",
    "funnels": "🎯",
    "templates": "📝",
    "notifications": "🔔",
    "warming": "🔥",
    "stats": "📈",
    "security": "🔐",
}

@dataclass
class Section:
    """Represents a section in a menu message"""
    title: str
    items: List[str] = field(default_factory=list)
    emoji: str = ""
    
    def render(self) -> str:
        """Render section as HTML string"""
        if not self.items:
            return ""
        
        header = f"<b>{self.emoji} {self.title}:</b>" if self.emoji else f"<b>{self.title}:</b>"
        
        lines = [header]
        for i, item in enumerate(self.items):
            prefix = "└" if i == len(self.items) - 1 else "├"
            lines.append(f"{prefix} {item}")
        
        return "\n".join(lines)


class MenuMessage:
    """Unified menu message builder with consistent styling"""
    
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        role: str = "guest",
        sections: Optional[Dict[str, List[str]]] = None
    ):
        self.title = title
        self.subtitle = subtitle
        self.role = role
        self.sections: List[Section] = []
        
        if sections:
            for section_title, items in sections.items():
                emoji = SECTION_EMOJIS.get(section_title.lower(), "")
                self.add_section(section_title, items, emoji)
    
    def add_section(self, title: str, items: List[str], emoji: str = "") -> "MenuMessage":
        """Add a section to the message"""
        self.sections.append(Section(title=title, items=items, emoji=emoji))
        return self
    
    def add_status_line(self, label: str, value: str, emoji: str = "") -> "MenuMessage":
        """Add a single status line section"""
        if emoji:
            self.sections.append(Section(title="", items=[f"{emoji} {label}: <b>{value}</b>"]))
        else:
            self.sections.append(Section(title="", items=[f"{label}: <b>{value}</b>"]))
        return self
    
    def render(self) -> str:
        """Build the complete HTML message"""
        role_emoji = ROLE_EMOJIS.get(self.role, "🌐")
        
        lines = [f"{role_emoji} <b>{self.title}</b>"]
        
        if self.subtitle:
            lines.append(f"<i>{self.subtitle}</i>")
        
        lines.append(DIVIDER)
        
        role_name = ROLE_NAMES.get(self.role, "Гість")
        lines.append(f"<b>📋 Статус:</b> {role_name}")
        lines.append("")
        
        for section in self.sections:
            rendered = section.render()
            if rendered:
                lines.append(rendered)
                lines.append("")
        
        return "\n".join(lines).strip()


class MessageBuilder:
    """Fluent builder for constructing complex messages"""
    
    def __init__(self, title: str = "", emoji: str = ""):
        self._title = title
        self._emoji = emoji
        self._subtitle = ""
        self._sections: List[str] = []
        self._footer = ""
        self._divider_type = "single"
    
    def title(self, text: str, emoji: str = "") -> "MessageBuilder":
        """Set the title"""
        self._title = text
        if emoji:
            self._emoji = emoji
        return self
    
    def subtitle(self, text: str) -> "MessageBuilder":
        """Set the subtitle (italic)"""
        self._subtitle = text
        return self
    
    def divider(self, double: bool = False) -> "MessageBuilder":
        """Add a divider line"""
        div = DIVIDER_DOUBLE if double else DIVIDER
        self._sections.append(div)
        return self
    
    def section(self, title: str, items: List[str], emoji: str = "") -> "MessageBuilder":
        """Add a section with bullet points"""
        sec = Section(title=title, items=items, emoji=emoji)
        self._sections.append(sec.render())
        return self
    
    def text(self, content: str) -> "MessageBuilder":
        """Add raw text"""
        self._sections.append(content)
        return self
    
    def stats(self, stats: Dict[str, Any], emoji_map: Optional[Dict[str, str]] = None) -> "MessageBuilder":
        """Add statistics section"""
        lines = ["<b>📊 СТАТИСТИКА:</b>"]
        items = list(stats.items())
        for i, (key, value) in enumerate(items):
            emoji = emoji_map.get(key, "") if emoji_map else ""
            prefix = "└" if i == len(items) - 1 else "├"
            if emoji:
                lines.append(f"{prefix} {emoji} {key}: <b>{value}</b>")
            else:
                lines.append(f"{prefix} {key}: <b>{value}</b>")
        self._sections.append("\n".join(lines))
        return self
    
    def info(self, items: Dict[str, str]) -> "MessageBuilder":
        """Add info section with key-value pairs"""
        lines = ["<b>📋 ІНФОРМАЦІЯ:</b>"]
        item_list = list(items.items())
        for i, (key, value) in enumerate(item_list):
            prefix = "└" if i == len(item_list) - 1 else "├"
            lines.append(f"{prefix} {key}: <b>{value}</b>")
        self._sections.append("\n".join(lines))
        return self
    
    def footer(self, text: str) -> "MessageBuilder":
        """Set footer text"""
        self._footer = text
        return self
    
    def build(self) -> str:
        """Build the complete HTML message"""
        lines = []
        
        if self._title:
            if self._emoji:
                lines.append(f"{self._emoji} <b>{self._title}</b>")
            else:
                lines.append(f"<b>{self._title}</b>")
        
        if self._subtitle:
            lines.append(f"<i>{self._subtitle}</i>")
        
        if lines:
            lines.append(DIVIDER)
        
        for section in self._sections:
            lines.append(section)
            lines.append("")
        
        if self._footer:
            lines.append(DIVIDER)
            lines.append(f"<i>{self._footer}</i>")
        
        return "\n".join(lines).strip()


class UniversalPaginator:
    """Universal pagination for any list of items"""
    
    def __init__(
        self,
        items: List[Any],
        view_type: str,
        per_page: int = 10,
        callback_prefix: str = "page",
        current_page: int = 1,
        item_formatter: Optional[Any] = None
    ):
        self.items = items
        self.view_type = view_type
        self.per_page = per_page
        self.callback_prefix = callback_prefix
        self.current_page = current_page
        self.item_formatter = item_formatter or self._default_formatter
        
        self.total_pages = max(1, (len(items) + per_page - 1) // per_page)
    
    def _default_formatter(self, item: Any, index: int) -> tuple[str, str]:
        """Default item formatter, returns (text, callback_data)"""
        if hasattr(item, 'name'):
            name = item.name
        elif isinstance(item, dict) and 'name' in item:
            name = item['name']
        else:
            name = str(item)
        
        if hasattr(item, 'id'):
            item_id = getattr(item, 'id')
        elif isinstance(item, dict) and 'id' in item:
            item_id = item.get('id', index)
        else:
            item_id = index
        
        return (name[:30], f"{self.view_type}_view_{item_id}")
    
    def get_page_items(self) -> List[Any]:
        """Get items for current page"""
        start = (self.current_page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]
    
    def get_navigation_buttons(self) -> List[InlineKeyboardButton]:
        """Get navigation buttons"""
        buttons = []
        
        if self.current_page > 1:
            buttons.append(InlineKeyboardButton(
                text="◀️ Попередня",
                callback_data=f"{self.callback_prefix}:{self.view_type}:{self.current_page - 1}"
            ))
        
        buttons.append(InlineKeyboardButton(
            text=f"📄 {self.current_page}/{self.total_pages}",
            callback_data="noop"
        ))
        
        if self.current_page < self.total_pages:
            buttons.append(InlineKeyboardButton(
                text="Наступна ▶️",
                callback_data=f"{self.callback_prefix}:{self.view_type}:{self.current_page + 1}"
            ))
        
        return buttons
    
    def get_item_buttons(self) -> List[List[InlineKeyboardButton]]:
        """Get buttons for items on current page"""
        buttons = []
        page_items = self.get_page_items()
        
        for i, item in enumerate(page_items):
            global_index = (self.current_page - 1) * self.per_page + i
            text, callback = self.item_formatter(item, global_index)
            buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])
        
        return buttons
    
    def get_keyboard(
        self,
        back_button: Optional[InlineKeyboardButton] = None,
        extra_buttons: Optional[List[List[InlineKeyboardButton]]] = None
    ) -> InlineKeyboardMarkup:
        """Build complete keyboard with pagination"""
        buttons = self.get_item_buttons()
        
        if self.total_pages > 1:
            buttons.append(self.get_navigation_buttons())
        
        if extra_buttons:
            buttons.extend(extra_buttons)
        
        if back_button:
            buttons.append([back_button])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def get_page_info(self) -> str:
        """Get page info text"""
        start = (self.current_page - 1) * self.per_page + 1
        end = min(self.current_page * self.per_page, len(self.items))
        return f"📄 Сторінка {self.current_page}/{self.total_pages} (показано {start}-{end} з {len(self.items)})"


def create_menu_message(
    title: str,
    subtitle: str = "",
    role: str = "guest",
    sections: Optional[Dict[str, List[str]]] = None
) -> str:
    """Quick function to create a menu message"""
    return MenuMessage(title, subtitle, role, sections).render()


def create_info_message(
    title: str,
    subtitle: str = "",
    info: Optional[Dict[str, str]] = None,
    stats: Optional[Dict[str, Any]] = None,
    footer: str = ""
) -> str:
    """Quick function to create an info message"""
    builder = MessageBuilder().title(title).subtitle(subtitle)
    
    if info:
        builder.info(info)
    
    if stats:
        builder.stats(stats)
    
    if footer:
        builder.footer(footer)
    
    return builder.build()
