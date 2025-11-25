from aiogram import Router
from aiogram.types import Message
from locales.i18n import get_text

router = Router()

@router.message()
async def fallback(message: Message):
    await message.answer(
        f"{get_text(message.from_user.id, 'menu')}\n\n"
        "Я не понял твою команду. Используй кнопки."
    )

