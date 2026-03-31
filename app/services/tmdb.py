from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories import tmdb_metadata_cache as tmdb_cache_repository


class TmdbConfigurationError(Exception):
    """Raised when TMDB client configuration is missing."""


class TmdbLookupError(Exception):
    """Raised when TMDB cannot resolve a requested identifier."""


@dataclass(frozen=True)
class TmdbFindResult:
    tmdb_id: int
    media_type: str
    payload: dict[str, Any]
    resolved_show_tmdb_id: int | None = None


class TmdbService:
    BASE_URL = "https://api.themoviedb.org/3"

    @staticmethod
    def is_enabled() -> bool:
        settings = get_settings()
        return settings.klug_metadata_enrichment_enabled and bool(
            settings.klug_tmdb_api_key
        )

    @staticmethod
    def find_by_external_id(
        session: Session,
        *,
        external_id: str | int,
        external_source: str,
        media_type: str,
    ) -> TmdbFindResult:
        payload = TmdbService._request_json(
            session,
            tmdb_type="find",
            tmdb_id=TmdbService._cache_key_id(external_id),
            sub_key=f"{external_source}:{media_type}",
            url_path=f"/find/{external_id}",
            params={"external_source": external_source},
        )
        if media_type == "movie":
            results = payload.get("movie_results")
            if not isinstance(results, list) or not results:
                raise TmdbLookupError(
                    f"TMDB /find returned no {media_type} result for {external_source}"
                )
            first = results[0]
            tmdb_id = first.get("id")
            if not isinstance(tmdb_id, int):
                raise TmdbLookupError("TMDB /find result did not include an integer id")
            return TmdbFindResult(
                tmdb_id=tmdb_id,
                media_type=media_type,
                payload=first,
            )

        tv_results = payload.get("tv_results")
        if isinstance(tv_results, list) and tv_results:
            first = tv_results[0]
            tmdb_id = first.get("id")
            if not isinstance(tmdb_id, int):
                raise TmdbLookupError("TMDB /find tv result did not include an integer id")
            return TmdbFindResult(
                tmdb_id=tmdb_id,
                media_type="tv",
                payload=first,
                resolved_show_tmdb_id=tmdb_id,
            )

        tv_episode_results = payload.get("tv_episode_results")
        if isinstance(tv_episode_results, list) and tv_episode_results:
            first = tv_episode_results[0]
            episode_tmdb_id = first.get("id")
            show_tmdb_id = first.get("show_id")
            if not isinstance(episode_tmdb_id, int) or not isinstance(show_tmdb_id, int):
                raise TmdbLookupError(
                    "TMDB /find tv episode result did not include integer episode/show ids"
                )
            return TmdbFindResult(
                tmdb_id=episode_tmdb_id,
                media_type="tv_episode",
                payload=first,
                resolved_show_tmdb_id=show_tmdb_id,
            )

        raise TmdbLookupError(
            f"TMDB /find returned no {media_type} result for {external_source}"
        )

    @staticmethod
    def get_movie_details(session: Session, *, tmdb_id: int) -> dict[str, Any]:
        return TmdbService._request_json(
            session,
            tmdb_type="movie",
            tmdb_id=tmdb_id,
            sub_key="details",
            url_path=f"/movie/{tmdb_id}",
        )

    @staticmethod
    def get_tv_details(session: Session, *, tmdb_id: int) -> dict[str, Any]:
        return TmdbService._request_json(
            session,
            tmdb_type="tv",
            tmdb_id=tmdb_id,
            sub_key="details",
            url_path=f"/tv/{tmdb_id}",
        )

    @staticmethod
    def get_episode_details(
        session: Session,
        *,
        show_tmdb_id: int,
        season_number: int,
        episode_number: int,
    ) -> dict[str, Any]:
        return TmdbService._request_json(
            session,
            tmdb_type="tv_episode",
            tmdb_id=show_tmdb_id,
            sub_key=f"s{season_number}e{episode_number}",
            url_path=f"/tv/{show_tmdb_id}/season/{season_number}/episode/{episode_number}",
        )

    @staticmethod
    def _cache_key_id(external_id: str | int) -> int:
        if isinstance(external_id, int):
            return external_id
        digest = hashlib.sha1(str(external_id).encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    @staticmethod
    def _request_json(
        session: Session,
        *,
        tmdb_type: str,
        tmdb_id: int,
        sub_key: str,
        url_path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        settings = get_settings()
        if not settings.klug_tmdb_api_key:
            raise TmdbConfigurationError("KLUG_TMDB_API_KEY is not configured")

        cache_entry = tmdb_cache_repository.get_cache_entry(
            session,
            tmdb_type=tmdb_type,
            tmdb_id=tmdb_id,
            sub_key=sub_key,
        )
        now = datetime.now(UTC)
        if cache_entry is not None and (
            cache_entry.expires_at is None or cache_entry.expires_at > now
        ):
            return cache_entry.payload

        request_params = {"api_key": settings.klug_tmdb_api_key, **(params or {})}
        with httpx.Client(timeout=15.0) as client:
            response = client.get(f"{TmdbService.BASE_URL}{url_path}", params=request_params)
            response.raise_for_status()
            payload = response.json()

        expires_at = now + timedelta(hours=max(1, settings.klug_metadata_cache_ttl_hours))
        tmdb_cache_repository.upsert_cache_entry(
            session,
            tmdb_type=tmdb_type,
            tmdb_id=tmdb_id,
            sub_key=sub_key,
            payload=payload,
            fetched_at=now,
            expires_at=expires_at,
            etag=response.headers.get("etag"),
            source_url=str(response.request.url),
        )
        return payload
