import os
import uuid
from datetime import date

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
