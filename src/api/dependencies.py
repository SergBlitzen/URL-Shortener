from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from application.services import ShortLinkService
from application.ports.uow import UnitOfWork
from infra.database import async_session_factory
from infra.repositories import SQLAShortLinkRepository
from infra.sqlalcmemy_uow import SQLAlchemyUOW


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_uow(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnitOfWork:
    short_link_repo = SQLAShortLinkRepository(session)

    return SQLAlchemyUOW(
        session=session,
        short_link_repo=short_link_repo,
    )


async def get_short_link_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> ShortLinkService:
    return ShortLinkService(uow)


ShortLinkServiceDep = Annotated[
    ShortLinkService,
    Depends(get_short_link_service)
]

ShortCodePath = Annotated[
    str,
    Path(
        min_length=6,
        max_length=6,
        pattern=r"^[A-Za-z0-9]+$",
    ),
]
