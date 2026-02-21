from __future__ import annotations

from datetime import UTC, datetime
from hmac import compare_digest

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.auth import (
    SESSION_COOKIE_NAME,
    create_session_token,
    get_session_expiration_epoch,
    is_session_authenticated,
)
from app.core.config import Settings, get_settings
from app.schemas.session import (
    SessionLoginRequest,
    SessionLoginResponse,
    SessionStatusResponse,
)

router = APIRouter(prefix="/session", tags=["session"])


def _session_secret(settings: Settings) -> str:
    if settings.klug_session_secret:
        return settings.klug_session_secret
    if settings.klug_session_password:
        return settings.klug_session_password
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Session authentication is not configured",
    )


def _expires_at_from_epoch(value: int | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=UTC)


@router.post("/login", response_model=SessionLoginResponse)
def login(
    payload: SessionLoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
) -> SessionLoginResponse:
    configured_password = settings.klug_session_password
    if not configured_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session login is not configured",
        )

    if not compare_digest(payload.password, configured_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session credentials",
        )

    token, exp = create_session_token(
        secret=_session_secret(settings),
        ttl_seconds=settings.klug_session_ttl_seconds,
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.klug_session_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "prod",
    )
    return SessionLoginResponse(
        authenticated=True,
        auth_mode=settings.klug_api_auth_mode,
        expires_at=_expires_at_from_epoch(exp),
    )


@router.delete("/logout", response_model=SessionStatusResponse)
def logout(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> SessionStatusResponse:
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return SessionStatusResponse(
        authenticated=False,
        auth_mode=settings.klug_api_auth_mode,
        expires_at=None,
    )


@router.get("/me", response_model=SessionStatusResponse)
def me(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> SessionStatusResponse:
    authenticated = is_session_authenticated(request, settings)
    expires_at = _expires_at_from_epoch(get_session_expiration_epoch(request, settings))
    return SessionStatusResponse(
        authenticated=authenticated,
        auth_mode=settings.klug_api_auth_mode,
        expires_at=expires_at if authenticated else None,
    )
