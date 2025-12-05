from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from helpers.buttons import btn_match
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event
from states import IssueStates

router = Router()

def t(uid, key):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang][key]


# запуск поломки
@router.message(lambda m: btn_match(m.text, ["полом", "бузулуу"]))
async def issue_start(message: Message, state: FSMContext):
    uid = message.from_user.id

    await state.set_state(IssueStates.waiting_description)
    await message.answer(t(uid, "issue_prompt_description"))


@router.message(IssueStates.waiting_description)
async def issue_desc(message: Message, state: FSMContext):
    uid = message.from_user.id

    if len(message.text.strip()) < 3:
        await message.answer(t(uid, "issue_empty_description"))
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(IssueStates.waiting_photo)
    await message.answer(t(uid, "issue_prompt_photo"))


@router.message(F.photo, IssueStates.waiting_photo)
async def issue_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()

    payload = {
        "user_id": uid,
        "issue": data["description"],
        "photo_file_id": message.photo[-1].file_id
    }

    await send_event("issue", payload)
    lang = USER_LANG.get(uid, "ru")
    await message.answer(t(uid, "issue_saved"), reply_markup=main_menu(MESSAGES[lang]))
    await state.clear()


@router.message(IssueStates.waiting_photo)
async def wrong_issue_photo(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "issue_photo_required"))
