"""
Shared UI Components for consistent UX across all menus
- Inline search
- Pagination
- Progress indicators
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Callable, Any, Optional
import math

DIVIDER = "───────────────"

class Paginator:
    """Universal pagination component for any list data"""
    
    def __init__(
        self, 
        items: List[Any], 
        page: int = 1, 
        per_page: int = 10,
        callback_prefix: str = "page"
    ):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.callback_prefix = callback_prefix
        self.total_pages = max(1, math.ceil(len(items) / per_page))
    
    @property
    def current_items(self) -> List[Any]:
        """Get items for current page"""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    def get_nav_buttons(self) -> List[InlineKeyboardButton]:
        """Generate navigation buttons"""
        buttons = []
        
        if self.has_prev:
            buttons.append(InlineKeyboardButton(
                text="◀️", 
                callback_data=f"{self.callback_prefix}:{self.page - 1}"
            ))
        
        buttons.append(InlineKeyboardButton(
            text=f"{self.page}/{self.total_pages}",
            callback_data="page_info"
        ))
        
        if self.has_next:
            buttons.append(InlineKeyboardButton(
                text="▶️",
                callback_data=f"{self.callback_prefix}:{self.page + 1}"
            ))
        
        return buttons
    
    def get_info_text(self) -> str:
        """Get pagination info text"""
        start = (self.page - 1) * self.per_page + 1
        end = min(self.page * self.per_page, len(self.items))
        return f"📊 {start}-{end} з {len(self.items)}"


class ProgressBar:
    """Native collab-style progress indicator"""
    
    @staticmethod
    def render(progress: int, width: int = 8) -> str:
        """Render native collab progress bar"""
        progress = max(0, min(100, progress))
        filled = int(width * progress / 100)
        empty = width - filled
        bar = "●" * filled + "○" * empty
        return f"{bar} {progress}%"
    
    @staticmethod
    def render_emoji(progress: int) -> str:
        """Render emoji-based progress"""
        progress = max(0, min(100, progress))
        
        if progress == 100:
            return "●●●●●●●● 100%"
        elif progress >= 87:
            return "●●●●●●●○ 87%"
        elif progress >= 75:
            return "●●●●●●○○ 75%"
        elif progress >= 62:
            return "●●●●●○○○ 62%"
        elif progress >= 50:
            return "●●●●○○○○ 50%"
        elif progress >= 37:
            return "●●●○○○○○ 37%"
        elif progress >= 25:
            return "●●○○○○○○ 25%"
        elif progress >= 12:
            return "●○○○○○○○ 12%"
        else:
            return "○○○○○○○○ 0%"
    
    @staticmethod
    def render_detailed(progress: int, label: str = "Прогрес") -> str:
        """Render detailed progress with label"""
        bar = ProgressBar.render(progress)
        return f"<b>{label}:</b> {bar}"
    
    @staticmethod
    def render_steps(current: int, total: int) -> str:
        """Render step-based progress"""
        filled = min(current, total)
        empty = max(0, total - current)
        bar = "●" * filled + "○" * empty
        return f"{bar} ({current}/{total})"


class InlineSearchBuilder:
    """Builder for inline search functionality"""
    
    @staticmethod
    def build_search_button(callback_data: str, placeholder: str = "Пошук...") -> InlineKeyboardButton:
        """Create a search button that triggers switch_inline_query"""
        return InlineKeyboardButton(
            text=f"🔍 {placeholder}",
            switch_inline_query_current_chat=""
        )
    
    @staticmethod
    def filter_items(items: List[Any], query: str, key_func: Callable[[Any], str]) -> List[Any]:
        """Filter items by search query"""
        if not query:
            return items
        
        query_lower = query.lower()
        return [item for item in items if query_lower in key_func(item).lower()]


class MenuBuilder:
    """Helper to build consistent menus"""
    
    @staticmethod
    def build_grid(
        buttons: List[tuple], 
        columns: int = 2, 
        back_callback: str = "back_to_menu"
    ) -> InlineKeyboardMarkup:
        """Build a grid layout from (text, callback) tuples"""
        keyboard = []
        row = []
        
        for text, callback in buttons:
            row.append(InlineKeyboardButton(text=text, callback_data=callback))
            if len(row) >= columns:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def build_list(
        items: List[Any],
        format_func: Callable[[Any], tuple],
        page: int = 1,
        per_page: int = 10,
        callback_prefix: str = "item",
        back_callback: str = "back_to_menu"
    ) -> InlineKeyboardMarkup:
        """Build a paginated list menu"""
        paginator = Paginator(items, page, per_page, f"{callback_prefix}_page")
        
        keyboard = []
        for item in paginator.current_items:
            text, callback = format_func(item)
            keyboard.append([InlineKeyboardButton(text=text, callback_data=callback)])
        
        if paginator.total_pages > 1:
            keyboard.append(paginator.get_nav_buttons())
        
        keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_divider() -> str:
    """Generate consistent divider - 15 chars single line"""
    return DIVIDER


class UniversalPaginator(Paginator):
    """Extended paginator with support for different view types"""
    
    def __init__(
        self,
        items: List[Any],
        view_type: str,
        page: int = 1,
        per_page: int = 10,
        item_formatter: Optional[Callable[[Any, int], tuple]] = None
    ):
        callback_prefix = f"{view_type}_page"
        super().__init__(items, page, per_page, callback_prefix)
        self.view_type = view_type
        self.item_formatter = item_formatter or self._default_formatter
    
    def _default_formatter(self, item: Any, index: int) -> tuple:
        """Default item formatter, returns (text, callback_data)"""
        if hasattr(item, 'name'):
            name = getattr(item, 'name', 'Item')
        elif isinstance(item, dict) and 'name' in item:
            name = item.get('name', 'Item')
        else:
            name = str(item)
        
        if hasattr(item, 'id'):
            item_id = getattr(item, 'id')
        elif isinstance(item, dict) and 'id' in item:
            item_id = item.get('id', index)
        else:
            item_id = index
        
        return (str(name)[:30], f"{self.view_type}_view_{item_id}")
    
    def get_item_buttons(self) -> List[List[InlineKeyboardButton]]:
        """Get buttons for items on current page"""
        buttons = []
        for i, item in enumerate(self.current_items):
            global_index = (self.page - 1) * self.per_page + i
            text, callback = self.item_formatter(item, global_index)
            buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])
        return buttons
    
    def build_keyboard(
        self,
        back_callback: str = "back_to_menu",
        extra_buttons: Optional[List[List[InlineKeyboardButton]]] = None
    ) -> InlineKeyboardMarkup:
        """Build complete keyboard with pagination"""
        buttons = self.get_item_buttons()
        
        if self.total_pages > 1:
            buttons.append(self.get_nav_buttons())
        
        if extra_buttons:
            buttons.extend(extra_buttons)
        
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


class StatusIndicator:
    """Status indicators for various states"""
    
    ICONS = {
        "online": "🟢",
        "offline": "⚪",
        "busy": "🟡",
        "error": "🔴",
        "warning": "🟠",
        "success": "✅",
        "pending": "⏳",
        "active": "🔵",
        "paused": "⏸",
    }
    
    @staticmethod
    def get(status: str, with_text: bool = False) -> str:
        """Get status icon, optionally with text"""
        icon = StatusIndicator.ICONS.get(status.lower(), "⚪")
        if with_text:
            return f"{icon} {status.capitalize()}"
        return icon
    
    @staticmethod
    def health(value: int) -> str:
        """Get health indicator based on percentage"""
        if value >= 80:
            return "🟢"
        elif value >= 50:
            return "🟡"
        elif value >= 20:
            return "🟠"
        else:
            return "🔴"
    
    @staticmethod
    def trend(current: float, previous: float) -> str:
        """Get trend indicator"""
        if current > previous:
            return "📈"
        elif current < previous:
            return "📉"
        else:
            return "➡️"
