from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.frontend import WEB_ROOT, router as frontend_router
from app.api.health import router as health_router
from app.api.horrorfest import router as horrorfest_router
from app.api.imports import router as imports_router
from app.api.import_batches import router as import_batches_router
from app.api.library import router as library_router
from app.api.metadata_enrichment import router as metadata_enrichment_router
from app.api.media_items import router as media_items_router
from app.api.playback_events import router as playback_events_router
from app.api.scrobble_activity import router as scrobble_activity_router
from app.api.session import router as session_router
from app.api.shows import router as shows_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router
from app.api.watch_events import router as watch_events_router
from app.api.webhooks import router as webhooks_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Klug Media API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.mount("/web", StaticFiles(directory=WEB_ROOT), name="web")
    app.include_router(frontend_router)
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(horrorfest_router, prefix=settings.api_v1_prefix)
    app.include_router(session_router, prefix=settings.api_v1_prefix)
    app.include_router(stats_router, prefix=settings.api_v1_prefix)
    app.include_router(imports_router, prefix=settings.api_v1_prefix)
    app.include_router(import_batches_router, prefix=settings.api_v1_prefix)
    app.include_router(library_router, prefix=settings.api_v1_prefix)
    app.include_router(metadata_enrichment_router, prefix=settings.api_v1_prefix)
    app.include_router(users_router, prefix=settings.api_v1_prefix)
    app.include_router(shows_router, prefix=settings.api_v1_prefix)
    app.include_router(media_items_router, prefix=settings.api_v1_prefix)
    app.include_router(playback_events_router, prefix=settings.api_v1_prefix)
    app.include_router(scrobble_activity_router, prefix=settings.api_v1_prefix)
    app.include_router(watch_events_router, prefix=settings.api_v1_prefix)
    app.include_router(webhooks_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
