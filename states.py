from aiogram.fsm.state import State, StatesGroup

class FuelStates(StatesGroup):
    waiting_photo = State()
    waiting_liters = State()

class IssueStates(StatesGroup):
    waiting_description = State()
    waiting_photo = State()
