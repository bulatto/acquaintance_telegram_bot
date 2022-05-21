from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from telegram_bot.constants import ButtonNames as BN


def get_actions_keyboard():
    """Клавиатура с выбором возможных действий"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for button_name in [BN.SEND_INFORMATION_FORM, BN.SEND_STORY]:
        kb.add(button_name)
    return kb


# Словарь с клавиатурой действия для ответа
actions_kb_params = dict(reply_markup=get_actions_keyboard())
# Клавиатура с единственной кнопкой "Вернуться"
RETURN_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).add(BN.RETURN)
