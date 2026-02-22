from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from app.core.datetime_utils import to_utc_z_string


class KlugBaseModel(BaseModel):
    @field_serializer("*", when_used="json", check_fields=False)
    def _serialize_datetimes(self, value: object) -> object:
        if isinstance(value, datetime):
            return to_utc_z_string(value)
        return value


class KlugORMModel(KlugBaseModel):
    model_config = ConfigDict(from_attributes=True)
