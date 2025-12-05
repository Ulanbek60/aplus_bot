from aiogram import Router, F
from aiogram.types import Message

from services.user_service import user_service
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu

router = Router()


def lang_pack(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(F.text)
async def profile_handler(message: Message):
    uid = message.from_user.id
    lp = lang_pack(uid)

    # Мы ловим только команды профиля
    if message.text.lower() not in ["профиль", "profile", "профильим"]:
        return

    status, resp = await user_service.get_profile(uid)

    if status != 200 or not resp or resp.get("error"):
        await message.answer(lp["backend_error"])
        await message.answer(lp["menu"], reply_markup=main_menu(lp))
        return

    name = resp.get("name", "—")
    phone = resp.get("phone", "—")
    vehicle = resp.get("vehicle_id")

    vehicle_text = vehicle if vehicle else lp["vehicle_none"]

    msg = (
        f"📄 <b>{lp['profile_title']}</b>\n"
        f"{lp['profile_name']}: <b>{name}</b>\n"
        f"{lp['profile_phone']}: <b>{phone}</b>\n"
        f"{lp['profile_vehicle']}: <b>{vehicle_text}</b>"
    )

    await message.answer(
        msg,
        parse_mode="HTML",
        reply_markup=main_menu(lp)
    )
