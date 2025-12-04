# handlers/registration.py

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from dateutil.parser import parse as date_parse

from states import FullRegistrationStates
from locales.i18n import USER_LANG, MESSAGES
from services.user_service import user_service
from services.vehicle_service import vehicle_service
from services.state import PENDING_USERS

router = Router()


def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


def vehicle_translate(uid, raw_type):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]["vehicle_types"].get(raw_type, raw_type)


def vehicle_reverse(uid, local_type):
    lang = USER_LANG.get(uid, "ru")
    lookup = MESSAGES[lang]["vehicle_types"]
    for k, v in lookup.items():
        if v == local_type:
            return k
    return local_type


def normalize_phone(p: str):
    p = p.replace(" ", "").replace("-", "")
    if p.startswith("+996") and len(p) == 13:
        return p
    if p.startswith("996") and len(p) == 12:
        return "+" + p
    if p.startswith("0") and len(p) == 10:
        return "+996" + p[1:]
    if len(p) == 9:
        return "+996" + p
    return None


# ============================================================
# ВЫБОР ЯЗЫКА
# ============================================================

@router.message(FullRegistrationStates.waiting_language)
async def reg_language(message: Message, state: FSMContext):
    text = message.text.lower()
    if "рус" in text:
        lang = "ru"
    elif "кырг" in text:
        lang = "kg"
    else:
        await message.answer("Используйте кнопки.")
        return

    USER_LANG[message.from_user.id] = lang
    await state.update_data(language=lang)

    await state.set_state(FullRegistrationStates.waiting_name)
    await message.answer(t(message.from_user.id, "reg_name"), reply_markup=ReplyKeyboardRemove())


# ============================================================
# ИМЯ
# ============================================================

@router.message(FullRegistrationStates.waiting_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    await state.set_state(FullRegistrationStates.waiting_surname)
    await message.answer(t(message.from_user.id, "reg_surname"))


# ============================================================
# ФАМИЛИЯ
# ============================================================

@router.message(FullRegistrationStates.waiting_surname)
async def reg_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.strip())

    await state.set_state(FullRegistrationStates.waiting_birthdate)
    await message.answer(t(message.from_user.id, "reg_birthdate"))


# ============================================================
# ДАТА РОЖДЕНИЯ
# ============================================================

@router.message(FullRegistrationStates.waiting_birthdate)
async def reg_birthdate(message: Message, state: FSMContext):
    try:
        d = date_parse(message.text.strip(), dayfirst=True)
    except Exception:
        await message.answer(t(message.from_user.id, "wrong_birthdate"))
        return

    await state.update_data(birthdate=d.strftime("%Y-%m-%d"))

    await state.set_state(FullRegistrationStates.waiting_phone)
    await message.answer(t(message.from_user.id, "reg_phone"))


# ============================================================
# ТЕЛЕФОН
# ============================================================

@router.message(FullRegistrationStates.waiting_phone)
async def reg_phone(message: Message, state: FSMContext):
    phone = normalize_phone(message.text.strip())
    if not phone:
        await message.answer(t(message.from_user.id, "wrong_phone"))
        return

    await state.update_data(phone=phone)

    await state.set_state(FullRegistrationStates.waiting_passport_id)
    await message.answer(t(message.from_user.id, "reg_passport_id"))


# ============================================================
# ПАСПОРТ ID
# ============================================================

@router.message(FullRegistrationStates.waiting_passport_id)
async def reg_passport(message: Message, state: FSMContext):
    pid = message.text.strip().upper()

    if not (pid[:2].isalpha() and pid[2:].isdigit()):
        await message.answer(t(message.from_user.id, "wrong_passport"))
        return

    await state.update_data(passport_id=pid)

    await state.set_state(FullRegistrationStates.waiting_iin)
    await message.answer(t(message.from_user.id, "reg_iin"))


# ============================================================
# ИНН
# ============================================================

@router.message(FullRegistrationStates.waiting_iin)
async def reg_iin(message: Message, state: FSMContext):
    iin = message.text.strip()

    if not iin.isdigit() or len(iin) != 14:
        await message.answer(t(message.from_user.id, "wrong_iin"))
        return

    await state.update_data(iin=iin)

    await state.set_state(FullRegistrationStates.waiting_address)
    await message.answer(t(message.from_user.id, "reg_address"))


# ============================================================
# АДРЕС
# ============================================================

@router.message(FullRegistrationStates.waiting_address)
async def reg_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())

    await state.set_state(FullRegistrationStates.waiting_passport_front)
    await message.answer(t(message.from_user.id, "reg_passport_front"))


# ============================================================
# ПАСПОРТ ПЕРЕД
# ============================================================

@router.message(F.photo, FullRegistrationStates.waiting_passport_front)
async def reg_passport_front(message: Message, state: FSMContext):
    await state.update_data(passport_front=message.photo[-1].file_id)

    await state.set_state(FullRegistrationStates.waiting_passport_back)
    await message.answer(t(message.from_user.id, "reg_passport_back"))


@router.message(FullRegistrationStates.waiting_passport_front)
async def wrong_front(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ============================================================
# ПАСПОРТ ЗАД
# ============================================================

@router.message(F.photo, FullRegistrationStates.waiting_passport_back)
async def reg_passport_back(message: Message, state: FSMContext):
    await state.update_data(passport_back=message.photo[-1].file_id)

    await state.set_state(FullRegistrationStates.waiting_license)
    await message.answer(t(message.from_user.id, "reg_license"))


@router.message(FullRegistrationStates.waiting_passport_back)
async def wrong_passport_back(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ============================================================
# ВОДИТЕЛЬСКИЕ ПРАВА
# ============================================================

@router.message(F.photo, FullRegistrationStates.waiting_license)
async def reg_license(message: Message, state: FSMContext):
    await state.update_data(driver_license=message.photo[-1].file_id)

    await state.set_state(FullRegistrationStates.waiting_selfie)
    await message.answer(t(message.from_user.id, "reg_selfie"))


@router.message(FullRegistrationStates.waiting_license)
async def wrong_license(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ============================================================
# СЕЛФИ
# ============================================================

@router.message(F.photo, FullRegistrationStates.waiting_selfie)
async def reg_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)

    status, vehicles = await vehicle_service.get_vehicle_list()
    if status != 200:
        await message.answer(t(message.from_user.id, "vehicle_error"))
        return

    uid = message.from_user.id
    translated_types = sorted(
        {vehicle_translate(uid, v["type"]) for v in vehicles}
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=tp)] for tp in translated_types],
        resize_keyboard=True
    )

    await state.update_data(vehicles=vehicles)
    await state.set_state(FullRegistrationStates.waiting_vehicle_type)

    await message.answer(t(uid, "vehicle_type_prompt"), reply_markup=kb)


@router.message(FullRegistrationStates.waiting_selfie)
async def wrong_selfie(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ============================================================
# ВЫБОР ТИПА ТЕХНИКИ
# ============================================================

@router.message(FullRegistrationStates.waiting_vehicle_type)
async def reg_vehicle_type(message: Message, state: FSMContext):
    uid = message.from_user.id
    local_type = message.text.strip()
    raw_type = vehicle_reverse(uid, local_type)

    data = await state.get_data()
    vehicles = data["vehicles"]

    filtered = [v for v in vehicles if v["type"] == raw_type]

    if not filtered:
        await message.answer(t(uid, "vehicle_type_prompt"))
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=v["name"])] for v in filtered],
        resize_keyboard=True
    )

    await state.update_data(filtered_vehicles=filtered)

    await state.set_state(FullRegistrationStates.waiting_vehicle_select)
    await message.answer(t(uid, "vehicle_select_prompt"), reply_markup=kb)


# ============================================================
# ВЫБОР КОНКРЕТНОЙ ТЕХНИКИ (ФИНАЛ + full_register)
# ============================================================

@router.message(FullRegistrationStates.waiting_vehicle_select)
async def reg_vehicle_select(message: Message, state: FSMContext):
    uid = message.from_user.id
    name = message.text.strip()

    data = await state.get_data()
    vehicles = data["filtered_vehicles"]

    found = next((v for v in vehicles if v["name"] == name), None)
    if not found:
        await message.answer(t(uid, "vehicle_select_prompt"))
        return

    payload = {
        "telegram_id": uid,
        "name": data["name"],
        "surname": data["surname"],
        "birthdate": data["birthdate"],
        "phone": data["phone"],
        "passport_id": data["passport_id"],
        "iin": data["iin"],
        "address": data["address"],
        "passport_front": data["passport_front"],
        "passport_back": data["passport_back"],
        "driver_license": data["driver_license"],
        "selfie": data["selfie"],
        "language": data["language"],
        "role": "driver",
        "vehicle_id": found["id"]
    }

    status, resp = await user_service.full_register(**payload)

    if status != 200:
        await message.answer(t(uid, "register_error"))
        return


    PENDING_USERS.add(uid)
    await message.answer(t(uid, "pending_vehicle"), reply_markup=ReplyKeyboardRemove())
    await state.clear()
