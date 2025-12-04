from aiogram.fsm.state import State, StatesGroup

class FuelStates(StatesGroup):
    waiting_photo = State()
    waiting_liters = State()

class IssueStates(StatesGroup):
    waiting_description = State()
    waiting_photo = State()

class FullRegistrationStates(StatesGroup):
    waiting_language = State()

    waiting_name = State()
    waiting_surname = State()
    waiting_birthdate = State()

    waiting_phone = State()
    waiting_passport_id = State()
    waiting_iin = State()
    waiting_address = State()

    waiting_passport_front = State()
    waiting_passport_back = State()
    waiting_license = State()
    waiting_selfie = State()

    waiting_vehicle_type = State()
    waiting_vehicle_select = State()
