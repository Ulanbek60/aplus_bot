from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from locales.i18n import USER_LANG, MESSAGES
from keyboards import request_phone_keyboard, main_menu
from services.backend_client import send_event

router = Router()


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


# Проверка, авторизован ли пользователь
def is_authorized(uid: int):
    from data.users import AUTH_USERS
    return uid in AUTH_USERS


@router.message(F.contact)
async def auth_receive_phone(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    phone = message.contact.phone_number

    payload = {
        "user_id": uid,
        "phone": phone
    }

    try:
        resp = await send_event("auth", payload)
    except:
        await message.answer(t['backend_error'])
        return

    # backend должен вернуть что-то типа { "authorized": true/false }
    if not resp or not resp.get("authorized"):
        await message.answer(t["auth_denied"])
        return

    # сохраняем авторизацию локально
    from data.users import AUTH_USERS
    AUTH_USERS[uid] = {"phone": phone}

    await message.answer(
        t["auth_success"],
        reply_markup=main_menu(t)
    )
