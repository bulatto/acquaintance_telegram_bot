class ImproperlyConfigured(Exception):
    """Исключение о том, что проект неправильно сконфигурирован."""
    pass


class ApplicationLogicException(Exception):
    """Исключение с нарушений логики проекта."""
    pass
