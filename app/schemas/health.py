from app.schemas.base import KlugBaseModel


class HealthResponse(KlugBaseModel):
    status: str
    service: str
