from telegram_bot.settings import ADMIN_OBJS_COUNT_SETTING


# Поле, котором хранится никнэйм пользователя
USERNAME_FIELD = 'username'
# Максимальная длина сообщения телеграм (найдено в интернете)
MAX_TELEGRAM_MESSAGE_LENGTH = 4096


class Messages:
    """Класс для хранения сообщений, которые используются в проекте."""

    # Стартовое сообщение
    START = (
        'Добро пожаловать. Вас приветствует бот от группы "Развлечения". '
        'Здесь вы можете оставить свою анкету, чтобы её выложили '
        'в телеграм канале и на вас обратили внимание, '
        'либо можете рассказывать интересные '
        'истории и наблюдения из вашей жизни'
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
    IMAGE_PROCESSING_ERROR = 'При обработке изображения произошла ошибка'
    BOT_NOT_AUTHORIZED_IN_CHANNEL = (
        'Бот должен состоять в канале, куда пересылются анкеты и истории')

    # Сообщение для действий с историями
    SEND_STORY = (
        'Напишите интересную историю и отправьте сообщение. '
        'В случае успешного рассмотрения администратором вашей анкеты '
        'она будет выложена в телеграм канал'
    )
    STORY_PROCESSED = 'Ваша история успешно сохранена'
    STORY_ALREADY_PUBLISHED = 'История уже была опубликована'
    STORY_NOT_FOUNDED = 'История не найдена в базе данных'
    STORY_PUBLISHED_SUCCESSFULLY = 'История успешно опубликована'

    # Сообщение для действий с анкетами
    SEND_INFORMATION_FORM = (
        'Напишите информацию о себе (можно приложить 1 изображение) и '
        'отправьте сообщение. '
        'В случае успешного рассмотрения администратором вашей анкеты '
        'она будет выложена в телеграм канал'
    )
    INFORMATION_FORM_PROCESSED = 'Ваша анкета успешно сохранена'
    INFO_ALREADY_PUBLISHED = 'Анкета уже была опубликована'
    INFO_NOT_FOUNDED = 'Анкета не найдена в базе данных'
    INFO_PUBLISHED_SUCCESSFULLY = 'Анкета успешно опубликована'


class ButtonNames:
    """Названия кнопок."""
    SEND_INFORMATION_FORM = 'Отправить анкету'
    SEND_STORY = 'Отправить интересную историю'
    RETURN = 'Вернуться'


class AdminButtonNames:
    """Названия админских кнопок"""

    GET_STORIES = f'Получить {ADMIN_OBJS_COUNT_SETTING} историй'
    GET_INFORMATION_FORMS = f'Получить {ADMIN_OBJS_COUNT_SETTING} анкет'

    APPROVE_STORY = 'Опубликовать историю'
    APPROVE_STORY_CODE = 'approve_story'
    STORIES_IS_EMPTY = 'Список историй пуст'
    DELETE_STORY = 'Удалить'
    DELETE_STORY_CODE = 'delete_story'

    APPROVE_PERSON_INFO = 'Опубликовать анкету'
    APPROVE_PERSON_INFO_CODE = 'approve_user_info'
    PERSON_INFOS_IS_EMPTY = 'Список анкет пуст'
    DELETE_PERSON_INFO = 'Удалить'
    DELETE_PERSON_INFO_CODE = 'delete_user_info'

    ADMIN_KEYS = (
        GET_STORIES, GET_INFORMATION_FORMS
    )
