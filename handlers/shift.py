from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from helpers.buttons import btn_match
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event
from datetime import datetime

router = Router()


def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


# 🍏 НАЧАТЬ СМЕНУ (RU+KG, с эмодзи)
@router.message(lambda m: btn_match(m.text, ["начать", "баштоо"]))
async def start_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = USER_LANG.get(uid, "ru")

    now = datetime.utcnow().isoformat() + "Z"

    payload = {
        "user_id": uid,
        "action": "start_shift",
        "start_at": now
    }

    try:
        await send_event("shift", payload)
        await message.answer(
            t(uid, "shift_started"),
            reply_markup=main_menu(MESSAGES[lang])
        )
    except:
        await message.answer(
            t(uid, "shift_started_offline"),
            reply_markup=main_menu(MESSAGES[lang])
        )


# 🔴 ЗАКРЫТЬ СМЕНУ (RU+KG)
@router.message(lambda m: btn_match(m.text, ["закрыть", "жабуу"]))
async def end_shift(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = USER_LANG.get(uid, "ru")

    now = datetime.utcnow().isoformat() + "Z"

    payload = {
        "user_id": uid,
        "action": "end_shift",
        "end_at": now
    }

    try:
        await send_event("shift", payload)
        await message.answer(
            t(uid, "shift_closed"),
            reply_markup=main_menu(MESSAGES[lang])
        )
    except:
        await message.answer(
            t(uid, "shift_closed_offline"),
            reply_markup=main_menu(MESSAGES[lang])
        )
