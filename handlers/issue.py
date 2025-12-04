from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext
from datetime import datetime

from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event
from states import IssueStates

router = Router()


def t(uid):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


def is_issue_button(text, uid):
    lang = USER_LANG.get(uid, "ru")
    return text == MESSAGES[lang]["report_issue"]


@router.message(lambda m: is_issue_button(m.text, m.from_user.id))
async def issue_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    await state.set_state(IssueStates.waiting_description)
    await message.answer(lang_pack["issue_prompt_description"], reply_markup=main_menu(lang_pack))


@router.message(IssueStates.waiting_description)
async def issue_receive_description(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    text = message.text.strip()
    if not text:
        await message.answer(lang_pack["issue_empty_description"], reply_markup=main_menu(lang_pack))
        return

    await state.update_data(issue_description=text)
    await state.set_state(IssueStates.waiting_photo)

    await message.answer(lang_pack["issue_prompt_photo"], reply_markup=main_menu(lang_pack))


@router.message(F.photo, IssueStates.waiting_photo)
async def issue_receive_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)

    photo: PhotoSize = message.photo[-1]
    payload = {
        "user_id": uid,
        "issue": (await state.get_data()).get("issue_description"),
        "photo_file_id": photo.file_id,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    try:
        await send_event("issue", payload)
    except Exception:
        await message.answer(lang_pack["issue_send_error"])
        await state.clear()
        return

    await message.answer(lang_pack["issue_saved"], reply_markup=main_menu(lang_pack))
    await state.clear()


@router.message(lambda m: True, IssueStates.waiting_photo)
async def issue_no_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang_pack = t(uid)
    await message.answer(lang_pack["issue_photo_required"], reply_markup=main_menu(lang_pack))


