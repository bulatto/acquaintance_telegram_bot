from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from telegram_bot.settings import ADMINS_USERNAMES


class AdminFilter(BoundFilter):
    """Фильтр, что пользователь является администратором бота"""
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        username = message.from_user.username
        return bool(username and username in ADMINS_USERNAMES)
