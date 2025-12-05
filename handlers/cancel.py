# handlers/cancel.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu

router = Router()


def is_cancel(text, uid):
    lang = USER_LANG.get(uid, "ru")
    return text == MESSAGES[lang]["cancel"]


@router.message(lambda m: is_cancel(m.text, m.from_user.id))
async def cancel_handler(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = USER_LANG.get(uid, "ru")
    pack = MESSAGES[lang]

    await state.clear()
    await message.answer(pack["menu"], reply_markup=main_menu(pack))
