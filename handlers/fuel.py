from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import FuelStates
from keyboards import main_menu
from locales.i18n import USER_LANG, MESSAGES
from services.backend_client import send_event

router = Router()


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(F.text == "Заправка")
async def fuel_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    await state.set_state(FuelStates.waiting_photo)
    await message.answer(t["ask_fuel_photo"])


@router.message(F.photo, FuelStates.waiting_photo)
async def fuel_receive_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)

    await state.set_state(FuelStates.waiting_liters)
    await message.answer(t["ask_fuel_liters"])


@router.message(F.text.regexp(r"^\d+(?:[.,]\d+)?$"), FuelStates.waiting_liters)
async def fuel_receive_liters(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    liters = float(message.text.replace(",", "."))
    user_data = await state.get_data()

    payload = {
        "user_id": uid,
        "liters": liters,
        "photo_file_id": user_data.get("photo_id"),
    }

    try:
        await send_event("fuel", payload)
    except Exception:
        await message.answer("Сервер недоступен. Попробуйте позже.")
        await state.clear()
        return

    await message.answer(
        t["saved"],
        reply_markup=main_menu(t)
    )

    await state.clear()


# ОТМЕНА — работает в любом состоянии!
@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    await state.clear()
    await message.answer(t["menu"], reply_markup=main_menu(t))
