import uuid
from dataclasses import dataclass

from domain.value_objects import Url, ShortCode


@dataclass(eq=False)
class ShortLink:
    id: uuid.UUID
    url: Url
    code: ShortCode
    clicks_count: int = 0

    @classmethod
    def create(
        cls,
        url: str,
        code: str,
    ):
        return cls(
            id=uuid.uuid4(),
            url=Url(url),
            code=ShortCode(code),
        )

    def register_click(self):
        self.clicks_count += 1
