from datetime import UTC, datetime


def ensure_timezone_aware(value: datetime, *, field_name: str) -> datetime:
    """Reject naive datetimes so callers must send timezone-aware values."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone information")
    return value


def to_utc_z_string(value: datetime) -> str:
    """Serialize datetimes as UTC ISO-8601 with trailing Z."""
    aware_value = ensure_timezone_aware(value, field_name="datetime")
    return aware_value.astimezone(UTC).isoformat().replace("+00:00", "Z")
