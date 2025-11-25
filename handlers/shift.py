from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event

router = Router()

# in-memory storage for shifts
USER_SHIFT = {}


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(F.text == "Начать смену")
async def start_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    user_state = USER_SHIFT.get(uid)
    if user_state and user_state.get("status") == "active":
        await message.answer(t.get("shift_already_started", "Смена уже начата."), reply_markup=main_menu(t))
        return

    now = datetime.utcnow().isoformat() + "Z"
    USER_SHIFT[uid] = {"status": "active", "start_at": now}

    payload = {
        "user_id": uid,
        "action": "start_shift",
        "start_at": now
    }
    try:
        await send_event("shift", payload)
    except Exception:
        # если бэкенд недоступен — все равно сохраняем локально и уведомляем
        await message.answer(t.get("shift_started_offline", "Смена начата (локально). Бэкенд недоступен."), reply_markup=main_menu(t))
        return

    await message.answer(t.get("shift_started", "Смена началась."), reply_markup=main_menu(t))


@router.message(F.text == "Закрыть смену")
async def end_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    user_state = USER_SHIFT.get(uid)
    if not user_state or user_state.get("status") != "active":
        await message.answer(t.get("shift_not_started", "Нельзя закрыть смену — она ещё не начата."), reply_markup=main_menu(t))
        return

    now = datetime.utcnow().isoformat() + "Z"
    USER_SHIFT[uid]["status"] = "inactive"
    USER_SHIFT[uid]["end_at"] = now

    payload = {
        "user_id": uid,
        "action": "end_shift",
        "start_at": USER_SHIFT[uid].get("start_at"),
        "end_at": now
    }

    try:
        await send_event("shift", payload)
    except Exception:
        await message.answer(t.get("shift_closed_offline", "Смена закрыта (локально). Бэкенд недоступен."), reply_markup=main_menu(t))
        return

    await message.answer(t.get("shift_closed", "Смена закрыта."), reply_markup=main_menu(t))


@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)
    await state.clear()
    await message.answer(t.get("menu", "Главное меню"), reply_markup=main_menu(t))
