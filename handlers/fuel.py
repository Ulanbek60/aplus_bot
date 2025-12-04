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


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


def is_fuel_button(text, uid):
    lang = USER_LANG.get(uid, "ru")
    return text == MESSAGES[lang]["fuel"]


@router.message(lambda m: is_fuel_button(m.text, m.from_user.id))
async def fuel_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    await state.set_state(FuelStates.waiting_photo)
    await message.answer(lang_pack["ask_fuel_photo"])

    logger.info(f"User {uid} started fuel report")


@router.message(F.photo, FuelStates.waiting_photo)
async def fuel_receive_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)

    await state.set_state(FuelStates.waiting_liters)
    await message.answer(lang_pack["ask_fuel_liters"])

    logger.info(f"User {uid} uploaded fuel photo")


@router.message(FuelStates.waiting_photo)
async def fuel_no_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    await message.answer(lang_pack["fuel_photo_required"], reply_markup=main_menu(lang_pack))


@router.message(F.text.regexp(r"^\d+(?:[.,]\d+)?$"), FuelStates.waiting_liters)
async def fuel_receive_liters(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    liters = float(message.text.replace(",", "."))

    if liters <= 0 or liters > 500:
        await message.answer(lang_pack["fuel_invalid_amount"], reply_markup=main_menu(lang_pack))
        return

    data = await state.get_data()

    payload = {
        "user_id": uid,
        "liters": liters,
        "photo_file_id": data.get("photo_id"),
    }

    try:
        await send_event("fuel", payload)
    except Exception:
        await message.answer(lang_pack["backend_error"], reply_markup=main_menu(lang_pack))
        await state.clear()
        return

    await message.answer(lang_pack["saved"], reply_markup=main_menu(lang_pack))
    await state.clear()


@router.message(FuelStates.waiting_liters)
async def fuel_invalid_liters(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    await message.answer(lang_pack["fuel_need_number"], reply_markup=main_menu(lang_pack))
