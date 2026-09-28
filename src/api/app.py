from fastapi import FastAPI

from api.errors import register_exception_handlers
from api.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="URL shortener",
        version="0.1.0"
    )
    app.include_router(router)

    register_exception_handlers(app)

    return app


app = create_app()
