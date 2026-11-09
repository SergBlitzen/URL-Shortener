from application.exceptions import (
    ShortLinkCreationFailed,
    ShortLinkNotFound,
)
from application.ports.exceptions import ShortCodeConflict
from application.ports.uow import UnitOfWork
from application.ports.utils import ShortCodeGenerator
from domain.exceptions import InvalidUrlError
from domain.models import ShortLink
from infra.db.pool_monitor import PoolMonitor
from infra.db.session_helpers import acquire_connection, timed_rollback


class ShortLinkService:
    MAX_CREATE_ATTEMPTS = 3
    CODE_GENERATOR = ShortCodeGenerator()

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_short_link(
        self,
        url: str,
        pool_monitor: PoolMonitor | None = None,
    ) -> ShortLink:

        async with self.uow as uow:
            uow.session = await acquire_connection(
                uow.session,
                pool_monitor,
            )

            for _ in range(self.MAX_CREATE_ATTEMPTS):
                try:
                    code = self.CODE_GENERATOR.generate()
                    short_link = ShortLink.create(
                        url=url,
                        code=code,
                    )
                except InvalidUrlError as exc:
                    raise ShortLinkCreationFailed("Неверный URL") from exc

                try:
                    await uow.short_links.add(short_link)
                    await uow.commit()

                    return short_link

                except ShortCodeConflict:
                    await timed_rollback(
                        uow.session,
                        pool_monitor,
                    )
                    await uow.rollback()

            raise ShortLinkCreationFailed()

    async def get_by_code(
        self,
        code: str,
        pool_monitor: PoolMonitor | None = None,
    ) -> ShortLink:

        async with self.uow as uow:
            uow.session = await acquire_connection(
                uow.session,
                pool_monitor,
            )
            short_link = await uow.short_links.get_by_code_and_update_clicks(code)

            if short_link is None:
                raise ShortLinkNotFound(code)

            short_link.register_click()
            await uow.short_links.save(short_link)
            await uow.commit()

            return short_link
