import asyncio
import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.executor import Executor

from telegram_bot.constants import ConstantMessages as Messages, ButtonNames
from telegram_bot.db import setup_db
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.keyboards import get_actions_keyboard
from telegram_bot.settings import TOKEN
from telegram_bot.states import ProjectStates


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
runner = Executor(dp)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """Выдает стартовое сообщение."""
    await message.answer(Messages.START, reply_markup=get_actions_keyboard())


@dp.message_handler(lambda m: ButtonNames.SEND_INFORMATION_FORM in m.text)
async def send_information_form(message: types.Message):
    """Обработчик нажатия на кнопку отправки анкеты сообщений."""
    await message.answer(Messages.SEND_INFORMATION_FORM)
    await ProjectStates.send_information_form.set()


@dp.message_handler(state=ProjectStates.send_information_form)
async def send_information_form_saving(
        message: types.Message, state: FSMContext):
    """Сохранение анкеты."""
    # TODO: добавить сохранение данных и обработку изображений
    # TODO: проверить, как обрабатываются png файлы
    print(message.text)
    await message.answer(Messages.INFORMATION_FORM_PROCESSED)
    await state.finish()


@dp.message_handler(lambda m: ButtonNames.SEND_STORY in m.text)
async def send_story(message: types.Message):
    """Обработчик нажатия на кнопку отправки интересной истории."""
    await message.answer(Messages.SEND_STORY)
    await ProjectStates.send_story.set()


@dp.message_handler(state=ProjectStates.send_story)
async def story_saving(
        message: types.Message, state: FSMContext):
    """Сохранение истории."""
    # TODO: добавить сохранение данных
    print(message.text)
    await message.answer(Messages.STORY_PROCESSED)
    await state.finish()


@dp.message_handler(commands=['get_code'])
async def get_code_handler(message: types.Message):
    pass


@dp.message_handler()
async def unknown_message_handler(message: types.Message):
    """Обработчик неизвестных сообщений."""
    await message.answer(Messages.UNKNOWN_MESSAGE)


if __name__ == '__main__':
    setup_db(runner)
    loop = asyncio.get_event_loop()
    runner.start_polling(dp)
