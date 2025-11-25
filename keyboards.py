from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Русский")],
            [KeyboardButton(text="Кыргызча")],
        ],
        resize_keyboard=True
    )


def main_menu(t):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["start_shift"])],
            [KeyboardButton(text=t["end_shift"])],
            [
                KeyboardButton(text=t["fuel"]),
                KeyboardButton(text=t["report_issue"])
            ],
            [KeyboardButton(text=t["cancel"])]
        ],
        resize_keyboard=True
    )


def request_phone_keyboard(t):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["send_phone"], request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

