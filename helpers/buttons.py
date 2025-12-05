import re

def clean(text: str):
    if not text:
        return ""
    # удаляем все emoji и лишнее
    text = re.sub(r"[^\w\sА-Яа-яЁё]", "", text)
    return text.lower().strip()


def btn_match(message_text: str, words: list[str]):
    """
    message_text — текст кнопки от юзера
    words — список ключевых слов (ru + kg)

    Работает:
    - с эмодзи
    - с пробелами
    - с кириллицей
    - с обоими языками
    """
    t = clean(message_text)
    for w in words:
        if w in t:
            return True
    return False
