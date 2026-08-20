# Changelog

Klug Media releases are personal deployment checkpoints. They do not guarantee
backward compatibility or support for environments outside the documented home
server deployment.

## [1.1.0] - Unreleased

### Added

- Primary Jellyfin Playback Start/Stop ingestion with raw playback evidence,
  mapped users, idempotent delivery, and cross-source watch deduplication.
- A 90-day Jellyfin reconciliation workflow with dry runs, cursor overlap,
  import batches, and honest handling of unavailable older rewatch dates.
- Admin controls for Jellyfin status, user mapping, reconciliation, and filtered
  scrobble activity.
- Repeatable Jellyfin collection snapshots and collection browsing for movies,
  shows, and episodes.
- Watched-library browsing, richer history navigation, media detail links, and an
  active user profile selector.
- Expanded Horrorfest analytics, drilldowns, comparison views, curation reports,
  and CSV exports.
- Unraid container deployment and GitHub Container Registry publishing with
  immutable commit and semantic-version image tags.

### Changed

- Jellyfin is now the primary playback hub while Kodi/Node-RED remains available
  during a seven-day shadow cutover.
- Reconciliation checks through an item's runtime so Jellyfin playback-start and
  Kodi playback-stop timestamps do not create duplicate watches.
- Authenticated operator sessions can perform marked same-origin UI writes, and
  valid sessions remain usable when unrelated dashboard requests fail.
- Browser-served frontend assets require cache revalidation after deployments.
