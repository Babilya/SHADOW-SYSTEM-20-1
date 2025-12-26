from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class NavigationStates(StatesGroup):
    main_menu = State()
    botnet = State()
    osint = State()
    campaigns = State()
    analytics = State()
    settings = State()
    team = State()
    funnels = State()
    funnel_edit = State()
    admin_panel = State()
    profile = State()
    help = State()
    subscription = State()

class NavigationManager:
    @staticmethod
    async def push_state(state: FSMContext, new_state: str, menu_name: str):
        data = await state.get_data()
        history: List[dict] = data.get("nav_history", [])
        current = data.get("current_menu")
        if current:
            history.append({"state": current, "menu": data.get("current_menu_name", "main")})
        await state.update_data(
            nav_history=history,
            current_menu=new_state,
            current_menu_name=menu_name
        )
    
    @staticmethod
    async def pop_state(state: FSMContext) -> Optional[dict]:
        data = await state.get_data()
        history: List[dict] = data.get("nav_history", [])
        if history:
            prev = history.pop()
            await state.update_data(
                nav_history=history,
                current_menu=prev.get("state", "main"),
                current_menu_name=prev.get("menu", "main")
            )
            return prev
        await state.update_data(current_menu="main", current_menu_name="main")
        return {"state": "main", "menu": "main"}
    
    @staticmethod
    async def get_current(state: FSMContext) -> str:
        data = await state.get_data()
        return data.get("current_menu", "main")
    
    @staticmethod
    async def reset(state: FSMContext):
        await state.update_data(nav_history=[], current_menu="main", current_menu_name="main")
    
    @staticmethod
    async def go_to_main(state: FSMContext):
        await state.update_data(nav_history=[], current_menu="main", current_menu_name="main")

nav_manager = NavigationManager()
