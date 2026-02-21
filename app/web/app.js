const authStatus = document.getElementById("auth-status");
const loginCard = document.getElementById("login-card");
const appCard = document.getElementById("app-card");
const detailCard = document.getElementById("detail-card");
const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
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
const importStatus = document.getElementById("import-status");
const importSummary = document.getElementById("import-summary");
const importErrorsStatus = document.getElementById("import-errors-status");
const importErrorsList = document.getElementById("import-errors-list");
const historyMediaType = document.getElementById("history-media-type");
const historyLimitSelect = document.getElementById("history-limit");
const historyApply = document.getElementById("history-apply");
const historyStatus = document.getElementById("history-status");
const historyBody = document.getElementById("history-body");
const historyPrev = document.getElementById("history-prev");
const historyNext = document.getElementById("history-next");
const historyPage = document.getElementById("history-page");
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
};

let historyOffset = 0;
let historyLimit = Number.parseInt(historyLimitSelect.value, 10);

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
  if (authenticated) {
    loadImportPreferences();
  }
}

async function checkSession() {
  authStatus.textContent = "Checking session...";
  try {
    const response = await api("/api/v1/session/me");
    if (!response.ok) {
      setAuthenticatedUI(false, "Session check failed");
      return;
    }
    const payload = await response.json();
    if (payload.authenticated) {
      setAuthenticatedUI(true, "Authenticated");
      await loadDashboardData();
    } else {
      setAuthenticatedUI(false, "Not authenticated");
    }
  } catch (_error) {
    setAuthenticatedUI(false, "Session check failed");
  }
}

async function loadDashboardData() {
  await Promise.all([loadShows(), loadProgress(), loadHistory()]);
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

function clearImportErrorsUi() {
  importErrorsStatus.textContent = "";
  importErrorsList.innerHTML = "";
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

function loadImportPreferences() {
  importUserId.value = window.localStorage.getItem(IMPORT_PREF_KEYS.userId) || "";

  const savedMode = window.localStorage.getItem(IMPORT_PREF_KEYS.mode);
  if (savedMode === "bootstrap" || savedMode === "incremental") {
    importMode.value = savedMode;
  }

  importDryRun.checked = window.localStorage.getItem(IMPORT_PREF_KEYS.dryRun) !== "false";
  importResume.checked = window.localStorage.getItem(IMPORT_PREF_KEYS.resume) === "true";
}

function saveImportPreferences() {
  window.localStorage.setItem(IMPORT_PREF_KEYS.userId, importUserId.value.trim());
  window.localStorage.setItem(IMPORT_PREF_KEYS.mode, importMode.value);
  window.localStorage.setItem(IMPORT_PREF_KEYS.dryRun, String(importDryRun.checked));
  window.localStorage.setItem(IMPORT_PREF_KEYS.resume, String(importResume.checked));
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

  importStatus.textContent = "Running import...";
  importSummary.textContent = "";
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
      importSummary.textContent = JSON.stringify(payload, null, 2);
      return;
    }
    importStatus.textContent = `Import finished: inserted ${payload.inserted_count}, skipped ${payload.skipped_count}, errors ${payload.error_count}, rejected ${payload.rejected_before_import}`;
    importSummary.textContent = formatImportSummary(payload);
    if (payload.error_count > 0 && payload.import_batch_id) {
      await loadImportBatchErrors(payload.import_batch_id);
    } else {
      clearImportErrorsUi();
    }
    await loadDashboardData();
  } catch (_error) {
    importStatus.textContent = "Import request failed. Check network and server logs.";
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

function buildHistoryQuery() {
  const params = new URLSearchParams();
  params.set("limit", String(historyLimit));
  params.set("offset", String(historyOffset));
  if (historyMediaType.value) {
    params.set("media_type", historyMediaType.value);
  }
  return params.toString();
}

async function loadHistory() {
  historyStatus.textContent = "Loading history...";
  historyBody.innerHTML = "";
  try {
    const response = await api(`/api/v1/watch-events?${buildHistoryQuery()}`);
    if (!response.ok) {
      historyStatus.textContent = "Failed to load history";
      setHistoryPagination(0);
      return;
    }
    const rows = await response.json();
    if (rows.length === 0) {
      historyStatus.textContent = "No events for current filter/page";
      setHistoryPagination(0);
      return;
    }
    for (const row of rows) {
      const tr = document.createElement("tr");
      const watchedAt = new Date(row.watched_at).toLocaleString();
      const completed = row.completed ? "yes" : "no";
      const progress = row.progress_percent === null ? "-" : `${row.progress_percent}%`;
      const title = row.display_title || row.media_item_title || row.media_item_id;
      const type = row.media_item_type || "-";
      tr.innerHTML = `
        <td>${watchedAt}</td>
        <td>${title}</td>
        <td>${type}</td>
        <td>${row.playback_source}</td>
        <td>${completed}</td>
        <td>${progress}</td>
      `;
      historyBody.appendChild(tr);
    }
    historyStatus.textContent = `Loaded ${rows.length} event(s)`;
    setHistoryPagination(rows.length);
  } catch (_error) {
    historyStatus.textContent = "Failed to load history";
    setHistoryPagination(0);
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

historyPrev.addEventListener("click", async () => {
  historyOffset = Math.max(0, historyOffset - historyLimit);
  await loadHistory();
});

historyNext.addEventListener("click", async () => {
  historyOffset += historyLimit;
  await loadHistory();
});

importForm.addEventListener("submit", runImport);

logoutBtn.addEventListener("click", async () => {
  await api("/api/v1/session/logout", { method: "DELETE" });
  detailCard.classList.add("hidden");
  await checkSession();
});

checkSession();
