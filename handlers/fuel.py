from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import FuelStates
from keyboards import main_menu
from locales.i18n import USER_LANG, MESSAGES
from services.backend_client import send_event
import logging

router = Router()
logger = logging.getLogger(__name__)


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


def is_fuel_button(text: str) -> bool:
    """Проверяет, является ли текст кнопкой заправки на любом языке"""
    return text in ["Заправка", "Толтуруу (Заправка)"]


@router.message(lambda m: is_fuel_button(m.text) if m.text else False)
async def fuel_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    await state.set_state(FuelStates.waiting_photo)
    await message.answer(t["ask_fuel_photo"])

    logger.info(f"User {uid} started fuel report")


@router.message(F.photo, FuelStates.waiting_photo)
async def fuel_receive_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)

    await state.set_state(FuelStates.waiting_liters)
    await message.answer(t["ask_fuel_liters"])

    logger.info(f"User {uid} uploaded fuel photo")


@router.message(FuelStates.waiting_photo)
async def fuel_no_photo(message: Message, state: FSMContext):
    """Если прислали НЕ фото"""
    uid = message.from_user.id
    t = get_t(uid)

    await message.answer(
        t.get("fuel_photo_required", "Нужно отправить фото чека. Попробуй ещё раз."),
        reply_markup=main_menu(t)
    )


@router.message(F.text.regexp(r"^\d+(?:[.,]\d+)?$"), FuelStates.waiting_liters)
async def fuel_receive_liters(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    liters = float(message.text.replace(",", "."))

    # Валидация литров
    if liters <= 0 or liters > 500:
        await message.answer(
            t.get("fuel_invalid_amount", "Некорректное количество литров (1–500)."),
            reply_markup=main_menu(t)
        )
        return

    user_data = await state.get_data()
    payload = {
        "user_id": uid,
        "liters": liters,
        "photo_file_id": user_data.get("photo_id"),
    }

    try:
        await send_event("fuel", payload)
        logger.info(f"User {uid} reported {liters}L fuel")
    except Exception as e:
        logger.error(f"Backend error for user {uid}: {e}")

        await message.answer(
            t.get("backend_error", "Сервер недоступен. Попробуйте позже."),
            reply_markup=main_menu(t)
        )
        await state.clear()
        return

    await message.answer(
        t["saved"],
        reply_markup=main_menu(t)
    )
    await state.clear()


@router.message(FuelStates.waiting_liters)
async def fuel_invalid_liters(message: Message, state: FSMContext):
    """Если прислали не число"""
    uid = message.from_user.id
    t = get_t(uid)

    await message.answer(
        t.get("fuel_need_number", "Нужно написать число (например: 25 или 25.5)"),
        reply_markup=main_menu(t)
    )
