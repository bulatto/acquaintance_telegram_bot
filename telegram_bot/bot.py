import asyncio
import logging

from aiogram import Bot
from aiogram import types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils import exceptions
from aiogram.utils.executor import Executor
from telegram_bot.constants import AdminButtonNames
from telegram_bot.constants import ButtonNames
from telegram_bot.constants import ConstantMessages as Messages
from telegram_bot.db import setup_db
from telegram_bot.filters import AdminFilter
from telegram_bot.filters import is_admin_message
from telegram_bot.helpers import generate_file_name
from telegram_bot.helpers import get_absolute_media_path
from telegram_bot.helpers import get_upload_file_path
from telegram_bot.keyboards import RETURN_KEYBOARD
from telegram_bot.keyboards import get_actions_kb_params
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from telegram_bot.settings import CHANNEL_USERNAME, REDIS_STORAGE_PARAMS
from telegram_bot.settings import TOKEN
from telegram_bot.states import ProjectStates


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=RedisStorage2(**REDIS_STORAGE_PARAMS))
dp.filters_factory.bind(AdminFilter)
runner = Executor(dp)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def answer_with_actions_keyboard(message, text):
    """Обычный ответ на сообщение с выдачей клавиатуры действий"""
    await message.answer(
        text,
        **get_actions_kb_params(is_admin_message(message))
    )


async def cancel_action(message, state=None):
    """Отмена действий и вывод обычной клавиатуры с действиями."""
    await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)
    if state:
        await state.finish()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """Выдает стартовое сообщение."""
    await message.answer(Messages.START)
    await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)


@dp.message_handler(Text(ButtonNames.SEND_INFORMATION_FORM))
async def send_information_form(message: types.Message):
    """Обработчик нажатия на кнопку отправки анкеты сообщений."""
    await message.answer(
        Messages.SEND_INFORMATION_FORM, reply_markup=RETURN_KEYBOARD)
    await ProjectStates.send_information_form.set()


# TODO: может сделать всплывающую форму с разными полями (?)
#  как у бота @BurgerKingBot
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
            image_params = dict(
                image_file_id=photo.file_id,
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
    await answer_with_actions_keyboard(
        message, Messages.INFORMATION_FORM_PROCESSED)
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

    await answer_with_actions_keyboard(message, Messages.STORY_PROCESSED)
    await state.finish()


@dp.message_handler(Text(AdminButtonNames.GET_STORIES), is_admin=True)
async def get_user_stories(message: types.Message, state: FSMContext):
    """Получение админом историй."""

    user_stories = await Story.filter(
        is_published=False
    ).limit(AdminButtonNames.ADMIN_COUNT_SETTING)

    if len(user_stories) == 0:
        await message.answer(AdminButtonNames.STORIES_IS_EMPTY)

    for story in user_stories:
        story_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                AdminButtonNames.APPROVE_STORY,
                callback_data=f'{AdminButtonNames.APPROVE_STORY_CODE}_{story.id}'
            )
        )
        await message.answer(story.text, reply_markup=story_keyboard)


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_STORY_CODE in c.data)
async def process_story_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка истории в канал"""
    if CHANNEL_USERNAME:
        try:
            await bot.send_message(
                CHANNEL_USERNAME, callback_query.message.text)
        except exceptions.Unauthorized:
            await callback_query.message.answer(
                Messages.BOT_NOT_AUTHORIZED_IN_CHANNEL)
        finally:  # Помечаем историю как отправленную
            story_id = int(callback_query.data.split('_')[-1])
            await Story.filter(id=story_id).update(is_published=True)
    else:
        await callback_query.message.answer(Messages.CHANNEL_URL_NOT_FOUND)


@dp.message_handler(Text(
    AdminButtonNames.GET_INFORMATION_FORMS), is_admin=True)
async def get_user_info_forms(message: types.Message, state: FSMContext):
    """Получение админом анкет."""

    if message.text == ButtonNames.RETURN:
        await cancel_action(message, state)
        return

    persons_information = await PersonInformation.filter(
        is_published=False
    ).limit(AdminButtonNames.ADMIN_COUNT_SETTING)

    if len(persons_information) == 0:
        await message.answer(AdminButtonNames.PERSON_INFOS_IS_EMPTY)

    for person_info in persons_information:
        story_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                AdminButtonNames.APPROVE_PERSON_INFO,
                callback_data=(
                    f'{AdminButtonNames.APPROVE_PERSON_INFO_CODE}_'
                    f'{person_info.id}'
                )
            )
        )
        await message.answer_photo(
            person_info.image_file_id, person_info.text,
            reply_markup=story_keyboard)


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_PERSON_INFO_CODE in c.data)
async def process_person_info_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка анкеты в канал"""
    if not CHANNEL_USERNAME:
        await callback_query.message.answer(Messages.CHANNEL_URL_NOT_FOUND)
        return

    try:
        # TODO: возможно тут не всегда будет фото
        # TODO: добавить логирование и обработку ошибок Exception
        await bot.send_photo(
            CHANNEL_USERNAME,
            callback_query.message.photo[-1].file_id,
            caption=callback_query.message.html_text
        )
    except exceptions.Unauthorized:
        await callback_query.message.answer(
            Messages.BOT_NOT_AUTHORIZED_IN_CHANNEL)
    finally:
        # Помечаем историю как отправленную
        person_info_id = int(callback_query.data.split('_')[-1])
        await PersonInformation.filter(
            id=person_info_id).update(is_published=True)


@dp.message_handler(content_types=[ContentType.ANY])
async def unknown_message_handler(message: types.Message):
    """Обработчик неизвестных сообщений."""
    await message.answer(Messages.UNKNOWN_MESSAGE)


if __name__ == '__main__':
    setup_db(runner)
    loop = asyncio.get_event_loop()
    runner.start_polling(dp)
