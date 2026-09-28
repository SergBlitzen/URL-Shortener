import secrets
import string

import pytest

from application.ports.exceptions import ShortCodeConflict
from application.services import ShortLinkService
from domain.models import ShortLink


class FakeShortLinkRepository:

    def __init__(self):
        self.links = {}

    async def add(self, short_link: ShortLink) -> None:
        if short_link.code in self.links:
            raise ShortCodeConflict
        self.links[short_link.code] = short_link

    async def get_by_code(self, code: str) -> ShortLink | None:
        if code in self.links:
            return self.links[code]
        else:
            return None

    async def save(self, short_link) -> None:
        self.links[short_link.code] = short_link


class FakeUnitOfWork:

    def __init__(self):
        self.short_links = FakeShortLinkRepository()
        self.commited = False
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.closed = True

    async def commit(self) -> None:
        self.commited = True

    async def rollback(self) -> None:
        self.commited = False


class FakeSingleCodeGenerator:
    SHORT_CODE_ALPHABET = "a"
    SHORT_CODE_LENGTH = 6

    def generate(self):
        return "".join(
            secrets.choice(self.SHORT_CODE_ALPHABET)
            for _ in range(self.SHORT_CODE_LENGTH)
        )



@pytest.fixture
def uow():
    return FakeUnitOfWork()


@pytest.fixture
def short_link_service(uow):
    return ShortLinkService(uow=uow)


@pytest.fixture
def single_code_generator():
    return FakeSingleCodeGenerator()
