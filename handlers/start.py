from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import language_keyboard, main_menu
from locales.i18n import USER_LANG, get_text

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        get_text(message.from_user.id, "start"),
        reply_markup=language_keyboard()
    )

@router.message(lambda m: m.text in ["Русский", "Кыргызча"])
async def lang_choose(message: Message, state: FSMContext):
    lang = "ru" if message.text == "Русский" else "kg"
    USER_LANG[message.from_user.id] = lang

    from locales.i18n import MESSAGES

    await message.answer(
        MESSAGES[lang]["menu"],
        reply_markup=main_menu(MESSAGES[lang])
    )
