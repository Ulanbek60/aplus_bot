from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext
from datetime import datetime

from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.backend_client import send_event
from states import IssueStates

router = Router()


def get_t(uid: int):
    lang = USER_LANG.get(uid, "ru")
    return MESSAGES[lang]


@router.message(F.text == "Сообщить о поломке")
async def issue_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    await state.set_state(IssueStates.waiting_description)
    await message.answer(
        t.get("issue_prompt_description", "Опишите проблему словами."),
        reply_markup=main_menu(t)
    )


@router.message(IssueStates.waiting_description)
async def issue_receive_description(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    text = message.text.strip()
    if not text:
        await message.answer(t.get("issue_empty_description", "Пожалуйста, опишите проблему несколько слов."), reply_markup=main_menu(t))
        return

    # сохраняем описание во временном хранилище состояния
    await state.update_data(issue_description=text)
    await state.set_state(IssueStates.waiting_photo)

    await message.answer(
        t.get("issue_prompt_photo", "Теперь отправь фото поломки (обязательно)."),
        reply_markup=main_menu(t)
    )


@router.message(F.photo, IssueStates.waiting_photo)
async def issue_receive_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)

    photo: PhotoSize = message.photo[-1]
    photo_file_id = photo.file_id

    data = await state.get_data()
    description = data.get("issue_description", "")

    # payload с метаданными
    payload = {
        "user_id": uid,
        "issue": description,
        "photo_file_id": photo_file_id,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    # отправляем на backend
    try:
        await send_event("issue", payload)
    except Exception as e:
        # если бэкенд упал — логируем и говорим пользователю аккуратно
        await message.answer(t.get("issue_send_error", "Ошибка при отправке на сервер. Попробуйте позже."))
        await state.clear()
        return

    await message.answer(
        t.get("issue_saved", "Спасибо, информация о поломке отправлена."),
        reply_markup=main_menu(t)
    )

    await state.clear()


@router.message(lambda m: True, IssueStates.waiting_photo)
async def issue_no_photo(message: Message, state: FSMContext):
    # если пользователь отправил не фото
    uid = message.from_user.id
    t = get_t(uid)
    await message.answer(
        t.get("issue_photo_required", "Нужно отправить фото. Попробуй ещё раз."),
        reply_markup=main_menu(t)
    )


# отмена разрешена в любом состоянии — если уже есть общий cancel handler, можно убрать этот
@router.message(F.text == "Отмена")
async def issue_cancel(message: Message, state: FSMContext):
    uid = message.from_user.id
    t = get_t(uid)
    await state.clear()
    await message.answer(t.get("menu", "Главное меню"), reply_markup=main_menu(t))
