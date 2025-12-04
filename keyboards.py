from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇷🇺 Русский"),
                KeyboardButton(text="🇰🇬 Кыргызча")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def request_phone_keyboard(messages):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=messages["send_phone"], request_contact=True)]
        ],
        resize_keyboard=True
    )


def main_menu(t):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"🟢 {t['start_shift']}")],
            [KeyboardButton(text=f"🔴 {t['end_shift']}")],
            [
                KeyboardButton(text=f"⛽ {t['fuel']}"),
                KeyboardButton(text=f"🛠 {t['report_issue']}")
            ],
            [KeyboardButton(text=f"❌ {t['cancel']}")]
        ],
        resize_keyboard=True
    )

def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/start")]],
        resize_keyboard=True
    )


def cancel_keyboard(t):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="cancel")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )