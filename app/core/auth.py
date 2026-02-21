from __future__ import annotations

import base64
import hashlib
import hmac
import json
from hmac import compare_digest
from time import time
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
SESSION_COOKIE_NAME = "klug_session"


def _is_request_auth_required(request: Request, settings: Settings) -> bool:
    if settings.klug_api_auth_mode == "disabled":
        return False
    if settings.klug_api_auth_mode == "all":
        return True
    return request.method in {"POST", "PUT", "PATCH", "DELETE"}


def _session_secret(settings: Settings) -> str | None:
    return settings.klug_session_secret or settings.klug_session_password


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def _sign(value: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256)
    return _b64url_encode(digest.digest())


def _build_session_payload(*, ttl_seconds: int) -> dict[str, Any]:
    now = int(time())
    return {
        "sub": "local_session",
        "iat": now,
        "exp": now + ttl_seconds,
    }


def create_session_token(*, secret: str, ttl_seconds: int) -> tuple[str, int]:
    payload = _build_session_payload(ttl_seconds=ttl_seconds)
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    encoded_payload = _b64url_encode(payload_json.encode("utf-8"))
    signature = _sign(encoded_payload, secret)
    return f"{encoded_payload}.{signature}", int(payload["exp"])


def decode_session_token(*, token: str, secret: str) -> dict[str, Any] | None:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError:
        return None

    expected_signature = _sign(encoded_payload, secret)
    if not compare_digest(signature, expected_signature):
        return None

    try:
        payload_raw = _b64url_decode(encoded_payload)
        payload = json.loads(payload_raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None
    return payload


def is_session_authenticated(request: Request, settings: Settings) -> bool:
    secret = _session_secret(settings)
    if not secret:
        return False

    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return False

    payload = decode_session_token(token=token, secret=secret)
    if payload is None:
        return False

    exp = payload.get("exp")
    if not isinstance(exp, int):
        return False
    return exp > int(time())


def get_session_expiration_epoch(request: Request, settings: Settings) -> int | None:
    secret = _session_secret(settings)
    if not secret:
        return None
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    payload = decode_session_token(token=token, secret=secret)
    if payload is None:
        return None
    exp = payload.get("exp")
    if not isinstance(exp, int):
        return None
    return exp


def require_request_auth(
    request: Request,
    provided_api_key: str | None = Depends(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    if not _is_request_auth_required(request, settings):
        return

    expected_api_key = settings.klug_api_key
    secret = _session_secret(settings)

    # If no credential mechanism is configured, keep local-dev permissive behavior.
    if not expected_api_key and not secret:
        return

    if expected_api_key and provided_api_key and compare_digest(provided_api_key, expected_api_key):
        return

    if is_session_authenticated(request, settings):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
    )
