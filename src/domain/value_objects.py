import string
from dataclasses import dataclass
from urllib.parse import urlparse

from domain.exceptions import InvalidUrlError, InvalidShortCodeError


SHORT_CODE_ALPHABET = frozenset(
    string.ascii_lowercase + string.digits
)
SHORT_CODE_LENGTH = 6


@dataclass(frozen=True)
class Url:
    value: str

    def __post_init__(self) -> None:
        try:
            parsed = urlparse(self.value)
        except (AttributeError, ValueError) as exc:
            raise InvalidUrlError(self.value) from exc

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
        ):
            raise InvalidUrlError(self.value)


@dataclass(frozen=True)
class ShortCode:
    value: str

    def __post_init__(self) -> None:
        if (
            len(self.value) != SHORT_CODE_LENGTH
            or any(
                char not in SHORT_CODE_ALPHABET
                for char in self.value
            )
        ):
            raise InvalidShortCodeError(self.value)
