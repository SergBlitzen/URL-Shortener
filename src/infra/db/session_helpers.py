import time

from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.pool_monitor import PoolMonitor


async def acquire_connection(
    session: AsyncSession,
    pool_monitor: PoolMonitor | None,
):
    if pool_monitor:
        started_at = time.perf_counter()

        connection = await session.connection()

        duration_ms = (
            time.perf_counter() - started_at
        ) * 1000

        pool_monitor.record_acquire(duration_ms)

        return connection

    return session


async def timed_rollback(
    session: AsyncSession,
    monitor: PoolMonitor | None,
):
    if not monitor:
        return

    started = time.perf_counter()

    try:
        await session.rollback()
    finally:
        duration_ms = (
            time.perf_counter() - started
        ) * 1000

        monitor.rollback_times_ms.append(duration_ms)
