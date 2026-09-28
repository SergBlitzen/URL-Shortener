from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from application.exceptions import ShortLinkCreationFailed, ShortLinkNotFound


def register_exception_handlers(app: FastAPI) -> None:


    @app.exception_handler(ShortLinkNotFound)
    async def handle_not_found_url(
        request: Request,
        exc: ShortLinkNotFound,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "detail": "URL not found"
            }
        )

    @app.exception_handler(ShortLinkCreationFailed)
    async def handle_create_failure(
        request: Request,
        exc: ShortLinkCreationFailed,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Short link creation failure"
            }
        )
