import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from api.errors import register_exception_handlers
from api.router import router
from infra.database import engine
from infra.db.pool_monitor import PoolMonitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("LIFESPAN START", flush=True)

    pool_monitor = PoolMonitor(engine)
    print("MONITOR CREATED", flush=True)

    app.state.pool_monitor = pool_monitor

    task = asyncio.create_task(
        pool_monitor.run(interval=1.0)
    )

    try:
        yield
    finally:
        task.cancel()

        with suppress(asyncio.CancelledError):
            await task

        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="URL shortener",
        version="0.1.0",
        lifespan=lifespan
    )
    app.include_router(router)

    register_exception_handlers(app)

    return app


app = create_app()
