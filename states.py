from aiogram.fsm.state import State, StatesGroup

class FuelStates(StatesGroup):
    waiting_photo = State()
    waiting_liters = State()

class IssueStates(StatesGroup):
    waiting_description = State()
    waiting_photo = State()

class RegistrationStates(StatesGroup):
    waiting_phone = State()
    waiting_name = State()
    waiting_surname = State()
    waiting_vehicle = State()

