from datetime import datetime

from pydantic import Field

from app.schemas.base import KlugBaseModel


class SessionLoginRequest(KlugBaseModel):
    password: str = Field(min_length=1)


class SessionLoginResponse(KlugBaseModel):
    authenticated: bool
    auth_mode: str
    expires_at: datetime | None = None


class SessionStatusResponse(KlugBaseModel):
    authenticated: bool
    auth_mode: str
    expires_at: datetime | None = None
