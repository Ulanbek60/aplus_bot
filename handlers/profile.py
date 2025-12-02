from aiogram import Router, F
from aiogram.types import Message

from services.api_client import backend_api
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu

router = Router()


def t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(F.text.lower() == "профиль")
@router.message(F.text.lower() == "profile")
async def profile_handler(message: Message):
    uid = message.from_user.id
    text = t(uid)

    resp = await backend_api.get_profile(uid)

    if not resp or resp.get("error"):
        await message.answer(text.get("backend_error", "Сервер недоступен."))

        await message.answer(
            text.get("menu", "Главное меню"),
            reply_markup=main_menu(text)
        )
        return

    # профиль получен
    name = resp.get("name", "—")
    phone = resp.get("phone", "—")
    vehicle = resp.get("vehicle")  # может быть None

    vehicle_text = (
        f"{vehicle.get('name')} (ID {vehicle.get('id')})"
        if vehicle else
        "Не закреплено"
    )

    msg = (
        f"👤 <b>Ваш профиль</b>\n"
        f"Имя: <b>{name}</b>\n"
        f"Телефон: <b>{phone}</b>\n"
        f"Техника: <b>{vehicle_text}</b>"
    )

    await message.answer(
        msg,
        parse_mode="HTML",
        reply_markup=main_menu(text)
    )
