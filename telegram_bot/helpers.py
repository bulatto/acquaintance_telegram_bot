import os
import uuid
from datetime import date
from functools import partial

from aiogram.types import PhotoSize

from telegram_bot.constants import AdminButtonNames, Messages
from telegram_bot.exceptions import ImageProcessingException, \
    ApplicationLogicException
from telegram_bot.models import PersonInformation
from telegram_bot.settings import MEDIA_DIR


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


get_story_callback_data = partial(
    get_callback_data, AdminButtonNames.APPROVE_STORY_CODE)
get_person_info_callback_data = partial(
    get_callback_data, AdminButtonNames.APPROVE_PERSON_INFO_CODE)


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

    if message.photo:
        photo = message.photo[-1]
        image_params = dict(image_file_id=photo.file_id)
    else:
        image_params = {}

    person_info = await PersonInformation.create(text=text, **image_params)
    return person_info
