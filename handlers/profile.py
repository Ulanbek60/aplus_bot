# handlers/profile.py
from aiogram import Router
from aiogram.types import Message

from services.api_client import backend_api
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu

router = Router()


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(lambda m: m.text.lower() in ["профиль", "profile", "профильим", "профильим"])  # KG можно добавить ещё
async def profile_handler(message: Message):
    uid = message.from_user.id
    lang_pack = t(uid)

    status, profile = await backend_api.get_profile(uid)

    if status != 200 or not profile:
        await message.answer(lang_pack["backend_error"])
        await message.answer(lang_pack["menu"], reply_markup=main_menu(lang_pack))
        return

    # Получаем локализованные поля
    name = profile.get("name", "—")
    surname = profile.get("surname", "")
    phone = profile.get("phone", "—")
    role = profile.get("role", "driver")
    status_text = profile.get("status", "—")

    vehicle_id = profile.get("vehicle_id")
    vehicle_text = vehicle_id if vehicle_id else lang_pack.get("vehicle_none", "Не прикреплено")

    # Локализованный текст
    msg = (
        f"<b>{lang_pack['profile_title']}</b>\n"
        f"{lang_pack['profile_name']}: <b>{name} {surname}</b>\n"
        f"{lang_pack['profile_phone']}: <b>{phone}</b>\n"
        f"{lang_pack['profile_role']}: <b>{role}</b>\n"
        f"{lang_pack['profile_status']}: <b>{status_text}</b>\n"
        f"{lang_pack['profile_vehicle']}: <b>{vehicle_text}</b>"
    )

    await message.answer(msg, parse_mode="HTML", reply_markup=main_menu(lang_pack))
