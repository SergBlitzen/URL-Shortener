class DomainError(Exception):
    pass


class InvalidUrlError(DomainError):
    """Введённый URL не является корректным"""


class InvalidShortCodeError(DomainError):
    """Короткая ссылка не является валидным кодом"""
