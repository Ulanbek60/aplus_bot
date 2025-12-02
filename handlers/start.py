# handlers/start.py (замена функции cmd_start / smart_start)
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import language_keyboard, request_phone_keyboard, main_menu, start_keyboard
from locales.i18n import USER_LANG, get_text, MESSAGES
from services.user_service import user_service
from states import RegistrationStates

router = Router()

@router.message(CommandStart() | F.text == "/start")
async def smart_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id

    # Пробуем получить профиль
    status, data = await user_service.get_profile(uid)

    # backend недоступен
    if status is None and data is None:
        await message.answer("Сервер временно недоступен. Можешь всё равно нажать /start позже.", reply_markup=start_keyboard())
        return

    # если 404 или профиль показывает что нужно регистрация
    if status == 404 or (isinstance(data, dict) and data.get("status") == "registration"):
        USER_LANG[uid] = "ru"
        await state.set_state(RegistrationStates.waiting_phone)
        await message.answer(get_text(uid, "start"), reply_markup=language_keyboard())
        await message.answer(MESSAGES["ru"]["auth_ask_phone"], reply_markup=request_phone_keyboard(MESSAGES["ru"]))
        return

    # найден профиль — вычитываем язык и роль
    if isinstance(data, dict) and data.get("language"):
        USER_LANG[uid] = data["language"]

    lang = USER_LANG.get(uid, "ru")
    lang_pack = MESSAGES[lang]

    user_status = (data or {}).get("status")
    role = (data or {}).get("role")

    if user_status == "pending_vehicle":
        await message.answer("Ваша заявка на привязку техники находится на рассмотрении.\nОжидайте подтверждения администратора.")
        return

    if role == "driver" and user_status == "active":
        await message.answer(lang_pack["menu"], reply_markup=main_menu(lang_pack))
        return

    if role == "mechanic":
        await message.answer("Меню механика будет тут. (В разработке)")
        return

    await message.answer("Профиль в неопределённом состоянии. Свяжитесь с админом.")
