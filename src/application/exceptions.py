class ApplicationError(Exception):
    pass


class ShortLinkNotFound(ApplicationError):
    """URL не найден"""


class ShortLinkCreationFailed(ApplicationError):
    """Ошибка создания короткой ссылки"""
