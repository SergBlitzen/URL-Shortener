from sqlalchemy.ext.asyncio import AsyncSession

from infra.repositories import SQLAShortLinkRepository


class SQLAlchemyUOW:

    def __init__(self, session: AsyncSession, short_link_repo: SQLAShortLinkRepository):
        self.session = session
        self.short_links = short_link_repo

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            await self.rollback()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
