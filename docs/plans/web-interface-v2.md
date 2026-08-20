# Klug Daily Interface Modernization

Status: **Approved — waiting for the `v1.1.0` tag**

This document is the durable implementation plan and progress record for Klug's
daily-use interface modernization. Update the checklist and progress log at each
phase boundary so implementation can resume safely after context compaction.

## Release gate

Runtime implementation must not begin until all of the following are true:

- [ ] The seven-day Jellyfin/Kodi shadow period has completed successfully.
- [ ] Live watches from the primary Kodi client, another Kodi machine, and a
      native Jellyfin client have been verified without duplicates.
- [ ] Travis has explicitly authorized the `v1.1.0` tag and push.
- [ ] The `v1.1.0` semantic container image has been published and verified.

## Phase checklist

- [x] Phase 0: approved plan saved in the repository.
- [ ] Phase 0: `v1.1.0` release gate completed.
- [ ] Phase 1: paginated History API and compact `/next` shell.
- [ ] Phase 2: complete History workspace and daily-use validation.
- [ ] Phase 3: Horrorfest workbench.
- [ ] Phase 4: Library, Collection, Shows, and global search.
- [ ] Phase 5: Dashboard/Admin parity and new-interface promotion.
- [ ] Post-promotion: retain `/classic` throughout `v1.2.0`.
- [ ] Following minor release: remove `/classic` after explicit confirmation.

## Decision log

- History is the default authenticated page; Dashboard is secondary.
- Desktop and ultrawide information density drive the design while mobile
  remains functional.
- Horrorfest is the second workspace migrated after History.
- `/next` is a temporary parallel interface, not a permanent second product.
- The existing UI remains at `/` until parity and daily-use validation succeed.
- The classic UI remains at `/classic` for one tagged release after promotion.
- The API remains `/api/v1`; "v2" describes only the interface project.
- Use dependency-free JavaScript ES modules and plain CSS. Do not add React, a
  bundler, or an npm framework.
- Saved views and presentation preferences remain browser-local in this release.
- First-release editing is single-record and reversible: inline rating and
  Horrorfest ordering are allowed; bulk corrections and destructive actions are
  not.
- Jellyfin collection refresh and reconciliation remain operator-triggered.

## Summary

Build a new daily-use interface alongside the current UI, validate it
incrementally, then promote it to the primary Klug interface.

- Develop the new interface at `/next`; keep `/` unchanged throughout
  development.
- Keep FastAPI, server-served static files, plain CSS, and dependency-free
  JavaScript ES modules.
- Preserve the existing session authentication and API security boundaries.
- Make History the primary daily workspace and use shared drawers, compact
  toolbars, URL-backed navigation, accurate pagination, and server-side sorting.
- Target the promoted interface for `v1.2.0` after `v1.1.0` establishes the
  pre-redesign stable checkpoint.

## Architecture and public interfaces

### Frontend structure and routing

- Add a modular interface under `app/web/next/`:
  - a compact index/login shell;
  - shared modules for API requests, authentication, routing, URL state,
    preferences, formatting, notifications, keyboard handling, and DOM helpers;
  - reusable components for the shell, toolbar, paginated results, drawer,
    profile menu, status indicators, saved views, and confirmation dialogs;
  - separate page modules for History, Horrorfest, Library, Collection, Shows,
    Dashboard, and Admin;
  - split CSS into tokens/theme, shell/layout, shared components, and page styles.
- Add `GET /next` and `GET /next/`, both serving the new index with
  `Cache-Control: no-cache`. Assets remain under the existing `/web` mount.
- Use query-backed navigation rather than deep URL paths:
  - `/next?view=history`
  - `/next?view=history&q=from&source=jellyfin&page=2`
  - `/next?view=horrorfest&mode=analytics&year=2026`
- Use `history.pushState` for navigation and `replaceState` for debounced filter
  changes. Back/Forward must restore page, filters, sort, pagination, and open
  media/watch context.
- URL state is authoritative for navigation and data filters. Local storage is
  limited to active user, theme, density, sidebar state, visible columns, and
  saved views.
- Validate URL values against allowlists. Invalid values fall back to defaults
  and are removed when the URL is canonicalized.
- Preserve the existing session cookie and `X-Klug-UI-Request` behavior. Never
  store credentials or API keys in frontend state.

### New paginated API contracts

Keep existing list endpoints unchanged while `/` and `/next` coexist. Add
paginated variants using this reusable envelope:

```json
{
  "items": [],
  "total": 0,
  "limit": 25,
  "offset": 0
}
```

- Add `GET /api/v1/watch-events/page` supporting:
  - `user_id`
  - `query`
  - `media_type`
  - `playback_source`
  - `completed`
  - `rated`
  - `rating_min` and `rating_max`
  - `rewatch`
  - `horrorfest_year`
  - `local_date_from` and `local_date_to`
  - `include_deleted` and `deleted_only`
  - `sort`: `watched_at`, `title`, `rating`, `runtime`, or `source`
  - `direction`: `asc` or `desc`
  - `limit` from 10 through 100 and a nonnegative `offset`
- Apply sorting in PostgreSQL. Every sort receives deterministic secondary
  ordering by `watched_at DESC`, then `watch_id`.
- Return lean `WatchHistoryRowRead` items containing:
  - watch and media IDs;
  - UTC and user-local watch times;
  - media type, movie/episode title, show title, season/episode coordinates, and
    year;
  - source, effective runtime, completion, rating, rewatch, deletion state,
    version override, and Horrorfest coordinates.
- Add `GET /api/v1/watch-events/{watch_id}/detail` returning the selected row plus
  progress, origin, import/provenance, source-event identifiers, audit fields,
  deletion fields, media metadata summary, and recent related watches.
- Continue using existing single-watch mutation endpoints for correction,
  rating, version override, delete, restore, and Horrorfest actions.
- Add equivalent paginated variants as their pages migrate:
  - `/api/v1/library/movies|episodes|shows/page`
  - `/api/v1/collection/movies|episodes|shows/page`
  - `/api/v1/scrobble-activity/page`
- Paginated Library and Collection endpoints retain current filters and add
  server-side `sort` and `direction`.
- Add `GET /api/v1/search/media` for the command palette. Return media type,
  identity, human-readable title/coordinates, year, poster, collection presence,
  watch count, and latest-watch date.
- Add `GET /api/v1/dashboard/attention` returning timestamped counters and typed
  navigation targets for unrated watches, unmatched scrobbles, failed/skipped
  enrichment, failed imports, stale collection snapshots, and Jellyfin state.
- Extend Jellyfin status with last collection-snapshot time/status/counts. Do not
  expose credentials or raw configuration secrets.
- Use existing indexes initially. Capture `EXPLAIN ANALYZE` for combined History
  filters on production-scale test data and add an Alembic index only when a
  measured query requires it.

### Shared interaction rules

- Application header:
  - sticky and approximately 60 px tall;
  - page title on the left;
  - API health, refresh age, refresh button, and profile menu on the right;
  - health details are available on demand; authentication internals stay in the
    profile menu.
- Sidebar:
  - approximately 216 px expanded and 72 px collapsed;
  - compact Klug mark, icon-and-label navigation, visual separation before
    Admin, and a collapse control;
  - profile menu at the bottom;
  - remembered collapsed state;
  - inline SVG icons with accessible labels and no external dependency.
- Profile menu:
  - username, theme, density, active-user switching when multiple users exist,
    session expiry, and logout;
  - with one user, display identity without a redundant selector.
- Desktop breakpoints:
  - `>=1280 px`: expanded/collapsible sidebar and desktop tables;
  - `768–1279 px`: collapsed sidebar or overlay navigation;
  - `<768 px`: overlay navigation, full-screen drawers, and two-line result cards.
- Drawers:
  - 500 px desktop width and full-screen mobile width;
  - close by button or Escape;
  - trap focus while modal;
  - optional pinned mode only at `>=1600 px`;
  - warn before closing, changing rows, navigating, or refreshing when dirty.
- Mutations are pessimistic: disable the affected control, wait for success,
  then refresh the row and counters. On failure, retain form state and show a
  readable retryable error.
- First release supports safe inline rating and Horrorfest ordering only. It does
  not include multi-row correction, bulk deletion, or broad bulk mutation.

## Implementation phases

### Phase 0 — Durable plan and release gate

- Save this document, link it from `PROJECT_CONTEXT.md`, and commit it separately.
- Finish the seven-day Jellyfin/Kodi validation.
- Update the `1.1.0` changelog date only when validation succeeds.
- Create and push the `v1.1.0` tag only after explicit authorization.
- Confirm the semantic container image before runtime interface work begins.

### Phase 1 — API foundation and compact shell

- Implement the page envelope, History page endpoint, detail endpoint, filters,
  exact totals, and server-side sorting.
- Add repository/service tests for counts and stable ordering before frontend
  consumption.
- Create `/next` with the existing login and session-validation behavior.
- Implement the modular API client, router, URL codec, preference store, toast
  region, confirmation dialog, and drawer primitive.
- Build the compact header, collapsible sidebar, profile menu, theme, active-user
  handling, health indicator, and active-page refresh.
- Show a History placeholder after login; History is the fallback for invalid or
  absent `view` values.
- Do not change `/`.

Phase acceptance:

- [ ] Login/logout works independently at `/` and `/next`.
- [ ] The same session works in both interfaces.
- [ ] Sidebar and header preferences survive refresh.
- [ ] Back/Forward restores navigation.
- [ ] Health and session failures remain distinct.
- [ ] Keyboard and mobile navigation remain usable.

### Phase 2 — Complete History workspace

- Build a compact primary toolbar with:
  - title search debounced at 300 ms;
  - media type;
  - date preset;
  - More Filters;
  - Reset;
  - rows per page and refresh.
- More Filters contains custom local dates, source, completion, rating state and
  range, rewatch, Horrorfest year, and deleted state.
- Default to all active history sorted newest-first with no hidden date limit.
- Include built-in views for Recent, Last 30 Days, Unrated, Rewatches, Movies,
  Episodes, Current Horrorfest, and Deleted.
- Allow named browser-local views in `klug.next.saved_views.v1`. Store validated
  filters, sort, row count, density, and visible columns; support rename/delete.
- Group chronological History by local date only when sorting by watch time.
  Other sorts use an ungrouped table.
- Default columns are Watched, Title, Type, Source, Rating, and Status.
- Render episodes as `Show · S03E10 — Episode title`, with graceful metadata
  fallbacks.
- Put runtime, rewatch, version, Horrorfest membership, and deletion state in
  compact secondary information without redundant badges.
- Provide sticky headers, pagination above and below, exact `x–y of total`
  counts, header sorting, compact/comfortable density, and visible-column choices.
- Clicking a row opens Watch Detail with:
  - human-readable identity and summary;
  - inline rating;
  - correction form;
  - version/runtime override;
  - delete/restore controls;
  - collapsed Technical Details;
  - sticky Save/Cancel area.
- Keyboard behavior:
  - Up/Down changes selection;
  - Enter opens detail;
  - Escape closes menus and drawers;
  - `/` focuses History search outside form controls.
- Preserve filters/page after edits. If an edit removes the row from the active
  filter, close the drawer, adjust an empty page, and explain what changed.
- Validate `/next` in daily use before Phase 3.

### Phase 3 — Horrorfest workbench

- Replace the monolithic page with URL-backed Log, Analytics, Curation, and
  Export modes.
- Log:
  - active year and include-removed controls;
  - dense rows with order, local time, title/year, runtime, source, rating,
    rewatch, and status;
  - sticky header/order column;
  - safe inline rating and target-order edits;
  - shared drawer for include/remove/restore, audit, and media/watch detail;
  - confirmation for removal, but not reversible ordering changes.
- Analytics:
  - preserve annual, daily, source, rating, title, decade, comparison, and
    leaderboard capabilities;
  - sticky matrix title columns with horizontal scrolling;
  - shared-drawer drilldowns;
  - URL-backed selected years, sorts, and filters.
- Curation:
  - separate staples, streaks, gaps, and dormant views;
  - sortable dense tables linked to History and media detail;
  - consistent loading, empty, and error states.
- Export:
  - collect existing CSV actions in one workspace;
  - retain contextual exports in originating views.
- Reuse existing Horrorfest APIs unless missing totals or server sorting are
  demonstrated. Do not duplicate analytics calculations in JavaScript.
- Validate against the classic interface and representative historical
  Excel-derived views.

### Phase 4 — Library, Collection, Shows, and global search

- Add paginated Library and Collection endpoints with totals and stable sorting.
- Library:
  - Movies, Episodes, and Shows modes;
  - dense rows with watch count, latest watch/rating, enrichment, and Horrorfest
    signals;
  - URL-backed search, watch state, year/show, enrichment, sort, and pagination;
  - shared media drawer with metadata, recent watches, collection presence, and
    History links.
- Collection:
  - preserve its meaning as Jellyfin-owned media;
  - Movies, Episodes, and Shows modes;
  - filters for present/missing, library, type, added date, and metadata state;
  - prominent last collection-snapshot status.
- Shows:
  - browse shows/seasons without permanent detail panels;
  - preserve season expansion;
  - open episodes in media detail or filtered History;
  - retain show/season context in URL history.
- Add `Ctrl+K` command palette:
  - remote media search;
  - page and built-in-view navigation;
  - media detail;
  - Manual Add and current Horrorfest client commands;
  - debouncing and stale-request cancellation.

### Phase 5 — Dashboard, Admin, parity, and promotion

- Dashboard remains secondary and contains compact statistics, recent activity,
  current Horrorfest progress, and the unified Needs Attention inbox.
- Every attention item opens the relevant URL-backed filtered view.
- Migrate Admin while preserving imports, manual watch entry, scrobble activity,
  Jellyfin mapping/reconciliation, collection snapshot controls, and enrichment.
- Add operator-triggered Jellyfin collection snapshot dry-run/run controls and
  last-snapshot status. Do not add scheduling.
- Complete feature parity against `/`.
- Promotion:
  - serve the new interface at `/`;
  - move the previous interface to `/classic`;
  - redirect `/next` to `/` while preserving query parameters;
  - update README and project context;
  - release as `v1.2.0` after production verification.
- Retain `/classic` throughout `v1.2.0`, then remove it in the following minor
  release only after explicit confirmation.

## Test, acceptance, and rollout plan

### Automated backend tests

- Page envelope, limits, offsets, empty pages, and exact totals.
- Every History filter individually and in representative combinations.
- Local-date filtering in the selected user's timezone.
- Stable ascending/descending ordering for every supported sort.
- Episode/show/title projection and missing-metadata fallbacks.
- Deleted-row visibility.
- Watch-detail missing IDs and complete audit/provenance mapping.
- Paginated Library, Collection, and Scrobble Activity.
- Attention counters and typed navigation targets.
- Search ranking and user isolation.
- Classic endpoints retain current shapes while `/classic` exists.

### Frontend tests

- Use Node's built-in test runner for pure ES modules; add no JavaScript framework.
- Cover URL parsing/serialization/canonicalization, Back/Forward restoration,
  saved-view validation, pagination, date presets, identity formatting,
  dirty-form guards, stale-request cancellation, and page state transitions.
- Extend pytest frontend coverage for `/next`, assets, cache headers,
  authentication, `/classic`, and final promotion.
- Run `node --check` across all modules and add Node tests to GitHub Actions.

### Manual browser acceptance

Test dark and light themes at:

- 3440×1440 ultrawide;
- 1920×1080 desktop;
- 1280×800 compact desktop/tablet;
- approximately 390 px mobile width.

Verify:

- header/sidebar reclaim meaningful space;
- History browses without an open detail panel;
- totals and sorting remain correct across pages;
- filters, saved views, Back/Forward, refresh, and bookmarks restore correctly;
- keyboard focus/navigation is visible;
- drawers protect unsaved changes;
- rating, correction, version, delete/restore, Horrorfest ordering, imports,
  reconciliation, and enrichment still work;
- retries or double clicks do not create duplicate writes;
- failures preserve input and provide actionable errors;
- API keys and technical identifiers do not appear in ordinary page chrome.

### Release gates

- Split each phase into tested, reviewable commits and update this checklist at
  phase boundaries.
- Run full pytest, Ruff, JavaScript syntax/tests, `/`, `/next`, `/docs`, and new
  endpoint smoke checks before completing each phase.
- During coexistence, `/` must remain usable even if `/next` is incomplete.
- Use `/next` as the normal daily interface for at least seven days before
  promotion, including History correction, Horrorfest, and Admin workflows.
- Promotion requires no unresolved parity blockers and explicit authorization to
  tag/push the release.

## Assumptions and defaults

- Travis is the primary audience; Klug remains a personal home-server app.
- Desktop/ultrawide density takes priority, but mobile remains functional.
- History is the default page and Horrorfest is the second migrated workspace.
- The current Klug palette and visual identity remain authoritative.
- Active-user context is reused; a sole user is selected automatically.
- Saved views and presentation preferences are browser-local.
- No bulk destructive or multi-watch correction tools are included.
- No frontend framework, build system, or new database table is introduced.
- PostgreSQL remains authoritative and existing write/auth/security behavior is
  unchanged.
- Collection refresh and Jellyfin reconciliation remain operator-triggered.

## Progress log

- 2026-08-20: Plan approved. Durable plan document created. Runtime work remains
  gated on successful shadow validation and the explicit `v1.1.0` release.
