from aiogram.types import ReplyKeyboardMarkup
from telegram_bot.constants import ButtonNames as BN
from telegram_bot.constants import AdminButtonNames


def get_actions_keyboard(is_admin=False):
    """Клавиатура с выбором возможных действий"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for button_name in [BN.SEND_INFORMATION_FORM, BN.SEND_STORY]:
        kb.add(button_name)

    if is_admin:
        for admin_button in AdminButtonNames.ADMIN_KEYS:
            kb.add(admin_button)

    return kb


def get_actions_kb_params(is_admin):
    return dict(reply_markup=get_actions_keyboard(is_admin))


# Словарь с клавиатурой действия для ответа
actions_kb_params = dict(reply_markup=get_actions_keyboard())
# Клавиатура с единственной кнопкой "Вернуться"
RETURN_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).add(BN.RETURN)
