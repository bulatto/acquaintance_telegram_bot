import asyncio
import logging
import traceback

import sentry_sdk
from aiogram import Bot
from aiogram import types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram.utils.executor import Executor
from sentry_sdk import capture_exception
from sentry_sdk import capture_message
from telegram_bot.constants import START_COMMAND
from telegram_bot.constants import AdminButtonNames
from telegram_bot.constants import ButtonNames
from telegram_bot.constants import Messages
from telegram_bot.db import setup_db
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.filters import AdminFilter
from telegram_bot.helpers import PersonInfoToChannelResender
from telegram_bot.helpers import StoryToChannelResender
from telegram_bot.helpers import answer_with_actions_keyboard
from telegram_bot.helpers import check_return_or_start_cmd
from telegram_bot.helpers import create_person_info_from_message
from telegram_bot.helpers import get_obj_id_from_callback_data
from telegram_bot.keyboards import RETURN_KEYBOARD
from telegram_bot.keyboards import get_person_info_keyboard_markup
from telegram_bot.keyboards import get_story_keyboard_markup
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from telegram_bot.settings import ADMIN_OBJS_COUNT_SETTING
from telegram_bot.settings import REDIS_STORAGE_PARAMS
from telegram_bot.settings import SENTRY_URL
from telegram_bot.settings import TOKEN
from telegram_bot.states import ProjectStates

if SENTRY_URL:
    sentry_sdk.init(
        SENTRY_URL,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=RedisStorage2(**REDIS_STORAGE_PARAMS))
dp.filters_factory.bind(AdminFilter)
runner = Executor(dp)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def answer(message, text, photo_file_id=None, **kwargs):
    """Ответ на сообщение с текстом/изображением и доп. параметрами"""
    if photo_file_id:
        await message.answer_photo(photo_file_id, text, **kwargs)
    else:
        await message.answer(text, **kwargs)


@dp.message_handler(commands=[START_COMMAND])
async def process_start_command(message: types.Message):
    """Выдает стартовое сообщение."""
    await message.answer(Messages.START)
    await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)


@dp.message_handler(Text(ButtonNames.SEND_INFORMATION_FORM))
async def send_information_form(message: types.Message):
    """Обработчик нажатия на кнопку отправки анкеты сообщений."""
    await message.answer(
        Messages.SEND_INFORMATION_FORM, parse_mode="Markdown")
    await message.answer(
        Messages.INFORMATION_FORM_TEMPLATE, reply_markup=RETURN_KEYBOARD)
    await ProjectStates.send_information_form.set()


# TODO: может сделать всплывающую форму с разными полями (?)
#  как у бота @DurgerKingBot (да, название именно такое:))
@dp.message_handler(state=ProjectStates.send_information_form,
                    content_types=[ContentType.ANY])
async def send_information_form_saving(
        message: types.Message, state: FSMContext):
    """Сохранение анкеты."""

    return_or_start_cmd = await check_return_or_start_cmd(message, state)
    if return_or_start_cmd:
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
    return_or_start_cmd = await check_return_or_start_cmd(message, state)
    if return_or_start_cmd:
        return

    await Story.create(text=message.text, user_id=message.from_user.id)

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
        await message.answer(
            story.text, reply_markup=get_story_keyboard_markup(story.id))


@dp.callback_query_handler(
    lambda c: AdminButtonNames.DELETE_STORY_CODE in c.data)
async def delete_story(callback_query: types.CallbackQuery):
    """Удаление истории вместе с сообщением."""
    story_id = get_obj_id_from_callback_data(callback_query.data)
    await Story.filter(id=story_id).delete()
    await callback_query.message.delete()


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_STORY_CODE in c.data)
async def process_story_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка истории в канал"""
    story_id = get_obj_id_from_callback_data(callback_query.data)
    await StoryToChannelResender(story_id, callback_query.message).send()


@dp.callback_query_handler(
    lambda c: AdminButtonNames.NEED_TO_EDIT_STORY_CODE in c.data)
async def need_to_edit_story(callback_query: types.CallbackQuery,
                             state: FSMContext):
    """Отправка истории на редактирование вместе с сообщением от админа."""
    story_id = get_obj_id_from_callback_data(callback_query.data)
    await state.set_data({'user_story_id': story_id})

    await callback_query.message.answer(
        AdminButtonNames.NEED_TO_EDIT_TO_ADMIN, reply_markup=RETURN_KEYBOARD)

    await ProjectStates.need_to_edit_story.set()


@dp.message_handler(state=ProjectStates.need_to_edit_story)
async def need_to_edit_story_send_msg(
        message: types.Message, state: FSMContext):
    """Отправка истории на редактирование вместе с сообщением от админа."""

    return_or_start_cmd = await check_return_or_start_cmd(message, state)
    if return_or_start_cmd:
        return

    state_data = await state.get_data()
    user_story_id = state_data.get('user_story_id', None)
    if user_story_id:
        story = await Story.filter(id=user_story_id).first()

        await bot.send_message(
            story.user_id,
            f'{AdminButtonNames.ADMIN_ANSWER}\n{Messages.STORY_NEED_TO_EDIT}',
            parse_mode="Markdown"
        )
        await bot.send_message(story.user_id, story.text)
        await bot.send_message(
            story.user_id, f'{AdminButtonNames.ADMIN_ANSWER}\n{message.text}',
            parse_mode="Markdown"
        )
        await answer_with_actions_keyboard(
            message, AdminButtonNames.ADMIN_MSG_SENDED)
    else:
        raise ApplicationLogicException('История не найдена!')
    await state.finish()


@dp.message_handler(Text(
    AdminButtonNames.GET_PERSON_INFO), is_admin=True)
async def get_user_info_forms(message: types.Message, state: FSMContext):
    """Получение админом анкет."""

    persons_information = await PersonInformation.filter(
        is_published=False
    ).limit(ADMIN_OBJS_COUNT_SETTING)

    if not persons_information:
        raise ApplicationLogicException(AdminButtonNames.PERSON_INFOS_IS_EMPTY)

    for person_info in persons_information:
        await answer(
            message, person_info.text, person_info.image_file_id,
            reply_markup=get_person_info_keyboard_markup(person_info.id)
        )


@dp.callback_query_handler(
    lambda c: AdminButtonNames.DELETE_PERSON_INFO_CODE in c.data)
async def delete_person_info(callback_query: types.CallbackQuery):
    """Удаление анкеты вместе с сообщением."""
    info_id = get_obj_id_from_callback_data(callback_query.data)
    await PersonInformation.filter(id=info_id).delete()
    await callback_query.message.delete()


@dp.callback_query_handler(
    lambda c: AdminButtonNames.APPROVE_PERSON_INFO_CODE in c.data)
async def process_person_info_approve(callback_query: types.CallbackQuery):
    """Авто-пересылка анкеты в канал"""
    person_info_id = get_obj_id_from_callback_data(callback_query.data)
    await PersonInfoToChannelResender(
        person_info_id, callback_query.message).send()


@dp.callback_query_handler(
    lambda c: AdminButtonNames.NEED_TO_EDIT_PERSON_INFO_CODE in c.data)
async def need_to_edit_person_info(callback_query: types.CallbackQuery,
                             state: FSMContext):
    """Отправка анкеты на редактирование вместе с сообщением от админа."""
    person_info_id = get_obj_id_from_callback_data(callback_query.data)
    await state.set_data({'user_person_info_id': person_info_id})

    await callback_query.message.answer(
        AdminButtonNames.NEED_TO_EDIT_TO_ADMIN, reply_markup=RETURN_KEYBOARD)

    await ProjectStates.need_to_edit_person_info.set()


@dp.message_handler(state=ProjectStates.need_to_edit_person_info)
async def need_to_edit_person_info_send_msg(
        message: types.Message, state: FSMContext):
    """Отправка анкеты на редактирование вместе с сообщением от админа."""

    return_or_start_cmd = await check_return_or_start_cmd(message, state)
    if return_or_start_cmd:
        return

    state_data = await state.get_data()
    user_person_info_id = state_data.get('user_person_info_id', None)
    if user_person_info_id:
        person_info = await PersonInformation.filter(
            id=user_person_info_id).first()

        await bot.send_message(
            person_info.user_id,
            f'{AdminButtonNames.ADMIN_ANSWER}\n{Messages.INFO_NEED_TO_EDIT}',
            parse_mode="Markdown"
        )
        await bot.send_photo(
            person_info.user_id, person_info.image_file_id, person_info.text)
        await bot.send_message(
            person_info.user_id,
            f'{AdminButtonNames.ADMIN_ANSWER}\n{message.text}',
            parse_mode="Markdown"
        )
        await answer_with_actions_keyboard(
            message, AdminButtonNames.ADMIN_MSG_SENDED)
    else:
        raise ApplicationLogicException('Анкета не найдена!')
    await state.finish()


@dp.message_handler(Text(AdminButtonNames.SEND_SENTRY_ERROR_CMD))
async def send_test_setnry_error(message: types.Message):
    """Обработчик отправки тестового сообщения в Sentry."""
    capture_message('Тестовое сообщение в Sentry')
    await answer_with_actions_keyboard(
        message, 'Тестовое сообщение в Sentry отправлено!')


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
        # Отправка ошибки в Sentry
        if SENTRY_URL:
            capture_exception(error)
        traceback.print_exc()

    return True


if __name__ == '__main__':
    setup_db(runner)
    loop = asyncio.get_event_loop()
    runner.start_polling(dp)
