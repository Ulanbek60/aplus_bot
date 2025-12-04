# handlers/registration.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from dateutil.parser import parse as date_parse

from states import FullRegistrationStates
from locales.i18n import USER_LANG, MESSAGES
from services.user_service import user_service
from services.vehicle_service import vehicle_service

router = Router()

# перевод российских типов
TRANSLATE_VEHICLE_RU = {
    "Lorry": "Грузовик",
    "Excavator": "Экскаватор",
    "Pump": "Насос",
}

TRANSLATE_VEHICLE_KG = {
    "Lorry": "Жүк ташуучу",
    "Excavator": "Экскаватор",
    "Pump": "Насос",
}

REVERSE_RU = {v: k for k, v in TRANSLATE_VEHICLE_RU.items()}
REVERSE_KG = {v: k for k, v in TRANSLATE_VEHICLE_KG.items()}


def normalize_phone(p: str) -> str | None:
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


def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


# ==========================
# 1. ЯЗЫК
# ==========================

@router.message(FullRegistrationStates.waiting_language)
async def choose_language(message: Message, state: FSMContext):
    lang = message.text.lower()

    if lang not in ("ru", "kg"):
        await message.answer("Пожалуйста, выберите язык кнопками.")
        return

    USER_LANG[message.from_user.id] = lang
    await state.update_data(language=lang)

    await state.set_state(FullRegistrationStates.waiting_name)
    await message.answer(t(message.from_user.id, "reg_name"))


# ==========================
# 2. ИМЯ
# ==========================

@router.message(FullRegistrationStates.waiting_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(FullRegistrationStates.waiting_surname)

    await message.answer(t(message.from_user.id, "reg_surname"))


# ==========================
# 3. ФАМИЛИЯ
# ==========================

@router.message(FullRegistrationStates.waiting_surname)
async def reg_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.strip())
    await state.set_state(FullRegistrationStates.waiting_birthdate)

    await message.answer(t(message.from_user.id, "reg_birthdate"))


# ==========================
# 4. ДАТА РОЖДЕНИЯ
# ==========================

@router.message(FullRegistrationStates.waiting_birthdate)
async def reg_birthdate(message: Message, state: FSMContext):
    try:
        d = date_parse(message.text.strip(), dayfirst=True)
    except Exception:
        await message.answer(t(message.from_user.id, "reg_birthdate"))
        return

    await state.update_data(birthdate=d.strftime("%Y-%m-%d"))
    await state.set_state(FullRegistrationStates.waiting_phone)

    await message.answer(t(message.from_user.id, "reg_phone"))


# ==========================
# 5. ТЕЛЕФОН
# ==========================

@router.message(FullRegistrationStates.waiting_phone)
async def reg_phone(message: Message, state: FSMContext):
    phone = normalize_phone(message.text.strip())

    if not phone:
        await message.answer("Неверный номер. Примеры: +996777150112 / 0777150112 / 777150112")
        return

    await state.update_data(phone=phone)
    await state.set_state(FullRegistrationStates.waiting_passport_id)

    await message.answer(t(message.from_user.id, "reg_passport_id"))


# ==========================
# 6. ПАСПОРТ ID
# ==========================

@router.message(FullRegistrationStates.waiting_passport_id)
async def reg_passport_id(message: Message, state: FSMContext):
    pid = message.text.strip().upper()

    if not (pid[:2].isalpha() and pid[2:].isdigit()):
        await message.answer("Пример: ID3562161 / AN3562161")
        return

    await state.update_data(passport_id=pid)
    await state.set_state(FullRegistrationStates.waiting_iin)

    await message.answer(t(message.from_user.id, "reg_iin"))


# ==========================
# 7. ИНН
# ==========================

@router.message(FullRegistrationStates.waiting_iin)
async def reg_iin(message: Message, state: FSMContext):
    iin = message.text.strip()

    if not iin.isdigit() or len(iin) != 14:
        await message.answer("ИНН должен быть ровно 14 цифр.")
        return

    await state.update_data(iin=iin)
    await state.set_state(FullRegistrationStates.waiting_address)

    await message.answer(t(message.from_user.id, "reg_address"))


# ==========================
# 8. АДРЕС
# ==========================

@router.message(FullRegistrationStates.waiting_address)
async def reg_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    await state.set_state(FullRegistrationStates.waiting_passport_front)

    await message.answer(t(message.from_user.id, "reg_passport_front"))


# ==========================
# 9. ПАСПОРТ ПЕРЕД (фото)
# ==========================

@router.message(F.photo, FullRegistrationStates.waiting_passport_front)
async def reg_pass_front(message: Message, state: FSMContext):
    await state.update_data(passport_front=message.photo[-1].file_id)
    await state.set_state(FullRegistrationStates.waiting_passport_back)

    await message.answer(t(message.from_user.id, "reg_passport_back"))


@router.message(FullRegistrationStates.waiting_passport_front)
async def reg_pass_front_wrong(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ==========================
# 10. ПАСПОРТ ЗАД (фото)
# ==========================

@router.message(F.photo, FullRegistrationStates.waiting_passport_back)
async def reg_pass_back(message: Message, state: FSMContext):
    await state.update_data(passport_back=message.photo[-1].file_id)
    await state.set_state(FullRegistrationStates.waiting_license)

    await message.answer(t(message.from_user.id, "reg_license"))


@router.message(FullRegistrationStates.waiting_passport_back)
async def reg_pass_back_wrong(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ==========================
# 11. ВОДИТЕЛЬСКИЕ ПРАВА (фото)
# ==========================

@router.message(F.photo, FullRegistrationStates.waiting_license)
async def reg_license(message: Message, state: FSMContext):
    await state.update_data(driver_license=message.photo[-1].file_id)
    await state.set_state(FullRegistrationStates.waiting_selfie)

    await message.answer(t(message.from_user.id, "reg_selfie"))


@router.message(FullRegistrationStates.waiting_license)
async def reg_license_wrong(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ==========================
# 12. СЕЛФИ (фото) + full_register
# ==========================

@router.message(F.photo, FullRegistrationStates.waiting_selfie)
async def reg_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)

    data = await state.get_data()

    payload = {
        "telegram_id": message.from_user.id,
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
        "role": "driver"
    }

    status, resp = await user_service.full_register(**payload)

    if status != 200:
        await message.answer("Ошибка регистрации.")
        return

    # Загружаем список техники
    status, vehicles = await vehicle_service.get_vehicle_list()
    if status != 200:
        await message.answer("Ошибка загрузки техники.")
        return

    lang = USER_LANG.get(message.from_user.id, "ru")

    # Переводим типы
    translated_types = set()

    for v in vehicles:
        t_raw = v["type"]
        if lang == "kg":
            t_local = TRANSLATE_VEHICLE_KG.get(t_raw, t_raw)
        else:
            t_local = TRANSLATE_VEHICLE_RU.get(t_raw, t_raw)
        translated_types.add(t_local)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in sorted(translated_types)],
        resize_keyboard=True
    )

    await state.update_data(vehicles=vehicles)
    await state.set_state(FullRegistrationStates.waiting_vehicle_type)

    await message.answer(t(message.from_user.id, "reg_vehicle_type"), reply_markup=kb)


@router.message(FullRegistrationStates.waiting_selfie)
async def reg_selfie_wrong(message: Message):
    await message.answer(t(message.from_user.id, "need_photo"))


# ==========================
# 13. ВЫБОР ТИПА ТЕХНИКИ
# ==========================

@router.message(FullRegistrationStates.waiting_vehicle_type)
async def reg_vehicle_type(message: Message, state: FSMContext):
    data = await state.get_data()
    vehicles = data["vehicles"]

    selected_local = message.text.strip()
    lang = USER_LANG.get(message.from_user.id, "ru")

    # обратный перевод
    if lang == "kg":
        selected_raw = REVERSE_KG.get(selected_local, selected_local)
    else:
        selected_raw = REVERSE_RU.get(selected_local, selected_local)

    filtered = [v for v in vehicles if v["type"] == selected_raw]

    if not filtered:
        await message.answer("Такого типа нет.")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=v["name"])] for v in filtered],
        resize_keyboard=True
    )

    await state.update_data(filtered_vehicles=filtered)
    await state.set_state(FullRegistrationStates.waiting_vehicle_select)

    await message.answer(t(message.from_user.id, "vehicle_select"), reply_markup=kb)


# ==========================
# 14. ВЫБОР МОДЕЛИ ТЕХНИКИ
# ==========================

@router.message(FullRegistrationStates.waiting_vehicle_select)
async def reg_vehicle_select(message: Message, state: FSMContext):
    data = await state.get_data()
    vehicles = data["filtered_vehicles"]

    selected_name = message.text.strip()
    found = next((v for v in vehicles if v["name"] == selected_name), None)

    if not found:
        await message.answer("Выберите технику кнопкой.")
        return

    vehicle_id = found["id"]
    telegram_id = message.from_user.id

    status, resp = await user_service.request_vehicle(telegram_id, vehicle_id)

    if status != 200:
        await message.answer("Ошибка отправки заявки.")
        return

    await message.answer(t(message.from_user.id, "pending_vehicle"))
    await state.clear()
