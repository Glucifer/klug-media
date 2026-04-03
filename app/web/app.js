const authStatus = document.getElementById("auth-status");
const loginCard = document.getElementById("login-card");
const appCard = document.getElementById("app-card");
const detailCard = document.getElementById("detail-card");
const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
const opsHealth = document.getElementById("ops-health");
const opsAuthMode = document.getElementById("ops-auth-mode");
const opsSession = document.getElementById("ops-session");
const opsLastRefresh = document.getElementById("ops-last-refresh");
const showList = document.getElementById("show-list");
const showsStatus = document.getElementById("shows-status");
const statsStatus = document.getElementById("stats-status");
const statsSummaryCards = document.getElementById("stats-summary-cards");
const statsMonthlyBody = document.getElementById("stats-monthly-body");
const statsHorrorfestBody = document.getElementById("stats-horrorfest-body");
const importForm = document.getElementById("import-form");
const importFile = document.getElementById("import-file");
const importUserId = document.getElementById("import-user-id");
const importMode = document.getElementById("import-mode");
const importDryRun = document.getElementById("import-dry-run");
const importResume = document.getElementById("import-resume");
const importUseLatestCursor = document.getElementById("import-use-latest-cursor");
const importStatus = document.getElementById("import-status");
const importCursorBefore = document.getElementById("import-cursor-before");
const importCursorAfter = document.getElementById("import-cursor-after");
const importLastCursor = document.getElementById("import-last-cursor");
const importSummary = document.getElementById("import-summary");
const importErrorsStatus = document.getElementById("import-errors-status");
const importErrorsList = document.getElementById("import-errors-list");
const manualWatchForm = document.getElementById("manual-watch-form");
const manualWatchUserId = document.getElementById("manual-watch-user-id");
const manualWatchWatchedAt = document.getElementById("manual-watch-watched-at");
const manualWatchPlaybackSource = document.getElementById("manual-watch-playback-source");
const manualWatchMediaType = document.getElementById("manual-watch-media-type");
const manualWatchTmdbId = document.getElementById("manual-watch-tmdb-id");
const manualWatchShowTmdbId = document.getElementById("manual-watch-show-tmdb-id");
const manualWatchTmdbEpisodeId = document.getElementById("manual-watch-tmdb-episode-id");
const manualWatchSeasonNumber = document.getElementById("manual-watch-season-number");
const manualWatchEpisodeNumber = document.getElementById("manual-watch-episode-number");
const manualWatchRatingValue = document.getElementById("manual-watch-rating-value");
const manualWatchCreatedBy = document.getElementById("manual-watch-created-by");
const manualWatchCompleted = document.getElementById("manual-watch-completed");
const manualWatchStatus = document.getElementById("manual-watch-status");
const manualWatchDetail = document.getElementById("manual-watch-detail");
const importHistoryStatusFilter = document.getElementById("import-history-status-filter");
const importHistoryClearFilter = document.getElementById("import-history-clear-filter");
const importHistoryStatus = document.getElementById("import-history-status");
const importHistoryBody = document.getElementById("import-history-body");
const importDetailStatus = document.getElementById("import-detail-status");
const importCopyDetail = document.getElementById("import-copy-detail");
const importDownloadErrors = document.getElementById("import-download-errors");
const importDetail = document.getElementById("import-detail");
const libraryQuery = document.getElementById("library-query");
const libraryShowQuery = document.getElementById("library-show-query");
const libraryYear = document.getElementById("library-year");
const libraryEnrichmentStatus = document.getElementById("library-enrichment-status");
const libraryWatched = document.getElementById("library-watched");
const libraryLimitSelect = document.getElementById("library-limit");
const libraryApply = document.getElementById("library-apply");
const libraryStatus = document.getElementById("library-status");
const libraryFilterSummary = document.getElementById("library-filter-summary");
const libraryHead = document.getElementById("library-head");
const libraryBody = document.getElementById("library-body");
const libraryPrev = document.getElementById("library-prev");
const libraryNext = document.getElementById("library-next");
const libraryPage = document.getElementById("library-page");
const historyMediaType = document.getElementById("history-media-type");
const historyQuery = document.getElementById("history-query");
const historyLocalDateFrom = document.getElementById("history-local-date-from");
const historyLocalDateTo = document.getElementById("history-local-date-to");
const historyIncludeDeleted = document.getElementById("history-include-deleted");
const historyLimitSelect = document.getElementById("history-limit");
const historyApply = document.getElementById("history-apply");
const historyStatus = document.getElementById("history-status");
const historyContextBanner = document.getElementById("history-context-banner");
const historyContextText = document.getElementById("history-context-text");
const historyContextReturn = document.getElementById("history-context-return");
const historyContextClear = document.getElementById("history-context-clear");
const historyBody = document.getElementById("history-body");
const historyFilterSummary = document.getElementById("history-filter-summary");
const historyPrev = document.getElementById("history-prev");
const historyNext = document.getElementById("history-next");
const historyPage = document.getElementById("history-page");
const historyDetailStatus = document.getElementById("history-detail-status");
const historyDetail = document.getElementById("history-detail");
const historyEditorUpdatedBy = document.getElementById("history-editor-updated-by");
const historyEditorReason = document.getElementById("history-editor-reason");
const historyEditorWatchedAt = document.getElementById("history-editor-watched-at");
const historyEditorMediaItemId = document.getElementById("history-editor-media-item-id");
const historyEditorVersionName = document.getElementById("history-editor-version-name");
const historyEditorRuntimeMinutes = document.getElementById("history-editor-runtime-minutes");
const historyEditorCompleted = document.getElementById("history-editor-completed");
const historyEditorRewatch = document.getElementById("history-editor-rewatch");
const historySave = document.getElementById("history-save");
const historyOpenMedia = document.getElementById("history-open-media");
const historySaveVersion = document.getElementById("history-save-version");
const historyClearVersion = document.getElementById("history-clear-version");
const historyDelete = document.getElementById("history-delete");
const historyRestore = document.getElementById("history-restore");
const ratingsLimitSelect = document.getElementById("ratings-limit");
const ratingsApply = document.getElementById("ratings-apply");
const ratingsStatus = document.getElementById("ratings-status");
const ratingsBody = document.getElementById("ratings-body");
const ratingsDetailStatus = document.getElementById("ratings-detail-status");
const ratingsDetail = document.getElementById("ratings-detail");
const ratingsUpdatedBy = document.getElementById("ratings-updated-by");
const ratingsReason = document.getElementById("ratings-reason");
const ratingsValue = document.getElementById("ratings-value");
const ratingsSave = document.getElementById("ratings-save");
const horrorfestYearSelect = document.getElementById("horrorfest-year-select");
const horrorfestIncludeRemoved = document.getElementById("horrorfest-include-removed");
const horrorfestRefresh = document.getElementById("horrorfest-refresh");
const horrorfestStatus = document.getElementById("horrorfest-status");
const horrorfestLogPanel = document.getElementById("horrorfest-log-panel");
const horrorfestAnalyticsPanel = document.getElementById("horrorfest-analytics-panel");
const horrorfestBody = document.getElementById("horrorfest-body");
const horrorfestDetailStatus = document.getElementById("horrorfest-detail-status");
const horrorfestDetail = document.getElementById("horrorfest-detail");
const horrorfestUpdatedBy = document.getElementById("horrorfest-updated-by");
const horrorfestReason = document.getElementById("horrorfest-reason");
const horrorfestTargetOrder = document.getElementById("horrorfest-target-order");
const horrorfestIncludeWatchId = document.getElementById("horrorfest-include-watch-id");
const horrorfestMove = document.getElementById("horrorfest-move");
const horrorfestRemove = document.getElementById("horrorfest-remove");
const horrorfestRestore = document.getElementById("horrorfest-restore");
const horrorfestInclude = document.getElementById("horrorfest-include");
const horrorfestOpenMedia = document.getElementById("horrorfest-open-media");
const horrorfestConfigYear = document.getElementById("horrorfest-config-year");
const horrorfestConfigLabel = document.getElementById("horrorfest-config-label");
const horrorfestConfigStart = document.getElementById("horrorfest-config-start");
const horrorfestConfigEnd = document.getElementById("horrorfest-config-end");
const horrorfestConfigNotes = document.getElementById("horrorfest-config-notes");
const horrorfestConfigActive = document.getElementById("horrorfest-config-active");
const horrorfestConfigSave = document.getElementById("horrorfest-config-save");
const activitySource = document.getElementById("activity-source");
const activityStatus = document.getElementById("activity-status");
const activityOnlyUnmatched = document.getElementById("activity-only-unmatched");
const activityOnlyWithWatch = document.getElementById("activity-only-with-watch");
const activityLimitSelect = document.getElementById("activity-limit");
const activityApply = document.getElementById("activity-apply");
const activityStatusText = document.getElementById("activity-status-text");
const activityBody = document.getElementById("activity-body");
const activityPrev = document.getElementById("activity-prev");
const activityNext = document.getElementById("activity-next");
const activityPage = document.getElementById("activity-page");
const activityDetailStatus = document.getElementById("activity-detail-status");
const activityDetail = document.getElementById("activity-detail");
const enrichmentStatusFilter = document.getElementById("enrichment-status-filter");
const enrichmentMissingIds = document.getElementById("enrichment-missing-ids");
const enrichmentLimitSelect = document.getElementById("enrichment-limit");
const enrichmentApply = document.getElementById("enrichment-apply");
const enrichmentProcessPending = document.getElementById("enrichment-process-pending");
const enrichmentStatusText = document.getElementById("enrichment-status-text");
const enrichmentBody = document.getElementById("enrichment-body");
const enrichmentDetailStatus = document.getElementById("enrichment-detail-status");
const enrichmentDetail = document.getElementById("enrichment-detail");
const dashboardHistoryStatus = document.getElementById("dashboard-history-status");
const dashboardHistoryBody = document.getElementById("dashboard-history-body");
const dashboardRatingsStatus = document.getElementById("dashboard-ratings-status");
const dashboardRatingsBody = document.getElementById("dashboard-ratings-body");
const dashboardEnrichmentStatus = document.getElementById("dashboard-enrichment-status");
const dashboardEnrichmentBody = document.getElementById("dashboard-enrichment-body");
const dashboardAttentionGrid = document.getElementById("dashboard-attention-grid");
const dashboardUnratedOpen = document.getElementById("dashboard-unrated-open");
const dashboardEnrichmentOpen = document.getElementById("dashboard-enrichment-open");
const horrorfestYearSummary = document.getElementById("horrorfest-year-summary");
const refreshData = document.getElementById("refresh-data");
const logoutBtn = document.getElementById("logout-btn");
const themeToggle = document.getElementById("theme-toggle");
const detailTitle = document.getElementById("detail-title");
const detailProgress = document.getElementById("detail-progress");
const detailStatus = document.getElementById("detail-status");
const detailSummary = document.getElementById("detail-summary");
const episodeList = document.getElementById("episode-list");
const mediaPanel = document.getElementById("media-panel");
const mediaPanelTitle = document.getElementById("media-panel-title");
const mediaPanelStatus = document.getElementById("media-panel-status");
const mediaPanelOpenHistory = document.getElementById("media-panel-open-history");
const mediaPanelBody = document.getElementById("media-panel-body");
const mediaPanelClose = document.getElementById("media-panel-close");
const horrorfestYearMetrics = document.getElementById("horrorfest-year-metrics");
const horrorfestContextBanner = document.getElementById("horrorfest-context-banner");
const horrorfestContextText = document.getElementById("horrorfest-context-text");
const horrorfestContextReturn = document.getElementById("horrorfest-context-return");
const horrorfestContextClear = document.getElementById("horrorfest-context-clear");
const horrorfestAnalyticsStatus = document.getElementById("horrorfest-analytics-status");
const horrorfestAnalyticsRefresh = document.getElementById("horrorfest-analytics-refresh");
const horrorfestAnalyticsOpenLog = document.getElementById("horrorfest-analytics-open-log");
const horrorfestAnalyticsYearsBody = document.getElementById("horrorfest-analytics-years-body");
const horrorfestAnalyticsDetailStatus = document.getElementById("horrorfest-analytics-detail-status");
const horrorfestAnalyticsSummaryCards = document.getElementById("horrorfest-analytics-summary-cards");
const horrorfestAnalyticsDailyBody = document.getElementById("horrorfest-analytics-daily-body");
const horrorfestAnalyticsSourcesBody = document.getElementById("horrorfest-analytics-sources-body");
const horrorfestAnalyticsRatingsBody = document.getElementById("horrorfest-analytics-ratings-body");
const adminContextBanner = document.getElementById("admin-context-banner");
const adminContextText = document.getElementById("admin-context-text");
const adminContextReturn = document.getElementById("admin-context-return");
const adminContextClear = document.getElementById("admin-context-clear");
const navButtons = Array.from(document.querySelectorAll("[data-view-target]"));
const viewPanels = Array.from(document.querySelectorAll(".view-panel[data-view]"));
const adminNavButtons = Array.from(document.querySelectorAll("[data-admin-view-target]"));
const adminPanels = Array.from(document.querySelectorAll(".admin-panel[data-admin-view]"));
const jumpButtons = Array.from(document.querySelectorAll("[data-jump-view]"));
const historySortButtons = Array.from(document.querySelectorAll("[data-history-sort]"));
const historyPresetButtons = Array.from(document.querySelectorAll("[data-history-preset]"));
const libraryModeButtons = Array.from(document.querySelectorAll("[data-library-mode]"));
const horrorfestModeButtons = Array.from(document.querySelectorAll("[data-horrorfest-mode]"));
const horrorfestAnalyticsSortButtons = Array.from(
  document.querySelectorAll("[data-horrorfest-analytics-sort]")
);

const IMPORT_PREF_KEYS = {
  userId: "klug.import_user_id",
  mode: "klug.import_mode",
  dryRun: "klug.import_dry_run",
  resume: "klug.import_resume",
  lastCursor: "klug.import_last_cursor",
  importHistoryStatusFilter: "klug.import_history_status_filter",
};
const MANUAL_WATCH_PREF_KEYS = {
  userId: "klug.manual_watch_user_id",
  playbackSource: "klug.manual_watch_playback_source",
  createdBy: "klug.manual_watch_created_by",
};
const UI_PREF_KEYS = {
  theme: "klug.ui_theme",
  activeView: "klug.active_view",
  activeAdminView: "klug.active_admin_view",
  historyQuery: "klug.history_query",
  libraryMode: "klug.library_mode",
  libraryQuery: "klug.library_query",
  libraryShowQuery: "klug.library_show_query",
  libraryYear: "klug.library_year",
  libraryEnrichmentStatus: "klug.library_enrichment_status",
  libraryWatched: "klug.library_watched",
  libraryLimit: "klug.library_limit",
  historyLinkedContext: "klug.history_linked_context",
  dashboardAdminContext: "klug.dashboard_admin_context",
  dashboardHorrorfestContext: "klug.dashboard_horrorfest_context",
  horrorfestMode: "klug.horrorfest_mode",
};
const IMPORT_UPLOAD_MAX_MB = 25;
const IMPORT_UPLOAD_MAX_BYTES = IMPORT_UPLOAD_MAX_MB * 1024 * 1024;

let historyOffset = 0;
let historyLimit = Number.parseInt(historyLimitSelect.value, 10);
let historyRows = [];
let libraryOffset = 0;
let libraryLimit = Number.parseInt(libraryLimitSelect.value, 10);
let libraryMode = window.localStorage.getItem(UI_PREF_KEYS.libraryMode) || "movies";
let selectedHistoryId = null;
let historySortKey = "watched_at";
let historySortDirection = "desc";
let ratingsLimit = Number.parseInt(ratingsLimitSelect.value, 10);
let ratingsRows = [];
let selectedRatingWatchId = null;
let horrorfestYears = [];
let horrorfestRows = [];
let horrorfestAnalyticsYears = [];
let selectedHorrorfestEntryId = null;
let selectedHorrorfestAnalyticsYear = null;
let horrorfestMode = window.localStorage.getItem(UI_PREF_KEYS.horrorfestMode) || "log";
let horrorfestAnalyticsSortKey = "year";
let horrorfestAnalyticsSortDirection = "desc";
let activityOffset = 0;
let activityLimit = Number.parseInt(activityLimitSelect.value, 10);
let selectedActivityId = null;
let enrichmentLimit = Number.parseInt(enrichmentLimitSelect.value, 10);
let selectedEnrichmentId = null;
const importHistoryById = new Map();
let importHistoryRows = [];
let selectedImportBatchId = null;
let selectedImportBatchDetail = null;
let statsSummaryData = null;
let statsMonthlyRowsData = [];
let statsHorrorfestRowsData = [];
let libraryRows = [];
let linkedHistoryContext = null;
let selectedShowDetail = null;
let selectedMediaItemId = null;
let selectedMediaDetail = null;
const showSeasonExpandState = new Map();
let dashboardAdminContext = null;
let dashboardHorrorfestContext = null;
let dashboardEnrichmentPreviewStatus = "";

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  return response;
}

function renderStatusChip(label, tone = "neutral") {
  return `<span class="status-chip status-${tone}">${label}</span>`;
}

function parseOptionalBoolean(value) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return null;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatRuntimeHours(runtimeSeconds) {
  if (!runtimeSeconds) {
    return "-";
  }
  return `${formatDecimalValue(Number(runtimeSeconds) / 3600)}h`;
}

function formatRuntimeMinutes(runtimeSeconds) {
  if (!runtimeSeconds) {
    return "-";
  }
  return `${Math.round(Number(runtimeSeconds) / 60)} min`;
}

function renderDetailItems(items) {
  return items
    .map(
      ([label, value]) => `
        <div class="detail-item">
          <div class="detail-label">${escapeHtml(label)}</div>
          <div class="detail-value">${value === null || value === undefined || value === "" ? "-" : value}</div>
        </div>
      `
    )
    .join("");
}

function renderMetaPills(items) {
  return items
    .map(
      ([label, value]) => `
        <div class="meta-pill">
          <div class="meta-pill-label">${escapeHtml(label)}</div>
          <div class="meta-pill-value">${value === null || value === undefined || value === "" ? "-" : value}</div>
        </div>
      `
    )
    .join("");
}

function formatDateInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function setHistoryDatePreset(preset) {
  const now = new Date();
  if (preset === "last-30") {
    const start = new Date(now);
    start.setDate(start.getDate() - 29);
    historyLocalDateFrom.value = formatDateInputValue(start);
    historyLocalDateTo.value = formatDateInputValue(now);
  } else if (preset === "this-year") {
    historyLocalDateFrom.value = `${now.getFullYear()}-01-01`;
    historyLocalDateTo.value = formatDateInputValue(now);
  } else {
    historyQuery.value = "";
    historyMediaType.value = "";
    historyLocalDateFrom.value = "";
    historyLocalDateTo.value = "";
    historyIncludeDeleted.checked = false;
    window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
    clearLinkedHistoryContext({ clearQuery: false });
  }
}

function loadPersistedLinkedHistoryContext() {
  const raw = window.localStorage.getItem(UI_PREF_KEYS.historyLinkedContext);
  if (!raw) {
    linkedHistoryContext = null;
    return;
  }
  try {
    linkedHistoryContext = JSON.parse(raw);
  } catch (_error) {
    linkedHistoryContext = null;
    window.localStorage.removeItem(UI_PREF_KEYS.historyLinkedContext);
  }
}

function persistLinkedHistoryContext() {
  if (linkedHistoryContext) {
    window.localStorage.setItem(
      UI_PREF_KEYS.historyLinkedContext,
      JSON.stringify(linkedHistoryContext)
    );
  } else {
    window.localStorage.removeItem(UI_PREF_KEYS.historyLinkedContext);
  }
}

function loadPersistedDashboardContexts() {
  const adminRaw = window.localStorage.getItem(UI_PREF_KEYS.dashboardAdminContext);
  const horrorfestRaw = window.localStorage.getItem(UI_PREF_KEYS.dashboardHorrorfestContext);
  try {
    dashboardAdminContext = adminRaw ? JSON.parse(adminRaw) : null;
  } catch (_error) {
    dashboardAdminContext = null;
    window.localStorage.removeItem(UI_PREF_KEYS.dashboardAdminContext);
  }
  try {
    dashboardHorrorfestContext = horrorfestRaw ? JSON.parse(horrorfestRaw) : null;
  } catch (_error) {
    dashboardHorrorfestContext = null;
    window.localStorage.removeItem(UI_PREF_KEYS.dashboardHorrorfestContext);
  }
}

function persistDashboardAdminContext() {
  if (dashboardAdminContext) {
    window.localStorage.setItem(
      UI_PREF_KEYS.dashboardAdminContext,
      JSON.stringify(dashboardAdminContext)
    );
  } else {
    window.localStorage.removeItem(UI_PREF_KEYS.dashboardAdminContext);
  }
}

function persistDashboardHorrorfestContext() {
  if (dashboardHorrorfestContext) {
    window.localStorage.setItem(
      UI_PREF_KEYS.dashboardHorrorfestContext,
      JSON.stringify(dashboardHorrorfestContext)
    );
  } else {
    window.localStorage.removeItem(UI_PREF_KEYS.dashboardHorrorfestContext);
  }
}

function renderHistoryContextBanner() {
  if (!linkedHistoryContext) {
    historyContextBanner.classList.add("hidden");
    historyContextText.textContent =
      "History is currently linked to another browse surface.";
    return;
  }
  historyContextBanner.classList.remove("hidden");
  const sourceLabel =
    linkedHistoryContext.sourceView === "media-panel"
      ? "Media detail"
      : linkedHistoryContext.sourceView === "library"
        ? "Library"
        : linkedHistoryContext.sourceView === "shows"
          ? "Shows"
          : linkedHistoryContext.sourceView === "dashboard"
            ? "Dashboard"
        : "browse";
  const linkLabel = linkedHistoryContext.label || "selected media";
  let filterLabel = `linked context for ${linkLabel}`;
  if (linkedHistoryContext.mediaItemId) {
    filterLabel = `media item filter for ${linkLabel}`;
  } else if (linkedHistoryContext.appliesQuery) {
    filterLabel = `title filter for ${linkLabel}`;
  } else if (linkedHistoryContext.type === "month_range") {
    filterLabel = `month drilldown for ${linkLabel}`;
  } else if (linkedHistoryContext.type === "unrated_queue") {
    filterLabel = `unrated queue context`;
  } else if (linkedHistoryContext.type === "horrorfest_year_window") {
    filterLabel = `Horrorfest history slice for ${linkLabel}`;
  }
  historyContextText.textContent = `Opened from ${sourceLabel}. History is currently using a linked ${filterLabel}.`;
  historyContextReturn.textContent =
    linkedHistoryContext.sourceView === "library"
      ? "Back to Library"
      : linkedHistoryContext.sourceView === "shows"
        ? "Back to Shows"
        : linkedHistoryContext.sourceView === "dashboard"
          ? "Back to Dashboard"
        : "Close Link";
}

function clearLinkedHistoryContext({ clearQuery = true } = {}) {
  const shouldClearQuery = Boolean(linkedHistoryContext?.appliesQuery) && clearQuery;
  linkedHistoryContext = null;
  persistLinkedHistoryContext();
  if (shouldClearQuery) {
    historyQuery.value = "";
    window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
  }
  renderHistoryContextBanner();
  renderHistoryFilterSummary();
}

function setLinkedHistoryContext(context) {
  linkedHistoryContext = context;
  persistLinkedHistoryContext();
  renderHistoryContextBanner();
  renderHistoryFilterSummary();
}

function renderAdminContextBanner() {
  if (!dashboardAdminContext || dashboardAdminContext.adminView !== "enrichment") {
    adminContextBanner.classList.add("hidden");
    adminContextText.textContent = "Enrichment was opened from the dashboard.";
    return;
  }
  adminContextBanner.classList.remove("hidden");
  adminContextText.textContent = `Opened from Dashboard. Enrichment is currently filtered to ${dashboardAdminContext.label || dashboardAdminContext.enrichmentStatus || "selected rows"}.`;
}

function clearAdminContext({ clearFilter = false } = {}) {
  if (clearFilter) {
    enrichmentStatusFilter.value = "";
  }
  dashboardAdminContext = null;
  persistDashboardAdminContext();
  renderAdminContextBanner();
}

function setAdminContext(context) {
  dashboardAdminContext = context;
  persistDashboardAdminContext();
  renderAdminContextBanner();
}

function renderHorrorfestContextBanner() {
  if (!dashboardHorrorfestContext) {
    horrorfestContextBanner.classList.add("hidden");
    horrorfestContextText.textContent = "Horrorfest was opened from the dashboard.";
    return;
  }
  horrorfestContextBanner.classList.remove("hidden");
  horrorfestContextText.textContent = `Opened from Dashboard. Showing ${dashboardHorrorfestContext.label || `Horrorfest ${dashboardHorrorfestContext.year}`}.`;
}

function clearHorrorfestContext() {
  dashboardHorrorfestContext = null;
  persistDashboardHorrorfestContext();
  renderHorrorfestContextBanner();
}

function setHorrorfestContext(context) {
  dashboardHorrorfestContext = context;
  persistDashboardHorrorfestContext();
  renderHorrorfestContextBanner();
}

function setHorrorfestMode(mode) {
  horrorfestMode = mode === "analytics" ? "analytics" : "log";
  window.localStorage.setItem(UI_PREF_KEYS.horrorfestMode, horrorfestMode);
  for (const button of horrorfestModeButtons) {
    button.classList.toggle("active", button.dataset.horrorfestMode === horrorfestMode);
  }
  horrorfestLogPanel.classList.toggle("hidden", horrorfestMode !== "log");
  horrorfestAnalyticsPanel.classList.toggle("hidden", horrorfestMode !== "analytics");
}

function syncHorrorfestAnalyticsSortUi() {
  for (const button of horrorfestAnalyticsSortButtons) {
    const isActive = button.dataset.horrorfestAnalyticsSort === horrorfestAnalyticsSortKey;
    button.classList.toggle("active", isActive);
    if (isActive) {
      button.dataset.sortDirection = horrorfestAnalyticsSortDirection;
    } else {
      delete button.dataset.sortDirection;
    }
  }
}

function renderHistoryFilterSummary() {
  const chips = [];
  if (linkedHistoryContext?.mediaItemId) {
    chips.push(
      renderStatusChip(`linked media: ${escapeHtml(linkedHistoryContext.label || "selected media")}`, "success")
    );
  } else if (linkedHistoryContext?.appliesQuery) {
    chips.push(
      renderStatusChip(`linked title: ${escapeHtml(linkedHistoryContext.label || historyQuery.value.trim())}`, "success")
    );
  } else if (linkedHistoryContext?.label) {
    chips.push(renderStatusChip(`context: ${escapeHtml(linkedHistoryContext.label)}`, "success"));
  }
  if (
    historyQuery.value.trim() &&
    (!linkedHistoryContext?.appliesQuery ||
      historyQuery.value.trim() !== (linkedHistoryContext.query || "").trim())
  ) {
    chips.push(renderStatusChip(`title: ${escapeHtml(historyQuery.value.trim())}`, "info"));
  }
  if (historyMediaType.value) {
    chips.push(renderStatusChip(historyMediaType.value, "neutral"));
  }
  if (historyLocalDateFrom.value) {
    chips.push(renderStatusChip(`from ${historyLocalDateFrom.value}`, "warning"));
  }
  if (historyLocalDateTo.value) {
    chips.push(renderStatusChip(`to ${historyLocalDateTo.value}`, "warning"));
  }
  if (historyIncludeDeleted.checked) {
    chips.push(renderStatusChip("including deleted", "danger"));
  }
  const sortLabel =
    historySortKey === "watched_at"
      ? "watched"
      : historySortKey === "title"
        ? "title"
        : "rating";
  chips.push(renderStatusChip(`sort ${sortLabel} ${historySortDirection}`, "neutral"));
  historyFilterSummary.innerHTML = chips.length
    ? `Active filters: ${chips.join(" ")}`
    : "Showing the latest watches.";
}

function initializeTheme() {
  const savedTheme = window.localStorage.getItem(UI_PREF_KEYS.theme) || "dark";
  document.documentElement.dataset.theme = savedTheme;
  themeToggle.textContent =
    savedTheme === "dark" ? "Switch to Light" : "Switch to Dark";
}

function toggleTheme() {
  const currentTheme = document.documentElement.dataset.theme || "dark";
  const nextTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nextTheme;
  window.localStorage.setItem(UI_PREF_KEYS.theme, nextTheme);
  themeToggle.textContent =
    nextTheme === "dark" ? "Switch to Light" : "Switch to Dark";
}

function setActiveAdminView(viewName) {
  const targetView = viewName || "imports";
  for (const button of adminNavButtons) {
    button.classList.toggle("active", button.dataset.adminViewTarget === targetView);
  }
  for (const panel of adminPanels) {
    panel.classList.toggle("hidden", panel.dataset.adminView !== targetView);
  }
  window.localStorage.setItem(UI_PREF_KEYS.activeAdminView, targetView);
}

function setActiveView(viewName) {
  const targetView = viewName || "dashboard";
  for (const button of navButtons) {
    button.classList.toggle("active", button.dataset.viewTarget === targetView);
  }
  for (const panel of viewPanels) {
    panel.classList.toggle("hidden", panel.dataset.view !== targetView);
  }
  window.localStorage.setItem(UI_PREF_KEYS.activeView, targetView);
}

function initializeUiShell() {
  initializeTheme();
  historyQuery.value = window.localStorage.getItem(UI_PREF_KEYS.historyQuery) || "";
  libraryQuery.value = window.localStorage.getItem(UI_PREF_KEYS.libraryQuery) || "";
  libraryShowQuery.value = window.localStorage.getItem(UI_PREF_KEYS.libraryShowQuery) || "";
  libraryYear.value = window.localStorage.getItem(UI_PREF_KEYS.libraryYear) || "";
  libraryEnrichmentStatus.value =
    window.localStorage.getItem(UI_PREF_KEYS.libraryEnrichmentStatus) || "";
  libraryWatched.value = window.localStorage.getItem(UI_PREF_KEYS.libraryWatched) || "";
  libraryLimitSelect.value =
    window.localStorage.getItem(UI_PREF_KEYS.libraryLimit) || libraryLimitSelect.value;
  libraryLimit = Number.parseInt(libraryLimitSelect.value, 10);
  loadPersistedLinkedHistoryContext();
  loadPersistedDashboardContexts();
  setActiveView(window.localStorage.getItem(UI_PREF_KEYS.activeView) || "dashboard");
  setActiveAdminView(window.localStorage.getItem(UI_PREF_KEYS.activeAdminView) || "imports");
  setLibraryMode(window.localStorage.getItem(UI_PREF_KEYS.libraryMode) || "movies");
  setHorrorfestMode(window.localStorage.getItem(UI_PREF_KEYS.horrorfestMode) || "log");
  syncHistorySortUi();
  syncHorrorfestAnalyticsSortUi();
  renderHistoryContextBanner();
  renderAdminContextBanner();
  renderHorrorfestContextBanner();
  renderHistoryFilterSummary();
  renderLibraryFilterSummary();
}

function setAuthenticatedUI(authenticated, message) {
  authStatus.textContent = message;
  loginCard.classList.toggle("hidden", authenticated);
  appCard.classList.toggle("hidden", !authenticated);
  opsSession.textContent = `Session: ${authenticated ? "authenticated" : "not authenticated"}`;
  if (authenticated) {
    loadImportPreferences();
    initializeUiShell();
  }
}

async function loadOpsHealth() {
  try {
    const response = await fetch("/api/v1/health", { credentials: "include" });
    if (!response.ok) {
      opsHealth.textContent = "API Health: unavailable";
      return;
    }
    const payload = await response.json();
    opsHealth.textContent = `API Health: ${payload.status}`;
  } catch (_error) {
    opsHealth.textContent = "API Health: unavailable";
  }
}

function setLastRefreshNow() {
  opsLastRefresh.textContent = `Last Refresh: ${new Date().toLocaleString()}`;
}

function toggleManualWatchInputs() {
  const isMovie = manualWatchMediaType.value === "movie";
  manualWatchTmdbId.disabled = !isMovie;
  manualWatchShowTmdbId.disabled = isMovie;
  manualWatchTmdbEpisodeId.disabled = isMovie;
  manualWatchSeasonNumber.disabled = isMovie;
  manualWatchEpisodeNumber.disabled = isMovie;
}

function loadManualWatchPreferences() {
  manualWatchUserId.value =
    localStorage.getItem(MANUAL_WATCH_PREF_KEYS.userId) || importUserId.value || "";
  manualWatchPlaybackSource.value =
    localStorage.getItem(MANUAL_WATCH_PREF_KEYS.playbackSource) || "streaming";
  manualWatchCreatedBy.value =
    localStorage.getItem(MANUAL_WATCH_PREF_KEYS.createdBy) || "";
  if (!manualWatchWatchedAt.value) {
    const now = new Date();
    manualWatchWatchedAt.value = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
  }
  toggleManualWatchInputs();
}

function saveManualWatchPreferences() {
  localStorage.setItem(MANUAL_WATCH_PREF_KEYS.userId, manualWatchUserId.value.trim());
  localStorage.setItem(
    MANUAL_WATCH_PREF_KEYS.playbackSource,
    manualWatchPlaybackSource.value.trim()
  );
  localStorage.setItem(MANUAL_WATCH_PREF_KEYS.createdBy, manualWatchCreatedBy.value.trim());
}

async function checkSession() {
  authStatus.textContent = "Checking session...";
  await loadOpsHealth();
  try {
    const response = await api("/api/v1/session/me");
    if (!response.ok) {
      opsAuthMode.textContent = "Auth Mode: unavailable";
      setAuthenticatedUI(false, "Session check failed");
      return;
    }
    const payload = await response.json();
    opsAuthMode.textContent = `Auth Mode: ${payload.auth_mode}`;
    if (payload.authenticated) {
      setAuthenticatedUI(true, "Authenticated");
      await loadDashboardData();
    } else {
      setAuthenticatedUI(false, "Not authenticated");
    }
  } catch (_error) {
    opsAuthMode.textContent = "Auth Mode: unavailable";
    setAuthenticatedUI(false, "Session check failed");
  }
}

async function loadDashboardData() {
  loadManualWatchPreferences();
  await Promise.all([
    loadLibrary(),
    loadShows(),
    loadStats(),
    loadDashboardPreviews(),
    loadHistory(),
    loadUnratedWatches(),
    loadHorrorfestWorkspace(),
    loadImportHistory(),
    loadScrobbleActivity(),
    loadMetadataEnrichment(),
  ]);
  await loadDashboardNeedsAttention();
  setLastRefreshNow();
}

function formatDecimalValue(value, digits = 2) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return numeric.toFixed(digits);
}

function renderStatsSummaryCards(summary) {
  const cards = [
    ["Active Watches", summary.total_active_watches],
    ["Completed", summary.total_completed_watches],
    ["Rewatches", summary.total_rewatches],
    ["Watch Time", `${formatDecimalValue(summary.total_watch_time_hours)}h`],
    ["Movies", summary.movie_watch_count],
    ["Episodes", summary.episode_watch_count],
    ["Avg Rating", summary.average_rating_value ? formatDecimalValue(summary.average_rating_value) : "-"],
    ["Unrated Backlog", summary.unrated_completed_watch_count],
  ];
  statsSummaryCards.innerHTML = "";
  for (const [label, value] of cards) {
    const card = document.createElement("div");
    card.className = "stats-card";
    card.innerHTML = `
      <div class="stats-card-label">${label}</div>
      <div class="stats-card-value">${value}</div>
    `;
    statsSummaryCards.appendChild(card);
  }
}

function renderDashboardEmptyRow(body, colspan, message) {
  body.innerHTML = "";
  const tr = document.createElement("tr");
  tr.innerHTML = `<td colspan="${colspan}">${message}</td>`;
  body.appendChild(tr);
}

async function openHistoryForMedia({
  mediaItemId,
  label,
  mediaType = "",
  sourceView = "library",
  libraryModeValue = libraryMode,
  showId = null,
}) {
  if (!mediaItemId) {
    return;
  }
  historyOffset = 0;
  historyQuery.value = "";
  historyMediaType.value = mediaType || "";
  historyLocalDateFrom.value = "";
  historyLocalDateTo.value = "";
  historyIncludeDeleted.checked = false;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
  setLinkedHistoryContext({
    type: "media_item",
    mediaItemId,
    label,
    mediaType: mediaType || "",
    sourceView,
    libraryMode: libraryModeValue || libraryMode,
    showId,
    appliesQuery: false,
  });
  setActiveView("history");
  await loadHistory();
}

async function openHistoryForShow({
  title,
  label = title,
  sourceView = "library",
  libraryModeValue = libraryMode,
  showId = null,
}) {
  if (!title) {
    return;
  }
  historyOffset = 0;
  historyQuery.value = title;
  historyMediaType.value = "episode";
  historyLocalDateFrom.value = "";
  historyLocalDateTo.value = "";
  historyIncludeDeleted.checked = false;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, title);
  setLinkedHistoryContext({
    type: "show_title",
    query: title,
    label,
    sourceView,
    libraryMode: libraryModeValue || libraryMode,
    showId,
    appliesQuery: true,
  });
  setActiveView("history");
  await loadHistory();
}

async function returnHistoryContextToSource() {
  if (!linkedHistoryContext) {
    return;
  }
  if (linkedHistoryContext.sourceView === "library") {
    if (linkedHistoryContext.libraryMode) {
      setLibraryMode(linkedHistoryContext.libraryMode);
    }
    setActiveView("library");
    await loadLibrary();
    return;
  }
  if (linkedHistoryContext.sourceView === "shows") {
    const selectedShowId = linkedHistoryContext.showId || null;
    setActiveView("shows");
    await loadShows();
    if (selectedShowId) {
      await loadShowDetail(selectedShowId);
    }
    return;
  }
  if (linkedHistoryContext.sourceView === "dashboard") {
    setActiveView("dashboard");
    await loadDashboardData();
    return;
  }
  clearLinkedHistoryContext();
  await loadHistory();
}

function toDateInputValueFromIso(value) {
  if (!value) {
    return "";
  }
  return toDateTimeLocalValue(value).slice(0, 10);
}

async function openHistoryForMonth({ year, month }) {
  historyOffset = 0;
  historyQuery.value = "";
  historyMediaType.value = "";
  historyIncludeDeleted.checked = false;
  const monthStart = new Date(year, month - 1, 1);
  const monthEnd = new Date(year, month, 0);
  historyLocalDateFrom.value = formatDateInputValue(monthStart);
  historyLocalDateTo.value = formatDateInputValue(monthEnd);
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
  setLinkedHistoryContext({
    type: "month_range",
    label: `${year}-${String(month).padStart(2, "0")}`,
    sourceView: "dashboard",
    appliesQuery: false,
  });
  setActiveView("history");
  await loadHistory();
}

async function openHistoryForUnratedQueue() {
  historyOffset = 0;
  historyQuery.value = "";
  historyMediaType.value = "";
  historyLocalDateFrom.value = "";
  historyLocalDateTo.value = "";
  historyIncludeDeleted.checked = false;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
  setLinkedHistoryContext({
    type: "unrated_queue",
    label: "Unrated Queue",
    sourceView: "dashboard",
    appliesQuery: false,
  });
  setActiveView("history");
  await Promise.all([loadHistory(), loadUnratedWatches()]);
}

async function openHistoryForHorrorfestYear(selectedYear) {
  historyOffset = 0;
  historyQuery.value = "";
  historyMediaType.value = "movie";
  historyLocalDateFrom.value = toDateInputValueFromIso(selectedYear.window_start_at);
  historyLocalDateTo.value = toDateInputValueFromIso(selectedYear.window_end_at);
  historyIncludeDeleted.checked = false;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, "");
  setLinkedHistoryContext({
    type: "horrorfest_year_window",
    label: `Horrorfest ${selectedYear.horrorfest_year}`,
    sourceView: "dashboard",
    appliesQuery: false,
  });
  setActiveView("history");
  await loadHistory();
}

function getCurrentHorrorfestYearSummary() {
  if (!horrorfestYears.length) {
    return null;
  }
  const activeYear =
    horrorfestYears.find((row) => row.is_active) ||
    [...horrorfestYears].sort((left, right) => right.horrorfest_year - left.horrorfest_year)[0];
  if (!activeYear) {
    return null;
  }
  const statsRow =
    statsHorrorfestRowsData.find(
      (row) => row.horrorfest_year === activeYear.horrorfest_year
    ) || null;
  return {
    year: activeYear.horrorfest_year,
    label: activeYear.label || `Horrorfest ${activeYear.horrorfest_year}`,
    windowStartAt: activeYear.window_start_at,
    windowEndAt: activeYear.window_end_at,
    entryCount: statsRow?.entry_count ?? activeYear.entry_count ?? 0,
    averageRatingValue: statsRow?.average_rating_value ?? null,
    latestWatchAt: statsRow?.latest_watch_at ?? null,
  };
}

async function openDashboardHorrorfestYear(year, label = null) {
  setHorrorfestContext({
    year,
    label: label || `Horrorfest ${year}`,
    sourceView: "dashboard",
  });
  setActiveView("horrorfest");
  await loadHorrorfestWorkspace(String(year));
}

async function openDashboardEnrichment(status, label = null) {
  setAdminContext({
    adminView: "enrichment",
    enrichmentStatus: status || "",
    label: label || status || "selected enrichment rows",
    sourceView: "dashboard",
  });
  setActiveView("admin");
  setActiveAdminView("enrichment");
  enrichmentStatusFilter.value = status || "";
  await loadMetadataEnrichment();
}

function setLibraryMode(mode) {
  libraryMode = mode || "movies";
  for (const button of libraryModeButtons) {
    button.classList.toggle("active", button.dataset.libraryMode === libraryMode);
  }
  const isMovies = libraryMode === "movies";
  const isEpisodes = libraryMode === "episodes";
  libraryYear.disabled = !isMovies;
  libraryShowQuery.disabled = !isEpisodes;
  window.localStorage.setItem(UI_PREF_KEYS.libraryMode, libraryMode);
  renderLibraryFilterSummary();
}

function renderLibraryFilterSummary() {
  const chips = [renderStatusChip(`mode: ${libraryMode}`, "info")];
  if (libraryQuery.value.trim()) {
    chips.push(renderStatusChip(`title: ${escapeHtml(libraryQuery.value.trim())}`, "neutral"));
  }
  if (libraryMode === "episodes" && libraryShowQuery.value.trim()) {
    chips.push(
      renderStatusChip(`show: ${escapeHtml(libraryShowQuery.value.trim())}`, "neutral")
    );
  }
  if (libraryMode === "movies" && libraryYear.value.trim()) {
    chips.push(renderStatusChip(`year: ${escapeHtml(libraryYear.value.trim())}`, "neutral"));
  }
  if (libraryEnrichmentStatus.value) {
    chips.push(
      renderStatusChip(`enrichment: ${escapeHtml(libraryEnrichmentStatus.value)}`, "warning")
    );
  }
  if (libraryWatched.value) {
    chips.push(renderStatusChip(`watched: ${libraryWatched.value}`, "success"));
  }
  libraryFilterSummary.innerHTML = `Active filters: ${chips.join(" ")}`;
}

function setLibraryPagination(rowsLoaded) {
  const page = Math.floor(libraryOffset / libraryLimit) + 1;
  libraryPage.textContent = `Page ${page}`;
  libraryPrev.disabled = libraryOffset === 0;
  libraryNext.disabled = rowsLoaded < libraryLimit;
}

function buildLibraryQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(libraryLimit));
  params.set("offset", String(libraryOffset));
  if (libraryQuery.value.trim()) {
    params.set("query", libraryQuery.value.trim());
  }
  if (libraryEnrichmentStatus.value && libraryMode !== "shows") {
    params.set("enrichment_status", libraryEnrichmentStatus.value);
  }
  if (libraryWatched.value) {
    params.set("watched", libraryWatched.value);
  }
  if (libraryMode === "movies" && libraryYear.value.trim()) {
    params.set("year", libraryYear.value.trim());
  }
  if (libraryMode === "episodes" && libraryShowQuery.value.trim()) {
    params.set("show_query", libraryShowQuery.value.trim());
  }
  return params.toString();
}

function renderLibraryHeader() {
  if (libraryMode === "movies") {
    libraryHead.innerHTML =
      "<th>Title</th><th>Latest Watch</th><th>Watches</th><th>Latest Rating</th><th>Signals</th><th>Actions</th>";
    return;
  }
  if (libraryMode === "episodes") {
    libraryHead.innerHTML =
      "<th>Episode</th><th>Show</th><th>Latest Watch</th><th>Watches</th><th>Signals</th><th>Actions</th>";
    return;
  }
  libraryHead.innerHTML = "<th>Show</th><th>Year</th><th>Progress</th><th>Signals</th><th>Actions</th>";
}

function renderLibraryEmpty(message) {
  libraryBody.innerHTML = "";
  const tr = document.createElement("tr");
  const columnCount = libraryMode === "shows" ? 5 : 6;
  tr.innerHTML = `<td colspan="${columnCount}">${message}</td>`;
  libraryBody.appendChild(tr);
}

function renderLibraryRows() {
  libraryBody.innerHTML = "";
  if (!libraryRows.length) {
    renderLibraryEmpty("No watched media rows for the current filter.");
    return;
  }
  for (const row of libraryRows) {
    const tr = document.createElement("tr");
    tr.classList.add("history-row-clickable");
    if (libraryMode === "movies") {
      const signals = [
        row.horrorfest_year
          ? renderStatusChip(`HF ${row.horrorfest_year}`, "danger")
          : "",
        renderStatusChip(
          escapeHtml(row.enrichment_status),
          row.enrichment_status === "enriched"
            ? "success"
            : row.enrichment_status === "failed"
              ? "danger"
              : "warning"
        ),
      ]
        .filter(Boolean)
        .join(" ");
      tr.innerHTML = `
        <td>
          <div class="library-title-cell">
            ${
              row.media_item_id
                ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(row.title)}</button>`
                : escapeHtml(row.title)
            }
            <div class="muted">${escapeHtml(row.year || "-")}</div>
          </div>
        </td>
        <td>${row.latest_watched_at ? new Date(row.latest_watched_at).toLocaleDateString() : "-"}</td>
        <td>${escapeHtml(row.watch_count)}</td>
        <td>${row.latest_rating_value ? renderStatusChip(`${row.latest_rating_value}/${row.latest_rating_scale || 10}`, "info") : renderStatusChip("unrated", "neutral")}</td>
        <td><div class="history-badges">${signals}</div></td>
        <td>
          <div class="button-cluster compact-actions">
            <button class="secondary library-inline-button" data-media-item-open="${row.media_item_id}" type="button">Open Media</button>
            <button class="secondary library-inline-button" data-library-history-open="${row.media_item_id}" data-library-history-label="${escapeHtml(row.title)}" data-library-history-type="movie" type="button">Open History</button>
          </div>
        </td>
      `;
    } else if (libraryMode === "episodes") {
      const signals = [
        row.horrorfest_year
          ? renderStatusChip(`HF ${row.horrorfest_year}`, "danger")
          : "",
        renderStatusChip(
          escapeHtml(row.enrichment_status),
          row.enrichment_status === "enriched"
            ? "success"
            : row.enrichment_status === "failed"
              ? "danger"
              : "warning"
        ),
      ]
        .filter(Boolean)
        .join(" ");
      tr.innerHTML = `
        <td>
          <div class="library-title-cell">
            ${
              row.media_item_id
                ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(row.title)}</button>`
                : escapeHtml(row.title)
            }
            <div class="muted">S${String(row.season_number ?? "?").padStart(2, "0")}E${String(row.episode_number ?? "?").padStart(2, "0")}</div>
          </div>
        </td>
        <td>${escapeHtml(row.show_title || "-")}</td>
        <td>${row.latest_watched_at ? new Date(row.latest_watched_at).toLocaleDateString() : "-"}</td>
        <td>${escapeHtml(row.watch_count)}</td>
        <td><div class="history-badges">${signals}</div></td>
        <td>
          <div class="button-cluster compact-actions">
            <button class="secondary library-inline-button" data-media-item-open="${row.media_item_id}" type="button">Open Media</button>
            <button class="secondary library-inline-button" data-library-history-open="${row.media_item_id}" data-library-history-label="${escapeHtml(row.show_title ? `${row.show_title} - ${row.title}` : row.title)}" data-library-history-type="episode" type="button">Open History</button>
          </div>
        </td>
      `;
    } else {
      const signals = [
        Number(row.watched_percent) >= 100
          ? renderStatusChip("caught up", "success")
          : renderStatusChip(`${row.watched_episodes} watched`, "warning"),
      ].join(" ");
      tr.innerHTML = `
        <td>
          <div class="library-title-cell">
            <button class="media-link-button" data-library-show-open="${row.show_id}" type="button">${escapeHtml(row.title)}</button>
          </div>
        </td>
        <td>${escapeHtml(row.year || "-")}</td>
        <td>${escapeHtml(`${row.watched_episodes}/${row.total_episodes}`)}</td>
        <td><div class="history-badges">${signals} ${renderStatusChip(`${row.watched_percent}%`, Number(row.watched_percent) >= 100 ? "success" : Number(row.watched_percent) > 0 ? "warning" : "neutral")}</div></td>
        <td>
          <div class="button-cluster compact-actions">
            <button class="secondary library-inline-button" data-library-show-open="${row.show_id}" type="button">Show Detail</button>
            <button class="secondary library-inline-button" data-library-show-history="${escapeHtml(row.title)}" type="button">Open History</button>
            ${
              row.media_item_id
                ? `<button class="secondary library-inline-button" data-media-item-open="${row.media_item_id}" type="button">Open Media</button>`
                : ""
            }
          </div>
        </td>
      `;
    }
    libraryBody.appendChild(tr);
  }
}

async function openLibraryShow(showId) {
  if (!showId) {
    return;
  }
  setActiveView("shows");
  await loadShows();
  await loadShowDetail(showId);
}

async function loadLibrary() {
  renderLibraryHeader();
  renderLibraryFilterSummary();
  libraryStatus.textContent = "Loading watched library...";
  libraryBody.innerHTML = "";
  try {
    const response = await api(`/api/v1/library/${libraryMode}?${buildLibraryQuery()}`);
    if (!response.ok) {
      libraryStatus.textContent = "Failed to load watched library";
      renderLibraryEmpty("Watched library unavailable right now.");
      setLibraryPagination(0);
      return;
    }
    libraryRows = await response.json();
    if (!libraryRows.length) {
      libraryStatus.textContent = "No watched media rows for the current filter";
      renderLibraryEmpty("No watched media rows for the current filter.");
      setLibraryPagination(0);
      return;
    }
    renderLibraryRows();
    libraryStatus.textContent = `Loaded ${libraryRows.length} ${libraryMode} row(s)`;
    setLibraryPagination(libraryRows.length);
  } catch (_error) {
    libraryStatus.textContent = "Failed to load watched library";
    renderLibraryEmpty("Watched library unavailable right now.");
    setLibraryPagination(0);
  }
}

async function loadDashboardRecentHistoryPreview() {
  dashboardHistoryStatus.textContent = "Loading recent watches...";
  try {
    const response = await api("/api/v1/watch-events?limit=5&offset=0");
    if (!response.ok) {
      dashboardHistoryStatus.textContent = "Failed to load recent watches";
      renderDashboardEmptyRow(dashboardHistoryBody, 4, "Recent watch preview unavailable");
      return;
    }
    const rows = await response.json();
    dashboardHistoryBody.innerHTML = "";
    if (!rows.length) {
      dashboardHistoryStatus.textContent = "No watch history yet";
      renderDashboardEmptyRow(dashboardHistoryBody, 4, "No watch history yet");
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      const title = row.display_title || row.media_item_title || row.media_item_id;
      const signals = [
        row.rating_value ? renderStatusChip(`${row.rating_value}/10`, "info") : "",
        row.rewatch ? renderStatusChip("rewatch", "warning") : "",
        row.horrorfest_year ? renderStatusChip(`HF ${row.horrorfest_year}`, "danger") : "",
        row.is_deleted ? renderStatusChip("deleted", "neutral") : "",
      ]
        .filter(Boolean)
        .join(" ");
      tr.classList.toggle("history-row-clickable", Boolean(row.media_item_id));
      tr.innerHTML = `
        <td>${new Date(row.watched_at).toLocaleDateString()}</td>
        <td>
          <div class="library-title-cell">
            ${
              row.media_item_id
                ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(title)}</button>`
                : escapeHtml(title)
            }
            ${
              row.media_item_id
                ? `<div class="compact-actions"><button class="secondary library-inline-button" data-dashboard-history-open="${row.media_item_id}" data-dashboard-history-label="${escapeHtml(title)}" data-dashboard-history-type="${row.media_item_type || ""}" type="button">Open History</button></div>`
                : ""
            }
          </div>
        </td>
        <td>${row.playback_source}</td>
        <td>${signals || renderStatusChip("active", "success")}</td>
      `;
      dashboardHistoryBody.appendChild(tr);
    }
    dashboardHistoryStatus.textContent = `Showing ${rows.length} recent watch(es)`;
  } catch (_error) {
    dashboardHistoryStatus.textContent = "Failed to load recent watches";
    renderDashboardEmptyRow(dashboardHistoryBody, 4, "Recent watch preview unavailable");
  }
}

async function loadDashboardUnratedPreview() {
  dashboardRatingsStatus.textContent = "Loading unrated queue...";
  try {
    const response = await api("/api/v1/watch-events/unrated?limit=5");
    if (!response.ok) {
      dashboardRatingsStatus.textContent = "Failed to load unrated queue";
      renderDashboardEmptyRow(dashboardRatingsBody, 4, "Unrated queue unavailable");
      return;
    }
    const rows = await response.json();
    dashboardRatingsBody.innerHTML = "";
    if (!rows.length) {
      dashboardRatingsStatus.textContent = "No unrated completed watches";
      renderDashboardEmptyRow(dashboardRatingsBody, 4, "Nothing waiting on ratings");
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      const title = row.display_title || row.media_item_title || row.media_item_id;
      tr.classList.toggle("history-row-clickable", Boolean(row.media_item_id));
      tr.innerHTML = `
        <td>${new Date(row.watched_at).toLocaleDateString()}</td>
        <td>
          ${
            row.media_item_id
              ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(title)}</button>`
              : escapeHtml(title)
          }
        </td>
        <td>${row.playback_source}</td>
        <td><button class="secondary library-inline-button" data-dashboard-unrated-open type="button">Open Queue</button></td>
      `;
      dashboardRatingsBody.appendChild(tr);
    }
    dashboardRatingsStatus.textContent = `Showing ${rows.length} unrated watch(es)`;
  } catch (_error) {
    dashboardRatingsStatus.textContent = "Failed to load unrated queue";
    renderDashboardEmptyRow(dashboardRatingsBody, 4, "Unrated queue unavailable");
  }
}

async function loadDashboardEnrichmentPreview() {
  dashboardEnrichmentStatus.textContent = "Loading enrichment watchlist...";
  try {
    let response = await api("/api/v1/metadata-enrichment/items?enrichment_status=failed&limit=5");
    let previewLabel = "failed";
    if (!response.ok) {
      dashboardEnrichmentStatus.textContent = "Failed to load enrichment watchlist";
      renderDashboardEmptyRow(dashboardEnrichmentBody, 5, "Enrichment preview unavailable");
      return;
    }
    let rows = await response.json();
    if (!rows.length) {
      response = await api("/api/v1/metadata-enrichment/items?enrichment_status=pending&limit=5");
      previewLabel = "pending";
      if (!response.ok) {
        dashboardEnrichmentStatus.textContent = "Failed to load enrichment watchlist";
        renderDashboardEmptyRow(dashboardEnrichmentBody, 5, "Enrichment preview unavailable");
        return;
      }
      rows = await response.json();
    }

    dashboardEnrichmentBody.innerHTML = "";
    if (!rows.length) {
      dashboardEnrichmentStatus.textContent = "No pending or failed enrichment rows";
      renderDashboardEmptyRow(dashboardEnrichmentBody, 5, "Enrichment queue is clear");
      dashboardEnrichmentPreviewStatus = "";
      dashboardEnrichmentOpen.textContent = "Open Queue";
      return;
    }

    for (const row of rows) {
      const tr = document.createElement("tr");
      const tone =
        row.enrichment_status === "failed"
          ? "danger"
          : row.enrichment_status === "pending"
            ? "warning"
            : "info";
      tr.innerHTML = `
        <td>${row.title}</td>
        <td>${row.type}</td>
        <td>${renderStatusChip(row.enrichment_status, tone)}</td>
        <td>${row.next_action || "-"}</td>
        <td><button class="secondary library-inline-button" data-dashboard-enrichment-open="${row.enrichment_status}" type="button">Open Filter</button></td>
      `;
      dashboardEnrichmentBody.appendChild(tr);
    }
    dashboardEnrichmentStatus.textContent = `Showing ${previewLabel} enrichment rows`;
    dashboardEnrichmentPreviewStatus = previewLabel;
    dashboardEnrichmentOpen.textContent =
      previewLabel === "failed" ? "Open Failed" : "Open Pending";
  } catch (_error) {
    dashboardEnrichmentStatus.textContent = "Failed to load enrichment watchlist";
    renderDashboardEmptyRow(dashboardEnrichmentBody, 5, "Enrichment preview unavailable");
    dashboardEnrichmentPreviewStatus = "";
    dashboardEnrichmentOpen.textContent = "Open Queue";
  }
}

async function loadDashboardNeedsAttention() {
  dashboardAttentionGrid.innerHTML = "";
  const currentHorrorfest = getCurrentHorrorfestYearSummary();
  let failedCount = 0;
  let pendingCount = 0;
  try {
    const [failedResponse, pendingResponse] = await Promise.all([
      api("/api/v1/metadata-enrichment/items?enrichment_status=failed&limit=250"),
      api("/api/v1/metadata-enrichment/items?enrichment_status=pending&limit=250"),
    ]);
    if (failedResponse.ok) {
      failedCount = (await failedResponse.json()).length;
    }
    if (pendingResponse.ok) {
      pendingCount = (await pendingResponse.json()).length;
    }
  } catch (_error) {
    failedCount = 0;
    pendingCount = 0;
  }

  const importIssuesCount = importHistoryRows.filter((row) =>
    row.status === "failed" || row.status === "completed_with_errors"
  ).length;

  const cards = [
    {
      title: "Unrated Watches",
      value: statsSummaryData?.unrated_completed_watch_count ?? 0,
      subtitle: "Completed watches waiting for a rating.",
      tone: "warning",
      actionLabel: "Open Queue",
      actionKey: "unrated",
    },
    {
      title: "Failed Enrichment",
      value: failedCount,
      subtitle: "Media items that still need metadata help.",
      tone: failedCount ? "danger" : "success",
      actionLabel: "Open Failed",
      actionKey: "enrichment-failed",
    },
    {
      title: "Pending Enrichment",
      value: pendingCount,
      subtitle: "Queued rows waiting to be enriched.",
      tone: pendingCount ? "warning" : "success",
      actionLabel: "Open Pending",
      actionKey: "enrichment-pending",
    },
  ];

  if (currentHorrorfest) {
    cards.push({
      title: currentHorrorfest.label,
      value: currentHorrorfest.entryCount,
      subtitle: currentHorrorfest.latestWatchAt
        ? `Latest watch ${new Date(currentHorrorfest.latestWatchAt).toLocaleDateString()}`
        : "Open the current Horrorfest year.",
      tone: "danger",
      actionLabel: "Open Year",
      actionKey: "horrorfest-current",
      year: currentHorrorfest.year,
    });
  }

  if (importIssuesCount) {
    cards.push({
      title: "Import Issues",
      value: importIssuesCount,
      subtitle: "Recent imports with failures or recorded errors.",
      tone: "info",
      actionLabel: "Open Imports",
      actionKey: "imports-errors",
    });
  }

  dashboardAttentionGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="attention-card">
          <div class="stats-card-label">${escapeHtml(card.title)}</div>
          <div class="attention-card-value">${escapeHtml(card.value)}</div>
          <p class="muted">${escapeHtml(card.subtitle)}</p>
          <div class="compact-actions">
            <button class="secondary library-inline-button" data-dashboard-action="${card.actionKey}" ${card.year ? `data-dashboard-year="${card.year}"` : ""} type="button">${escapeHtml(card.actionLabel)}</button>
            ${
              card.actionKey === "horrorfest-current" && card.year
                ? `<button class="secondary library-inline-button" data-dashboard-action="horrorfest-history" data-dashboard-year="${card.year}" type="button">Open History</button>`
                : ""
            }
          </div>
        </article>
      `
    )
    .join("");
}

async function loadDashboardPreviews() {
  await Promise.all([
    loadDashboardRecentHistoryPreview(),
    loadDashboardUnratedPreview(),
    loadDashboardEnrichmentPreview(),
  ]);
}

async function loadStats() {
  statsStatus.textContent = "Loading stats...";
  statsSummaryCards.innerHTML = "";
  statsMonthlyBody.innerHTML = "";
  statsHorrorfestBody.innerHTML = "";
  try {
    const [summaryResponse, monthlyResponse, horrorfestResponse] = await Promise.all([
      api("/api/v1/stats/summary"),
      api("/api/v1/stats/monthly"),
      api("/api/v1/stats/horrorfest"),
    ]);
    if (!summaryResponse.ok || !monthlyResponse.ok || !horrorfestResponse.ok) {
      statsStatus.textContent = "Failed to load stats";
      return;
    }
    const [summary, monthlyRows, horrorfestRows] = await Promise.all([
      summaryResponse.json(),
      monthlyResponse.json(),
      horrorfestResponse.json(),
    ]);
    statsSummaryData = summary;
    statsMonthlyRowsData = monthlyRows;
    statsHorrorfestRowsData = horrorfestRows;

    renderStatsSummaryCards(summary);

    if (!monthlyRows.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="8">No monthly watch stats yet</td>';
      statsMonthlyBody.appendChild(tr);
    } else {
      for (const row of monthlyRows) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><button class="media-link-button" data-dashboard-month="${row.month}" data-dashboard-year="${row.year}" type="button">${row.year}-${String(row.month).padStart(2, "0")}</button></td>
          <td>${row.watch_count}</td>
          <td>${row.movie_count}</td>
          <td>${row.episode_count}</td>
          <td>${row.rewatch_count}</td>
          <td>${row.rated_watch_count}</td>
          <td>${formatDecimalValue(Number(row.total_runtime_seconds || 0) / 3600)}</td>
          <td>${row.average_rating_value ? formatDecimalValue(row.average_rating_value) : "-"}</td>
        `;
        statsMonthlyBody.appendChild(tr);
      }
    }

    if (!horrorfestRows.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="8">No Horrorfest stats yet</td>';
      statsHorrorfestBody.appendChild(tr);
    } else {
      for (const row of horrorfestRows) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><button class="media-link-button" data-dashboard-horrorfest-year="${row.horrorfest_year}" type="button">${row.horrorfest_year}</button></td>
          <td>${row.entry_count}</td>
          <td>${formatDecimalValue(row.total_runtime_hours)}</td>
          <td>${row.average_rating_value ? formatDecimalValue(row.average_rating_value) : "-"}</td>
          <td>${row.rated_entry_count}</td>
          <td>${row.rewatch_count}</td>
          <td>${row.first_watch_at ? new Date(row.first_watch_at).toLocaleString() : "-"}</td>
          <td>${row.latest_watch_at ? new Date(row.latest_watch_at).toLocaleString() : "-"}</td>
        `;
        statsHorrorfestBody.appendChild(tr);
      }
    }

    statsStatus.textContent = "Loaded stats";
  } catch (_error) {
    statsStatus.textContent = "Failed to load stats";
  }
}

async function loadShows() {
  showsStatus.textContent = "Loading shows...";
  showList.innerHTML = "";
  selectedShowDetail = null;
  detailCard.classList.add("hidden");
  try {
    const response = await api("/api/v1/shows");
    if (!response.ok) {
      showsStatus.textContent = "Failed to load shows";
      return;
    }
    const shows = await response.json();
    if (shows.length === 0) {
      showsStatus.textContent = "No shows found";
      return;
    }
    showsStatus.textContent = `Loaded ${shows.length} show(s)`;
    for (const show of shows) {
      const li = document.createElement("li");
      li.className = "show-browse-row";
      const latestWatchLabel = show.latest_watched_at
        ? new Date(show.latest_watched_at).toLocaleDateString()
        : "No watched episodes yet";
      li.innerHTML = `
        <div class="show-browse-main">
          <div class="show-browse-title">${escapeHtml(show.title)}</div>
          <div class="show-browse-meta">
            ${show.year ? renderStatusChip(String(show.year), "neutral") : ""}
            ${renderStatusChip(`${show.watched_episode_count || 0} watched`, show.watched_episode_count ? "success" : "neutral")}
            ${show.latest_watched_at ? renderStatusChip(`Latest ${escapeHtml(latestWatchLabel)}`, "info") : renderStatusChip("no recent watch", "warning")}
          </div>
        </div>
        <div class="compact-actions">
          <button class="secondary library-inline-button" data-show-open="${show.show_id}" type="button">Open Show</button>
          <button class="secondary library-inline-button" data-show-history="${escapeHtml(show.title)}" data-show-id="${show.show_id}" type="button">Open History</button>
        </div>
      `;
      showList.appendChild(li);
    }
  } catch (_error) {
    showsStatus.textContent = "Failed to load shows";
  }
}

function getSeasonStateKey(showId, seasonNumber) {
  return `${showId}:${seasonNumber ?? 0}`;
}

function isSeasonExpanded(showId, seasonNumber, defaultSeasonKey) {
  const key = getSeasonStateKey(showId, seasonNumber);
  if (showSeasonExpandState.has(key)) {
    return showSeasonExpandState.get(key);
  }
  return String(seasonNumber ?? 0) === defaultSeasonKey;
}

function toggleSeasonExpanded(showId, seasonNumber) {
  const key = getSeasonStateKey(showId, seasonNumber);
  const currentlyExpanded = showSeasonExpandState.get(key) ?? false;
  showSeasonExpandState.set(key, !currentlyExpanded);
}

function getShowDetailSummary(detail) {
  const watchedEpisodes = detail.episodes.filter((episode) => episode.watched_by_user).length;
  const latestWatchedAt = detail.episodes
    .map((episode) => episode.latest_watched_at)
    .filter(Boolean)
    .sort()
    .at(-1);
  return {
    watchedEpisodes,
    latestWatchedAt,
  };
}

async function loadShowDetail(showId) {
  detailStatus.textContent = "Loading detail...";
  detailCard.classList.remove("hidden");
  episodeList.innerHTML = "";
  detailSummary.innerHTML = "";
  try {
    const response = await api(`/api/v1/shows/${showId}`);
    if (!response.ok) {
      detailStatus.textContent = "Failed to load show detail";
      return;
    }
    const detail = await response.json();
    selectedShowDetail = detail;
    detailTitle.textContent = detail.show.title;
    const summary = getShowDetailSummary(detail);
    detailProgress.textContent = summary.latestWatchedAt
      ? `Watched episodes logged in Klug: ${summary.watchedEpisodes} · Latest watch ${new Date(summary.latestWatchedAt).toLocaleString()}`
      : `Watched episodes logged in Klug: ${summary.watchedEpisodes}`;
    detailSummary.innerHTML = `
      <section class="detail-section">
        <h4>Show Snapshot</h4>
        <div class="meta-pill-grid">
          ${renderMetaPills([
            ["Watched Episodes", summary.watchedEpisodes],
            ["Latest Watch", summary.latestWatchedAt ? new Date(summary.latestWatchedAt).toLocaleDateString() : "-"],
            ["TMDB", detail.show.tmdb_id],
            ["Year", detail.show.year || "-"],
          ])}
        </div>
        <div class="detail-grid">
          ${renderDetailItems([
            ["TVDB", escapeHtml(detail.show.tvdb_id || "-")],
            ["IMDB", escapeHtml(detail.show.imdb_id || "-")],
            ["Episode Rows", detail.episodes.length],
          ])}
        </div>
      </section>
    `;

    const groupedEpisodes = new Map();
    for (const episode of detail.episodes) {
      const seasonKey = String(episode.season_number ?? 0);
      const existing = groupedEpisodes.get(seasonKey) || [];
      existing.push(episode);
      groupedEpisodes.set(seasonKey, existing);
    }

    const seasons = Array.from(groupedEpisodes.entries()).sort(
      ([left], [right]) => Number(left) - Number(right)
    );
    const firstWatchedSeason =
      seasons.find(([, seasonEpisodes]) => seasonEpisodes.some((ep) => ep.watched_by_user))?.[0] ??
      seasons[0]?.[0] ??
      "0";
    for (const [seasonKey, seasonEpisodes] of seasons) {
      const seasonSection = document.createElement("li");
      const watchedCount = seasonEpisodes.filter((ep) => ep.watched_by_user).length;
      const heading = Number(seasonKey) === 0 ? "Specials" : `Season ${seasonKey}`;
      const expanded = isSeasonExpanded(detail.show.show_id, seasonKey, firstWatchedSeason);
      const listItems = seasonEpisodes
        .sort((left, right) => (left.episode_number ?? 0) - (right.episode_number ?? 0))
        .map((ep) => {
          const watchedLabel =
            ep.watched_by_user === null
              ? `watches: ${ep.watched_count}`
              : ep.watched_by_user
                ? "watched"
                : "not watched";
          return `
            <li>
              <div class="episode-row">
                <div class="episode-copy">
                  <div class="history-title-main">${escapeHtml(`E${ep.episode_number ?? "?"} - ${ep.title}`)}</div>
                  <div class="history-badges">
                    ${ep.watched_by_user ? renderStatusChip("watched", "success") : renderStatusChip(watchedLabel, ep.watched_count ? "warning" : "neutral")}
                    ${ep.latest_watched_at ? renderStatusChip(`Last ${escapeHtml(new Date(ep.latest_watched_at).toLocaleDateString())}`, "info") : ""}
                  </div>
                </div>
                <div class="compact-actions">
                  <button class="secondary episode-detail-button" data-media-item-detail-id="${ep.media_item_id}" type="button">Open Media</button>
                  <button class="secondary library-inline-button" data-show-episode-history="${ep.media_item_id}" data-show-episode-label="${escapeHtml(`${detail.show.title} · ${ep.title}`)}" data-show-id="${detail.show.show_id}" type="button">Open History</button>
                </div>
              </div>
            </li>
          `;
        })
        .join("");
      seasonSection.className = "season-group";
      seasonSection.innerHTML = `
        <div class="season-heading">
          <button class="season-toggle" data-show-season-toggle="${seasonKey}" data-show-id="${detail.show.show_id}" type="button">
            <span>${expanded ? "Hide" : "Show"}</span>
            <span>${escapeHtml(heading)}</span>
          </button>
          <div class="season-heading-actions">
            ${renderStatusChip(`${watchedCount}/${seasonEpisodes.length} watched`, watchedCount === seasonEpisodes.length ? "success" : watchedCount ? "warning" : "neutral")}
            <button class="secondary library-inline-button" data-show-season-history="${escapeHtml(detail.show.title)}" data-show-season-label="${escapeHtml(`${detail.show.title} · ${heading}`)}" data-show-id="${detail.show.show_id}" type="button">Open History</button>
          </div>
        </div>
        <ul class="season-list ${expanded ? "" : "hidden"}">${listItems}</ul>
      `;
      episodeList.appendChild(seasonSection);
    }
    detailStatus.textContent = `Loaded ${detail.episodes.length} episode(s)`;
  } catch (_error) {
    detailStatus.textContent = "Failed to load show detail";
  }
}

function closeMediaPanel() {
  mediaPanel.classList.add("hidden");
  mediaPanelStatus.textContent = "Select a watch or episode to inspect richer media detail.";
  mediaPanelBody.innerHTML = "";
  mediaPanelOpenHistory.disabled = true;
  selectedMediaItemId = null;
  selectedMediaDetail = null;
}

function renderMediaRecentWatch(row) {
  const signals = [
    row.rating_value ? renderStatusChip(`${row.rating_value}/10`, "info") : "",
    row.rewatch ? renderStatusChip("rewatch", "warning") : "",
    row.is_horrorfest_watch ? renderStatusChip(`HF ${row.horrorfest_year}`, "danger") : "",
  ]
    .filter(Boolean)
    .join(" ");
  return `
    <li>
      <div class="history-title-cell">
        <div class="history-title-main">${escapeHtml(new Date(row.watched_at_local || row.watched_at).toLocaleString())}</div>
        <div class="history-meta-row">
          ${renderStatusChip(escapeHtml(row.playback_source), "info")}
          ${row.completed ? renderStatusChip("completed", "success") : renderStatusChip("partial", "warning")}
          ${signals}
        </div>
        <div class="muted">${escapeHtml(row.watch_version_name || formatRuntimeMinutes(row.effective_runtime_seconds))}</div>
      </div>
    </li>
  `;
}

async function openMediaDetail(mediaItemId) {
  if (!mediaItemId) {
    return;
  }
  selectedMediaItemId = mediaItemId;
  mediaPanel.classList.remove("hidden");
  mediaPanelTitle.textContent = "Loading media detail...";
  mediaPanelStatus.textContent = `Loading media item ${mediaItemId}...`;
  mediaPanelOpenHistory.disabled = true;
  mediaPanelBody.innerHTML = "";
  try {
    const response = await api(`/api/v1/media-items/${mediaItemId}`);
    if (!response.ok) {
      mediaPanelTitle.textContent = "Media detail unavailable";
      mediaPanelStatus.textContent = "Failed to load media detail.";
      return;
    }
    const detail = await response.json();
    selectedMediaDetail = detail;
    mediaPanelTitle.textContent = detail.title;
    mediaPanelStatus.textContent = `${detail.type} · ${detail.enrichment_status}`;
    mediaPanelOpenHistory.disabled = false;
    const poster = detail.poster_url
      ? `<img class="media-panel-poster" src="${escapeHtml(detail.poster_url)}" alt="${escapeHtml(detail.title)} poster" />`
      : '<div class="media-panel-poster-placeholder">No Poster</div>';
    const recentWatches = detail.recent_watches.length
      ? `<ul class="recent-watch-list">${detail.recent_watches.map((row) => renderMediaRecentWatch(row)).join("")}</ul>`
      : `<p class="muted">No watch history yet for this media item.</p>`;
    mediaPanelBody.innerHTML = `
      <section class="detail-section">
        <div class="media-panel-hero">
          ${poster}
          <div class="media-panel-copy">
            <div class="media-panel-header-copy">
              <div class="media-panel-title-line">
                <h4>${escapeHtml(detail.title)}</h4>
                ${renderStatusChip(escapeHtml(detail.type), "neutral")}
                ${detail.year ? renderStatusChip(String(detail.year), "info") : ""}
              </div>
              <div class="detail-subtitle">
                ${detail.release_date ? escapeHtml(new Date(detail.release_date).toLocaleDateString()) : "Release date unavailable"}
              </div>
            </div>
            <div class="meta-pill-grid">
              ${renderMetaPills([
                ["Runtime", formatRuntimeMinutes(detail.base_runtime_seconds)],
                ["Latest Rating", detail.latest_rating_value ? `${detail.latest_rating_value}/${detail.latest_rating_scale || 10}` : "-"],
                ["Watch Count", detail.watch_count],
                ["Completed", detail.completed_watch_count],
                ["Latest Watch", detail.latest_watch_at ? new Date(detail.latest_watch_at).toLocaleDateString() : "-"],
              ])}
            </div>
            ${
              detail.summary
                ? `<p class="media-panel-summary">${escapeHtml(detail.summary)}</p>`
                : '<p class="muted">No summary available yet.</p>'
            }
          </div>
        </div>
      </section>
      ${
        detail.show
          ? `<section class="detail-section">
              <h4>Show Linkage</h4>
              <div class="detail-grid">
                ${renderDetailItems([
                  ["Show", escapeHtml(detail.show.title)],
                  ["Show TMDB", escapeHtml(detail.show.tmdb_id)],
                  ["Season", escapeHtml(detail.season_number || "-")],
                  ["Episode", escapeHtml(detail.episode_number || "-")],
                ])}
              </div>
            </section>`
          : ""
      }
      <section class="detail-section">
        <h4>Metadata & IDs</h4>
        <div class="detail-grid compact-grid">
          ${renderDetailItems([
            ["Enrichment", renderStatusChip(escapeHtml(detail.enrichment_status), detail.enrichment_status === "enriched" ? "success" : detail.enrichment_status === "failed" ? "danger" : "warning")],
            ["Source", escapeHtml(detail.metadata_source || "-")],
            ["Updated", escapeHtml(detail.metadata_updated_at ? new Date(detail.metadata_updated_at).toLocaleString() : "-")],
            ["TMDB", escapeHtml(detail.tmdb_id || "-")],
            ["IMDB", escapeHtml(detail.imdb_id || "-")],
            ["TVDB", escapeHtml(detail.tvdb_id || "-")],
          ])}
        </div>
        ${detail.enrichment_error ? `<p class="muted">Latest enrichment issue: ${escapeHtml(detail.enrichment_error)}</p>` : ""}
      </section>
      <section class="detail-section">
        <h4>Recent Watches</h4>
        <p class="detail-subtitle">Recent watches stay visible here, but the media summary remains the primary view.</p>
        ${recentWatches}
      </section>
    `;
  } catch (_error) {
    mediaPanelTitle.textContent = "Media detail unavailable";
    mediaPanelStatus.textContent = "Failed to load media detail.";
  }
}

function formatImportSummary(summary) {
  return [
    `batch_id: ${summary.import_batch_id}`,
    `status: ${summary.status}`,
    `dry_run: ${summary.dry_run}`,
    `processed: ${summary.processed_count}`,
    `inserted: ${summary.inserted_count}`,
    `skipped: ${summary.skipped_count}`,
    `errors: ${summary.error_count}`,
    `rejected_before_import: ${summary.rejected_before_import}`,
    `media_items_created: ${summary.media_items_created}`,
    `shows_created: ${summary.shows_created}`,
    `cursor_before: ${JSON.stringify(summary.cursor_before)}`,
    `cursor_after: ${JSON.stringify(summary.cursor_after)}`,
  ].join("\n");
}

function formatCursor(cursor) {
  if (!cursor) {
    return "none";
  }
  return JSON.stringify(cursor);
}

function renderImportCursorInfo(summary) {
  importCursorBefore.textContent = `Cursor before: ${formatCursor(summary.cursor_before)}`;
  importCursorAfter.textContent = `Cursor after: ${formatCursor(summary.cursor_after)}`;
}

function renderLastLocalCursor() {
  const cursor = window.localStorage.getItem(IMPORT_PREF_KEYS.lastCursor);
  importLastCursor.textContent = `Last successful local cursor: ${cursor || "none"}`;
}

function clearImportErrorsUi() {
  importErrorsStatus.textContent = "";
  importErrorsList.innerHTML = "";
}

function formatImportBatchDetail(batch) {
  return [
    `import_batch_id: ${batch.import_batch_id}`,
    `source: ${batch.source}`,
    `source_detail: ${batch.source_detail || "n/a"}`,
    `status: ${batch.status}`,
    `started_at: ${batch.started_at}`,
    `finished_at: ${batch.finished_at || "n/a"}`,
    `watch_events_inserted: ${batch.watch_events_inserted}`,
    `media_items_inserted: ${batch.media_items_inserted}`,
    `media_versions_inserted: ${batch.media_versions_inserted}`,
    `tags_added: ${batch.tags_added}`,
    `errors_count: ${batch.errors_count}`,
    `notes: ${batch.notes || "n/a"}`,
    `parameters: ${JSON.stringify(batch.parameters || {})}`,
  ].join("\n");
}

function renderImportErrors(errors) {
  importErrorsList.innerHTML = "";
  if (!errors.length) {
    importErrorsStatus.textContent = "No import-batch errors were recorded.";
    return;
  }
  importErrorsStatus.textContent = `Showing ${errors.length} import-batch error(s):`;
  for (const error of errors) {
    const li = document.createElement("li");
    const ref = error.entity_ref ? ` [${error.entity_ref}]` : "";
    li.textContent = `${error.severity}${ref}: ${error.message}`;
    importErrorsList.appendChild(li);
  }
}

async function loadImportBatchErrors(importBatchId) {
  try {
    const response = await api(`/api/v1/import-batches/${importBatchId}/errors?limit=25`);
    if (!response.ok) {
      importErrorsStatus.textContent = "Failed to load import-batch errors.";
      importErrorsList.innerHTML = "";
      return;
    }
    const errors = await response.json();
    renderImportErrors(errors);
  } catch (_error) {
    importErrorsStatus.textContent = "Failed to load import-batch errors.";
    importErrorsList.innerHTML = "";
  }
}

async function loadImportBatchDetail(importBatchId) {
  importDetailStatus.textContent = `Loading detail for batch ${importBatchId}...`;
  try {
    const response = await api(`/api/v1/import-batches/${importBatchId}`);
    if (!response.ok) {
      importDetailStatus.textContent = `Failed to load detail for batch ${importBatchId}.`;
      importDetail.textContent = "";
      return;
    }
    const batch = await response.json();
    selectedImportBatchId = importBatchId;
    selectedImportBatchDetail = batch;
    syncSelectedImportHistoryRow();
    importDetailStatus.textContent = `Showing detail for batch ${importBatchId}`;
    importDetail.textContent = formatImportBatchDetail(batch);
  } catch (_error) {
    selectedImportBatchDetail = null;
    syncSelectedImportHistoryRow();
    importDetailStatus.textContent = `Failed to load detail for batch ${importBatchId}.`;
    importDetail.textContent = "";
  }
}

function syncSelectedImportHistoryRow() {
  const rows = importHistoryBody.querySelectorAll("tr[data-import-batch-id]");
  for (const row of rows) {
    const rowBatchId = row.getAttribute("data-import-batch-id");
    row.classList.toggle("selected", rowBatchId === selectedImportBatchId);
  }
  importDownloadErrors.disabled = selectedImportBatchId === null;
  importCopyDetail.disabled =
    selectedImportBatchId === null || selectedImportBatchDetail === null;
}

function renderImportHistoryRows() {
  importHistoryBody.innerHTML = "";
  importHistoryById.clear();

  const statusFilter = importHistoryStatusFilter.value;
  const filteredBatches = importHistoryRows.filter(
    (batch) => !statusFilter || batch.status === statusFilter
  );

  if (!filteredBatches.length) {
    importHistoryStatus.textContent = statusFilter
      ? `No import batches with status '${statusFilter}'.`
      : "No import batches found.";
    return;
  }

  importHistoryStatus.textContent = `Loaded ${filteredBatches.length} import batch(es).`;
  for (const batch of filteredBatches) {
    importHistoryById.set(batch.import_batch_id, batch);
    const tr = document.createElement("tr");
    const startedAt = new Date(batch.started_at).toLocaleString();
    const inserted = batch.watch_events_inserted ?? 0;
    const errors = batch.errors_count ?? 0;
    tr.innerHTML = `
      <td>${startedAt}</td>
      <td>${batch.status}</td>
      <td>${batch.source}</td>
      <td>${inserted}</td>
      <td>${errors}</td>
      <td class="row">
        <button class="secondary" data-import-batch-id="${batch.import_batch_id}" data-action="reuse-settings">Reuse Settings</button>
        <button class="secondary" data-import-batch-id="${batch.import_batch_id}" data-action="view-errors">View Errors</button>
      </td>
    `;
    tr.dataset.importBatchId = batch.import_batch_id;
    importHistoryBody.appendChild(tr);
  }
  syncSelectedImportHistoryRow();
}

async function loadImportHistory() {
  importHistoryStatus.textContent = "Loading import history...";
  importHistoryRows = [];
  selectedImportBatchId = null;
  selectedImportBatchDetail = null;
  importDownloadErrors.disabled = true;
  importCopyDetail.disabled = true;
  importHistoryBody.innerHTML = "";
  try {
    const response = await api("/api/v1/import-batches?limit=20");
    if (!response.ok) {
      importHistoryStatus.textContent = "Failed to load import history.";
      return;
    }

    importHistoryRows = await response.json();
    renderImportHistoryRows();
    const latestBatch = importHistoryRows[0];
    if (latestBatch) {
      await loadImportBatchDetail(latestBatch.import_batch_id);
    }
  } catch (_error) {
    importHistoryStatus.textContent = "Failed to load import history.";
  }
}

function applyImportSettingsFromBatch(batch) {
  const params = batch && typeof batch.parameters === "object" ? batch.parameters : {};
  const modeFromParams = params.mode;
  const modeFromSourceDetail = batch.source_detail;
  if (modeFromParams === "bootstrap" || modeFromParams === "incremental") {
    importMode.value = modeFromParams;
  } else if (modeFromSourceDetail === "bootstrap" || modeFromSourceDetail === "incremental") {
    importMode.value = modeFromSourceDetail;
  }
  if (typeof params.resume_from_latest === "boolean") {
    importResume.checked = params.resume_from_latest;
  } else {
    importResume.checked = false;
  }
  if (typeof params.dry_run === "boolean") {
    importDryRun.checked = params.dry_run;
  }
  saveImportPreferences();
}

function loadImportPreferences() {
  importUserId.value = window.localStorage.getItem(IMPORT_PREF_KEYS.userId) || "";

  const savedMode = window.localStorage.getItem(IMPORT_PREF_KEYS.mode);
  if (savedMode === "bootstrap" || savedMode === "incremental") {
    importMode.value = savedMode;
  }

  importDryRun.checked = window.localStorage.getItem(IMPORT_PREF_KEYS.dryRun) !== "false";
  importResume.checked = window.localStorage.getItem(IMPORT_PREF_KEYS.resume) === "true";
  const savedHistoryStatusFilter = window.localStorage.getItem(
    IMPORT_PREF_KEYS.importHistoryStatusFilter
  );
  if (
    savedHistoryStatusFilter === "" ||
    savedHistoryStatusFilter === "running" ||
    savedHistoryStatusFilter === "completed" ||
    savedHistoryStatusFilter === "completed_with_errors" ||
    savedHistoryStatusFilter === "failed"
  ) {
    importHistoryStatusFilter.value = savedHistoryStatusFilter;
  }
  renderLastLocalCursor();
}

function saveImportPreferences() {
  window.localStorage.setItem(IMPORT_PREF_KEYS.userId, importUserId.value.trim());
  window.localStorage.setItem(IMPORT_PREF_KEYS.mode, importMode.value);
  window.localStorage.setItem(IMPORT_PREF_KEYS.dryRun, String(importDryRun.checked));
  window.localStorage.setItem(IMPORT_PREF_KEYS.resume, String(importResume.checked));
}

function saveLastLocalCursor(cursor) {
  if (!cursor) {
    return;
  }
  window.localStorage.setItem(IMPORT_PREF_KEYS.lastCursor, JSON.stringify(cursor));
}

function isUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value
  );
}

function inferFileFormat(fileName) {
  const lowered = fileName.toLowerCase();
  if (lowered.endsWith(".json")) {
    return "json";
  }
  if (lowered.endsWith(".csv")) {
    return "csv";
  }
  return null;
}

function parseApiError(payload) {
  const detail = payload && typeof payload === "object" ? payload.detail : null;

  if (typeof detail === "string") {
    if (detail.includes("Uploaded file is empty")) {
      return "The selected file is empty.";
    }
    if (detail.includes("Could not detect upload format")) {
      return "Use a .json or .csv file, or rename the file to include the correct extension.";
    }
    if (detail.includes("No valid rows available for import")) {
      return "No valid rows were found after preprocessing.";
    }
    if (detail.includes("user_id is required")) {
      return "User UUID is required for legacy backup imports.";
    }
    if (detail.includes("exceeds max size")) {
      return detail;
    }
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (first && typeof first.msg === "string") {
      return `Request validation failed: ${first.msg}`;
    }
  }

  return "Import failed due to an unknown error.";
}

function formatManualWatchDetail(payload) {
  return [
    `watch_id: ${payload.watch_id}`,
    `media_item_id: ${payload.media_item_id}`,
    `watched_at: ${payload.watched_at}`,
    `playback_source: ${payload.playback_source}`,
    `completed: ${payload.completed}`,
    `rating_value: ${payload.rating_value || "n/a"}`,
    `rating_scale: ${payload.rating_scale || "n/a"}`,
    `origin_kind: ${payload.origin_kind}`,
    `horrorfest_year: ${payload.horrorfest_year || "n/a"}`,
    `horrorfest_watch_order: ${payload.horrorfest_watch_order || "n/a"}`,
  ].join("\n");
}

async function submitManualWatch(event) {
  event.preventDefault();
  saveManualWatchPreferences();
  manualWatchStatus.textContent = "Submitting manual watch...";
  manualWatchDetail.textContent = "";

  const payload = {
    user_id: manualWatchUserId.value.trim(),
    watched_at: new Date(manualWatchWatchedAt.value).toISOString(),
    playback_source: manualWatchPlaybackSource.value.trim(),
    media_type: manualWatchMediaType.value,
    completed: manualWatchCompleted.checked,
    rating_value: manualWatchRatingValue.value
      ? Number.parseInt(manualWatchRatingValue.value, 10)
      : null,
    created_by: manualWatchCreatedBy.value.trim() || null,
  };
  if (payload.media_type === "movie") {
    payload.tmdb_id = manualWatchTmdbId.value
      ? Number.parseInt(manualWatchTmdbId.value, 10)
      : null;
  } else {
    payload.show_tmdb_id = manualWatchShowTmdbId.value
      ? Number.parseInt(manualWatchShowTmdbId.value, 10)
      : null;
    payload.tmdb_episode_id = manualWatchTmdbEpisodeId.value
      ? Number.parseInt(manualWatchTmdbEpisodeId.value, 10)
      : null;
    payload.season_number = manualWatchSeasonNumber.value
      ? Number.parseInt(manualWatchSeasonNumber.value, 10)
      : null;
    payload.episode_number = manualWatchEpisodeNumber.value
      ? Number.parseInt(manualWatchEpisodeNumber.value, 10)
      : null;
  }

  const response = await api("/api/v1/watch-events/manual", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    manualWatchStatus.textContent =
      errorPayload?.detail || "Manual watch submission failed.";
    manualWatchDetail.textContent = errorPayload ? JSON.stringify(errorPayload, null, 2) : "";
    return;
  }

  const created = await response.json();
  manualWatchStatus.textContent = `Created manual watch ${created.watch_id}`;
  manualWatchDetail.textContent = formatManualWatchDetail(created);
  await loadDashboardData();
}

async function runImport(event) {
  event.preventDefault();
  const selectedFile = importFile.files && importFile.files[0];
  if (!selectedFile) {
    importStatus.textContent = "Choose a file before running import";
    return;
  }
  const trimmedUserId = importUserId.value.trim();
  if (!trimmedUserId) {
    importStatus.textContent = "User UUID is required for legacy backup imports";
    return;
  }
  if (!isUuid(trimmedUserId)) {
    importStatus.textContent = "User UUID format is invalid";
    return;
  }

  const inferredFormat = inferFileFormat(selectedFile.name);
  if (!inferredFormat) {
    importStatus.textContent = "Unsupported file type. Use a .json or .csv file.";
    return;
  }
  if (selectedFile.size > IMPORT_UPLOAD_MAX_BYTES) {
    importStatus.textContent = `File exceeds ${IMPORT_UPLOAD_MAX_MB} MB limit.`;
    return;
  }

  importStatus.textContent = "Running import...";
  importSummary.textContent = "";
  importCursorBefore.textContent = "Cursor before: pending";
  importCursorAfter.textContent = "Cursor after: pending";
  clearImportErrorsUi();
  importForm.querySelector("button[type='submit']").disabled = true;
  saveImportPreferences();

  const formData = new FormData();
  formData.append("input_file", selectedFile);
  formData.append("input_schema", "legacy_backup");
  formData.append("file_format", inferredFormat);
  formData.append("mode", importMode.value);
  formData.append("dry_run", String(importDryRun.checked));
  formData.append("resume_from_latest", String(importResume.checked));
  formData.append("user_id", trimmedUserId);

  try {
    const response = await fetch("/api/v1/imports/watch-events/legacy-source/upload", {
      method: "POST",
      credentials: "include",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      importStatus.textContent = parseApiError(payload);
      importCursorBefore.textContent = "Cursor before: unavailable";
      importCursorAfter.textContent = "Cursor after: unavailable";
      importSummary.textContent = JSON.stringify(payload, null, 2);
      return;
    }
    importStatus.textContent = `Import finished: inserted ${payload.inserted_count}, skipped ${payload.skipped_count}, errors ${payload.error_count}, rejected ${payload.rejected_before_import}`;
    importSummary.textContent = formatImportSummary(payload);
    renderImportCursorInfo(payload);
    saveLastLocalCursor(payload.cursor_after);
    renderLastLocalCursor();
    if (payload.error_count > 0 && payload.import_batch_id) {
      await loadImportBatchErrors(payload.import_batch_id);
    } else {
      clearImportErrorsUi();
    }
    await loadDashboardData();
  } catch (_error) {
    importStatus.textContent = "Import request failed. Check network and server logs.";
    importCursorBefore.textContent = "Cursor before: unavailable";
    importCursorAfter.textContent = "Cursor after: unavailable";
    clearImportErrorsUi();
  } finally {
    importForm.querySelector("button[type='submit']").disabled = false;
  }
}

function setHistoryPagination(rowsLoaded) {
  const page = Math.floor(historyOffset / historyLimit) + 1;
  historyPage.textContent = `Page ${page} · showing ${rowsLoaded} row(s) · offset ${historyOffset}`;
  historyPrev.disabled = historyOffset === 0;
  historyNext.disabled = rowsLoaded < historyLimit;
}

function syncSelectedRatingRow() {
  const rows = ratingsBody.querySelectorAll("tr[data-watch-id]");
  for (const row of rows) {
    row.classList.toggle("selected", row.dataset.watchId === selectedRatingWatchId);
  }
}

function formatRatingDetail(row) {
  return [
    `watch_id: ${row.watch_id}`,
    `display_title: ${row.display_title || row.media_item_title || row.media_item_id}`,
    `watched_at_utc: ${row.watched_at}`,
    `watched_at_local: ${row.watched_at_local || "n/a"}`,
    `playback_source: ${row.playback_source}`,
    `completed: ${row.completed}`,
    `rating_value: ${row.rating_value || "n/a"}`,
    `rating_scale: ${row.rating_scale || "n/a"}`,
  ].join("\n");
}

function populateRatingEditor(row) {
  selectedRatingWatchId = row.watch_id;
  syncSelectedRatingRow();
  ratingsDetailStatus.textContent = `Rating ${row.display_title || row.media_item_title || row.watch_id}`;
  ratingsDetail.textContent = formatRatingDetail(row);
  ratingsValue.value = "";
}

async function loadUnratedWatches() {
  ratingsStatus.textContent = "Loading unrated watches...";
  ratingsBody.innerHTML = "";
  ratingsRows = [];
  selectedRatingWatchId = null;
  try {
    const response = await api(`/api/v1/watch-events/unrated?limit=${ratingsLimit}`);
    if (!response.ok) {
      ratingsStatus.textContent = "Failed to load unrated watches";
      ratingsDetailStatus.textContent = "Select an unrated watch to rate it.";
      ratingsDetail.textContent = "";
      return;
    }
    const rows = await response.json();
    ratingsRows = rows;
    if (!rows.length) {
      ratingsStatus.textContent = "No unrated completed watches";
      ratingsDetailStatus.textContent = "Select an unrated watch to rate it.";
      ratingsDetail.textContent = "";
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      tr.dataset.watchId = row.watch_id;
      tr.innerHTML = `
        <td>${new Date(row.watched_at).toLocaleString()}</td>
        <td>${row.display_title || row.media_item_title || row.media_item_id}</td>
        <td>${row.playback_source}</td>
        <td>${renderStatusChip("awaiting rating", "warning")}</td>
      `;
      ratingsBody.appendChild(tr);
    }
    ratingsStatus.textContent = `Loaded ${rows.length} unrated watch(es)`;
    populateRatingEditor(rows[0]);
  } catch (_error) {
    ratingsStatus.textContent = "Failed to load unrated watches";
    ratingsDetailStatus.textContent = "Select an unrated watch to rate it.";
    ratingsDetail.textContent = "";
  }
}

async function saveWatchRating() {
  if (!selectedRatingWatchId) {
    ratingsDetailStatus.textContent = "Select an unrated watch first.";
    return;
  }
  if (!ratingsValue.value) {
    ratingsDetailStatus.textContent = "Choose a rating from 1 to 10.";
    return;
  }
  const response = await api(`/api/v1/watch-events/${selectedRatingWatchId}/rate`, {
    method: "POST",
    body: JSON.stringify({
      updated_by: ratingsUpdatedBy.value.trim(),
      update_reason: ratingsReason.value.trim() || null,
      rating_value: Number.parseInt(ratingsValue.value, 10),
    }),
  });
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    ratingsDetailStatus.textContent = errorPayload?.detail || "Failed to save rating.";
    return;
  }
  const updated = await response.json();
  ratingsDetailStatus.textContent = `Saved ${updated.rating_value}/10 for ${updated.media_item_id}`;
  await Promise.all([loadUnratedWatches(), loadHistory()]);
}

function syncSelectedHorrorfestRow() {
  const rows = horrorfestBody.querySelectorAll("tr[data-horrorfest-entry-id]");
  for (const row of rows) {
    row.classList.toggle(
      "selected",
      row.dataset.horrorfestEntryId === selectedHorrorfestEntryId
    );
  }
}

function formatHorrorfestDetail(row) {
  return [
    `horrorfest_entry_id: ${row.horrorfest_entry_id}`,
    `watch_id: ${row.watch_id}`,
    `horrorfest_year: ${row.horrorfest_year}`,
    `watch_order: ${row.watch_order ?? "n/a"}`,
    `source_kind: ${row.source_kind}`,
    `watched_at: ${row.watched_at}`,
    `title: ${row.display_title}`,
    `rating_value: ${row.rating_value ?? "n/a"}`,
    `effective_runtime_seconds: ${row.effective_runtime_seconds ?? "n/a"}`,
    `completed: ${row.completed}`,
    `rewatch: ${row.rewatch}`,
    `is_removed: ${row.is_removed}`,
    `removed_at: ${row.removed_at || "n/a"}`,
    `removed_by: ${row.removed_by || "n/a"}`,
    `removed_reason: ${row.removed_reason || "n/a"}`,
    `updated_at: ${row.updated_at || "n/a"}`,
    `updated_by: ${row.updated_by || "n/a"}`,
    `update_reason: ${row.update_reason || "n/a"}`,
  ].join("\n");
}

function renderHorrorfestYearMetrics(selectedYear, rows) {
  const activeRows = rows.filter((row) => !row.is_removed);
  const ratedRows = activeRows.filter((row) => row.rating_value !== null);
  const totalRuntimeSeconds = activeRows.reduce(
    (total, row) => total + Number(row.effective_runtime_seconds || 0),
    0
  );
  const averageRating =
    ratedRows.length > 0
      ? ratedRows.reduce((total, row) => total + Number(row.rating_value || 0), 0) / ratedRows.length
      : null;
  const firstWatch = activeRows[0]?.watched_at || null;
  const latestWatch = activeRows[activeRows.length - 1]?.watched_at || null;
  const cards = [
    ["Entries", activeRows.length],
    ["Runtime", formatRuntimeHours(totalRuntimeSeconds)],
    ["Avg Rating", averageRating ? formatDecimalValue(averageRating) : "-"],
    ["First Watch", firstWatch ? new Date(firstWatch).toLocaleDateString() : "-"],
    ["Latest Watch", latestWatch ? new Date(latestWatch).toLocaleDateString() : "-"],
  ];
  horrorfestYearMetrics.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="stats-card">
          <div class="stats-card-label">${escapeHtml(label)}</div>
          <div class="stats-card-value">${escapeHtml(value)}</div>
        </div>
      `
    )
    .join("");
  horrorfestYearSummary.textContent =
    `${selectedYear.horrorfest_year}: ${activeRows.length} active entr${activeRows.length === 1 ? "y" : "ies"} ` +
    `from ${new Date(selectedYear.window_start_at).toLocaleDateString()} to ` +
    `${new Date(selectedYear.window_end_at).toLocaleDateString()}.`;
}

function sortHorrorfestAnalyticsRows(rows) {
  const direction = horrorfestAnalyticsSortDirection === "asc" ? 1 : -1;
  const getSortableValue = (row) => {
    if (horrorfestAnalyticsSortKey === "year") {
      return row.horrorfest_year || 0;
    }
    if (horrorfestAnalyticsSortKey === "average_rating_value") {
      return Number(row.average_rating_value || 0);
    }
    return Number(row[horrorfestAnalyticsSortKey] || 0);
  };
  return [...rows].sort((left, right) => {
    const leftValue = getSortableValue(left);
    const rightValue = getSortableValue(right);
    if (leftValue === rightValue) {
      return right.horrorfest_year - left.horrorfest_year;
    }
    return leftValue > rightValue ? direction : -direction;
  });
}

function renderHorrorfestAnalyticsSummary(summary) {
  const cards = [
    ["Watches", summary.watch_count],
    ["Watch Days", summary.watch_days],
    ["New", summary.new_watch_count],
    ["Rewatch", summary.rewatch_count],
    ["Runtime", formatDecimalValue(summary.total_runtime_hours)],
    ["Avg/Day", formatDecimalValue(summary.average_watches_per_day)],
    ["Avg Hrs/Day", formatDecimalValue(summary.average_runtime_hours_per_day)],
    ["Avg Min/Watch", formatDecimalValue(summary.average_runtime_minutes_per_watch)],
    ["Avg Rating", summary.average_rating_value ? formatDecimalValue(summary.average_rating_value) : "-"],
    ["First Watch", summary.first_watch_at ? new Date(summary.first_watch_at).toLocaleDateString() : "-"],
    ["Latest Watch", summary.latest_watch_at ? new Date(summary.latest_watch_at).toLocaleDateString() : "-"],
  ];
  horrorfestAnalyticsSummaryCards.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="stats-card">
          <div class="stats-card-label">${escapeHtml(label)}</div>
          <div class="stats-card-value">${escapeHtml(value)}</div>
        </div>
      `
    )
    .join("");
}

function renderHorrorfestAnalyticsDetail(detail) {
  renderHorrorfestAnalyticsSummary(detail.summary);
  horrorfestAnalyticsDetailStatus.textContent = `Showing analytics for Horrorfest ${detail.summary.horrorfest_year}.`;

  horrorfestAnalyticsDailyBody.innerHTML = "";
  if (!detail.daily_rows.length) {
    horrorfestAnalyticsDailyBody.innerHTML = '<tr><td colspan="4">No daily analytics yet</td></tr>';
  } else {
    for (const row of detail.daily_rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${new Date(`${row.watch_date}T00:00:00`).toLocaleDateString()}</td>
        <td>${row.watch_count}</td>
        <td>${formatDecimalValue(row.total_runtime_hours)}</td>
        <td>${row.average_rating_value ? formatDecimalValue(row.average_rating_value) : "-"}</td>
      `;
      horrorfestAnalyticsDailyBody.appendChild(tr);
    }
  }

  horrorfestAnalyticsSourcesBody.innerHTML = "";
  if (!detail.source_rows.length) {
    horrorfestAnalyticsSourcesBody.innerHTML = '<tr><td colspan="4">No playback-source analytics yet</td></tr>';
  } else {
    for (const row of detail.source_rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${escapeHtml(row.playback_source)}</td>
        <td>${row.watch_count}</td>
        <td>${formatDecimalValue(row.total_runtime_hours)}</td>
        <td>${row.average_rating_value ? formatDecimalValue(row.average_rating_value) : "-"}</td>
      `;
      horrorfestAnalyticsSourcesBody.appendChild(tr);
    }
  }

  horrorfestAnalyticsRatingsBody.innerHTML = "";
  if (!detail.rating_rows.length) {
    horrorfestAnalyticsRatingsBody.innerHTML = '<tr><td colspan="2">No ratings recorded yet</td></tr>';
  } else {
    for (const row of detail.rating_rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${formatDecimalValue(row.rating_value)}</td>
        <td>${row.watch_count}</td>
      `;
      horrorfestAnalyticsRatingsBody.appendChild(tr);
    }
  }
}

function renderHorrorfestAnalyticsYears() {
  syncHorrorfestAnalyticsSortUi();
  horrorfestAnalyticsYearsBody.innerHTML = "";
  if (!horrorfestAnalyticsYears.length) {
    horrorfestAnalyticsYearsBody.innerHTML =
      '<tr><td colspan="11">No Horrorfest analytics available yet</td></tr>';
    return;
  }
  const rows = sortHorrorfestAnalyticsRows(horrorfestAnalyticsYears);
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.dataset.horrorfestAnalyticsYear = String(row.horrorfest_year);
    tr.classList.add("history-row-clickable");
    tr.classList.toggle("selected", row.horrorfest_year === selectedHorrorfestAnalyticsYear);
    tr.innerHTML = `
      <td>${row.horrorfest_year}</td>
      <td>${row.watch_count}</td>
      <td>${row.watch_days}</td>
      <td>${row.new_watch_count}</td>
      <td>${row.rewatch_count}</td>
      <td>${formatDecimalValue(row.total_runtime_hours)}</td>
      <td>${formatDecimalValue(row.average_watches_per_day)}</td>
      <td>${formatDecimalValue(row.average_runtime_hours_per_day)}</td>
      <td>${formatDecimalValue(row.average_runtime_minutes_per_watch)}</td>
      <td>${row.average_rating_value ? formatDecimalValue(row.average_rating_value) : "-"}</td>
      <td>
        <div class="compact-actions">
          <button class="secondary library-inline-button" data-horrorfest-analytics-inspect="${row.horrorfest_year}" type="button">Inspect Year</button>
          <button class="secondary library-inline-button" data-horrorfest-analytics-open-log="${row.horrorfest_year}" type="button">Open Log</button>
        </div>
      </td>
    `;
    horrorfestAnalyticsYearsBody.appendChild(tr);
  }
}

async function loadHorrorfestAnalyticsDetail(year) {
  horrorfestAnalyticsDetailStatus.textContent = `Loading analytics for Horrorfest ${year}...`;
  const response = await api(`/api/v1/horrorfest/analytics/years/${year}`);
  if (!response.ok) {
    horrorfestAnalyticsDetailStatus.textContent = `Failed to load analytics for Horrorfest ${year}.`;
    horrorfestAnalyticsSummaryCards.innerHTML = "";
    horrorfestAnalyticsDailyBody.innerHTML = "";
    horrorfestAnalyticsSourcesBody.innerHTML = "";
    horrorfestAnalyticsRatingsBody.innerHTML = "";
    return;
  }
  const detail = await response.json();
  selectedHorrorfestAnalyticsYear = detail.summary.horrorfest_year;
  if (horrorfestYears.find((row) => row.horrorfest_year === selectedHorrorfestAnalyticsYear)) {
    horrorfestYearSelect.value = String(selectedHorrorfestAnalyticsYear);
  }
  horrorfestAnalyticsOpenLog.disabled = false;
  renderHorrorfestAnalyticsYears();
  renderHorrorfestAnalyticsDetail(detail);
}

async function loadHorrorfestAnalytics(preferredYear = null) {
  horrorfestAnalyticsStatus.textContent = "Loading Horrorfest analytics...";
  horrorfestAnalyticsYearsBody.innerHTML = "";
  horrorfestAnalyticsSummaryCards.innerHTML = "";
  horrorfestAnalyticsDailyBody.innerHTML = "";
  horrorfestAnalyticsSourcesBody.innerHTML = "";
  horrorfestAnalyticsRatingsBody.innerHTML = "";
  horrorfestAnalyticsOpenLog.disabled = true;
  try {
    const response = await api("/api/v1/horrorfest/analytics/years");
    if (!response.ok) {
      horrorfestAnalyticsStatus.textContent = "Failed to load Horrorfest analytics";
      return;
    }
    horrorfestAnalyticsYears = await response.json();
    renderHorrorfestAnalyticsYears();
    if (!horrorfestAnalyticsYears.length) {
      selectedHorrorfestAnalyticsYear = null;
      horrorfestAnalyticsStatus.textContent = "No Horrorfest analytics available yet";
      horrorfestAnalyticsDetailStatus.textContent = "Select a Horrorfest year to inspect its analytics.";
      return;
    }
    const selectedYear =
      Number.parseInt(preferredYear || "", 10) ||
      selectedHorrorfestAnalyticsYear ||
      horrorfestYears.find((row) => row.is_active)?.horrorfest_year ||
      horrorfestAnalyticsYears[0].horrorfest_year;
    await loadHorrorfestAnalyticsDetail(selectedYear);
    horrorfestAnalyticsStatus.textContent = `Loaded analytics for ${horrorfestAnalyticsYears.length} Horrorfest year(s).`;
  } catch (_error) {
    horrorfestAnalyticsStatus.textContent = "Failed to load Horrorfest analytics";
  }
}

function populateHorrorfestYearConfig(yearRow) {
  if (!yearRow) {
    horrorfestConfigYear.value = "";
    horrorfestConfigLabel.value = "";
    horrorfestConfigStart.value = "";
    horrorfestConfigEnd.value = "";
    horrorfestConfigNotes.value = "";
    horrorfestConfigActive.checked = true;
    return;
  }
  horrorfestConfigYear.value = String(yearRow.horrorfest_year);
  horrorfestConfigLabel.value = yearRow.label || "";
  horrorfestConfigStart.value = toDateTimeLocalValue(yearRow.window_start_at);
  horrorfestConfigEnd.value = toDateTimeLocalValue(yearRow.window_end_at);
  horrorfestConfigNotes.value = yearRow.notes || "";
  horrorfestConfigActive.checked = yearRow.is_active;
}

function populateHorrorfestDetail(row) {
  selectedHorrorfestEntryId = row.horrorfest_entry_id;
  syncSelectedHorrorfestRow();
  horrorfestDetailStatus.textContent = `Selected Horrorfest watch ${row.display_title}`;
  horrorfestDetail.textContent = formatHorrorfestDetail(row);
  horrorfestTargetOrder.value = row.watch_order || "";
  horrorfestOpenMedia.disabled = !row.media_item_id;
}

async function loadHorrorfestYears(preferredYear = null) {
  const response = await api("/api/v1/horrorfest/years");
  if (!response.ok) {
    throw new Error("Failed to load Horrorfest years");
  }
  horrorfestYears = await response.json();
  const previousSelection = preferredYear || horrorfestYearSelect.value;
  horrorfestYearSelect.innerHTML = "";
  if (!horrorfestYears.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No years configured";
    horrorfestYearSelect.appendChild(option);
    populateHorrorfestYearConfig(null);
    return null;
  }
  for (const yearRow of horrorfestYears) {
    const option = document.createElement("option");
    option.value = String(yearRow.horrorfest_year);
    option.textContent = `${yearRow.horrorfest_year} (${yearRow.entry_count} watches)`;
    horrorfestYearSelect.appendChild(option);
  }
  const matchingSelection = horrorfestYears.find(
    (item) => String(item.horrorfest_year) === previousSelection
  );
  if (matchingSelection) {
    horrorfestYearSelect.value = previousSelection;
  } else if (!horrorfestYearSelect.value) {
    horrorfestYearSelect.value = String(horrorfestYears[0].horrorfest_year);
  }
  const selectedYear =
    horrorfestYears.find(
      (item) => String(item.horrorfest_year) === horrorfestYearSelect.value
    ) || horrorfestYears[0];
  horrorfestYearSelect.value = String(selectedYear.horrorfest_year);
  populateHorrorfestYearConfig(selectedYear);
  return selectedYear;
}

async function loadHorrorfest(preferredYear = null) {
  horrorfestStatus.textContent = "Loading Horrorfest years...";
  horrorfestYearSummary.textContent = "Select a year to inspect its ordered challenge log.";
  horrorfestYearMetrics.innerHTML = "";
  horrorfestBody.innerHTML = "";
  horrorfestRows = [];
  selectedHorrorfestEntryId = null;
  horrorfestOpenMedia.disabled = true;
  renderHorrorfestContextBanner();
  try {
    const selectedYear = await loadHorrorfestYears(preferredYear);
    if (!selectedYear) {
      horrorfestStatus.textContent = "No Horrorfest years configured yet";
      horrorfestYearSummary.textContent = "Configure a year to begin using Horrorfest.";
      horrorfestDetailStatus.textContent = "Configure a year to begin using Horrorfest.";
      horrorfestDetail.textContent = "";
      return;
    }
    const response = await api(
      `/api/v1/horrorfest/years/${selectedYear.horrorfest_year}/entries?include_removed=${horrorfestIncludeRemoved.checked}`
    );
    if (!response.ok) {
      horrorfestStatus.textContent = "Failed to load Horrorfest entries";
      return;
    }
    horrorfestRows = await response.json();
    if (!horrorfestRows.length) {
      horrorfestStatus.textContent = `Year ${selectedYear.horrorfest_year} is configured with no matching entries yet`;
      horrorfestYearSummary.textContent =
        `${selectedYear.horrorfest_year}: no active entries in the current filter.`;
      horrorfestDetailStatus.textContent = "Select a Horrorfest row to inspect or correct.";
      horrorfestDetail.textContent = "";
      return;
    }
    renderHorrorfestYearMetrics(selectedYear, horrorfestRows);
    selectedHorrorfestAnalyticsYear = selectedYear.horrorfest_year;
    for (const row of horrorfestRows) {
      const tr = document.createElement("tr");
      const signals = [
        row.rating_value ? renderStatusChip(`${row.rating_value}/10`, "info") : "",
        row.rewatch ? renderStatusChip("rewatch", "warning") : "",
      ]
        .filter(Boolean)
        .join(" ");
      tr.dataset.horrorfestEntryId = row.horrorfest_entry_id;
      tr.innerHTML = `
        <td>${row.watch_order ?? "-"}</td>
        <td>
          <div class="horrorfest-title-cell">
            <div class="horrorfest-row-main">
              ${
                row.media_item_id
                  ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(row.display_title)}</button>`
                  : `<div class="horrorfest-title-main">${escapeHtml(row.display_title)}</div>`
              }
            </div>
            <div class="muted">${escapeHtml(row.source_kind)}</div>
          </div>
        </td>
        <td>${new Date(row.watched_at).toLocaleString()}</td>
        <td><div class="horrorfest-signals">${signals || renderStatusChip("unrated", "neutral")}</div></td>
        <td>${formatRuntimeMinutes(row.effective_runtime_seconds)}</td>
        <td>${row.is_removed ? renderStatusChip("removed", "neutral") : renderStatusChip("active", "success")}</td>
      `;
      horrorfestBody.appendChild(tr);
    }
    horrorfestStatus.textContent = `Loaded ${horrorfestRows.length} Horrorfest row(s) for ${selectedYear.horrorfest_year}`;
    populateHorrorfestDetail(horrorfestRows[0]);
  } catch (_error) {
    horrorfestStatus.textContent = "Failed to load Horrorfest";
    horrorfestOpenMedia.disabled = true;
  }
}

async function loadHorrorfestWorkspace(preferredYear = null) {
  await loadHorrorfest(preferredYear);
  await loadHorrorfestAnalytics(preferredYear);
}

function selectedHorrorfestYear() {
  return Number.parseInt(horrorfestYearSelect.value, 10);
}

async function saveHorrorfestYear() {
  if (!horrorfestConfigYear.value || !horrorfestConfigStart.value || !horrorfestConfigEnd.value) {
    horrorfestStatus.textContent = "Year, window start, and window end are required.";
    return;
  }
  const yearValue = Number.parseInt(horrorfestConfigYear.value, 10);
  const response = await api(`/api/v1/horrorfest/years/${yearValue}`, {
    method: "PUT",
    body: JSON.stringify({
      window_start_at: new Date(horrorfestConfigStart.value).toISOString(),
      window_end_at: new Date(horrorfestConfigEnd.value).toISOString(),
      label: horrorfestConfigLabel.value.trim() || null,
      notes: horrorfestConfigNotes.value.trim() || null,
      is_active: horrorfestConfigActive.checked,
    }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    horrorfestStatus.textContent = payload?.detail || "Failed to save Horrorfest year.";
    return;
  }
  horrorfestStatus.textContent = `Saved Horrorfest year ${yearValue}.`;
  await loadHorrorfestWorkspace(String(yearValue));
  horrorfestYearSelect.value = String(yearValue);
}

async function mutateHorrorfestEntry(action, payload = null) {
  const selected = horrorfestRows.find(
    (item) => item.horrorfest_entry_id === selectedHorrorfestEntryId
  );
  if (!selected) {
    horrorfestDetailStatus.textContent = "Select a Horrorfest entry first.";
    return;
  }
  const response = await api(
    `/api/v1/horrorfest/entries/${selected.horrorfest_entry_id}/${action}`,
    {
      method: "POST",
      body: JSON.stringify(
        payload || {
          updated_by: horrorfestUpdatedBy.value.trim(),
          update_reason: horrorfestReason.value.trim() || null,
        }
      ),
    }
  );
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    horrorfestDetailStatus.textContent =
      errorPayload?.detail || `Failed to ${action} Horrorfest entry.`;
    return;
  }
  const updated = await response.json();
  horrorfestDetailStatus.textContent = `${action} completed for Horrorfest watch ${updated.watch_id}.`;
  await Promise.all([loadHorrorfestWorkspace(), loadHistory(), loadUnratedWatches()]);
}

async function includeWatchInHorrorfest() {
  const watchId = horrorfestIncludeWatchId.value.trim();
  if (!watchId) {
    horrorfestDetailStatus.textContent = "Enter a watch UUID to include in Horrorfest.";
    return;
  }
  const response = await api(`/api/v1/horrorfest/watch-events/${watchId}/include`, {
    method: "POST",
    body: JSON.stringify({
      horrorfest_year: selectedHorrorfestYear(),
      updated_by: horrorfestUpdatedBy.value.trim(),
      update_reason: horrorfestReason.value.trim() || null,
      target_order: horrorfestTargetOrder.value
        ? Number.parseInt(horrorfestTargetOrder.value, 10)
        : null,
    }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    horrorfestDetailStatus.textContent =
      payload?.detail || "Failed to include watch in Horrorfest.";
    return;
  }
  const updated = await response.json();
  horrorfestDetailStatus.textContent = `Included watch ${updated.watch_id} in Horrorfest ${updated.horrorfest_year}.`;
  await Promise.all([loadHorrorfestWorkspace(String(updated.horrorfest_year)), loadHistory()]);
}

function buildHistoryQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(historyLimit));
  params.set("offset", String(historyOffset));
  if (linkedHistoryContext?.mediaItemId) {
    params.set("media_item_id", linkedHistoryContext.mediaItemId);
  }
  if (historyQuery.value.trim()) {
    params.set("query", historyQuery.value.trim());
  }
  if (historyMediaType.value) {
    params.set("media_type", historyMediaType.value);
  }
  if (historyLocalDateFrom.value) {
    params.set("local_date_from", historyLocalDateFrom.value);
  }
  if (historyLocalDateTo.value) {
    params.set("local_date_to", historyLocalDateTo.value);
  }
  if (historyIncludeDeleted.checked) {
    params.set("include_deleted", "true");
  }
  return params.toString();
}

function buildHistoryEndpoint() {
  if (linkedHistoryContext?.type === "unrated_queue") {
    return `/api/v1/watch-events/unrated?${buildHistoryQuery()}`;
  }
  return `/api/v1/watch-events?${buildHistoryQuery()}`;
}

function syncHistorySortUi() {
  for (const button of historySortButtons) {
    const isActive = button.dataset.historySort === historySortKey;
    button.classList.toggle("active", isActive);
    if (isActive) {
      button.dataset.sortDirection = historySortDirection;
    } else {
      delete button.dataset.sortDirection;
    }
  }
}

function sortHistoryRows(rows) {
  const decorated = rows.map((row, index) => ({ row, index }));
  decorated.sort((left, right) => {
    let comparison = 0;
    if (historySortKey === "title") {
      const leftTitle = (left.row.display_title || left.row.media_item_title || "").toLowerCase();
      const rightTitle = (right.row.display_title || right.row.media_item_title || "").toLowerCase();
      comparison = leftTitle.localeCompare(rightTitle);
    } else if (historySortKey === "rating") {
      const leftRating = Number(left.row.rating_value || 0);
      const rightRating = Number(right.row.rating_value || 0);
      comparison = leftRating - rightRating;
    } else {
      comparison =
        new Date(left.row.watched_at).getTime() - new Date(right.row.watched_at).getTime();
    }

    if (comparison === 0) {
      comparison = left.index - right.index;
    }
    return historySortDirection === "asc" ? comparison : comparison * -1;
  });
  return decorated.map((item) => item.row);
}

function syncSelectedHistoryRow() {
  const rows = historyBody.querySelectorAll("tr[data-watch-id]");
  for (const row of rows) {
    row.classList.toggle("selected", row.dataset.watchId === selectedHistoryId);
  }
}

function toDateTimeLocalValue(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return offsetDate.toISOString().slice(0, 16);
}

function formatHistoryDetail(row) {
  const title = row.display_title || row.media_item_title || row.media_item_id;
  const signals = [
    row.rating_value ? renderStatusChip(`${row.rating_value}/10`, "info") : renderStatusChip("unrated", "neutral"),
    row.rewatch ? renderStatusChip("rewatch", "warning") : renderStatusChip("first watch", "success"),
    row.horrorfest_year ? renderStatusChip(`HF ${row.horrorfest_year} #${row.horrorfest_watch_order ?? "?"}`, "danger") : "",
    row.is_deleted ? renderStatusChip("deleted", "neutral") : "",
  ]
    .filter(Boolean)
    .join(" ");

  return `
    <section class="detail-section">
      <h4>${escapeHtml(title)}</h4>
      <div class="history-badges">${signals}</div>
      <div class="detail-grid">
        ${renderDetailItems([
          ["Watched (Local)", escapeHtml(row.watched_at_local ? new Date(row.watched_at_local).toLocaleString() : "n/a")],
          ["Watched (UTC)", escapeHtml(new Date(row.watched_at).toISOString())],
          ["Playback Source", renderStatusChip(escapeHtml(row.playback_source), "info")],
          ["Media Type", renderStatusChip(escapeHtml(row.media_item_type || "unknown"), "neutral")],
          ["Rating", escapeHtml(row.rating_value ? `${row.rating_value}/10` : "-")],
          ["Runtime", escapeHtml(formatRuntimeMinutes(row.effective_runtime_seconds))],
        ])}
      </div>
    </section>
    <section class="detail-section">
      <h4>Identifiers</h4>
      <div class="detail-grid">
        ${renderDetailItems([
          ["Watch ID", escapeHtml(row.watch_id)],
          ["Media Item ID", escapeHtml(row.media_item_id)],
          ["Timezone", escapeHtml(row.user_timezone || "n/a")],
          ["Source Event", escapeHtml(row.source_event_id || "n/a")],
        ])}
      </div>
    </section>
    <section class="detail-section">
      <h4>Correction State</h4>
      <div class="detail-grid">
        ${renderDetailItems([
          ["Completed", escapeHtml(row.completed ? "yes" : "no")],
          ["Deleted", escapeHtml(row.is_deleted ? "yes" : "no")],
          ["Version Override", escapeHtml(row.watch_version_name || "default")],
          ["Operator", escapeHtml(row.updated_by || "n/a")],
          ["Update Reason", escapeHtml(row.update_reason || "n/a")],
          ["Deleted Reason", escapeHtml(row.deleted_reason || "n/a")],
        ])}
      </div>
    </section>
  `;
}

function populateHistoryEditor(row) {
  selectedHistoryId = row.watch_id;
  syncSelectedHistoryRow();
  historyDetailStatus.textContent = `Selected ${row.display_title || row.media_item_title || row.watch_id}`;
  historyDetail.innerHTML = formatHistoryDetail(row);
  historyEditorWatchedAt.value = toDateTimeLocalValue(row.watched_at);
  historyEditorMediaItemId.value = row.media_item_id || "";
  historyEditorVersionName.value = row.watch_version_name || "";
  historyEditorRuntimeMinutes.value =
    row.watch_runtime_seconds ? String(Math.round(row.watch_runtime_seconds / 60)) : "";
  historyEditorCompleted.checked = Boolean(row.completed);
  historyEditorRewatch.checked = Boolean(row.rewatch);
  historyDelete.disabled = row.is_deleted;
  historyRestore.disabled = !row.is_deleted;
  historyOpenMedia.disabled = !row.media_item_id;
}

function renderHistoryRows() {
  historyBody.innerHTML = "";
  const rows = sortHistoryRows(historyRows);
  for (const row of rows) {
    const tr = document.createElement("tr");
    const watchedAt = new Date(row.watched_at).toLocaleString();
    const title = row.display_title || row.media_item_title || row.media_item_id;
    const badges = [
      row.horrorfest_year ? renderStatusChip(`HF ${row.horrorfest_year}`, "danger") : "",
      row.rewatch ? renderStatusChip("rewatch", "warning") : "",
      row.is_deleted ? renderStatusChip("deleted", "neutral") : "",
    ]
      .filter(Boolean)
      .join(" ");
    const statusBadges = [
      row.completed ? renderStatusChip("completed", "success") : renderStatusChip("partial", "warning"),
      renderStatusChip(row.playback_source, "info"),
    ].join(" ");
    tr.dataset.watchId = row.watch_id;
    tr.classList.add("history-row-clickable");
    tr.innerHTML = `
      <td>${watchedAt}</td>
      <td>
        <div class="history-title-cell">
          <div class="history-row-main">
            ${
              row.media_item_id
                ? `<button class="media-link-button" data-media-item-open="${row.media_item_id}" type="button">${escapeHtml(title)}</button>`
                : `<div class="history-title-main">${escapeHtml(title)}</div>`
            }
          </div>
          <div class="history-badges">${badges}</div>
        </div>
      </td>
      <td>${row.rating_value ? renderStatusChip(`${row.rating_value}/10`, "info") : renderStatusChip("unrated", "neutral")}</td>
      <td>${renderStatusChip(escapeHtml(row.media_item_type || "-"), "neutral")}</td>
      <td>${escapeHtml(row.playback_source)}</td>
      <td><div class="signal-stack">${statusBadges}</div></td>
    `;
    historyBody.appendChild(tr);
  }
  syncSelectedHistoryRow();
}

async function loadHistory() {
  historyStatus.textContent = "Loading history...";
  historyBody.innerHTML = "";
  historyRows = [];
  selectedHistoryId = null;
  historyOpenMedia.disabled = true;
  renderHistoryFilterSummary();
  try {
    const response = await api(buildHistoryEndpoint());
    if (!response.ok) {
      historyStatus.textContent = "Failed to load history";
      setHistoryPagination(0);
      historyDetailStatus.textContent = "Select a watch event to inspect or correct.";
      historyDetail.innerHTML = "";
      return;
    }
    const rows = await response.json();
    historyRows = rows;
    if (rows.length === 0) {
      historyStatus.textContent =
        linkedHistoryContext?.type === "unrated_queue"
          ? "No unrated watches matched the current queue view"
          : linkedHistoryContext
            ? "No watch events matched the linked browse context"
            : "No events for current filter/page";
      setHistoryPagination(0);
      historyDetailStatus.textContent =
        linkedHistoryContext?.type === "unrated_queue"
          ? "No unrated watches are currently waiting for ratings."
          : linkedHistoryContext
            ? "No watch events matched the linked browse context. Clear the link or return to Library."
            : "Select a watch event to inspect or correct.";
      historyDetail.innerHTML = "";
      return;
    }
    renderHistoryRows();
    historyStatus.textContent =
      linkedHistoryContext?.type === "unrated_queue"
        ? `Loaded ${rows.length} unrated watch(es) for the current page`
        : `Loaded ${rows.length} event(s) for the current page`;
    setHistoryPagination(rows.length);
    populateHistoryEditor(sortHistoryRows(rows)[0]);
  } catch (_error) {
    historyStatus.textContent = "Failed to load history";
    setHistoryPagination(0);
    historyDetailStatus.textContent = "Select a watch event to inspect or correct.";
    historyDetail.innerHTML = "";
    historyOpenMedia.disabled = true;
  }
}

async function correctHistoryWatch() {
  if (!selectedHistoryId) {
    historyDetailStatus.textContent = "Select a watch event before saving a correction.";
    return;
  }
  const payload = {
    updated_by: historyEditorUpdatedBy.value.trim(),
    update_reason: historyEditorReason.value.trim() || null,
    watched_at: historyEditorWatchedAt.value ? new Date(historyEditorWatchedAt.value).toISOString() : null,
    media_item_id: historyEditorMediaItemId.value.trim() || null,
    completed: historyEditorCompleted.checked,
    rewatch: historyEditorRewatch.checked,
  };
  const response = await api(`/api/v1/watch-events/${selectedHistoryId}/correct`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    historyDetailStatus.textContent = errorPayload?.detail || "Failed to save correction.";
    return;
  }
  const updated = await response.json();
  historyDetailStatus.textContent = `Saved correction for ${updated.display_title || updated.media_item_id || updated.watch_id}`;
  await loadHistory();
  const selectedRow = historyRows.find((item) => item.watch_id === updated.watch_id);
  if (selectedRow) {
    populateHistoryEditor(selectedRow);
  }
}

async function setHistoryDeletedState(action) {
  if (!selectedHistoryId) {
    historyDetailStatus.textContent = "Select a watch event first.";
    return;
  }
  const payload = {
    updated_by: historyEditorUpdatedBy.value.trim(),
    update_reason: historyEditorReason.value.trim() || null,
  };
  const response = await api(`/api/v1/watch-events/${selectedHistoryId}/${action}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    historyDetailStatus.textContent = errorPayload?.detail || `Failed to ${action} watch event.`;
    return;
  }
  await loadHistory();
}

async function saveHistoryVersion(clearOverride) {
  if (!selectedHistoryId) {
    historyDetailStatus.textContent = "Select a watch event first.";
    return;
  }
  const payload = {
    updated_by: historyEditorUpdatedBy.value.trim(),
    update_reason: historyEditorReason.value.trim() || null,
    version_name: clearOverride ? null : historyEditorVersionName.value.trim() || null,
    runtime_minutes:
      clearOverride || !historyEditorRuntimeMinutes.value
        ? null
        : Number.parseInt(historyEditorRuntimeMinutes.value, 10),
    clear_override: clearOverride,
  };
  const response = await api(`/api/v1/watch-events/${selectedHistoryId}/version`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    historyDetailStatus.textContent =
      errorPayload?.detail || "Failed to save version override.";
    return;
  }
  const updated = await response.json();
  historyDetailStatus.textContent = clearOverride
    ? `Cleared version override for ${updated.media_item_id}`
    : `Saved version override for ${updated.media_item_id}`;
  await loadHistory();
  const selectedRow = historyRows.find((item) => item.watch_id === updated.watch_id);
  if (selectedRow) {
    populateHistoryEditor(selectedRow);
  }
}

function setActivityPagination(rowsLoaded) {
  const page = Math.floor(activityOffset / activityLimit) + 1;
  activityPage.textContent = `Page ${page}`;
  activityPrev.disabled = activityOffset === 0;
  activityNext.disabled = rowsLoaded < activityLimit;
}

function buildActivityQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(activityLimit));
  params.set("offset", String(activityOffset));
  if (activitySource.value) {
    params.set("playback_source", activitySource.value);
  }
  if (activityStatus.value) {
    params.set("decision_status", activityStatus.value);
  }
  if (activityOnlyUnmatched.checked) {
    params.set("only_unmatched", "true");
  }
  if (activityOnlyWithWatch.checked) {
    params.set("only_with_watch", "true");
  }
  return params.toString();
}

function syncSelectedActivityRow() {
  const rows = activityBody.querySelectorAll("tr[data-playback-event-id]");
  for (const row of rows) {
    const playbackEventId = row.getAttribute("data-playback-event-id");
    row.classList.toggle("selected", playbackEventId === selectedActivityId);
  }
}

function formatActivityResult(row) {
  const label = row.result_label || row.decision_status || "unknown";
  const tone =
    row.decision_status === "watch_event_created"
      ? "success"
      : row.decision_status === "duplicate_watch_event_skipped"
        ? "warning"
        : row.decision_status === "recorded_only"
          ? "neutral"
          : "info";
  return renderStatusChip(label, tone);
}

function formatActivityTitle(row) {
  if (row.media_type === "episode" && row.season_number !== null && row.episode_number !== null) {
    return `${row.guessed_title} S${String(row.season_number).padStart(2, "0")}E${String(row.episode_number).padStart(2, "0")}`;
  }
  return row.guessed_title;
}

function formatActivityDetail(event) {
  return [
    `playback_event_id: ${event.playback_event_id}`,
    `occurred_at: ${event.occurred_at}`,
    `collector: ${event.collector}`,
    `playback_source: ${event.playback_source}`,
    `event_type: ${event.event_type}`,
    `title: ${event.title}`,
    `media_type: ${event.media_type}`,
    `tmdb_id: ${event.tmdb_id || "n/a"}`,
    `imdb_id: ${event.imdb_id || "n/a"}`,
    `tvdb_id: ${event.tvdb_id || "n/a"}`,
    `decision_status: ${event.decision_status || "n/a"}`,
    `decision_reason: ${event.decision_reason || "n/a"}`,
    `watch_id: ${event.watch_id || "n/a"}`,
    "",
    JSON.stringify(event.payload || {}, null, 2),
  ].join("\n");
}

function syncSelectedEnrichmentRow() {
  const rows = enrichmentBody.querySelectorAll("tr[data-media-item-id]");
  for (const row of rows) {
    const mediaItemId = row.getAttribute("data-media-item-id");
    row.classList.toggle("selected", mediaItemId === selectedEnrichmentId);
  }
}

function buildEnrichmentQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(enrichmentLimit));
  if (enrichmentStatusFilter.value) {
    params.set("enrichment_status", enrichmentStatusFilter.value);
  }
  if (enrichmentMissingIds.checked) {
    params.set("missing_ids_only", "true");
  }
  return params.toString();
}

function formatEnrichmentIds(row) {
  return [`tmdb:${row.tmdb_id || "-"}`, `tvdb:${row.tvdb_id || "-"}`, `imdb:${row.imdb_id || "-"}`].join(" ");
}

function formatEnrichmentStatus(row) {
  const tone =
    row.enrichment_status === "enriched"
      ? "success"
      : row.enrichment_status === "failed"
        ? "danger"
        : row.enrichment_status === "skipped"
          ? "neutral"
          : "warning";
  if (row.enrichment_status === "failed" && row.failure_code) {
    return renderStatusChip(`failed: ${row.failure_code}`, tone);
  }
  if (row.enrichment_status === "skipped" && row.failure_code) {
    return renderStatusChip(`skipped: ${row.failure_code}`, tone);
  }
  return renderStatusChip(row.enrichment_status, tone);
}

function formatEnrichmentMetadata(row) {
  const attemptedAt = row.enrichment_attempted_at
    ? new Date(row.enrichment_attempted_at).toLocaleString()
    : "not attempted";
  const updatedAt = row.metadata_updated_at
    ? new Date(row.metadata_updated_at).toLocaleString()
    : "not enriched";
  return `attempted: ${attemptedAt}\nupdated: ${updatedAt}`;
}

function formatEnrichmentDetail(row) {
  return [
    `media_item_id: ${row.media_item_id}`,
    `title: ${row.title}`,
    `type: ${row.type}`,
    `year: ${row.year || "n/a"}`,
    `tmdb_id: ${row.tmdb_id || "n/a"}`,
    `tvdb_id: ${row.tvdb_id || "n/a"}`,
    `imdb_id: ${row.imdb_id || "n/a"}`,
    `show_tmdb_id: ${row.show_tmdb_id || "n/a"}`,
    `season_number: ${row.season_number ?? "n/a"}`,
    `episode_number: ${row.episode_number ?? "n/a"}`,
    `enrichment_status: ${row.enrichment_status}`,
    `enrichment_error: ${row.enrichment_error || "n/a"}`,
    `failure_code: ${row.failure_code || "n/a"}`,
    `next_action: ${row.next_action || "n/a"}`,
    `last_lookup_kind: ${row.last_lookup_kind || "n/a"}`,
    `metadata_source: ${row.metadata_source || "n/a"}`,
    `enrichment_attempted_at: ${row.enrichment_attempted_at || "n/a"}`,
    `metadata_updated_at: ${row.metadata_updated_at || "n/a"}`,
    `base_runtime_seconds: ${row.base_runtime_seconds ?? "n/a"}`,
    "",
    row.summary || "No summary",
  ].join("\n");
}

async function loadMetadataEnrichment() {
  enrichmentStatusText.textContent = "Loading metadata enrichment queue...";
  enrichmentBody.innerHTML = "";
  selectedEnrichmentId = null;
  renderAdminContextBanner();
  try {
    const response = await api(`/api/v1/metadata-enrichment/items?${buildEnrichmentQuery()}`);
    if (!response.ok) {
      enrichmentStatusText.textContent = "Failed to load metadata enrichment queue";
      enrichmentDetailStatus.textContent = "Select a media item to inspect enrichment detail.";
      enrichmentDetail.textContent = "";
      return;
    }
    const rows = await response.json();
    if (rows.length === 0) {
      enrichmentStatusText.textContent = "No media items for current filter";
      enrichmentDetailStatus.textContent = "Select a media item to inspect enrichment detail.";
      enrichmentDetail.textContent = "";
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      tr.dataset.mediaItemId = row.media_item_id;
      tr.innerHTML = `
        <td>${row.title}</td>
        <td>${row.type}</td>
        <td>${formatEnrichmentIds(row)}</td>
        <td>${formatEnrichmentStatus(row)}</td>
        <td>${formatEnrichmentMetadata(row).replace("\n", "<br />")}</td>
        <td><button class="secondary" data-media-item-id="${row.media_item_id}" data-action="retry-enrichment">Retry</button></td>
      `;
      enrichmentBody.appendChild(tr);
    }
    enrichmentStatusText.textContent = `Loaded ${rows.length} media item(s)`;
    selectedEnrichmentId = rows[0].media_item_id;
    syncSelectedEnrichmentRow();
    enrichmentDetailStatus.textContent = `Showing enrichment detail for ${rows[0].title}`;
    enrichmentDetail.textContent = formatEnrichmentDetail(rows[0]);
  } catch (_error) {
    enrichmentStatusText.textContent = "Failed to load metadata enrichment queue";
    enrichmentDetailStatus.textContent = "Select a media item to inspect enrichment detail.";
    enrichmentDetail.textContent = "";
  }
}

async function retryMetadataEnrichment(mediaItemId) {
  enrichmentDetailStatus.textContent = `Retrying enrichment for ${mediaItemId}...`;
  const response = await api(`/api/v1/metadata-enrichment/items/${mediaItemId}/retry`, {
    method: "POST",
  });
  if (!response.ok) {
    enrichmentDetailStatus.textContent = `Failed to retry enrichment for ${mediaItemId}.`;
    return;
  }
  const payload = await response.json();
  selectedEnrichmentId = payload.media_item_id;
  await loadMetadataEnrichment();
}

async function processPendingMetadataEnrichment() {
  const batchLimit = Number.parseInt(enrichmentLimitSelect.value, 10);
  enrichmentLimit = batchLimit;
  enrichmentProcessPending.disabled = true;
  enrichmentApply.disabled = true;
  let totalProcessed = 0;
  let totalEnriched = 0;
  let totalFailed = 0;
  let totalSkipped = 0;
  let batchNumber = 0;

  try {
    while (true) {
      batchNumber += 1;
      enrichmentStatusText.textContent =
        `Processing metadata enrichment batch ${batchNumber} ` +
        `(chunk size ${batchLimit})...`;
      const response = await api(
        `/api/v1/metadata-enrichment/process-pending?limit=${batchLimit}`,
        { method: "POST" }
      );
      if (!response.ok) {
        enrichmentStatusText.textContent =
          `Failed during metadata enrichment batch ${batchNumber}`;
        return;
      }
      const payload = await response.json();
      totalProcessed += payload.processed_count || 0;
      totalEnriched += payload.enriched_count || 0;
      totalFailed += payload.failed_count || 0;
      totalSkipped += payload.skipped_count || 0;
      enrichmentStatusText.textContent =
        `Processed ${totalProcessed} pending item(s) so far ` +
        `(${totalEnriched} enriched, ${totalFailed} failed, ${totalSkipped} skipped). ` +
        `${payload.remaining_pending_count} pending remain.`;

      if ((payload.processed_count || 0) === 0 || (payload.remaining_pending_count || 0) === 0) {
        break;
      }
    }

    await loadMetadataEnrichment();
    enrichmentStatusText.textContent =
      `Finished processing pending metadata enrichment: ` +
      `${totalProcessed} processed, ${totalEnriched} enriched, ` +
      `${totalFailed} failed, ${totalSkipped} skipped.`;
  } finally {
    enrichmentProcessPending.disabled = false;
    enrichmentApply.disabled = false;
  }
}

async function loadScrobbleActivityDetail(playbackEventId) {
  activityDetailStatus.textContent = `Loading detail for ${playbackEventId}...`;
  try {
    const response = await api(`/api/v1/playback-events/${playbackEventId}`);
    if (!response.ok) {
      activityDetailStatus.textContent = `Failed to load detail for ${playbackEventId}.`;
      activityDetail.textContent = "";
      return;
    }
    const payload = await response.json();
    selectedActivityId = playbackEventId;
    syncSelectedActivityRow();
    activityDetailStatus.textContent = `Showing raw payload for ${playbackEventId}`;
    activityDetail.textContent = formatActivityDetail(payload);
  } catch (_error) {
    activityDetailStatus.textContent = `Failed to load detail for ${playbackEventId}.`;
    activityDetail.textContent = "";
  }
}

async function loadScrobbleActivity() {
  activityStatusText.textContent = "Loading scrobble activity...";
  activityBody.innerHTML = "";
  selectedActivityId = null;
  try {
    const response = await api(`/api/v1/scrobble-activity?${buildActivityQuery()}`);
    if (!response.ok) {
      activityStatusText.textContent = "Failed to load scrobble activity";
      setActivityPagination(0);
      return;
    }
    const rows = await response.json();
    if (rows.length === 0) {
      activityStatusText.textContent = "No scrobble activity for current filter/page";
      setActivityPagination(0);
      activityDetailStatus.textContent = "Select an activity row to inspect the raw payload.";
      activityDetail.textContent = "";
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      const occurredAt = new Date(row.occurred_at).toLocaleString();
      const matchedItem = row.matched_title || row.media_item_id || "-";
      tr.dataset.playbackEventId = row.playback_event_id;
      tr.innerHTML = `
        <td>${occurredAt}</td>
        <td>${row.username || row.user_id}</td>
        <td>${formatActivityTitle(row)}</td>
        <td>${row.playback_source}/${row.collector}</td>
        <td>${row.event_type}</td>
        <td>${matchedItem}</td>
        <td>${formatActivityResult(row)}</td>
      `;
      activityBody.appendChild(tr);
    }
    activityStatusText.textContent = `Loaded ${rows.length} activity row(s)`;
    setActivityPagination(rows.length);
    await loadScrobbleActivityDetail(rows[0].playback_event_id);
  } catch (_error) {
    activityStatusText.textContent = "Failed to load scrobble activity";
    setActivityPagination(0);
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.textContent = "";
  const password = document.getElementById("password").value;
  const response = await api("/api/v1/session/login", {
    method: "POST",
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    loginError.textContent = "Login failed";
    return;
  }
  await checkSession();
});

refreshData.addEventListener("click", async () => {
  await loadDashboardData();
});

historyApply.addEventListener("click", async () => {
  historyLimit = Number.parseInt(historyLimitSelect.value, 10);
  historyOffset = 0;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, historyQuery.value.trim());
  renderHistoryFilterSummary();
  await loadHistory();
});

historyQuery.addEventListener("change", () => {
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, historyQuery.value.trim());
  renderHistoryFilterSummary();
});

historyQuery.addEventListener("keydown", async (event) => {
  if (event.key !== "Enter") {
    return;
  }
  event.preventDefault();
  historyLimit = Number.parseInt(historyLimitSelect.value, 10);
  historyOffset = 0;
  window.localStorage.setItem(UI_PREF_KEYS.historyQuery, historyQuery.value.trim());
  renderHistoryFilterSummary();
  await loadHistory();
});

historyMediaType.addEventListener("change", async () => {
  historyOffset = 0;
  renderHistoryFilterSummary();
  await loadHistory();
});

historyLocalDateFrom.addEventListener("change", async () => {
  historyOffset = 0;
  renderHistoryFilterSummary();
  await loadHistory();
});

historyLocalDateTo.addEventListener("change", async () => {
  historyOffset = 0;
  renderHistoryFilterSummary();
  await loadHistory();
});

historyIncludeDeleted.addEventListener("change", async () => {
  historyOffset = 0;
  renderHistoryFilterSummary();
  await loadHistory();
});

for (const button of historyPresetButtons) {
  button.addEventListener("click", async () => {
    const preset = button.dataset.historyPreset;
    if (!preset) {
      return;
    }
    setHistoryDatePreset(preset);
    historyOffset = 0;
    window.localStorage.setItem(UI_PREF_KEYS.historyQuery, historyQuery.value.trim());
    renderHistoryFilterSummary();
    await loadHistory();
  });
}

historyPrev.addEventListener("click", async () => {
  historyOffset = Math.max(0, historyOffset - historyLimit);
  await loadHistory();
});

historyNext.addEventListener("click", async () => {
  historyOffset += historyLimit;
  await loadHistory();
});

historyBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const mediaButton = target.closest("button[data-media-item-open]");
  if (mediaButton instanceof HTMLButtonElement) {
    const mediaItemId = mediaButton.dataset.mediaItemOpen;
    if (mediaItemId) {
      await openMediaDetail(mediaItemId);
    }
    return;
  }
  const row = target.closest("tr[data-watch-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const selectedRow = historyRows.find((item) => item.watch_id === row.dataset.watchId);
  if (!selectedRow) {
    return;
  }
  populateHistoryEditor(selectedRow);
});

for (const button of historySortButtons) {
  button.addEventListener("click", () => {
    const sortKey = button.dataset.historySort;
    if (!sortKey) {
      return;
    }
    if (historySortKey === sortKey) {
      historySortDirection = historySortDirection === "asc" ? "desc" : "asc";
    } else {
      historySortKey = sortKey;
      historySortDirection = sortKey === "title" ? "asc" : "desc";
    }
    syncHistorySortUi();
    renderHistoryFilterSummary();
    if (historyRows.length) {
      renderHistoryRows();
      const selectedRow =
        historyRows.find((item) => item.watch_id === selectedHistoryId) ||
        sortHistoryRows(historyRows)[0];
      if (selectedRow) {
        populateHistoryEditor(selectedRow);
      }
    }
  });
}

ratingsApply.addEventListener("click", async () => {
  ratingsLimit = Number.parseInt(ratingsLimitSelect.value, 10);
  await loadUnratedWatches();
});

ratingsBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const row = target.closest("tr[data-watch-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const selectedRow = ratingsRows.find((item) => item.watch_id === row.dataset.watchId);
  if (!selectedRow) {
    return;
  }
  populateRatingEditor(selectedRow);
});

ratingsSave.addEventListener("click", async () => {
  await saveWatchRating();
});

horrorfestRefresh.addEventListener("click", async () => {
  await loadHorrorfestWorkspace();
});

horrorfestYearSelect.addEventListener("change", async () => {
  const selectedYearValue = horrorfestYearSelect.value;
  if (
    dashboardHorrorfestContext &&
    String(dashboardHorrorfestContext.year) !== selectedYearValue
  ) {
    clearHorrorfestContext();
  }
  const selected = horrorfestYears.find(
    (item) => String(item.horrorfest_year) === selectedYearValue
  );
  populateHorrorfestYearConfig(selected || null);
  selectedHorrorfestAnalyticsYear = Number.parseInt(selectedYearValue, 10);
  await loadHorrorfestWorkspace(selectedYearValue);
});

horrorfestIncludeRemoved.addEventListener("change", async () => {
  await loadHorrorfestWorkspace();
});

horrorfestBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const mediaButton = target.closest("button[data-media-item-open]");
  if (mediaButton instanceof HTMLButtonElement) {
    const mediaItemId = mediaButton.dataset.mediaItemOpen;
    if (mediaItemId) {
      await openMediaDetail(mediaItemId);
    }
    return;
  }
  const row = target.closest("tr[data-horrorfest-entry-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const selectedRow = horrorfestRows.find(
    (item) => item.horrorfest_entry_id === row.dataset.horrorfestEntryId
  );
  if (!selectedRow) {
    return;
  }
  populateHorrorfestDetail(selectedRow);
});

historyOpenMedia.addEventListener("click", async () => {
  const selectedRow = historyRows.find((item) => item.watch_id === selectedHistoryId);
  if (!selectedRow?.media_item_id) {
    historyDetailStatus.textContent = "Select a watch with a media item first.";
    return;
  }
  await openMediaDetail(selectedRow.media_item_id);
});

horrorfestOpenMedia.addEventListener("click", async () => {
  const selectedRow = horrorfestRows.find(
    (item) => item.horrorfest_entry_id === selectedHorrorfestEntryId
  );
  if (!selectedRow?.media_item_id) {
    horrorfestDetailStatus.textContent = "Select a Horrorfest watch with media detail first.";
    return;
  }
  await openMediaDetail(selectedRow.media_item_id);
});

for (const button of horrorfestModeButtons) {
  button.addEventListener("click", async () => {
    setHorrorfestMode(button.dataset.horrorfestMode || "log");
    if (horrorfestMode === "analytics") {
      await loadHorrorfestAnalytics(
        selectedHorrorfestAnalyticsYear ? String(selectedHorrorfestAnalyticsYear) : null
      );
    }
  });
}

for (const button of horrorfestAnalyticsSortButtons) {
  button.addEventListener("click", () => {
    const sortKey = button.dataset.horrorfestAnalyticsSort;
    if (!sortKey) {
      return;
    }
    if (horrorfestAnalyticsSortKey === sortKey) {
      horrorfestAnalyticsSortDirection =
        horrorfestAnalyticsSortDirection === "asc" ? "desc" : "asc";
    } else {
      horrorfestAnalyticsSortKey = sortKey;
      horrorfestAnalyticsSortDirection = sortKey === "year" ? "desc" : "desc";
    }
    renderHorrorfestAnalyticsYears();
  });
}

horrorfestAnalyticsRefresh.addEventListener("click", async () => {
  await loadHorrorfestAnalytics(
    selectedHorrorfestAnalyticsYear ? String(selectedHorrorfestAnalyticsYear) : null
  );
});

horrorfestAnalyticsOpenLog.addEventListener("click", async () => {
  if (!selectedHorrorfestAnalyticsYear) {
    horrorfestAnalyticsDetailStatus.textContent =
      "Select an analytics year before opening the log.";
    return;
  }
  horrorfestYearSelect.value = String(selectedHorrorfestAnalyticsYear);
  setHorrorfestMode("log");
  await loadHorrorfest(String(selectedHorrorfestAnalyticsYear));
});

horrorfestAnalyticsYearsBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const inspectButton = target.closest("button[data-horrorfest-analytics-inspect]");
  if (inspectButton instanceof HTMLButtonElement) {
    const year = Number.parseInt(
      inspectButton.dataset.horrorfestAnalyticsInspect || "",
      10
    );
    if (year) {
      await loadHorrorfestAnalyticsDetail(year);
    }
    return;
  }
  const openLogButton = target.closest("button[data-horrorfest-analytics-open-log]");
  if (openLogButton instanceof HTMLButtonElement) {
    const year = Number.parseInt(
      openLogButton.dataset.horrorfestAnalyticsOpenLog || "",
      10
    );
    if (year) {
      horrorfestYearSelect.value = String(year);
      setHorrorfestMode("log");
      await loadHorrorfest(String(year));
    }
    return;
  }
  const row = target.closest("tr[data-horrorfest-analytics-year]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const year = Number.parseInt(row.dataset.horrorfestAnalyticsYear || "", 10);
  if (year) {
    await loadHorrorfestAnalyticsDetail(year);
  }
});

mediaPanelClose.addEventListener("click", () => {
  closeMediaPanel();
});

episodeList.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const seasonToggle = target.closest("button[data-show-season-toggle]");
  if (seasonToggle instanceof HTMLButtonElement) {
    if (!selectedShowDetail) {
      return;
    }
    toggleSeasonExpanded(selectedShowDetail.show.show_id, seasonToggle.dataset.showSeasonToggle);
    await loadShowDetail(selectedShowDetail.show.show_id);
    return;
  }
  const seasonHistoryButton = target.closest("button[data-show-season-history]");
  if (seasonHistoryButton instanceof HTMLButtonElement) {
    const title = seasonHistoryButton.dataset.showSeasonHistory;
    const label = seasonHistoryButton.dataset.showSeasonLabel || title;
    const showId = seasonHistoryButton.dataset.showId || null;
    if (title) {
      await openHistoryForShow({
        title,
        label,
        sourceView: "shows",
        showId,
      });
    }
    return;
  }
  const episodeHistoryButton = target.closest("button[data-show-episode-history]");
  if (episodeHistoryButton instanceof HTMLButtonElement) {
    const mediaItemId = episodeHistoryButton.dataset.showEpisodeHistory;
    const label = episodeHistoryButton.dataset.showEpisodeLabel || "selected episode";
    const showId = episodeHistoryButton.dataset.showId || null;
    if (mediaItemId) {
      await openHistoryForMedia({
        mediaItemId,
        label,
        mediaType: "episode",
        sourceView: "shows",
        showId,
      });
    }
    return;
  }
  const button = target.closest("button[data-media-item-detail-id]");
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  const mediaItemId = button.dataset.mediaItemDetailId;
  if (!mediaItemId) {
    return;
  }
  await openMediaDetail(mediaItemId);
});

showList.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const openButton = target.closest("button[data-show-open]");
  if (openButton instanceof HTMLButtonElement) {
    const showId = openButton.dataset.showOpen;
    if (showId) {
      await loadShowDetail(showId);
    }
    return;
  }
  const historyButton = target.closest("button[data-show-history]");
  if (historyButton instanceof HTMLButtonElement) {
    const title = historyButton.dataset.showHistory;
    const showId = historyButton.dataset.showId || null;
    if (title) {
      await openHistoryForShow({
        title,
        sourceView: "shows",
        showId,
      });
    }
  }
});

dashboardHistoryBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const historyButton = target.closest("button[data-dashboard-history-open]");
  if (historyButton instanceof HTMLButtonElement) {
    const mediaItemId = historyButton.dataset.dashboardHistoryOpen;
    const label = historyButton.dataset.dashboardHistoryLabel || "selected media";
    const mediaType = historyButton.dataset.dashboardHistoryType || "";
    if (mediaItemId) {
      await openHistoryForMedia({
        mediaItemId,
        label,
        mediaType,
        sourceView: "dashboard",
      });
    }
    return;
  }
  const mediaButton = target.closest("button[data-media-item-open]");
  if (!(mediaButton instanceof HTMLButtonElement)) {
    return;
  }
  const mediaItemId = mediaButton.dataset.mediaItemOpen;
  if (!mediaItemId) {
    return;
  }
  await openMediaDetail(mediaItemId);
});

dashboardRatingsBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const unratedButton = target.closest("button[data-dashboard-unrated-open]");
  if (unratedButton instanceof HTMLButtonElement) {
    await openHistoryForUnratedQueue();
    return;
  }
  const mediaButton = target.closest("button[data-media-item-open]");
  if (!(mediaButton instanceof HTMLButtonElement)) {
    return;
  }
  const mediaItemId = mediaButton.dataset.mediaItemOpen;
  if (!mediaItemId) {
    return;
  }
  await openMediaDetail(mediaItemId);
});

dashboardEnrichmentBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-dashboard-enrichment-open]");
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  await openDashboardEnrichment(
    button.dataset.dashboardEnrichmentOpen || "",
    `${button.dataset.dashboardEnrichmentOpen || "selected"} enrichment`
  );
});

statsMonthlyBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-dashboard-month]");
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  const year = Number.parseInt(button.dataset.dashboardYear || "", 10);
  const month = Number.parseInt(button.dataset.dashboardMonth || "", 10);
  if (!Number.isFinite(year) || !Number.isFinite(month)) {
    return;
  }
  await openHistoryForMonth({ year, month });
});

statsHorrorfestBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-dashboard-horrorfest-year]");
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  const year = Number.parseInt(button.dataset.dashboardHorrorfestYear || "", 10);
  if (!Number.isFinite(year)) {
    return;
  }
  await openDashboardHorrorfestYear(year);
});

dashboardAttentionGrid.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-dashboard-action]");
  if (!(button instanceof HTMLButtonElement)) {
    return;
  }
  const action = button.dataset.dashboardAction;
  const year = Number.parseInt(button.dataset.dashboardYear || "", 10);
  if (action === "unrated") {
    await openHistoryForUnratedQueue();
  } else if (action === "enrichment-failed") {
    await openDashboardEnrichment("failed", "failed enrichment");
  } else if (action === "enrichment-pending") {
    await openDashboardEnrichment("pending", "pending enrichment");
  } else if (action === "horrorfest-current" && Number.isFinite(year)) {
    await openDashboardHorrorfestYear(year);
  } else if (action === "horrorfest-history" && Number.isFinite(year)) {
    const selectedYear = horrorfestYears.find((row) => row.horrorfest_year === year);
    if (selectedYear) {
      await openHistoryForHorrorfestYear(selectedYear);
    }
  } else if (action === "imports-errors") {
    setActiveView("admin");
    setActiveAdminView("imports");
    await loadImportHistory();
  }
});

horrorfestConfigSave.addEventListener("click", async () => {
  await saveHorrorfestYear();
});

horrorfestMove.addEventListener("click", async () => {
  if (!horrorfestTargetOrder.value) {
    horrorfestDetailStatus.textContent = "Enter a target order before moving.";
    return;
  }
  await mutateHorrorfestEntry("move", {
    updated_by: horrorfestUpdatedBy.value.trim(),
    update_reason: horrorfestReason.value.trim() || null,
    target_order: Number.parseInt(horrorfestTargetOrder.value, 10),
  });
});

horrorfestRemove.addEventListener("click", async () => {
  await mutateHorrorfestEntry("remove");
});

horrorfestRestore.addEventListener("click", async () => {
  await mutateHorrorfestEntry("restore");
});

horrorfestInclude.addEventListener("click", async () => {
  await includeWatchInHorrorfest();
});

historySave.addEventListener("click", async () => {
  await correctHistoryWatch();
});

historySaveVersion.addEventListener("click", async () => {
  await saveHistoryVersion(false);
});

historyClearVersion.addEventListener("click", async () => {
  await saveHistoryVersion(true);
});

historyDelete.addEventListener("click", async () => {
  await setHistoryDeletedState("delete");
});

historyRestore.addEventListener("click", async () => {
  await setHistoryDeletedState("restore");
});

activityApply.addEventListener("click", async () => {
  activityLimit = Number.parseInt(activityLimitSelect.value, 10);
  activityOffset = 0;
  await loadScrobbleActivity();
});

activitySource.addEventListener("change", async () => {
  activityOffset = 0;
  await loadScrobbleActivity();
});

activityStatus.addEventListener("change", async () => {
  activityOffset = 0;
  await loadScrobbleActivity();
});

activityOnlyUnmatched.addEventListener("change", async () => {
  activityOffset = 0;
  if (activityOnlyUnmatched.checked) {
    activityOnlyWithWatch.checked = false;
  }
  await loadScrobbleActivity();
});

activityOnlyWithWatch.addEventListener("change", async () => {
  activityOffset = 0;
  if (activityOnlyWithWatch.checked) {
    activityOnlyUnmatched.checked = false;
  }
  await loadScrobbleActivity();
});

activityPrev.addEventListener("click", async () => {
  activityOffset = Math.max(0, activityOffset - activityLimit);
  await loadScrobbleActivity();
});

activityNext.addEventListener("click", async () => {
  activityOffset += activityLimit;
  await loadScrobbleActivity();
});

activityBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const row = target.closest("tr[data-playback-event-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const playbackEventId = row.dataset.playbackEventId;
  if (!playbackEventId) {
    return;
  }
  await loadScrobbleActivityDetail(playbackEventId);
});

enrichmentApply.addEventListener("click", async () => {
  enrichmentLimit = Number.parseInt(enrichmentLimitSelect.value, 10);
  await loadMetadataEnrichment();
});

enrichmentStatusFilter.addEventListener("change", async () => {
  if (
    dashboardAdminContext?.adminView === "enrichment" &&
    enrichmentStatusFilter.value !== (dashboardAdminContext.enrichmentStatus || "")
  ) {
    clearAdminContext();
  }
  await loadMetadataEnrichment();
});

enrichmentMissingIds.addEventListener("change", async () => {
  await loadMetadataEnrichment();
});

enrichmentProcessPending.addEventListener("click", async () => {
  await processPendingMetadataEnrichment();
});

enrichmentBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-media-item-id]");
  if (button instanceof HTMLButtonElement) {
    const mediaItemId = button.dataset.mediaItemId;
    const action = button.dataset.action;
    if (mediaItemId && action === "retry-enrichment") {
      await retryMetadataEnrichment(mediaItemId);
    }
    return;
  }
  const row = target.closest("tr[data-media-item-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const mediaItemId = row.dataset.mediaItemId;
  if (!mediaItemId) {
    return;
  }
  selectedEnrichmentId = mediaItemId;
  syncSelectedEnrichmentRow();
  const cells = row.querySelectorAll("td");
  if (cells.length > 0) {
    enrichmentDetailStatus.textContent = `Showing enrichment detail for ${cells[0].textContent}`;
  }
  const response = await api(`/api/v1/metadata-enrichment/items?${buildEnrichmentQuery()}`);
  if (!response.ok) {
    enrichmentDetailStatus.textContent = `Failed to load enrichment detail for ${mediaItemId}.`;
    return;
  }
  const rows = await response.json();
  const selectedRow = rows.find((item) => item.media_item_id === mediaItemId);
  if (!selectedRow) {
    enrichmentDetailStatus.textContent = `Failed to load enrichment detail for ${mediaItemId}.`;
    return;
  }
  enrichmentDetail.textContent = formatEnrichmentDetail(selectedRow);
});

themeToggle.addEventListener("click", () => {
  toggleTheme();
});

dashboardUnratedOpen.addEventListener("click", async () => {
  await openHistoryForUnratedQueue();
});

dashboardEnrichmentOpen.addEventListener("click", async () => {
  await openDashboardEnrichment(
    dashboardEnrichmentPreviewStatus || "",
    `${dashboardEnrichmentPreviewStatus || "selected"} enrichment`
  );
});

adminContextReturn.addEventListener("click", async () => {
  setActiveView("dashboard");
  await loadDashboardData();
});

adminContextClear.addEventListener("click", async () => {
  clearAdminContext({ clearFilter: true });
  await loadMetadataEnrichment();
});

horrorfestContextReturn.addEventListener("click", async () => {
  setActiveView("dashboard");
  await loadDashboardData();
});

horrorfestContextClear.addEventListener("click", async () => {
  clearHorrorfestContext();
  await loadHorrorfestWorkspace();
});

for (const button of navButtons) {
  button.addEventListener("click", async () => {
    const targetView = button.dataset.viewTarget;
    setActiveView(targetView);
    if (targetView === "dashboard") {
      await loadDashboardData();
    } else if (targetView === "library") {
      await loadLibrary();
    } else if (targetView === "history") {
      await Promise.all([loadHistory(), loadUnratedWatches()]);
    } else if (targetView === "horrorfest") {
      await loadHorrorfestWorkspace(
        dashboardHorrorfestContext?.year ? String(dashboardHorrorfestContext.year) : null
      );
    } else if (targetView === "shows") {
      await loadShows();
    } else if (targetView === "admin") {
      const activeAdminView =
        window.localStorage.getItem(UI_PREF_KEYS.activeAdminView) || "imports";
      if (activeAdminView === "imports") {
        await loadImportHistory();
      } else if (activeAdminView === "scrobbler") {
        await loadScrobbleActivity();
      } else if (activeAdminView === "enrichment") {
        await loadMetadataEnrichment();
      }
    }
  });
}

for (const button of adminNavButtons) {
  button.addEventListener("click", async () => {
    const targetAdminView = button.dataset.adminViewTarget;
    setActiveAdminView(targetAdminView);
    if (targetAdminView === "imports") {
      await loadImportHistory();
    } else if (targetAdminView === "scrobbler") {
      await loadScrobbleActivity();
    } else if (targetAdminView === "enrichment") {
      await loadMetadataEnrichment();
    }
  });
}

for (const button of jumpButtons) {
  button.addEventListener("click", async () => {
    const targetView = button.dataset.jumpView;
    if (targetView) {
      setActiveView(targetView);
    }
    if (button.dataset.jumpAdmin) {
      setActiveAdminView(button.dataset.jumpAdmin);
    }
    if (targetView === "history") {
      await Promise.all([loadHistory(), loadUnratedWatches()]);
    } else if (targetView === "library") {
      await loadLibrary();
    } else if (targetView === "horrorfest") {
      await loadHorrorfestWorkspace(
        dashboardHorrorfestContext?.year ? String(dashboardHorrorfestContext.year) : null
      );
    } else if (targetView === "admin") {
      const targetAdminView = button.dataset.jumpAdmin || "imports";
      if (targetAdminView === "imports") {
        await loadImportHistory();
      } else if (targetAdminView === "scrobbler") {
        await loadScrobbleActivity();
      } else if (targetAdminView === "enrichment") {
        await loadMetadataEnrichment();
      }
    }
  });
}

importForm.addEventListener("submit", runImport);

manualWatchForm.addEventListener("submit", async (event) => {
  await submitManualWatch(event);
});

manualWatchMediaType.addEventListener("change", () => {
  toggleManualWatchInputs();
});

importUserId.addEventListener("change", () => {
  if (!manualWatchUserId.value.trim()) {
    manualWatchUserId.value = importUserId.value.trim();
  }
});

importUseLatestCursor.addEventListener("click", () => {
  importMode.value = "incremental";
  importResume.checked = true;
  saveImportPreferences();
  importStatus.textContent = "Configured incremental mode with resume_from_latest enabled.";
});

importHistoryStatusFilter.addEventListener("change", () => {
  window.localStorage.setItem(
    IMPORT_PREF_KEYS.importHistoryStatusFilter,
    importHistoryStatusFilter.value
  );
  selectedImportBatchId = null;
  selectedImportBatchDetail = null;
  importDetailStatus.textContent = "Select an import batch to view details.";
  importDetail.textContent = "";
  renderImportHistoryRows();
});

importHistoryClearFilter.addEventListener("click", () => {
  importHistoryStatusFilter.value = "";
  window.localStorage.setItem(IMPORT_PREF_KEYS.importHistoryStatusFilter, "");
  selectedImportBatchId = null;
  selectedImportBatchDetail = null;
  importDetailStatus.textContent = "Select an import batch to view details.";
  importDetail.textContent = "";
  renderImportHistoryRows();
});

importCopyDetail.addEventListener("click", async () => {
  if (!selectedImportBatchDetail) {
    importDetailStatus.textContent = "Select an import batch before copying detail.";
    return;
  }
  const payload = JSON.stringify(selectedImportBatchDetail, null, 2);
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(payload);
      importDetailStatus.textContent = `Copied detail for batch ${selectedImportBatchDetail.import_batch_id}.`;
      return;
    }
  } catch (_error) {
    // Fall through to execCommand fallback
  }

  try {
    const textarea = document.createElement("textarea");
    textarea.value = payload;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    importDetailStatus.textContent = `Copied detail for batch ${selectedImportBatchDetail.import_batch_id}.`;
  } catch (_error) {
    importDetailStatus.textContent = "Failed to copy detail to clipboard.";
  }
});

importDownloadErrors.addEventListener("click", async () => {
  if (!selectedImportBatchId) {
    importDetailStatus.textContent = "Select an import batch before downloading errors.";
    return;
  }
  importDetailStatus.textContent = `Preparing error export for batch ${selectedImportBatchId}...`;
  try {
    const response = await api(
      `/api/v1/import-batches/${selectedImportBatchId}/errors?limit=100`
    );
    if (!response.ok) {
      importDetailStatus.textContent = `Failed to export errors for batch ${selectedImportBatchId}.`;
      return;
    }
    const errors = await response.json();
    const payload = {
      export_generated_at: new Date().toISOString(),
      import_batch_id: selectedImportBatchId,
      error_count: errors.length,
      errors,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = `import-batch-${selectedImportBatchId}-errors.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(downloadUrl);
    importDetailStatus.textContent = `Downloaded ${errors.length} error(s) for batch ${selectedImportBatchId}.`;
  } catch (_error) {
    importDetailStatus.textContent = `Failed to export errors for batch ${selectedImportBatchId}.`;
  }
});

importHistoryBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const button = target.closest("button[data-import-batch-id]");
  if (button instanceof HTMLButtonElement) {
    const importBatchId = button.dataset.importBatchId;
    if (!importBatchId) {
      return;
    }
    const action = button.dataset.action;
    if (action === "view-errors") {
      importErrorsStatus.textContent = `Loading errors for batch ${importBatchId}...`;
      await loadImportBatchErrors(importBatchId);
      await loadImportBatchDetail(importBatchId);
      return;
    }
    if (action === "reuse-settings") {
      const batch = importHistoryById.get(importBatchId);
      if (!batch) {
        importStatus.textContent = "Could not load settings from selected batch.";
        return;
      }
      applyImportSettingsFromBatch(batch);
      importStatus.textContent = `Applied settings from batch ${importBatchId}.`;
      await loadImportBatchDetail(importBatchId);
      return;
    }
    return;
  }

  const row = target.closest("tr[data-import-batch-id]");
  if (!(row instanceof HTMLTableRowElement)) {
    return;
  }
  const rowBatchId = row.dataset.importBatchId;
  if (!rowBatchId) {
    return;
  }
  await loadImportBatchDetail(rowBatchId);
});

logoutBtn.addEventListener("click", async () => {
  await api("/api/v1/session/logout", { method: "DELETE" });
  detailCard.classList.add("hidden");
  await checkSession();
});

for (const button of libraryModeButtons) {
  button.addEventListener("click", async () => {
    const mode = button.dataset.libraryMode;
    if (!mode) {
      return;
    }
    setLibraryMode(mode);
    libraryOffset = 0;
    await loadLibrary();
  });
}

libraryApply.addEventListener("click", async () => {
  libraryLimit = Number.parseInt(libraryLimitSelect.value, 10);
  libraryOffset = 0;
  window.localStorage.setItem(UI_PREF_KEYS.libraryQuery, libraryQuery.value.trim());
  window.localStorage.setItem(UI_PREF_KEYS.libraryShowQuery, libraryShowQuery.value.trim());
  window.localStorage.setItem(UI_PREF_KEYS.libraryYear, libraryYear.value.trim());
  window.localStorage.setItem(
    UI_PREF_KEYS.libraryEnrichmentStatus,
    libraryEnrichmentStatus.value
  );
  window.localStorage.setItem(UI_PREF_KEYS.libraryWatched, libraryWatched.value);
  window.localStorage.setItem(UI_PREF_KEYS.libraryLimit, libraryLimitSelect.value);
  renderLibraryFilterSummary();
  await loadLibrary();
});

libraryPrev.addEventListener("click", async () => {
  libraryOffset = Math.max(0, libraryOffset - libraryLimit);
  await loadLibrary();
});

libraryNext.addEventListener("click", async () => {
  libraryOffset += libraryLimit;
  await loadLibrary();
});

libraryBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const mediaButton = target.closest("button[data-media-item-open]");
  if (mediaButton instanceof HTMLButtonElement) {
    const mediaItemId = mediaButton.dataset.mediaItemOpen;
    if (mediaItemId) {
      await openMediaDetail(mediaItemId);
    }
    return;
  }
  const historyButton = target.closest("button[data-library-history-open]");
  if (historyButton instanceof HTMLButtonElement) {
    const mediaItemId = historyButton.dataset.libraryHistoryOpen;
    const label = historyButton.dataset.libraryHistoryLabel || "selected media";
    const mediaType = historyButton.dataset.libraryHistoryType || "";
    if (mediaItemId) {
      await openHistoryForMedia({
        mediaItemId,
        label,
        mediaType,
        sourceView: "library",
      });
    }
    return;
  }
  const showHistoryButton = target.closest("button[data-library-show-history]");
  if (showHistoryButton instanceof HTMLButtonElement) {
    const title = showHistoryButton.dataset.libraryShowHistory;
    if (title) {
      await openHistoryForShow({
        title,
        sourceView: "library",
      });
    }
    return;
  }
  const showButton = target.closest("button[data-library-show-open]");
  if (showButton instanceof HTMLButtonElement) {
    const showId = showButton.dataset.libraryShowOpen;
    if (showId) {
      await openLibraryShow(showId);
    }
  }
});

historyContextReturn.addEventListener("click", async () => {
  await returnHistoryContextToSource();
});

historyContextClear.addEventListener("click", async () => {
  clearLinkedHistoryContext();
  await loadHistory();
});

mediaPanelOpenHistory.addEventListener("click", async () => {
  if (!selectedMediaItemId || !selectedMediaDetail) {
    return;
  }
  await openHistoryForMedia({
    mediaItemId: selectedMediaItemId,
    label: selectedMediaDetail.title,
    mediaType: selectedMediaDetail.type === "show" ? "" : selectedMediaDetail.type,
    sourceView: "media-panel",
    libraryModeValue: libraryMode,
  });
});

initializeUiShell();
checkSession();
