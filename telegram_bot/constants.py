from telegram_bot.settings import ADMIN_OBJS_COUNT_SETTING

START_COMMAND = 'start'

# Поле, котором хранится никнэйм пользователя
USERNAME_FIELD = 'username'
# Максимальная длина сообщения телеграм (найдено в интернете)
MAX_TELEGRAM_MESSAGE_LENGTH = 4096


class PersonInfoEnum:
    """Перечисление полей анкеты"""

    NAME_FIELD = 'name'
    AGE_FIELD = 'age'
    INTERESTS_FIELD = 'interests'
    ABOUT_FIELD = 'about'
    CONTACTS_FIELD = 'contacts'

    PERSON_INFO_FIELDS = {
        NAME_FIELD: 'Имя',
        AGE_FIELD: 'Возраст',
        INTERESTS_FIELD: 'Интересы',
        ABOUT_FIELD: 'О себе',
        CONTACTS_FIELD: 'Контакты',
    }

    PERSON_INFO_EXAMPLE = {
        PERSON_INFO_FIELDS[NAME_FIELD]: 'Павел',
        PERSON_INFO_FIELDS[AGE_FIELD]: '37',
        PERSON_INFO_FIELDS[INTERESTS_FIELD]:
            'Волейбол, квизы, настольные игры.',
        PERSON_INFO_FIELDS[ABOUT_FIELD]:
            'Создаю крутые вещи, в свободное время занимаюсь спортом. '
            'Люблю играть на гитаре. Ищу спутницу жизни :)',
        PERSON_INFO_FIELDS[CONTACTS_FIELD]: 'Telegram: @durov',
    }


class Messages:
    """Класс для хранения сообщений, которые используются в проекте."""

    # Стартовое сообщение
    START = (
        'Добро пожаловать. Вас приветствует бот от группы "Развлечения". '
        'Здесь вы можете оставить свою анкету, чтобы её выложили '
        'в телеграм канале https://t.me/znakomimsya_v_kazani '
        'и на вас обратили внимание, либо можете рассказывать интересные '
        'истории и наблюдения из вашей жизни.'
    )
    # Произошла ошибка
    ERROR = (
        'Произошла ошибка, повторите действие позже. Если ошибка будет '
        'повторяться, обратитесь к администратору'
    )
    # Неизвестное сообщение
    UNKNOWN_MESSAGE = 'Не понимаю вас :('

    # Возврат
    RETURN_TO_BEGINNING = 'Действие отменено'
    # Выбор действия
    CHOOSE_ACTION = 'Выберите действие, которое хотите выполнить'
    # Изображение необходимо отправлять правильно
    NEED_IMAGE_AS_PHOTO = (
        'Изображение должно быть отправлено в виде фотографии, а не документа')
    PERSON_INFORMATION_NOT_EXISTS = 'Не указан текст анкеты'
    PHOTO_NOT_EXISTS = 'Не добавлено фото к анкете'
    IMAGE_PROCESSING_ERROR = 'При обработке изображения произошла ошибка'
    BOT_NOT_AUTHORIZED_IN_CHANNEL = (
        'Бот должен состоять в канале, куда пересылаются анкеты и истории')
    BOT_NEED_ADMIN_RIGHTS = (
        'Бот должен иметь права администратора в канале, куда пересылаются '
        'анкеты и истории (для отправки сообщений)')

    # Сообщение для действий с историями
    SEND_STORY = (
        'Напишите интересную историю и отправьте сообщение. '
        'В случае успешного рассмотрения администратором вашей истории '
        'она будет выложена в телеграм канал.'
    )
    STORY_PROCESSED = 'Ваша история успешно сохранена'
    STORY_ALREADY_PUBLISHED = 'История уже была опубликована'
    STORY_NOT_FOUNDED = 'История не найдена в базе данных'
    STORY_PUBLISHED_SUCCESSFULLY = 'История успешно опубликована'
    STORY_NEED_TO_EDIT = 'Необходимо внести изменения в вашу историю:'

    person_info_example = f'\n'.join(
        f'*{key}: {value}*' for key, value in
        PersonInfoEnum.PERSON_INFO_EXAMPLE.items()
    )
    # Сообщение для действий с анкетами
    SEND_INFORMATION_FORM = (
        'Напишите информацию о себе, добавьте изображение и '
        'отправьте сообщение. '
        'В случае успешного рассмотрения администратором вашей анкеты '
        'она будет выложена в телеграм канал.\n\n'
        'Пример анкеты (но ваша креативность приветствуется!):'
        '\n{person_info_example}\n\n'
        'Ниже будет шаблон, который вы можете скопировать и заполнить'
    ).format(person_info_example=person_info_example)

    # Шаблон типовой анкеты
    INFORMATION_FORM_TEMPLATE = ':\n'.join(
        PersonInfoEnum.PERSON_INFO_FIELDS.values()) + ':'

    INFORMATION_FORM_PROCESSED = 'Ваша анкета успешно сохранена'
    INFO_ALREADY_PUBLISHED = 'Анкета уже была опубликована'
    INFO_NOT_FOUNDED = 'Анкета не найдена в базе данных'
    INFO_PUBLISHED_SUCCESSFULLY = 'Анкета успешно опубликована'
    INFO_NEED_TO_EDIT = 'Необходимо внести изменения в вашу анкету:'


class ButtonNames:
    """Названия кнопок."""
    SEND_INFORMATION_FORM = 'Отправить анкету'
    SEND_STORY = 'Отправить интересную историю'
    RETURN = 'Вернуться'


class AdminButtonNames:
    """Названия админских кнопок"""

    GET_STORIES = f'Получить {ADMIN_OBJS_COUNT_SETTING} историй'
    GET_PERSON_INFO = f'Получить {ADMIN_OBJS_COUNT_SETTING} анкет'

    APPROVE = 'Опубликовать'
    NEED_TO_EDIT = 'На исправление'
    DELETE = 'Удалить'

    APPROVE_STORY_CODE = 'approve_story'
    NEED_TO_EDIT_STORY_CODE = 'need_to_edit_story'
    DELETE_STORY_CODE = 'delete_story'
    STORIES_IS_EMPTY = 'Список историй пуст'

    APPROVE_PERSON_INFO_CODE = 'approve_user_info'
    NEED_TO_EDIT_PERSON_INFO_CODE = 'need_to_edit_user_info'
    DELETE_PERSON_INFO_CODE = 'delete_user_info'
    PERSON_INFOS_IS_EMPTY = 'Список анкет пуст'

    NEED_TO_EDIT_TO_ADMIN = (
        'Напишите свои замечания (что конкретно нужно исправить пользователю)')
    ADMIN_MSG_SENDED = 'Ваше замечание отправлено пользователю'

    ADMIN_ANSWER = '*[Ответ от администратора]*'

    ADMIN_KEYS = (
        GET_STORIES, GET_PERSON_INFO
    )

    SEND_SENTRY_ERROR_CMD = '/send_sentry_error'
