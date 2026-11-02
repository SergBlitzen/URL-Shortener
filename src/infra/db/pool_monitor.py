from __future__ import annotations

import asyncio
import logging
import os
import statistics
import time
from collections import deque, defaultdict

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn.error")


class MonitoredSyncSession(Session):
    pass


class PoolMonitor:
    def __init__(
        self,
        engine: AsyncEngine,
        *,
        window_size: int = 10_000,
    ) -> None:
        self.engine = engine

        self.checked_out = 0
        self.max_checked_out = 0

        self.hold_times_ms: deque[float] = deque(maxlen=window_size)
        self.acquire_times_ms: deque[float] = deque(maxlen=window_size)
        self.query_times_ms = defaultdict(
            lambda: deque(maxlen=10_000)
        )
        self.commit_times_ms = deque(maxlen=10_000)
        self.rollback_times_ms = deque(maxlen=10_000)

        self._install_events()

    def _install_events(self) -> None:
        sync_engine = self.engine.sync_engine

        @event.listens_for(sync_engine, "checkout")
        def on_checkout(
            dbapi_connection,
            connection_record,
            connection_proxy,
        ) -> None:
            self.checked_out += 1
            self.max_checked_out = max(
                self.max_checked_out,
                self.checked_out,
            )

            connection_record.info["monitor_checkout_at"] = (
                time.perf_counter()
            )

        @event.listens_for(sync_engine, "checkin")
        def on_checkin(
            dbapi_connection,
            connection_record,
        ) -> None:
            self.checked_out -= 1

            started_at = connection_record.info.pop(
                "monitor_checkout_at",
                None,
            )

            if started_at is None:
                return

            duration_ms = (
                time.perf_counter() - started_at
            ) * 1000

            self.hold_times_ms.append(duration_ms)

        @event.listens_for(
            self.engine.sync_engine,
            "before_cursor_execute",
        )
        def before_cursor_execute(
                conn,
                cursor,
                statement,
                parameters,
                context,
                executemany,
        ):
            context._monitor_query_started_at = time.perf_counter()

            context._monitor_query_type = (
                statement.lstrip().split(maxsplit=1)[0].upper()
            )

        @event.listens_for(
            self.engine.sync_engine,
            "after_cursor_execute",
        )
        def after_cursor_execute(
                conn,
                cursor,
                statement,
                parameters,
                context,
                executemany,
        ):
            started = getattr(
                context,
                "_monitor_query_started_at",
                None,
            )

            if started is None:
                return

            duration_ms = (time.perf_counter() - started) * 1000

            query_type = context._monitor_query_type

            self.query_times_ms[query_type].append(duration_ms)

        @event.listens_for(MonitoredSyncSession, "before_commit")
        def on_before_commit(session):
            session.info["_monitor_commit_started_at"] = (
                time.perf_counter()
            )

        @event.listens_for(MonitoredSyncSession, "after_commit")
        def on_after_commit(session):
            started = session.info.pop(
                "_monitor_commit_started_at",
                None,
            )

            if started is None:
                return

            duration_ms = (time.perf_counter() - started) * 1000

            self.commit_times_ms.append(duration_ms)

    def record_acquire(self, duration_ms: float) -> None:
        self.acquire_times_ms.append(duration_ms)

    async def run(self, interval: float = 1.0) -> None:
        while True:
            self.log_snapshot()
            await asyncio.sleep(interval)

    def log_snapshot(self) -> None:
        pool = self.engine.sync_engine.pool

        logger.info(
            "DB pool metrics pid=%s checked_out=%s "
            "max_checked_out=%s "
            "pool=%s "
            "hold=%s "
            "acquire=%s",
            os.getpid(),
            self.checked_out,
            self.max_checked_out,
            pool.status(),
            self._stats(self.hold_times_ms),
            self._stats(self.acquire_times_ms),
        )

        query_stats = {
            query_type: self._stats(times)
            for query_type, times in self.query_times_ms.items()
        }

        logger.info(
            "DB timings pid=%s query=%s commit=%s rollback=%s",
            os.getpid(),
            query_stats,
            self._stats(self.commit_times_ms),
            self._stats(self.rollback_times_ms),
        )

    @staticmethod
    def _stats(values: deque[float]) -> dict[str, float | int]:
        if not values:
            return {
                "count": 0,
            }

        data = sorted(values)

        return {
            "count": len(data),
            "p50_ms": round(_percentile(data, 0.50), 2),
            "p95_ms": round(_percentile(data, 0.95), 2),
            "p99_ms": round(_percentile(data, 0.99), 2),
            "max_ms": round(max(data), 2),
            "avg_ms": round(statistics.fmean(data), 2),
        }


def _percentile(
    sorted_values: list[float],
    percentile: float,
) -> float:
    if not sorted_values:
        return 0.0

    index = int(
        (len(sorted_values) - 1) * percentile
    )

    return sorted_values[index]