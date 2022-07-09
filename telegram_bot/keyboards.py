from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup
from telegram_bot.constants import AdminConsts
from telegram_bot.constants import ButtonNames as BN
from telegram_bot.constants import DialogConsts


def get_actions_keyboard(is_admin=False):
    """Клавиатура с выбором возможных действий"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for button_name in [
        BN.values[BN.SEND_INFORMATION_FORM], BN.values[BN.SEND_STORY],
        BN.values[BN.START_ANONYMOUS_DIALOG]
    ]:
        kb.add(button_name)

    if is_admin:
        for admin_button in AdminConsts.ADMIN_KEYS:
            kb.add(admin_button)

    return kb


def get_actions_kb_params(is_admin):
    return dict(reply_markup=get_actions_keyboard(is_admin))


# Словарь с клавиатурой действия для ответа
actions_kb_params = dict(reply_markup=get_actions_keyboard())
# Клавиатура с единственной кнопкой "Вернуться"
RETURN_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).add(BN.values[BN.RETURN])

# Клавиатура с единственной кнопкой "Остановить поиск собеседника"
STOP_DIALOG_SEARCH_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).add(BN.values[BN.SEARCH_STOP_BUTTON])

# Клавиатура с единственной кнопкой "Закончить диалог"
CANCEL_DIALOG_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).add(DialogConsts.CANCEL_DIALOG_BUTTON)


def get_story_keyboard_markup(story_id):
    """Получение кнопок для работы с историей."""
    from telegram_bot.helpers import get_callback_data
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            AdminConsts.APPROVE,
            callback_data=get_callback_data(
                AdminConsts.APPROVE_STORY_CODE, story_id),
        ),
        InlineKeyboardButton(
            AdminConsts.NEED_TO_EDIT,
            callback_data=get_callback_data(
                AdminConsts.NEED_TO_EDIT_STORY_CODE, story_id)
        ),
        InlineKeyboardButton(
            AdminConsts.DELETE,
            callback_data=get_callback_data(
                AdminConsts.DELETE_STORY_CODE, story_id)
        ),
    )


def get_person_info_keyboard_markup(person_info_id):
    """Получение кнопок для работы с анкетами."""
    from telegram_bot.helpers import get_callback_data
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            AdminConsts.APPROVE,
            callback_data=get_callback_data(
                AdminConsts.APPROVE_PERSON_INFO_CODE, person_info_id),
        ),
        InlineKeyboardButton(
            AdminConsts.NEED_TO_EDIT,
            callback_data=get_callback_data(
                AdminConsts.NEED_TO_EDIT_PERSON_INFO_CODE, person_info_id)
        ),
        InlineKeyboardButton(
            AdminConsts.DELETE,
            callback_data=get_callback_data(
                AdminConsts.DELETE_PERSON_INFO_CODE, person_info_id),
        ),
    )
