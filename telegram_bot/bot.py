import asyncio
import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram.utils.executor import Executor

from telegram_bot.constants import ConstantMessages as Messages, ButtonNames
from telegram_bot.db import setup_db
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.filters import AdminFilter
from telegram_bot.helpers import generate_file_name, \
    get_absolute_media_path, get_upload_file_path
from telegram_bot.keyboards import actions_kb_params, RETURN_KEYBOARD
from telegram_bot.models import Story, PersonInformation
from telegram_bot.settings import TOKEN, MEDIA_DIR
from telegram_bot.states import ProjectStates


bot = Bot(token=TOKEN)
# TODO: заменить на Redis
dp = Dispatcher(bot, storage=MemoryStorage())
dp.filters_factory.bind(AdminFilter)
runner = Executor(dp)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def cancel_action(message, state=None):
    """Отмена действий."""
    await message.answer(Messages.CHOOSE_ACTION, **actions_kb_params)
    if state:
        await state.finish()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """Выдает стартовое сообщение."""
    await message.answer(Messages.START)
    await message.answer(Messages.CHOOSE_ACTION, **actions_kb_params)


@dp.message_handler(Text(ButtonNames.SEND_INFORMATION_FORM))
async def send_information_form(message: types.Message):
    """Обработчик нажатия на кнопку отправки анкеты сообщений."""
    await message.answer(
        Messages.SEND_INFORMATION_FORM, reply_markup=RETURN_KEYBOARD)
    await ProjectStates.send_information_form.set()


@dp.message_handler(state=ProjectStates.send_information_form,
                    content_types=[ContentType.ANY])
async def send_information_form_saving(
        message: types.Message, state: FSMContext):
    """Сохранение анкеты."""
    if message.text == ButtonNames.RETURN:
        await cancel_action(message, state)
        return

    # Проверка на наличие документа
    if message.document:
        await message.answer(Messages.NEED_IMAGE_AS_PHOTO)
        return

    if not message.text and not message.caption:
        await message.answer(Messages.PERSON_INFORMATION_NOT_EXISTS)
        return

    if message.photo:
        try:
            photo = message.photo[-1]
            rel_image_path = get_upload_file_path(
                generate_file_name('jpg'), 'images')
            await photo.download(
                destination_file=get_absolute_media_path(rel_image_path))
            image_params = dict(
                image_file_id=photo.file_id,
                image_path=rel_image_path
            )
        except Exception:
            await message.answer(Messages.IMAGE_PROCESSING_ERROR)
            return
    else:
        image_params = {}

    await PersonInformation.create(
        text=message.text or message.caption or '',
        **image_params
    )
    await message.answer(
        Messages.INFORMATION_FORM_PROCESSED, **actions_kb_params)
    await state.finish()


@dp.message_handler(Text(ButtonNames.SEND_STORY))
async def send_story(message: types.Message):
    """Обработчик нажатия на кнопку отправки интересной истории."""
    await message.answer(Messages.SEND_STORY, reply_markup=RETURN_KEYBOARD)
    await ProjectStates.send_story.set()


@dp.message_handler(state=ProjectStates.send_story)
async def story_saving(
        message: types.Message, state: FSMContext):
    """Сохранение истории."""
    if message.text == ButtonNames.RETURN:
        await cancel_action(message, state)
        return

    await Story.create(text=message.text)
    await message.answer(Messages.STORY_PROCESSED, **actions_kb_params)
    await state.finish()


@dp.message_handler(content_types=[ContentType.ANY])
async def unknown_message_handler(message: types.Message):
    """Обработчик неизвестных сообщений."""
    await message.answer(Messages.UNKNOWN_MESSAGE)


if __name__ == '__main__':
    setup_db(runner)
    loop = asyncio.get_event_loop()
    runner.start_polling(dp)
