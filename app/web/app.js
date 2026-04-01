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
const progressStatus = document.getElementById("progress-status");
const progressBody = document.getElementById("progress-body");
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
const importHistoryStatusFilter = document.getElementById("import-history-status-filter");
const importHistoryClearFilter = document.getElementById("import-history-clear-filter");
const importHistoryStatus = document.getElementById("import-history-status");
const importHistoryBody = document.getElementById("import-history-body");
const importDetailStatus = document.getElementById("import-detail-status");
const importCopyDetail = document.getElementById("import-copy-detail");
const importDownloadErrors = document.getElementById("import-download-errors");
const importDetail = document.getElementById("import-detail");
const historyMediaType = document.getElementById("history-media-type");
const historyIncludeDeleted = document.getElementById("history-include-deleted");
const historyLimitSelect = document.getElementById("history-limit");
const historyApply = document.getElementById("history-apply");
const historyStatus = document.getElementById("history-status");
const historyBody = document.getElementById("history-body");
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
const refreshData = document.getElementById("refresh-data");
const logoutBtn = document.getElementById("logout-btn");
const detailTitle = document.getElementById("detail-title");
const detailProgress = document.getElementById("detail-progress");
const detailStatus = document.getElementById("detail-status");
const episodeList = document.getElementById("episode-list");

const IMPORT_PREF_KEYS = {
  userId: "klug.import_user_id",
  mode: "klug.import_mode",
  dryRun: "klug.import_dry_run",
  resume: "klug.import_resume",
  lastCursor: "klug.import_last_cursor",
  importHistoryStatusFilter: "klug.import_history_status_filter",
};
const IMPORT_UPLOAD_MAX_MB = 25;
const IMPORT_UPLOAD_MAX_BYTES = IMPORT_UPLOAD_MAX_MB * 1024 * 1024;

let historyOffset = 0;
let historyLimit = Number.parseInt(historyLimitSelect.value, 10);
let historyRows = [];
let selectedHistoryId = null;
let ratingsLimit = Number.parseInt(ratingsLimitSelect.value, 10);
let ratingsRows = [];
let selectedRatingWatchId = null;
let activityOffset = 0;
let activityLimit = Number.parseInt(activityLimitSelect.value, 10);
let selectedActivityId = null;
let enrichmentLimit = Number.parseInt(enrichmentLimitSelect.value, 10);
let selectedEnrichmentId = null;
const importHistoryById = new Map();
let importHistoryRows = [];
let selectedImportBatchId = null;
let selectedImportBatchDetail = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  return response;
}

function setAuthenticatedUI(authenticated, message) {
  authStatus.textContent = message;
  loginCard.classList.toggle("hidden", authenticated);
  appCard.classList.toggle("hidden", !authenticated);
  opsSession.textContent = `Session: ${authenticated ? "authenticated" : "not authenticated"}`;
  if (authenticated) {
    loadImportPreferences();
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
  await Promise.all([
    loadShows(),
    loadProgress(),
    loadHistory(),
    loadUnratedWatches(),
    loadImportHistory(),
    loadScrobbleActivity(),
    loadMetadataEnrichment(),
  ]);
  setLastRefreshNow();
}

async function loadShows() {
  showsStatus.textContent = "Loading shows...";
  showList.innerHTML = "";
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
      const button = document.createElement("button");
      button.className = "secondary";
      button.textContent = `${show.title} (${show.year || "n/a"})`;
      button.onclick = () => loadShowDetail(show.show_id);
      li.appendChild(button);
      showList.appendChild(li);
    }
  } catch (_error) {
    showsStatus.textContent = "Failed to load shows";
  }
}

async function loadProgress() {
  progressStatus.textContent = "Loading progress...";
  progressBody.innerHTML = "";
  try {
    const response = await api("/api/v1/shows/progress");
    if (!response.ok) {
      progressStatus.textContent = "Failed to load progress";
      return;
    }
    const rows = await response.json();
    if (rows.length === 0) {
      progressStatus.textContent = "No watched progress yet";
      return;
    }
    progressStatus.textContent = `Loaded ${rows.length} progress row(s)`;
    for (const row of rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.show_title}</td>
        <td>${row.watched_episodes}</td>
        <td>${row.total_episodes}</td>
        <td>${row.watched_percent}%</td>
      `;
      progressBody.appendChild(tr);
    }
  } catch (_error) {
    progressStatus.textContent = "Failed to load progress";
  }
}

async function loadShowDetail(showId) {
  detailStatus.textContent = "Loading detail...";
  detailCard.classList.remove("hidden");
  episodeList.innerHTML = "";
  try {
    const response = await api(`/api/v1/shows/${showId}`);
    if (!response.ok) {
      detailStatus.textContent = "Failed to load show detail";
      return;
    }
    const detail = await response.json();
    detailTitle.textContent = detail.show.title;
    const progress = detail.progress[0];
    detailProgress.textContent = progress
      ? `Progress: ${progress.watched_episodes}/${progress.total_episodes} (${progress.watched_percent}%)`
      : "Progress: no watched data yet";

    for (const ep of detail.episodes) {
      const li = document.createElement("li");
      const watchedLabel =
        ep.watched_by_user === null
          ? `watches: ${ep.watched_count}`
          : ep.watched_by_user
            ? "watched"
            : "not watched";
      li.textContent = `S${ep.season_number ?? "?"}E${ep.episode_number ?? "?"} - ${ep.title} (${watchedLabel})`;
      episodeList.appendChild(li);
    }
    detailStatus.textContent = `Loaded ${detail.episodes.length} episode(s)`;
  } catch (_error) {
    detailStatus.textContent = "Failed to load show detail";
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
  historyPage.textContent = `Page ${page}`;
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
        <td>Awaiting rating</td>
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

function buildHistoryQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(historyLimit));
  params.set("offset", String(historyOffset));
  if (historyMediaType.value) {
    params.set("media_type", historyMediaType.value);
  }
  if (historyIncludeDeleted.checked) {
    params.set("include_deleted", "true");
  }
  return params.toString();
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
  return [
    `watch_id: ${row.watch_id}`,
    `display_title: ${row.display_title || row.media_item_title || row.media_item_id}`,
    `watched_at_utc: ${row.watched_at}`,
    `watched_at_local: ${row.watched_at_local || "n/a"}`,
    `user_timezone: ${row.user_timezone || "n/a"}`,
    `media_item_id: ${row.media_item_id}`,
    `media_item_type: ${row.media_item_type || "n/a"}`,
    `playback_source: ${row.playback_source}`,
    `watch_version_name: ${row.watch_version_name || "n/a"}`,
    `watch_runtime_seconds: ${row.watch_runtime_seconds ?? "n/a"}`,
    `effective_runtime_seconds: ${row.effective_runtime_seconds ?? "n/a"}`,
    `completed: ${row.completed}`,
    `rewatch: ${row.rewatch}`,
    `is_deleted: ${row.is_deleted}`,
    `updated_at: ${row.updated_at || "n/a"}`,
    `updated_by: ${row.updated_by || "n/a"}`,
    `update_reason: ${row.update_reason || "n/a"}`,
    `deleted_at: ${row.deleted_at || "n/a"}`,
    `deleted_by: ${row.deleted_by || "n/a"}`,
    `deleted_reason: ${row.deleted_reason || "n/a"}`,
  ].join("\n");
}

function populateHistoryEditor(row) {
  selectedHistoryId = row.watch_id;
  syncSelectedHistoryRow();
  historyDetailStatus.textContent = `Showing correction detail for ${row.display_title || row.media_item_title || row.watch_id}`;
  historyDetail.textContent = formatHistoryDetail(row);
  historyEditorWatchedAt.value = toDateTimeLocalValue(row.watched_at);
  historyEditorMediaItemId.value = row.media_item_id || "";
  historyEditorVersionName.value = row.watch_version_name || "";
  historyEditorRuntimeMinutes.value =
    row.watch_runtime_seconds ? String(Math.round(row.watch_runtime_seconds / 60)) : "";
  historyEditorCompleted.checked = Boolean(row.completed);
  historyEditorRewatch.checked = Boolean(row.rewatch);
  historyDelete.disabled = row.is_deleted;
  historyRestore.disabled = !row.is_deleted;
}

async function loadHistory() {
  historyStatus.textContent = "Loading history...";
  historyBody.innerHTML = "";
  historyRows = [];
  selectedHistoryId = null;
  try {
    const response = await api(`/api/v1/watch-events?${buildHistoryQuery()}`);
    if (!response.ok) {
      historyStatus.textContent = "Failed to load history";
      setHistoryPagination(0);
      historyDetailStatus.textContent = "Select a watch event to inspect or correct.";
      historyDetail.textContent = "";
      return;
    }
    const rows = await response.json();
    historyRows = rows;
    if (rows.length === 0) {
      historyStatus.textContent = "No events for current filter/page";
      setHistoryPagination(0);
      historyDetailStatus.textContent = "Select a watch event to inspect or correct.";
      historyDetail.textContent = "";
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      const watchedAt = new Date(row.watched_at).toLocaleString();
      const completed = row.completed ? "yes" : "no";
      const progress = row.progress_percent === null ? "-" : `${row.progress_percent}%`;
      const title = row.display_title || row.media_item_title || row.media_item_id;
      const type = row.media_item_type || "-";
      const deletedBadge = row.is_deleted ? " [deleted]" : "";
      tr.dataset.watchId = row.watch_id;
      tr.innerHTML = `
        <td>${watchedAt}</td>
        <td>${title}${deletedBadge}</td>
        <td>${type}</td>
        <td>${row.playback_source}</td>
        <td>${completed}</td>
        <td>${progress}</td>
      `;
      historyBody.appendChild(tr);
    }
    historyStatus.textContent = `Loaded ${rows.length} event(s)`;
    setHistoryPagination(rows.length);
    populateHistoryEditor(rows[0]);
  } catch (_error) {
    historyStatus.textContent = "Failed to load history";
    setHistoryPagination(0);
    historyDetailStatus.textContent = "Select a watch event to inspect or correct.";
    historyDetail.textContent = "";
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
  if (row.result_label) {
    return row.result_label;
  }
  return row.decision_status || "unknown";
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
  if (row.enrichment_status === "failed" && row.failure_code) {
    return `failed (${row.failure_code})`;
  }
  if (row.enrichment_status === "skipped" && row.failure_code) {
    return `skipped (${row.failure_code})`;
  }
  return row.enrichment_status;
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
  enrichmentStatusText.textContent = "Processing pending metadata enrichment...";
  const response = await api(
    `/api/v1/metadata-enrichment/process-pending?limit=${enrichmentLimit}`,
    { method: "POST" }
  );
  if (!response.ok) {
    enrichmentStatusText.textContent = "Failed to process pending metadata enrichment";
    return;
  }
  const payload = await response.json();
  enrichmentStatusText.textContent = `Processed ${payload.processed_count} pending media item(s)`;
  await loadMetadataEnrichment();
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
  await loadHistory();
});

historyMediaType.addEventListener("change", async () => {
  historyOffset = 0;
  await loadHistory();
});

historyIncludeDeleted.addEventListener("change", async () => {
  historyOffset = 0;
  await loadHistory();
});

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

importForm.addEventListener("submit", runImport);

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

checkSession();
