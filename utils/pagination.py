from typing import List, Optional, Callable, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math

class Paginator:
    def __init__(
        self,
        items: List[Any],
        page_size: int = 5,
        callback_prefix: str = "page",
        item_callback_prefix: str = "item"
    ):
        self.items = items
        self.page_size = page_size
        self.callback_prefix = callback_prefix
        self.item_callback_prefix = item_callback_prefix
        self.total_pages = max(1, math.ceil(len(items) / page_size))
    
    def get_page(self, page: int = 1) -> List[Any]:
        page = max(1, min(page, self.total_pages))
        start = (page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end]
    
    def get_keyboard(
        self,
        page: int = 1,
        item_text_func: Optional[Callable[[Any], str]] = None,
        item_callback_func: Optional[Callable[[Any], str]] = None,
        extra_buttons: Optional[List[List[InlineKeyboardButton]]] = None,
        back_button: Optional[InlineKeyboardButton] = None
    ) -> InlineKeyboardMarkup:
        page = max(1, min(page, self.total_pages))
        page_items = self.get_page(page)
        
        buttons = []
        
        for item in page_items:
            text = item_text_func(item) if item_text_func else str(item)
            callback = item_callback_func(item) if item_callback_func else f"{self.item_callback_prefix}:{item}"
            buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])
        
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(text="◀️", callback_data=f"{self.callback_prefix}:{page-1}")
            )
        
        nav_buttons.append(
            InlineKeyboardButton(text=f"{page}/{self.total_pages}", callback_data="noop")
        )
        
        if page < self.total_pages:
            nav_buttons.append(
                InlineKeyboardButton(text="▶️", callback_data=f"{self.callback_prefix}:{page+1}")
            )
        
        if len(self.items) > self.page_size:
            buttons.append(nav_buttons)
        
        if extra_buttons:
            buttons.extend(extra_buttons)
        
        if back_button:
            buttons.append([back_button])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


class CallbackDataShortener:
    def __init__(self):
        self._registry: dict = {}
        self._reverse: dict = {}
        self._counter = 0
    
    def shorten(self, full_data: str, max_length: int = 64) -> str:
        if len(full_data) <= max_length:
            return full_data
        
        if full_data in self._reverse:
            return self._reverse[full_data]
        
        self._counter += 1
        short_id = f"s:{self._counter:x}"
        
        self._registry[short_id] = full_data
        self._reverse[full_data] = short_id
        
        return short_id
    
    def expand(self, short_data: str) -> str:
        if short_data.startswith("s:"):
            return self._registry.get(short_data, short_data)
        return short_data
    
    async def save_to_db(self, short_id: str, full_data: str):
        try:
            from database.connection import async_session
            from sqlalchemy import text
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO callback_registry (short_id, full_data, created_at)
                        VALUES (:short_id, :full_data, NOW())
                        ON CONFLICT (short_id) DO NOTHING
                    """),
                    {"short_id": short_id, "full_data": full_data}
                )
                await session.commit()
        except Exception:
            pass
    
    async def load_from_db(self, short_id: str) -> Optional[str]:
        try:
            from database.connection import async_session
            from sqlalchemy import text
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT full_data FROM callback_registry WHERE short_id = :short_id"),
                    {"short_id": short_id}
                )
                row = result.fetchone()
                return row.full_data if row else None
        except Exception:
            return None


paginator_cache: dict = {}
callback_shortener = CallbackDataShortener()


def create_paginated_keyboard(
    items: List[Any],
    page: int = 1,
    page_size: int = 5,
    callback_prefix: str = "page",
    item_text_func: Optional[Callable[[Any], str]] = None,
    item_callback_func: Optional[Callable[[Any], str]] = None,
    back_callback: str = "back"
) -> InlineKeyboardMarkup:
    paginator = Paginator(
        items=items,
        page_size=page_size,
        callback_prefix=callback_prefix
    )
    return paginator.get_keyboard(
        page=page,
        item_text_func=item_text_func,
        item_callback_func=item_callback_func,
        back_button=InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)
    )
