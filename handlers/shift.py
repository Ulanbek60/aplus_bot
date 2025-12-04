from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event

router = Router()

USER_SHIFT = {}


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


def is_start_shift(text, uid):
    lang = USER_LANG.get(uid, "ru")
    return text == MESSAGES[lang]["start_shift"]


def is_end_shift(text, uid):
    lang = USER_LANG.get(uid, "ru")
    return text == MESSAGES[lang]["end_shift"]


@router.message(lambda m: is_start_shift(m.text, m.from_user.id))
async def start_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    user_state = USER_SHIFT.get(uid)
    if user_state and user_state.get("status") == "active":
        await message.answer(lang_pack["shift_already_started"], reply_markup=main_menu(lang_pack))
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
        await message.answer(lang_pack["shift_started_offline"], reply_markup=main_menu(lang_pack))
        return

    await message.answer(lang_pack["shift_started"], reply_markup=main_menu(lang_pack))


@router.message(lambda m: is_end_shift(m.text, m.from_user.id))
async def end_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    user_state = USER_SHIFT.get(uid)
    if not user_state or user_state.get("status") != "active":
        await message.answer(lang_pack["shift_not_started"], reply_markup=main_menu(lang_pack))
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
        await message.answer(lang_pack["shift_closed_offline"], reply_markup=main_menu(lang_pack))
        return

    await message.answer(lang_pack["shift_closed"], reply_markup=main_menu(lang_pack))
