from telegram_bot.constants import Messages


class BaseProjectException(Exception):
    """Базовое исключение проекта."""
    pass


class ImproperlyConfigured(BaseProjectException):
    """Исключение о том, что проект неправильно сконфигурирован."""
    pass


class ApplicationLogicException(BaseProjectException):
    """Исключение с нарушений логики проекта."""
    pass


class ImageProcessingException(BaseProjectException):
    """Ошибка при обработке изображения"""
    def __init__(self, *args, **kwargs):
        if not args:
            args = (Messages.IMAGE_PROCESSING_ERROR,)
        super().__init__(*args, **kwargs)
