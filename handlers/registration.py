# handlers/registration.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from locales.i18n import USER_LANG, MESSAGES, get_text
from keyboards import request_phone_keyboard, main_menu
from services.user_service import user_service
from services.api_client import backend_api
from states import RegistrationStates

router = Router()

def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]

# Контакт (телефон) принимаем через request_contact клавиатуру
@router.message(F.contact, RegistrationStates.waiting_phone)
async def reg_receive_phone(message: Message, state: FSMContext):
    uid = message.from_user.id
    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    await state.set_state(RegistrationStates.waiting_name)
    await message.answer("Напиши своё имя (латиницей/кириллицей как удобно).", reply_markup=main_menu(t(uid)))

@router.message(RegistrationStates.waiting_phone)
async def reg_no_contact(message: Message, state: FSMContext):
    await message.answer("Нужно отправить контакт (кнопка).", reply_markup=main_menu(t(message.from_user.id)))

@router.message(RegistrationStates.waiting_name)
async def reg_receive_name(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Имя не может быть пустым.")
        return
    await state.update_data(name=text)
    await state.set_state(RegistrationStates.waiting_surname)
    await message.answer("Напиши фамилию.", reply_markup=main_menu(t(message.from_user.id)))

@router.message(RegistrationStates.waiting_surname)
async def reg_receive_surname(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    name = data.get("name")
    phone = data.get("phone")
    if not text or not name or not phone:
        await message.answer("Ошибка данных регистрации. Попробуй /start ещё раз.")
        await state.clear()
        return

    await state.update_data(surname=text)

    uid = message.from_user.id
    lang = USER_LANG.get(uid, "ru")

    # Отправляем на бэкенд регистрацию
    status, resp = await user_service.register_user(uid, phone, name, text, lang)
    if status is None:
        await message.answer("Сервер недоступен — не получилось зарегистрироваться. Попробуйте позже.")
        await state.clear()
        return

    if status >= 400:
        # backend вернул ошибку
        await message.answer(f"Ошибка регистрации: {resp}")
        await state.clear()
        return

    # Успех — backend отвечает данными профиля или статусом registration
    await message.answer("Регистрация отправлена. Сейчас предложу выбрать технику.", reply_markup=main_menu(t(uid)))

    # Теперь получаем список техники
    v_status, vehicles = await backend_api.get("/api/vehicles/list/")
    if v_status is None or vehicles is None:
        await message.answer("Не удалось получить список техники. Позже попробуйте /start.")
        await state.clear()
        return

    # Сделаем инлайн-кнопки с машинами (покажем первые 20)
    kb = InlineKeyboardMarkup(row_width=1)
    for v in vehicles[:20]:
        kb.add(InlineKeyboardButton(text=f"{v.get('name')} ({v.get('type')})", callback_data=f"select_vehicle:{v.get('id')}"))

    await state.set_state(RegistrationStates.waiting_vehicle)
    await message.answer("Выбери технику, которую хочешь привязать:", reply_markup=kb)

@router.callback_query(lambda c: c.data and c.data.startswith("select_vehicle:"), RegistrationStates.waiting_vehicle)
async def reg_select_vehicle(query: CallbackQuery, state: FSMContext):
    await query.answer()
    uid = query.from_user.id
    _, veh_id = query.data.split(":", 1)
    try:
        veh_id = int(veh_id)
    except:
        await query.message.edit_text("Неверный id техники.")
        await state.clear()
        return

    status, resp = await user_service.request_vehicle(uid, veh_id)
    if status is None:
        await query.message.answer("Сервер недоступен, заявка не отправлена.")
        await state.clear()
        return

    if status >= 400:
        await query.message.answer("Ошибка сервера при отправке заявки.")
        await state.clear()
        return

    await query.message.edit_text("Заявка на привязку техники отправлена. Ждите подтверждения администратора.")
    await state.clear()

# Cancel (локально для регистрации) — если хочешь общий cancel, см. ниже
@router.message(F.text == "Отмена")
async def reg_cancel(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    await message.answer(get_text(uid, "menu"), reply_markup=main_menu(MESSAGES[USER_LANG.get(uid, "ru")]))
