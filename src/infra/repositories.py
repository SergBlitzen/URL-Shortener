from sqlalchemy import select, update
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

    async def get_by_code_and_update_clicks(
        self,
        code: str
    ) -> ShortLink | None:
        stmt = (update(ShortLinkORM)
                .where(ShortLinkORM.code == code)
                .values(clicks_count=ShortLinkORM.clicks_count + 1)
                ).returning(
            ShortLinkORM.external_id,
            ShortLinkORM.url,
            ShortLinkORM.code,
            ShortLinkORM.clicks_count
        )

        result = await self.session.execute(stmt)
        short_link_data = result.fetchone()
        short_link = ShortLink(
            id=short_link_data[0],
            url=Url(short_link_data[1]),
            code=ShortCode(short_link_data[2]),
            clicks_count=short_link_data[3],
        )

        return short_link

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
