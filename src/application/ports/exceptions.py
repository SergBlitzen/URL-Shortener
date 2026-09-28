class ApplicationError(Exception):
    pass


class ShortCodeConflict(ApplicationError):
    """Коллизия кода для укороченной ссылки"""
