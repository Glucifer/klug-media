from __future__ import annotations

from hmac import compare_digest

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    provided_api_key: str | None = Depends(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    expected_api_key = settings.klug_api_key
    if not expected_api_key:
        return

    if provided_api_key and compare_digest(provided_api_key, expected_api_key):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )
