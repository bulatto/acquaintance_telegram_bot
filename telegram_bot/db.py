from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise import Tortoise, fields

from telegram_bot import settings


db = Tortoise()


async def on_startup(dispatcher: Dispatcher):
    await db.init(config=settings.TORTOISE_ORM)

    from telegram_bot import signals


async def on_shutdown(dispatcher: Dispatcher):
    await db.close_connections()


def setup_db(runner: Executor):
    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)
