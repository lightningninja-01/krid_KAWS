"""
Global exception handlers, registered once on the FastAPI app in main.py.

Ensures every AppException subclass returns a consistent JSON error shape
instead of leaking stack traces, and that truly unexpected exceptions are
logged with full context before returning a generic 500 to the client.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import AppException
from app.utils.logger import get_logger

log = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        log.warning(
            f"Handled application exception on {request.url.path}: {exc.message}",
            extra={"status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        log.error(f"Unhandled exception on {request.url.path}: {exc!r}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "message": "An unexpected error occurred."},
        )
