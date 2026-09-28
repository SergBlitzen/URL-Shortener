import secrets
import string
from typing import Protocol


class CodeGenerator(Protocol):
    def generate(self) -> str: ...


class ShortCodeGenerator:
    SHORT_CODE_ALPHABET = string.ascii_lowercase + string.digits
    SHORT_CODE_LENGTH = 6

    def generate(self):
        return "".join(
            secrets.choice(self.SHORT_CODE_ALPHABET)
            for _ in range(self.SHORT_CODE_LENGTH)
        )
