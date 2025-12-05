from aiogram import Router
from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from locales.i18n import USER_LANG, MESSAGES, get_text
from keyboards import main_menu
from helpers.buttons import btn_match
router = Router()

@router.message()
async def fallback(message: Message):
    await message.answer(
        f"{get_text(message.from_user.id, 'menu')}\n\n"
        "Я не понял твою команду. Используй кнопки."
    )

@router.message(lambda m: btn_match(m.text, ["отмена", "жокко"]))
async def cancel_any(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    lang = USER_LANG.get(uid, "ru")
    text = MESSAGES[lang]
    await message.answer(f"{text['menu']}\n\nЯ не понял вашу команду. Используйте кнопки.")
