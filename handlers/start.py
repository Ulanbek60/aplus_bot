# handlers/start.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from services.user_service import user_service
from keyboards import language_keyboard, main_menu
from locales.i18n import USER_LANG, MESSAGES
from states import FullRegistrationStates

router = Router()


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES.get(lang, MESSAGES["ru"])


@router.message(CommandStart())
async def smart_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    # Получаем профиль
    status, profile = await user_service.get_profile(uid)

    # Если профиля нет — отправляем на регистрацию
    if status == 404 or not profile or profile.get("status") == "registration":
        await state.set_state(FullRegistrationStates.waiting_language)

        await message.answer(
            "Выберите язык / Тилди тандаңыз:",
            reply_markup=language_keyboard()
        )
        return

    # Сохраняем язык
    lang = profile.get("language", "ru")
    USER_LANG[uid] = lang
    text = t(uid)

    role = profile.get("role")
    user_status = profile.get("status")

    # ---------------------
    # ЛОГИКА ДЛЯ ВОДИТЕЛЯ
    # ---------------------

    if role == "driver":

        # Ожидает подтверждения техники
        if user_status == "pending_vehicle":
            await message.answer(
                "Ваша заявка на подтверждении у администратора.\nПожалуйста, ожидайте."
            )
            return

        # Активный водитель → показываем меню
        if user_status == "active":
            await message.answer(
                text["menu"],
                reply_markup=main_menu(text)
            )
            return

    # ---------------------
    # ЛОГИКА ДЛЯ МЕХАНИКА
    # ---------------------

    if role == "mechanic" and user_status == "active":
        await message.answer(
            "Меню механика скоро будет доступно.",
        )
        return

    # ---------------------
    # Если что-то не так
    # ---------------------

    await message.answer("Ваш профиль в неопределённом состоянии. Обратитесь к администратору.")
