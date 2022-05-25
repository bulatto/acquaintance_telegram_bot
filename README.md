# acquaintance_telegram_bot
Telegram бот для сбора интересных историй и анкет для знакомств


# Первый запуск
- Склонировать проект с github
- Создать виртуальное окружение python 3.9
- Установить пакеты в виртуальное окружение проекта
  - Активировать виртуальное окружение
  - pip install requirements.txt
- Создать таблицу в базе данных
- Настроить redis 
- Зайти в папку проекта - `cd acquaintance_telegram_bot`
- Заполнить файл конфигурации проекта `telegram_bot.conf` (в качестве примера
можно взять файл `default.conf`)
- Установить переменные окружения:
  - export CONFIG_PATH=`путь_до_папки_где_находится_файл_конфигурации_проекта`
  - export PYTHONPATH=`путь_до_папки_acquaintance_telegram_bot`
- Выполнить команду для выполнения миграций в бд: `aerich migrate`
- Выполнить команду: `python telegram_bot/bot.py`


## Настройка redis на сервере
- sudo apt update
- sudo apt install redis-server -y
- sudo nano /etc/redis/redis.conf
  - "supervised no" поменять на "supervised systemd"
  - Расскомментировать "requirepass foobared", вместо "foobared" поставить 
    свой пароль
  - Сохранить
- sudo systemctl restart redis.service


# Полезная информация для разработчиков
- Команда инициализации базы и миграций - `aerich init-db`
- Команда создания файла миграций - `aerich migrate`
- Команда применения миграций - `aerich upgrade`
