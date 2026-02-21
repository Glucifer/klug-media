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
const refreshData = document.getElementById("refresh-data");
const logoutBtn = document.getElementById("logout-btn");
const detailTitle = document.getElementById("detail-title");
const detailProgress = document.getElementById("detail-progress");
const detailStatus = document.getElementById("detail-status");
const episodeList = document.getElementById("episode-list");

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
  await Promise.all([loadShows(), loadProgress()]);
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

logoutBtn.addEventListener("click", async () => {
  await api("/api/v1/session/logout", { method: "DELETE" });
  detailCard.classList.add("hidden");
  await checkSession();
});

checkSession();
