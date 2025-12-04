# handlers/start.py

import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from services.user_service import user_service
from keyboards import language_keyboard, main_menu
from locales.i18n import USER_LANG, MESSAGES
from states import FullRegistrationStates

router = Router()


def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


async def wait_for_approval(bot, uid):
    while True:
        status, profile = await user_service.get_profile(uid)

        if status == 200 and profile.get("status") == "active":
            USER_LANG[uid] = profile.get("language", "ru")

            await bot.send_message(uid, t(uid, "vehicle_approved"))
            await bot.send_message(uid, t(uid, "menu"), reply_markup=main_menu(MESSAGES[USER_LANG[uid]]))
            break

        await asyncio.sleep(10)


@router.message(CommandStart())
async def smart_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    status, profile = await user_service.get_profile(uid)

    if status == 404 or not profile or profile.get("status") == "registration":
        await state.set_state(FullRegistrationStates.waiting_language)
        await message.answer(t(uid, "choose_language"), reply_markup=language_keyboard())
        return

    USER_LANG[uid] = profile.get("language", "ru")
    lang_pack = MESSAGES[USER_LANG[uid]]

    role = profile.get("role")
    u_status = profile.get("status")

    if role == "driver" and u_status == "pending_vehicle":
        await message.answer(t(uid, "pending_vehicle"))
        asyncio.create_task(wait_for_approval(message.bot, uid))
        return

    if role == "driver" and u_status == "active":
        await message.answer(lang_pack["menu"], reply_markup=main_menu(lang_pack))
        return

    if role == "mechanic" and u_status == "active":
        await message.answer(t(uid, "mechanic_menu"))
        return

    await message.answer(t(uid, "profile_issue"))
