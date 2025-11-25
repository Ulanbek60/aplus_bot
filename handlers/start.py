from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import language_keyboard, main_menu, request_phone_keyboard
from locales.i18n import USER_LANG, get_text, MESSAGES

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id

    from data.users import AUTH_USERS
    authorized = uid in AUTH_USERS

    # если НЕ авторизован → только язык и запрос телефона
    if not authorized:
        lang_text = get_text(uid, "start")
        t = MESSAGES.get("ru")  # по умолчанию русский

        await message.answer(
            lang_text,
            reply_markup=language_keyboard()
        )

        await message.answer(
            t["auth_ask_phone"],
            reply_markup=request_phone_keyboard(t)
        )
        return

    # если авторизован → показываем меню
    lang = USER_LANG.get(uid, "ru")
    t = MESSAGES[lang]

    await message.answer(
        t["menu"],
        reply_markup=main_menu(t)
    )


@router.message(lambda m: m.text in ["Русский", "Кыргызча"])
async def lang_choose(message: Message, state: FSMContext):
    lang = "ru" if message.text == "Русский" else "kg"
    USER_LANG[message.from_user.id] = lang


    await message.answer(
        MESSAGES[lang]["menu"],
        reply_markup=main_menu(MESSAGES[lang])
    )
