from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import RegistrationStates
from locales.i18n import USER_LANG, MESSAGES
from keyboards import request_phone_keyboard, language_keyboard, main_menu

from services.user_service import user_service
from services.vehicle_service import vehicle_service

router = Router()


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


# -----------------------------
# /start
# -----------------------------
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    USER_LANG[uid] = "ru"

    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer(
        t(uid)["start"],
        reply_markup=language_keyboard()
    )
    await message.answer(
        t(uid)["auth_ask_phone"],
        reply_markup=request_phone_keyboard(t(uid))
    )


# -----------------------------
# Выбор языка
# -----------------------------
@router.message(lambda m: m.text in ["Русский", "Кыргызча"])
async def choose_lang(message: Message, state: FSMContext):
    lang = "ru" if message.text == "Русский" else "kg"
    USER_LANG[message.from_user.id] = lang

    await message.answer(
        MESSAGES[lang]["auth_ask_phone"],
        reply_markup=request_phone_keyboard(MESSAGES[lang])
    )


# -----------------------------
# Получаем телефон → имя
# -----------------------------
@router.message(F.contact, RegistrationStates.waiting_phone)
async def reg_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    await state.set_state(RegistrationStates.waiting_name)
    await message.answer("Введите ваше имя:")


# -----------------------------
# Получаем имя → фамилия
# -----------------------------
@router.message(RegistrationStates.waiting_name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    await state.set_state(RegistrationStates.waiting_surname)
    await message.answer("Введите вашу фамилию:")


# -----------------------------
# Получаем фамилию → backend register
# -----------------------------
@router.message(RegistrationStates.waiting_surname)
async def reg_surname(message: Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()

    name = data["name"]
    phone = data["phone"]
    surname = message.text.strip()
    language = USER_LANG[uid]

    status, resp = await user_service.register_user(
        telegram_id=uid,
        phone=phone,
        name=name,
        surname=surname,
        language=language
    )

    if status != 200:
        await message.answer(t(uid)["backend_error"])
        return

    await message.answer("Регистрация успешна.\nВыберите технику:")

    await send_vehicle_keyboard(message)


# -----------------------------
# Показываем список техники
# -----------------------------
async def send_vehicle_keyboard(message: Message):
    uid = message.from_user.id
    status, vehicles = await vehicle_service.get_vehicle_list()

    if status != 200:
        await message.answer(t(uid)["backend_error"])
        return

    kb = InlineKeyboardBuilder()

    for v in vehicles:
        kb.button(text=v["name"], callback_data=f"veh:{v['id']}")

    kb.adjust(1)

    await message.answer("👇 Выберите технику:", reply_markup=kb.as_markup())


# -----------------------------
# Пользователь выбрал технику
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("veh:"))
async def vehicle_selected(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    vehicle_id = callback.data.split(":")[1]

    status, resp = await user_service.request_vehicle(uid, vehicle_id)

    if status != 200:
        await callback.message.answer(t(uid)["backend_error"])
        return

    await callback.message.answer(
        "Ваша заявка отправлена администратору.\nОжидайте подтверждения."
    )

    await state.clear()
