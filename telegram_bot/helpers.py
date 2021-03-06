import os
import uuid
from datetime import date
from typing import Optional

from aiogram import Dispatcher
from aiogram.types import PhotoSize
from aiogram.utils import exceptions as aiogram_exceptions
from telegram_bot.constants import START_COMMAND
from telegram_bot.constants import ButtonNames as BN
from telegram_bot.constants import DialogConsts
from telegram_bot.constants import Messages
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.exceptions import ImageProcessingException
from telegram_bot.filters import is_admin_message
from telegram_bot.keyboards import get_actions_kb_params
from telegram_bot.models import AdminUserId
from telegram_bot.models import AnonymousDialog
from telegram_bot.models import ClickStats
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from telegram_bot.settings import CHANNEL_USERNAME
from telegram_bot.settings import MEDIA_DIR
from telegram_bot.validators import PersonInfoValidator
from tortoise.transactions import in_transaction


def log_button_click(func):
    """
    Декоратор для логирования статистики нажатий пользователями на
    основные кнопки бота.
    """

    async def inner(*args, **kwargs):
        # Есть случаи когда функция обработчик не принимает параметр "state",
        # но иногда она принимает его как позиционный аргумент,
        # а иногда как именованный.
        if 'state' in func.__code__.co_varnames and kwargs.get('state'):
            result = await func(*args, kwargs['state'])
        else:
            result = await func(*args)

        try:
            user_id = args[0].from_user.id
            button_name = args[0].text

            buttons_dict = dict(map(reversed, BN.values.items()))
            buttons_dict.update({f'/{START_COMMAND}': 0})

            await ClickStats.create(
                user_id=user_id, button=buttons_dict.get(button_name, -1)
            )
        except Exception:
            # Пока на всякий случай скрываем все ошибки тут
            pass

        return result

    return inner


def generate_file_name(suffix):
    """Генерация названия файла

    :param suffix: Расширение файла без точки

    :return
    """
    return f'{uuid.uuid4().hex[:10]}.{suffix}'


def get_upload_file_path(file_name, sub_dir_name=None, base_dir=None):
    """Формирует уникальный путь для загрузки файла.

    :param file_name: Название файла
    :param sub_dir_name: Название подпапки
    :param base_dir: Базовая директория

    :return: Уникальный путь до файла
    """
    path_parts = []
    if base_dir is not None:
        path_parts.append(base_dir)
    if sub_dir_name is not None:
        path_parts.append(sub_dir_name)

    today = date.today()
    path_parts.extend(list(map(str, [today.year, today.month, today.day])))
    path_parts.append(uuid.uuid4().hex[:10])
    os.makedirs(os.path.join(*path_parts))
    if file_name:
        path_parts.append(file_name)

    return os.path.join(*path_parts)


def get_absolute_media_path(rel_media_path):
    """Получение абсолютного пути до файла в медиа по относительному пути."""
    return str(MEDIA_DIR / rel_media_path)


async def download_photo(photo: PhotoSize) -> tuple[str, str]:
    """Загрузка изображения из телеграм

    :param photo: Объект фото из сообщения

    :return: Кортеж (относительный путь до файла; абсолютный путь до файла)

    """
    try:
        rel_image_path = get_upload_file_path(
            generate_file_name('jpg'), 'images')
        absolute_path = get_absolute_media_path(rel_image_path)
        await photo.download(destination_file=absolute_path)
    except Exception:
        # TODO: добавить логирование
        raise ImageProcessingException()
    else:
        return rel_image_path, absolute_path


def get_callback_data(code, obj_id):
    """Получение строки для callback_data

    :param code: Код события
    :param obj_id: id записи

    :return: Строка для параметра callbacK_data кнопки
    """
    return f'{code}_{obj_id}'


def get_obj_id_from_callback_data(callback_data):
    """Получение id записи из callback_data"""
    return int(callback_data.split('_')[-1])


async def create_person_info_from_message(message):
    """Создание анкеты пользователя из сообщения telegram

    :param message: Сообщение Telegram

    :return: Анкета пользователя
    """

    # Проверка на наличие документа
    if message.document:
        raise ApplicationLogicException(Messages.NEED_IMAGE_AS_PHOTO)

    text = message.text or message.caption or ''
    if not text:
        raise ApplicationLogicException(Messages.PERSON_INFORMATION_NOT_EXISTS)
    else:
        validation_error = PersonInfoValidator(text).validate()

    if message.photo:
        photo = message.photo[-1]
        image_params = dict(image_file_id=photo.file_id)
    else:
        no_photo_message = (
            f'{Messages.PHOTO_NOT_EXISTS}\n{validation_error}' if
            validation_error else Messages.PHOTO_NOT_EXISTS)

        raise ApplicationLogicException(no_photo_message)

    if validation_error:
        raise ApplicationLogicException(validation_error)

    person_info = await PersonInformation.create(
        text=text, user_id=message.from_user.id, **image_params)
    return person_info


async def send_message_to_channel(
        text: str,
        photo_file_id: Optional[str] = None,
        channel_username: str = CHANNEL_USERNAME
):
    """Отправка сообщения в телеграм канал

    :param text: Текст сообщения
    :param photo_file_id: id файла с фото или None, если его нет
    :param channel_username: Username канала, куда будет отправлено сообщение
    """
    from telegram_bot.bot import bot
    try:
        if photo_file_id:
            await bot.send_photo(
                channel_username, photo_file_id, caption=text)
        else:
            await bot.send_message(channel_username, text)
    except aiogram_exceptions.Unauthorized:
        raise ApplicationLogicException(Messages.BOT_NOT_AUTHORIZED_IN_CHANNEL)
    except aiogram_exceptions.NeedAdministratorRightsInTheChannel:
        raise ApplicationLogicException(Messages.BOT_NEED_ADMIN_RIGHTS)


async def cancel_action(message, state=None):
    """Отмена действий и вывод обычной клавиатуры с действиями."""
    await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)
    if state:
        await state.finish()


async def answer_with_actions_keyboard(message, text):
    """Обычный ответ на сообщение с выдачей клавиатуры действий"""

    # Пробуем обновить user_id для админов. user_id необходим для оповещения.
    if is_admin_message(message):
        await AdminUserId.get_or_create(
            username=message.from_user.username,
            defaults={'user_id': message.from_user.id}
        )

    await message.answer(
        text,
        **get_actions_kb_params(is_admin_message(message))
    )


async def check_return_or_start_cmd(message, state):
    """Проверка введенной команды для ключевых слов "Вернуться" и "/start"."""

    if message.text == BN.values[BN.RETURN]:
        await cancel_action(message, state)
        return True

    if message.text == f'/{START_COMMAND}':
        if state:
            await state.finish()
        await message.answer(Messages.START)
        await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)
        return True

    return False


@log_button_click
async def is_dialog_finished(message, state, dialog_partner_id):
    """Завершение диалога одним из пользователей."""

    from telegram_bot.bot import bot

    if (message.text == DialogConsts.CANCEL_DIALOG_BUTTON or
            message.text == BN.values[BN.SEARCH_STOP_BUTTON] or
            message.text == f'/{START_COMMAND}'):
        await message.answer(DialogConsts.LEFT_DIALOG)
        await state.finish()

        if message.text == f'/{START_COMMAND}':
            await message.answer(Messages.START)
        await answer_with_actions_keyboard(message, Messages.CHOOSE_ACTION)

        # Удаляем пользователя из поиска, если он решил остановить диалог
        await AnonymousDialog.filter(
            to_user_id__isnull=True, user_id=message.from_user.id
        ).delete()

        partner_dialog_state = Dispatcher.get_current().current_state(
            chat=dialog_partner_id, user=dialog_partner_id)
        if partner_dialog_state:
            partner_is_admin = await AdminUserId.filter(
                user_id=dialog_partner_id).exists()

            if dialog_partner_id:
                await bot.send_message(
                    dialog_partner_id, DialogConsts.PARTNER_LEFT_DIALOG
                )
                await bot.send_message(
                    dialog_partner_id, Messages.CHOOSE_ACTION,
                    **get_actions_kb_params(partner_is_admin)
                )
            await partner_dialog_state.finish()

        return True

    return False


class ToChannelResender:
    """Класс для переотправки сообщений в канал."""

    # Сообщение, если объект с id не будет найден
    obj_not_founded_message = ''
    # Сообщение, если объект уже ранее опубликовывался
    already_published_message = ''
    # Сообщение об успешной переотправке
    successful_message = ''
    # Модель переотправляемого объекта (анкета или история)
    model = None

    def __init__(self, obj_id, original_message):
        """
        :param obj_id: id отправляемого объекта в базе
        :param original_message: Оригинальное отправляемое сообщение, откуда
            будет браться текст и изображение
        """
        self.obj_id = obj_id
        self.original_message = original_message

    async def send(self):
        """Отправка сообщения в канал."""

        async with in_transaction():
            message = self.original_message
            obj = await self.model.filter(id=self.obj_id).first()
            if not obj:
                raise ApplicationLogicException(self.obj_not_founded_message)
            if obj.is_published:
                raise ApplicationLogicException(self.already_published_message)

            await send_message_to_channel(
                message.html_text,
                photo_file_id=message.photo[-1].file_id if
                message.photo else None
            )

            # Помечаем объект как отправленный
            obj.is_published = True
            await obj.save()

            await message.answer(self.successful_message)


class PersonInfoToChannelResender(ToChannelResender):
    """Класс для переотправки анкет в канал."""

    obj_not_founded_message = Messages.INFO_NOT_FOUNDED
    already_published_message = Messages.INFO_ALREADY_PUBLISHED
    successful_message = Messages.INFO_PUBLISHED_SUCCESSFULLY

    model = PersonInformation


class StoryToChannelResender(ToChannelResender):
    """Класс для переотправки историй в канал."""

    obj_not_founded_message = Messages.STORY_NOT_FOUNDED
    already_published_message = Messages.STORY_ALREADY_PUBLISHED
    successful_message = Messages.STORY_PUBLISHED_SUCCESSFULLY

    model = Story
