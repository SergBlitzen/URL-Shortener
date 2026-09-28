from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.ports.exceptions import ShortCodeConflict
from domain.models import ShortLink
from domain.value_objects import Url, ShortCode
from infra.errors import is_short_link_code_conflict
from infra.orm import ShortLinkORM


class SQLAShortLinkRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
            self,
            short_link: ShortLink,
    ) -> None:
        orm = self._to_orm(short_link)

        self.session.add(orm)

        try:
            await self.session.flush()

        except IntegrityError as exc:
            if is_short_link_code_conflict(exc):
                raise ShortCodeConflict from exc

            raise

    async def get_by_code(
        self,
        code: str,
    ) -> ShortLink | None:
        query = (select(ShortLinkORM)
                 .where(ShortLinkORM.code == code))

        result = await self.session.scalars(query)
        short_link_orm = result.one_or_none()

        if short_link_orm is not None:
            return self._from_orm(short_link_orm)
        else:
            return None

    async def save(
        self,
        short_link: ShortLink,
    ):
        query = (select(ShortLinkORM)
                 .where(ShortLinkORM.external_id == short_link.id))

        result = await self.session.scalars(query)
        short_link_orm = result.one_or_none()

        short_link_orm.clicks_count = short_link.clicks_count
        self.session.add(short_link_orm)

    @staticmethod
    def _to_orm(short_link: ShortLink) -> ShortLinkORM:
        return ShortLinkORM(
            external_id=short_link.id,
            url=short_link.url.value,
            code=short_link.code.value,
            clicks_count=short_link.clicks_count,
        )

    @staticmethod
    def _from_orm(short_link_orm: ShortLinkORM) -> ShortLink:
        return ShortLink(
            id=short_link_orm.external_id,
            url=Url(short_link_orm.url),
            code=ShortCode(short_link_orm.code),
            clicks_count=short_link_orm.clicks_count,
        )
