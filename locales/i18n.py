from locales import ru, kg

MESSAGES = {
    "ru": ru.MESSAGES,
    "kg": kg.MESSAGES,
}

USER_LANG = {}

def get_text(user_id: int, key: str):
    lang = USER_LANG.get(user_id, "ru")
    return MESSAGES[lang].get(key, "")
