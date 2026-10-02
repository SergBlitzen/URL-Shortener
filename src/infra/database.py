import asyncio
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings


engine = create_async_engine(
    settings.postgres_url,
    pool_pre_ping=True,
)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        yield session


async def monitor_pool():
    while True:
        print(
            f"pid={os.getpid()} "
            f"{engine.sync_engine.pool.status()}"
        )
        await asyncio.sleep(1)
