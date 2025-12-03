from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import RegistrationStates
from locales.i18n import USER_LANG, MESSAGES
from keyboards import request_phone_keyboard
from services.user_service import user_service

router = Router()


# 1) выбор языка
@router.message(RegistrationStates.waiting_language)
async def choose_language(message: Message, state: FSMContext):
    lang = message.text.lower()

    if lang not in ("ru", "kg", "en"):
        await message.answer("Пожалуйста, выберите язык с кнопок.")
        return

    USER_LANG[message.from_user.id] = lang
    await state.update_data(language=lang)

    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer(
        MESSAGES[lang]["auth_ask_phone"],
        reply_markup=request_phone_keyboard(MESSAGES[lang])
    )


# 2) запрос телефона
@router.message(RegistrationStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("Пожалуйста, используйте кнопку 'Отправить номер'")
        return

    await state.update_data(phone=message.contact.phone_number)
    lang = USER_LANG[message.from_user.id]

    await state.set_state(RegistrationStates.waiting_name)
    await message.answer(MESSAGES[lang]["ask_name"])


# 3) Имя
@router.message(RegistrationStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = USER_LANG[message.from_user.id]

    await state.set_state(RegistrationStates.waiting_surname)
    await message.answer(MESSAGES[lang]["ask_surname"])


# 4) Фамилия → отправка на backend
@router.message(RegistrationStates.waiting_surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    data = await state.get_data()

    telegram_id = message.from_user.id

    status, resp = await user_service.register_user(
        telegram_id=telegram_id,
        phone=data["phone"],
        name=data["name"],
        surname=data["surname"],
        language=data["language"]
    )

    if status != 200:
        await message.answer("Ошибка регистрации. Попробуйте позже.")
        return

    await message.answer("Вы успешно зарегистрированы! Ожидайте подтверждения транспорта.")
    await state.clear()
