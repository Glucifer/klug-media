from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.media_items import router as media_items_router
from app.api.users import router as users_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Klug Media API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(users_router, prefix=settings.api_v1_prefix)
    app.include_router(media_items_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
