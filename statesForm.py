from aiogram.fsm.state import StatesGroup, State

class File(StatesGroup):
   doc = State()
   groupName = State()