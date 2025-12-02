from aiogram import Router, F
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


# --------------------------------------------------------
# УМНЫЙ /start — главный вход во всю систему
# --------------------------------------------------------
@router.message(F.text == "/start")
async def smart_start(message: Message, state: FSMContext):
    await state.clear()

    uid = message.from_user.id

    # запросим профиль с backend
    status, data = await user_service.get_profile(uid)

    # --------------------------------------------------------
    # USER НЕ НАЙДЕН — НУЖНО ЗАПУСКАТЬ РЕГИСТРАЦИЮ
    # --------------------------------------------------------
    if status == 404 or data.get("status") == "registration":
        USER_LANG[uid] = "ru"

        await state.set_state(RegistrationStates.waiting_phone)

        await message.answer(
            t(uid)["start"],
            reply_markup=language_keyboard()
        )

        await message.answer(
            t(uid)["auth_ask_phone"],
            reply_markup=request_phone_keyboard(t(uid))
        )
        return

    # --------------------------------------------------------
    # USER НАЙДЕН — ЧИТАЕМ ЯЗЫК
    # --------------------------------------------------------
    if data.get("language"):
        USER_LANG[uid] = data["language"]

    lang_pack = t(uid)

    user_status = data.get("status")
    role = data.get("role")

    # --------------------------------------------------------
    # ВОДИТЕЛЬ ЖДЁТ ПОДТВЕРЖДЕНИЯ ТЕХНИКИ
    # --------------------------------------------------------
    if user_status == "pending_vehicle":
        await message.answer(
            "Ваша заявка на привязку техники находится на рассмотрении.\n"
            "Ожидайте подтверждения администратора."
        )
        return

    # --------------------------------------------------------
    # ВОДИТЕЛЬ АКТИВЕН → показываем главное меню
    # --------------------------------------------------------
    if role == "driver" and user_status == "active":
        await message.answer(
            lang_pack["menu"],
            reply_markup=main_menu(lang_pack)
        )
        return

    # --------------------------------------------------------
    # МЕХАНИК — своё меню (добавим позже)
    # --------------------------------------------------------
    if role == "mechanic":
        await message.answer("Меню механика будет тут. (В разработке)")
        return

    # --------------------------------------------------------
    # НЕОПРЕДЕЛЁННОЕ СОСТОЯНИЕ — fallback
    # --------------------------------------------------------
    await message.answer("Профиль в неопределённом состоянии. Свяжитесь с админом.")
