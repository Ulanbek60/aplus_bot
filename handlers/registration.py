from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import RegistrationStates
from locales.i18n import USER_LANG, MESSAGES
from keyboards import request_phone_keyboard, language_keyboard, main_menu
from services.backend_client import send_event
import aiohttp

router = Router()


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


# -----------------------------
# /start → запуск регистрации
# -----------------------------
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    USER_LANG[uid] = "ru"

    t = get_t(uid)

    await state.set_state(RegistrationStates.waiting_phone)

    await message.answer(
        t["start"],
        reply_markup=language_keyboard()
    )

    await message.answer(
        t["auth_ask_phone"],
        reply_markup=request_phone_keyboard(t)
    )


# -----------------------------
# язык выбран
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
# ПОЛУЧАЕМ ТЕЛЕФОН → ИМЯ
# -----------------------------
@router.message(F.contact, RegistrationStates.waiting_phone)
async def reg_phone(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    await state.set_state(RegistrationStates.waiting_name)
    await message.answer("Введите ваше имя:")


# -----------------------------
# ПОЛУЧАЕМ ИМЯ → ФАМИЛИЯ
# -----------------------------
@router.message(RegistrationStates.waiting_name)
async def reg_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)

    await state.set_state(RegistrationStates.waiting_surname)
    await message.answer("Введите вашу фамилию:")


# -----------------------------
# ПОЛУЧАЕМ ФАМИЛИЮ → РЕГИСТРАЦИЯ НА БЭКЕНДЕ
# -----------------------------
@router.message(RegistrationStates.waiting_surname)
async def reg_surname(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    surname = message.text.strip()

    data = await state.get_data()

    payload = {
        "telegram_id": uid,
        "phone": data["phone"],
        "name": data["name"],
        "surname": surname,
        "language": USER_LANG[uid]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/api/users/register/", json=payload) as resp:
            if resp.status != 200:
                await message.answer(t["backend_error"])
                return
            resp_data = await resp.json()

    await message.answer("Регистрация успешна.\nВыберите технику для работы:")

    await send_vehicle_list(message, state)


# -----------------------------
# ПОКАЗЫВАЕМ СПИСОК ТЕХНИКИ — INLINE KEYBOARD
# -----------------------------
async def send_vehicle_list(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/vehicles/list/") as resp:
            if resp.status != 200:
                await message.answer(t["backend_error"])
                return
            vehicles = await resp.json()

    kb = InlineKeyboardBuilder()

    for v in vehicles:
        kb.button(
            text=f"{v['name']}",
            callback_data=f"vehicle:{v['id']}"
        )

    kb.adjust(1)

    await message.answer("👇 Выберите технику:", reply_markup=kb.as_markup())


# -----------------------------
# ВОДИТЕЛЬ ВЫБРАЛ ТЕХНИКУ — ШЛЁМ BACKEND
# -----------------------------
@router.callback_query(lambda c: c.data.startswith("vehicle:"))
async def choose_vehicle(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    t = get_t(uid)

    vehicle_id = callback.data.split(":")[1]

    payload = {
        "telegram_id": uid,
        "vehicle_id": vehicle_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/api/users/request_vehicle/", json=payload) as resp:
            if resp.status != 200:
                await callback.message.answer(t["backend_error"])
                return

    await callback.message.answer(
        "Ваша заявка отправлена администратору.\nОжидайте подтверждения."
    )

    await state.clear()
