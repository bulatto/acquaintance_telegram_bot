import os
from configparser import ConfigParser
from pathlib import Path

from telegram_bot.exceptions import ImproperlyConfigured


# Название переменной с путем до папки с конфигурациями
CONFIG_ENV_VAR = 'CONFIG_PATH'
# Название файла с конфигурацией бота
CONFING_FILE_NAME = 'telegram_bot.conf'


CONFIG_PATH = os.getenv(CONFIG_ENV_VAR)
if not CONFIG_PATH:
    raise ImproperlyConfigured(
        f'{CONFIG_ENV_VAR} переменная окружения должна быть установлена!')

CONFIG_PATH = Path(CONFIG_PATH).resolve()
if not CONFIG_PATH.exists() or not CONFIG_PATH.is_dir():
    raise ImproperlyConfigured(
        f'В переменной окружения {CONFIG_ENV_VAR} находится некорректный путь')

CONFIG_FILE_PATH = CONFIG_PATH.joinpath(CONFING_FILE_NAME)
if not CONFIG_FILE_PATH.exists():
    raise ImproperlyConfigured(
        f'Конфигурационный файл "{CONFING_FILE_NAME}" не существует')

# Папка, где будут храниться все файлы
MEDIA_DIR = CONFIG_PATH.joinpath('media/')
if not MEDIA_DIR.exists():
    MEDIA_DIR.mkdir(parents=True)


CONF_FILES = [
    CONFIG_FILE_PATH,
]

# Секция с данными базы
DB_SECTION_NAME = 'database'


# Конфигурация проекта
conf = ConfigParser()
conf.read(CONF_FILES)

# Название секции в настройках
TELEGRAM_BOT_SECTION = 'telegram_bot'

telegram_bot_section = conf[TELEGRAM_BOT_SECTION]
DB_SECTION = conf[DB_SECTION_NAME]

# Токен телеграм бота
TOKEN = telegram_bot_section.get('TOKEN')
if not TOKEN:
    raise ImproperlyConfigured(
        f'Не задан токен телеграмма ([{TELEGRAM_BOT_SECTION}] TOKEN)')


# Разрешение изображения из telegram
TELEGRAM_IMAGE_SUFFIX = '.jpg'


# Параметры подключения к бд
DB_HOST = DB_SECTION.get('HOST', fallback='127.0.0.1')
DB_PORT = DB_SECTION.get('PORT', fallback='5432')
DB_NAME = DB_SECTION.get('NAME', fallback='database_name')
DB_USER = DB_SECTION.get('USER', fallback='user')
DB_PASSWORD = DB_SECTION.get('PASSWORD', fallback='password')
POSTGRES_URI = (
    f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["telegram_bot.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

# Никнеймы телеграм пользователей, у которых будут больше действий с ботом
# Перечислять через ;
ADMINS_USERNAMES = telegram_bot_section.get(
    'ADMINS_USERNAMES').strip().split(';')
