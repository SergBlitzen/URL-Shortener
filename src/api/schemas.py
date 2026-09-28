from pydantic import BaseModel

from domain.models import ShortLink


class ShortLinkCreate(BaseModel):
    url: str


class ShortLinkCode(BaseModel):
    code: str

    @classmethod
    def from_domain(cls, short_link: ShortLink) -> "ShortLinkCode":
        return cls(
            code=short_link.code.value,
        )
