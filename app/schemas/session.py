from datetime import datetime

from pydantic import BaseModel, Field


class SessionLoginRequest(BaseModel):
    password: str = Field(min_length=1)


class SessionLoginResponse(BaseModel):
    authenticated: bool
    auth_mode: str
    expires_at: datetime | None = None


class SessionStatusResponse(BaseModel):
    authenticated: bool
    auth_mode: str
    expires_at: datetime | None = None
