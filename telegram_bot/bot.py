import asyncio
import logging
import traceback

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
from telegram_bot.constants import Messages
from telegram_bot.db import setup_db
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.filters import AdminFilter
from telegram_bot.filters import is_admin_message
from telegram_bot.helpers import create_person_info_from_message, \
    get_story_callback_data, get_person_info_callback_data, \
    get_obj_id_from_callback_data, send_message_to_channel, \
    StoryToChannelResender, PersonInfoToChannelResender
from telegram_bot.keyboards import RETURN_KEYBOARD
from telegram_bot.keyboards import get_actions_kb_params
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from telegram_bot.settings import REDIS_STORAGE_PARAMS
from telegram_bot.settings import ADMIN_OBJS_COUNT_SETTING
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


async def answer(message, text, photo_file_id=None, **kwargs):
    """Ответ на сообщение с текстом/изображением и доп.параметрами"""
    if photo_file_id:
        await message.answer_photo(photo_file_id, text, **kwargs)
    else:
        await message.answer(text, **kwargs)


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

    await create_person_info_from_message(message)

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
    ).limit(ADMIN_OBJS_COUNT_SETTING)

    if not user_stories:
        raise ApplicationLogicException(AdminButtonNames.STORIES_IS_EMPTY)

    for story in user_stories:
        story_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                AdminButtonNames.APPROVE_STORY,
                callback_data=get_story_callback_data(story.id)
            )
        )
        await message.answer(story.text, reply_markup=story_keyboard)


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_STORY_CODE in c.data)
async def process_story_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка истории в канал"""
    story_id = get_obj_id_from_callback_data(callback_query.data)
    await StoryToChannelResender(story_id, callback_query.message).send()


@dp.message_handler(Text(
    AdminButtonNames.GET_INFORMATION_FORMS), is_admin=True)
async def get_user_info_forms(message: types.Message, state: FSMContext):
    """Получение админом анкет."""

    persons_information = await PersonInformation.filter(
        is_published=False
    ).limit(ADMIN_OBJS_COUNT_SETTING)

    if not persons_information:
        raise ApplicationLogicException(AdminButtonNames.PERSON_INFOS_IS_EMPTY)

    for person_info in persons_information:
        story_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                AdminButtonNames.APPROVE_PERSON_INFO,
                callback_data=get_person_info_callback_data(person_info.id)
            )
        )
        await answer(
            message, person_info.text, person_info.image_file_id,
            reply_markup=story_keyboard
        )


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_PERSON_INFO_CODE in c.data)
async def process_person_info_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка анкеты в канал"""
    person_info_id = get_obj_id_from_callback_data(callback_query.data)
    await PersonInfoToChannelResender(
        person_info_id, callback_query.message).send()


@dp.message_handler(content_types=[ContentType.ANY])
async def unknown_message_handler(message: types.Message):
    """Обработчик неизвестных сообщений."""
    await message.answer(Messages.UNKNOWN_MESSAGE)


@dp.errors_handler(exception=Exception)
async def message_not_modified_handler(update, error):
    """Обработка ошибок.

    В случае ApplicationLogicException, просто выводится сообщение из текста
    ошибки.
    В случае другой ошибки, выводится сообщение о непредвиденной ошибке,
    очищается контекст, и происходит выход на главный экран.
    """
    message = update.message or update.callback_query.message
    if isinstance(error, ApplicationLogicException):
        await message.answer(str(error))
    else:
        await answer_with_actions_keyboard(message, Messages.ERROR)
        state = dp.current_state()
        await state.finish()
        # TODO: добавить логирование
        traceback.print_exc()

    return True


if __name__ == '__main__':
    setup_db(runner)
    loop = asyncio.get_event_loop()
    runner.start_polling(dp)
