import os
import uuid
from datetime import date
from typing import Optional

from aiogram.types import PhotoSize
from aiogram.utils import exceptions as aiogram_exceptions
from telegram_bot.constants import Messages
from telegram_bot.exceptions import ApplicationLogicException
from telegram_bot.exceptions import ImageProcessingException
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from telegram_bot.settings import CHANNEL_USERNAME
from telegram_bot.settings import MEDIA_DIR
from telegram_bot.validators import PersonInfoValidator


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
        raise ApplicationLogicException(
            f'{Messages.PHOTO_NOT_EXISTS}\n{validation_error}')

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
        message = self.original_message
        obj = await self.model.filter(id=self.obj_id).first()
        if not obj:
            raise ApplicationLogicException(self.obj_not_founded_message)
        if obj.is_published:
            raise ApplicationLogicException(self.already_published_message)

        await send_message_to_channel(
            message.html_text,
            photo_file_id=message.photo[-1].file_id if message.photo else None
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
