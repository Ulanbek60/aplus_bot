from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.user_service import user_service
from keyboards import language_keyboard, request_phone_keyboard, main_menu
from locales.i18n import USER_LANG, MESSAGES
from states import RegistrationStates

router = Router()


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(CommandStart())
async def smart_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    # пробуем получить профиль
    status, data = await user_service.get_profile(uid)

    if status == 404 or data.get("status") == "registration":
        await state.set_state(RegistrationStates.waiting_language)

        await message.answer(
            "Выберите язык / Тилди тандаңыз:",
            reply_markup=language_keyboard()
        )
        return

    # если есть язык, сохраняем
    USER_LANG[uid] = data.get("language", "ru")
    lang_pack = t(uid)

    role = data.get("role")
    user_status = data.get("status")

    if user_status == "pending_vehicle":
        await message.answer("Ваша заявка на подтверждении у администратора.")
        return

    if role == "driver" and user_status == "active":
        await message.answer(
            lang_pack["menu"],
            reply_markup=main_menu(lang_pack)
        )
        return

    await message.answer("Ваш профиль в неопределённом состоянии. Свяжитесь с админом.")
