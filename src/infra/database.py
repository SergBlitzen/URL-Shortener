import asyncio
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from infra.db.pool_monitor import MonitoredSyncSession

engine = create_async_engine(
    settings.postgres_url,
    pool_size=15,
    max_overflow=0,
    pool_pre_ping=True,
)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    sync_session_class=MonitoredSyncSession,
)


async def get_async_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        yield session


async def monitor_pool():
    while True:
        print(
            f"pid={os.getpid()} "
            f"{engine.sync_engine.pool.status()}",
            flush=True
        )
        await asyncio.sleep(1)
