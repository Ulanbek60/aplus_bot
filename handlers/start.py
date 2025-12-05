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
from services.state import PENDING_USERS

router = Router()


def lang_pack(uid):
    """Безопасно возвращает языковой пакет"""
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


def t(uid, key):
    """Удобная функция для текста"""
    return lang_pack(uid)[key]


async def wait_for_approval(bot, uid):
    """Фоновая проверка, когда админ подтвердит технику"""
    while True:
        status, profile = await user_service.get_profile(uid)

        if status == 200 and profile.get("status") == "active":
            USER_LANG[uid] = profile.get("language", "ru")

            lp = lang_pack(uid)

            await bot.send_message(uid, lp["vehicle_approved"])
            await bot.send_message(uid, lp["menu"], reply_markup=main_menu(lp))

            break

        await asyncio.sleep(10)


@router.message(CommandStart())
async def smart_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    # Пробуем получить профиль пользователя
    status, profile = await user_service.get_profile(uid)

    # Если профиль отсутствует или на регистрации → отправляем на регистрацию
    if status == 404 or not profile or profile.get("status") == "registration":
        USER_LANG[uid] = "ru"  # пока временно ставим ru
        await state.set_state(FullRegistrationStates.waiting_language)
        await message.answer(
            MESSAGES["ru"]["choose_language"],
            reply_markup=language_keyboard()
        )
        return

    # Восстанавливаем язык
    USER_LANG[uid] = profile.get("language", "ru")
    lp = lang_pack(uid)

    role = profile.get("role")
    u_status = profile.get("status")

    # Ожидает подтверждения техники
    if role == "driver" and u_status == "pending_vehicle":
        PENDING_USERS.add(uid)
        await message.answer(lp["pending_vehicle"])
        return

    # Активный водитель
    if role == "driver" and u_status == "active":
        await message.answer(lp["menu"], reply_markup=main_menu(lp))
        return

    # Активный механик
    if role == "mechanic" and u_status == "active":
        await message.answer(lp["mechanic_menu"])
        return

    # Неизвестный статус
    await message.answer(lp["profile_issue"])
