from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from helpers.buttons import btn_match
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event
from states import FuelStates

router = Router()

def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


# Запуск заправки
@router.message(lambda m: btn_match(m.text, ["заправ", "толтуруу"]))
async def fuel_start(message: Message, state: FSMContext):
    uid = message.from_user.id

    await state.set_state(FuelStates.waiting_photo)
    await message.answer(t(uid, "ask_fuel_photo"))


@router.message(F.photo, FuelStates.waiting_photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)

    uid = message.from_user.id
    await state.set_state(FuelStates.waiting_liters)
    await message.answer(t(uid, "ask_fuel_liters"))


@router.message(FuelStates.waiting_photo)
async def wrong_photo(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "fuel_photo_required"))


@router.message(F.text, FuelStates.waiting_liters)
async def get_liters(message: Message, state: FSMContext):
    uid = message.from_user.id
    text = message.text.replace(",", ".")

    if not text.replace(".", "").isdigit():
        await message.answer(t(uid, "fuel_need_number"))
        return

    liters = float(text)
    if liters <= 0 or liters > 500:
        await message.answer(t(uid, "fuel_invalid_amount"))
        return

    data = await state.get_data()
    payload = {
        "user_id": uid,
        "liters": liters,
        "photo_file_id": data.get("photo")
    }

    await send_event("fuel", payload)
    lang = USER_LANG.get(uid, "ru")
    await message.answer(t(uid, "saved"), reply_markup=main_menu(MESSAGES[lang]))
    await state.clear()
