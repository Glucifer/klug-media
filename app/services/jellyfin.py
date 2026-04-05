from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings


class JellyfinConfigurationError(Exception):
    """Raised when Jellyfin client configuration is missing."""


class JellyfinClientError(Exception):
    """Raised when Jellyfin cannot be reached or returns invalid data."""


@dataclass(frozen=True)
class JellyfinLibrary:
    library_id: str
    name: str
    collection_type: str | None


@dataclass(frozen=True)
class JellyfinCollectionItem:
    source_item_id: str
    item_type: str
    library_id: str
    library_name: str
    title: str
    year: int | None
    tmdb_id: int | None
    imdb_id: str | None
    tvdb_id: int | None
    season_number: int | None
    episode_number: int | None
    show_source_item_id: str | None
    show_title: str | None
    show_year: int | None
    show_tmdb_id: int | None
    show_imdb_id: str | None
    show_tvdb_id: int | None
    added_at: datetime | None
    runtime_seconds: int | None
    file_path: str | None
    source_data: dict[str, Any]


class JellyfinClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_seconds: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = max(1, timeout_seconds)

    @classmethod
    def from_settings(cls) -> "JellyfinClient":
        settings = get_settings()
        if not settings.klug_jellyfin_base_url:
            raise JellyfinConfigurationError("KLUG_JELLYFIN_BASE_URL is not configured")
        if not settings.klug_jellyfin_api_key:
            raise JellyfinConfigurationError("KLUG_JELLYFIN_API_KEY is not configured")
        return cls(
            base_url=settings.klug_jellyfin_base_url,
            api_key=settings.klug_jellyfin_api_key,
            timeout_seconds=settings.klug_jellyfin_timeout_seconds,
        )

    def list_libraries(self) -> list[JellyfinLibrary]:
        payload = self._request_json("/Library/MediaFolders")
        items = payload.get("Items")
        if not isinstance(items, list):
            raise JellyfinClientError("Jellyfin library response did not include Items")

        libraries: list[JellyfinLibrary] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            library_id = raw.get("Id")
            name = raw.get("Name")
            if not isinstance(library_id, str) or not isinstance(name, str):
                continue
            collection_type = raw.get("CollectionType")
            libraries.append(
                JellyfinLibrary(
                    library_id=library_id,
                    name=name,
                    collection_type=collection_type if isinstance(collection_type, str) else None,
                )
            )
        return libraries

    def list_collection_items(self, *, library: JellyfinLibrary) -> list[JellyfinCollectionItem]:
        items: list[JellyfinCollectionItem] = []
        start_index = 0
        page_size = 200

        while True:
            payload = self._request_json(
                "/Items",
                params={
                    "parentId": library.library_id,
                    "recursive": "true",
                    "includeItemTypes": "Movie,Series,Episode",
                    "fields": "ProviderIds,Path,DateCreated,PremiereDate",
                    "startIndex": str(start_index),
                    "limit": str(page_size),
                },
            )
            raw_items = payload.get("Items")
            if not isinstance(raw_items, list):
                raise JellyfinClientError("Jellyfin items response did not include Items")

            parsed_items = [
                item
                for item in (
                    self._parse_collection_item(raw, library=library) for raw in raw_items
                )
                if item is not None
            ]
            items.extend(parsed_items)
            if len(raw_items) < page_size:
                break
            start_index += page_size

        return items

    def _request_json(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        headers = {
            "X-Emby-Token": self._api_key,
            "Accept": "application/json",
        }
        with httpx.Client(timeout=float(self._timeout_seconds)) as client:
            try:
                response = client.get(f"{self._base_url}{path}", params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
            except httpx.HTTPStatusError as exc:
                raise JellyfinClientError(
                    f"Jellyfin request failed with status {exc.response.status_code}"
                ) from exc
            except httpx.RequestError as exc:
                raise JellyfinClientError(
                    f"Jellyfin request failed: {exc.__class__.__name__}"
                ) from exc
            except ValueError as exc:
                raise JellyfinClientError("Jellyfin response was not valid JSON") from exc

        if not isinstance(payload, dict):
            raise JellyfinClientError("Jellyfin response payload must be an object")
        return payload

    def _parse_collection_item(
        self,
        raw: dict[str, Any],
        *,
        library: JellyfinLibrary,
    ) -> JellyfinCollectionItem | None:
        source_item_id = raw.get("Id")
        item_type = raw.get("Type")
        title = raw.get("Name")
        if not isinstance(source_item_id, str) or not isinstance(item_type, str):
            return None
        if item_type not in {"Movie", "Series", "Episode"}:
            return None

        provider_ids = raw.get("ProviderIds") if isinstance(raw.get("ProviderIds"), dict) else {}
        added_at = _parse_datetime(raw.get("DateCreated"))
        runtime_ticks = raw.get("RunTimeTicks")
        runtime_seconds = (
            int(runtime_ticks) // 10_000_000 if isinstance(runtime_ticks, int) else None
        )

        return JellyfinCollectionItem(
            source_item_id=source_item_id,
            item_type={"Movie": "movie", "Series": "show", "Episode": "episode"}[item_type],
            library_id=library.library_id,
            library_name=library.name,
            title=title.strip() if isinstance(title, str) and title.strip() else source_item_id,
            year=_coerce_year(raw.get("ProductionYear"), raw.get("PremiereDate")),
            tmdb_id=_parse_int(provider_ids.get("Tmdb")),
            imdb_id=_parse_text(provider_ids.get("Imdb")),
            tvdb_id=_parse_int(provider_ids.get("Tvdb")),
            season_number=_parse_int(raw.get("ParentIndexNumber")),
            episode_number=_parse_int(raw.get("IndexNumber")),
            show_source_item_id=_parse_text(raw.get("SeriesId")),
            show_title=_parse_text(raw.get("SeriesName")),
            show_year=_coerce_year(raw.get("SeriesProductionYear"), None),
            show_tmdb_id=_parse_int(provider_ids.get("SeriesTmdb")),
            show_imdb_id=_parse_text(provider_ids.get("SeriesImdb")),
            show_tvdb_id=_parse_int(provider_ids.get("SeriesTvdb")),
            added_at=added_at,
            runtime_seconds=runtime_seconds,
            file_path=_parse_text(raw.get("Path")),
            source_data={
                "provider_ids": provider_ids,
                "date_created": added_at.isoformat() if added_at else None,
                "premiere_date": _parse_text(raw.get("PremiereDate")),
                "series_id": _parse_text(raw.get("SeriesId")),
            },
        )


def _parse_text(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _parse_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _coerce_year(year_value: object, premiere_date: object) -> int | None:
    if isinstance(year_value, int):
        return year_value
    parsed = _parse_datetime(premiere_date)
    return parsed.year if parsed is not None else None
