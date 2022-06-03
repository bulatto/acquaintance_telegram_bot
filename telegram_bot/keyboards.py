from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton
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


def get_story_keyboard_markup(story_id):
    """Получение кнопок для работы с историей."""
    from telegram_bot.helpers import get_callback_data
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            AdminButtonNames.APPROVE,
            callback_data=get_callback_data(
                AdminButtonNames.APPROVE_STORY_CODE, story_id),
        ),
        InlineKeyboardButton(
            AdminButtonNames.NEED_TO_EDIT,
            callback_data=get_callback_data(
                AdminButtonNames.NEED_TO_EDIT_STORY_CODE, story_id)
        ),
        InlineKeyboardButton(
            AdminButtonNames.DELETE,
            callback_data=get_callback_data(
                AdminButtonNames.DELETE_STORY_CODE, story_id)
        ),
    )


def get_person_info_keyboard_markup(person_info_id):
    """Получение кнопок для работы с анкетами."""
    from telegram_bot.helpers import get_callback_data
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            AdminButtonNames.APPROVE,
            callback_data=get_callback_data(
                AdminButtonNames.APPROVE_PERSON_INFO_CODE, person_info_id),
        ),
        InlineKeyboardButton(
            AdminButtonNames.NEED_TO_EDIT,
            callback_data=get_callback_data(
                AdminButtonNames.NEED_TO_EDIT_PERSON_INFO_CODE, person_info_id)
        ),
        InlineKeyboardButton(
            AdminButtonNames.DELETE,
            callback_data=get_callback_data(
                AdminButtonNames.DELETE_PERSON_INFO_CODE, person_info_id),
        ),
    )
