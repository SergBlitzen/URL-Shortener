from typing import Protocol

from domain.models import ShortLink


class ShortLinkRepository(Protocol):

    async def add(self, short_link: ShortLink) -> None: ...

    async def get_by_code(self, code: str) -> ShortLink | None: ...

    async def save(self, short_link: ShortLink) -> None: ...


class UnitOfWork(Protocol):
    short_links: ShortLinkRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
