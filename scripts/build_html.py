"""HTML renderer for the darts dashboard. Pure function: payload dict in, HTML string out."""
import json

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#fafafa">
<title>PDC Tour-Card Form Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js" integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" crossorigin="anonymous"></script>
<style>
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:#fafafa; color:#1a1a1a; font-size:14px; }

header { padding:18px 22px 8px; border-bottom:1px solid #e5e5e5; background:#fff; }
h1 { margin:0 0 4px 0; font-size:18px; font-weight:600; }
.subtitle { color:#6b6b6b; font-size:12px; }

.tabs { display:flex; gap:4px; padding:8px 22px 0; background:#fff; border-bottom:1px solid #e5e5e5; }
.tab { padding:8px 16px; cursor:pointer; border-radius:6px 6px 0 0; font-weight:500; color:#6b6b6b;
  border:1px solid transparent; border-bottom:none; }
.tab.active { color:#1a1a1a; background:#fafafa; border-color:#e5e5e5; }
.tab:hover:not(.active) { background:#f5f5f5; }

.kpi-row { display:flex; gap:16px; padding:12px 22px; background:#fff; border-bottom:1px solid #e5e5e5;
  flex-wrap:wrap; }
.kpi { font-size:12px; color:#6b6b6b; }
.kpi b { display:block; color:#1a1a1a; font-size:18px; font-weight:600; }

.controls { padding:12px 22px; background:#fff; border-bottom:1px solid #e5e5e5;
  display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.controls input[type=search], .controls select {
  padding:6px 10px; border:1px solid #d0d0d0; border-radius:6px; font-size:13px; background:#fff; }
.controls input[type=search] { width:200px; }
.controls label { font-size:12px; color:#6b6b6b; display:flex; align-items:center; gap:6px; }

.legend { font-size:11px; color:#6b6b6b; padding:6px 22px 14px; }
.legend code { background:#f0f0f0; padding:1px 4px; border-radius:3px; }
.legend b { color:#1a1a1a; }

.table-wrap { padding:14px 22px 24px; }
table.main { width:100%; border-collapse:separate; border-spacing:0; background:#fff;
  border-radius:8px; overflow:hidden; box-shadow:0 1px 2px rgba(0,0,0,.04); }
table.main thead th { text-align:left; padding:10px 12px; font-weight:600; font-size:12px; color:#555;
  background:#f5f5f5; border-bottom:1px solid #e5e5e5; cursor:pointer; user-select:none; white-space:nowrap; }
table.main thead th:hover { background:#ececec; }
table.main thead th .arrow { color:#aaa; margin-left:4px; font-size:10px; }
table.main thead th.sorted .arrow { color:#1a1a1a; }
table.main tbody td { padding:9px 12px; border-bottom:1px solid #f0f0f0; }
table.main tbody tr { cursor:pointer; }
table.main tbody tr:hover td { background:#fafbff; }
table.main tbody tr.selected td { background:#fff8e1; }
.flag { display:inline-block; width:28px; font-weight:600; color:#888; font-size:11px; }
.num { font-variant-numeric:tabular-nums; text-align:right; }
.trend-pos { color:#198754; font-weight:600; }
.trend-neg { color:#c82333; font-weight:600; }
.trend-zero { color:#888; }
.bar { height:4px; background:#eee; border-radius:2px; margin-top:3px; overflow:hidden; }
.bar > span { display:block; height:100%; background:linear-gradient(90deg,#ff9c00,#ff6900); }
.stale { color:#c47100; }

#detail { position:fixed; right:0; top:0; bottom:0; width:480px; max-width:90vw; background:#fff;
  box-shadow:-2px 0 12px rgba(0,0,0,.08); padding:18px 22px; transform:translateX(110%);
  transition:transform .2s ease; overflow-y:auto; z-index:10; }
#detail.open { transform:translateX(0); }
#detail h2 { margin:0 0 4px; font-size:16px; }
#detail .close-x { position:absolute; top:12px; right:14px; cursor:pointer; font-size:22px;
  color:#999; line-height:1; }
#detail .close-x:hover { color:#333; }
#detail .player-meta { color:#6b6b6b; font-size:12px; margin-bottom:12px; }
#detail .summary-stats { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; background:#fafafa;
  border-radius:6px; padding:10px; margin-bottom:14px; }
#detail .summary-stats div { font-size:11px; color:#6b6b6b; }
#detail .summary-stats div b { display:block; color:#1a1a1a; font-size:15px; font-weight:600;
  font-variant-numeric:tabular-nums; }
#detail table { width:100%; border-collapse:collapse; }
#detail table td { padding:6px 8px; font-size:12px; border-bottom:1px solid #f0f0f0; }
#detail table th { padding:6px 8px; font-size:11px; text-align:left; color:#666; }
.result-W { color:#198754; font-weight:600; }
.result-L { color:#c82333; font-weight:600; }

/* COMPARE TAB */
.compare { padding:18px 22px 30px; }
.compare-controls { display:flex; gap:14px; align-items:flex-end; flex-wrap:wrap; margin-bottom:18px;
  background:#fff; padding:14px 16px; border-radius:8px; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.compare-controls .field { display:flex; flex-direction:column; gap:4px; }
.compare-controls label { font-size:11px; color:#6b6b6b; }
.compare-controls select, .compare-controls input { padding:6px 10px; border:1px solid #d0d0d0;
  border-radius:6px; font-size:13px; background:#fff; }
.compare-controls .swap { padding:6px 10px; cursor:pointer; background:#f5f5f5; border:1px solid #d0d0d0;
  border-radius:6px; font-size:13px; }
.compare-controls .swap:hover { background:#ececec; }

.compare-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.player-card { background:#fff; border-radius:8px; padding:16px 18px;
  box-shadow:0 1px 2px rgba(0,0,0,.04); }
.player-card h3 { margin:0 0 4px; font-size:16px; }
.player-card .meta { color:#6b6b6b; font-size:12px; margin-bottom:10px; }
.player-card .pa-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:8px;
  background:#fafafa; border-radius:6px; padding:10px; margin-bottom:12px; }
.player-card .pa-stats > div { font-size:10px; color:#6b6b6b; }
.player-card .pa-stats b { display:block; font-size:14px; color:#1a1a1a; font-weight:600;
  font-variant-numeric:tabular-nums; }
.player-card .delta-better { color:#198754; }
.player-card .delta-worse { color:#c82333; }
.player-card table { width:100%; border-collapse:collapse; font-size:12px; }
.player-card table td { padding:5px 6px; border-bottom:1px solid #f0f0f0; }
.player-card table th { padding:5px 6px; font-size:10px; color:#666; text-align:left; }

.chart-card { background:#fff; border-radius:8px; padding:16px; margin-top:16px;
  box-shadow:0 1px 2px rgba(0,0,0,.04); }
.chart-card h3 { margin:0 0 10px; font-size:14px; }
.chart-wrap { position:relative; height:280px; }

.h2h-card { background:#fff; border-radius:8px; padding:16px; margin-top:16px;
  box-shadow:0 1px 2px rgba(0,0,0,.04); }
.h2h-card h3 { margin:0 0 10px; font-size:14px; }
.common-table { width:100%; border-collapse:collapse; font-size:12px; }
.common-table th, .common-table td { padding:6px 8px; border-bottom:1px solid #f0f0f0; text-align:left; }
.common-table th { font-size:11px; color:#666; }
.common-table .num { text-align:right; font-variant-numeric:tabular-nums; }
.empty { color:#999; font-style:italic; padding:8px 0; font-size:12px; }

/* ============ MOBILE RESPONSIVE (≤ 768px) ============ */
#detailBackdrop { position:fixed; inset:0; background:rgba(0,0,0,.35); opacity:0;
  pointer-events:none; transition:opacity .2s ease; z-index:9; }
#detailBackdrop.open { opacity:1; pointer-events:auto; }

@media (max-width: 768px) {
  body { font-size: 13px; }
  header { padding:14px 14px 6px; }
  h1 { font-size:16px; }
  .subtitle { font-size:11px; }
  .tabs { padding:6px 10px 0; gap:2px; overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .tab { padding:8px 12px; font-size:13px; flex-shrink:0; }
  .kpi-row { padding:10px 14px; gap:12px; }
  .kpi b { font-size:15px; }
  .controls { padding:10px 14px; gap:8px; }
  .controls input[type=search] { width:100%; }
  .controls label { font-size:12px; }
  .legend { padding:6px 14px 12px; font-size:11px; }
  .table-wrap { padding:10px 0 16px; overflow-x:hidden; }

  /* Slim down to 5 essential columns on phones:
     Sea# | Player | C | Avg L10 | +/- vs opp.
     Hide: Opp avg(5), Trend(7), WR(8), SD(9), CO%(10), 180s(11), F9(12), SeaAvg(13), n(14), Last(15) */
  table.main thead th:nth-child(5),  table.main tbody td:nth-child(5),
  table.main thead th:nth-child(7),  table.main tbody td:nth-child(7),
  table.main thead th:nth-child(8),  table.main tbody td:nth-child(8),
  table.main thead th:nth-child(9),  table.main tbody td:nth-child(9),
  table.main thead th:nth-child(10), table.main tbody td:nth-child(10),
  table.main thead th:nth-child(11), table.main tbody td:nth-child(11),
  table.main thead th:nth-child(12), table.main tbody td:nth-child(12),
  table.main thead th:nth-child(13), table.main tbody td:nth-child(13),
  table.main thead th:nth-child(14), table.main tbody td:nth-child(14),
  table.main thead th:nth-child(15), table.main tbody td:nth-child(15) { display:none; }
  table.main thead th { padding:9px 6px; font-size:11px; }
  table.main tbody td { padding:11px 6px; font-size:13px; }
  table.main { border-radius:0; }

  /* Detail panel becomes a bottom-sheet */
  #detail {
    width:100%; max-width:none; right:0; left:0; top:auto; bottom:0;
    height:88vh; max-height:88vh; transform:translateY(110%);
    border-radius:14px 14px 0 0;
    box-shadow:0 -2px 20px rgba(0,0,0,.15);
  }
  #detail.open { transform:translateY(0); }
  #detail .close-x { font-size:26px; padding:6px; }
  /* Drag handle */
  #detail::before {
    content:""; position:absolute; top:8px; left:50%; transform:translateX(-50%);
    width:42px; height:4px; background:#ddd; border-radius:2px;
  }
  #detail h2 { margin-top:18px; }

  /* Compare tab — stack vertically */
  .compare { padding:14px; }
  .compare-controls { padding:12px; gap:10px; }
  .compare-controls .field { width:100%; }
  .compare-controls select { width:100%; }
  .compare-controls .swap { width:100%; }
  .compare-grid { grid-template-columns:1fr; gap:12px; }
  .player-card { padding:14px; }
  .player-card .pa-stats { grid-template-columns:repeat(3,1fr); padding:8px; }
  .player-card .pa-stats b { font-size:13px; }
  .player-card table { font-size:11px; }
  .player-card table td, .player-card table th { padding:5px 4px; }
  .chart-card, .h2h-card { padding:12px; }
  .chart-wrap { height:240px; }
  .common-table { font-size:11px; }
  .common-table th, .common-table td { padding:6px 4px; }
}

/* Very small phones — drop the rank column too to save width */
@media (max-width: 380px) {
  table.main thead th:nth-child(1), table.main tbody td:nth-child(1) { display:none; }
}
</style>
</head>
<body>
<header>
  <h1>PDC Tour-Card Form Dashboard</h1>
  <div class="subtitle"><span id="filter-desc"></span> · Fetched <span id="fetched"></span></div>
</header>

<div class="tabs">
  <div class="tab active" data-tab="form">Form table</div>
  <div class="tab" data-tab="compare">Compare players</div>
</div>

<!-- ============ FORM TAB ============ -->
<div id="tab-form">
  <div class="kpi-row">
    <div class="kpi"><b id="kpi-players">—</b>tour-card holders</div>
    <div class="kpi"><b id="kpi-matches">—</b>matches in window</div>
    <div class="kpi"><b id="kpi-mean">—</b>mean of last-10 avgs</div>
    <div class="kpi"><b id="kpi-fresh">—</b>played in 90d</div>
  </div>
  <div class="controls">
    <input type="search" id="search" placeholder="Search player or country…">
    <label>Min matches in window
      <select id="minmatches">
        <option value="0">0</option>
        <option value="3" selected>3</option>
        <option value="5">5</option>
        <option value="10">10</option>
      </select>
    </label>
    <label><input type="checkbox" id="freshonly"> Only played in last 90 days</label>
  </div>
  <div class="legend">
    <b>Avg L10</b> = 3-dart avg of last 10 matches · <b>Trend</b> = avg(last 5) − avg(prior 5) · <b>± SD</b> = consistency · <b>CO%</b> = season checkout % · <b>180s</b> = season total · <b>F9</b> = season first-9 average. Click any row for the match-by-match breakdown.
  </div>
  <div class="table-wrap">
    <table class="main"><thead><tr id="thead"></tr></thead><tbody id="tbody"></tbody></table>
  </div>
</div>

<div id="detailBackdrop" onclick="closeDetail()"></div>
<aside id="detail">
  <span class="close-x" onclick="closeDetail()">×</span>
  <h2 id="d-name"></h2>
  <div class="player-meta" id="d-meta"></div>
  <div class="summary-stats" id="d-summary"></div>
  <table>
    <thead><tr><th>#</th><th>Date</th><th>Tournament</th><th>Round</th>
      <th>Res</th><th>Score</th><th>Opponent</th><th class="num">Avg</th><th class="num">Opp avg</th><th class="num">+/−</th></tr></thead>
    <tbody id="d-matches"></tbody>
  </table>
  <div style="margin-top:14px;font-size:11px;">
    <a id="d-profile" target="_blank" rel="noopener">Open profile on dartsorakel.com →</a>
  </div>
</aside>

<!-- ============ COMPARE TAB ============ -->
<div id="tab-compare" style="display:none;">
  <div class="compare">
    <div class="compare-controls">
      <div class="field">
        <label for="cmpA">Player A</label>
        <select id="cmpA"></select>
      </div>
      <button class="swap" onclick="swapPlayers()">⇄ Swap</button>
      <div class="field">
        <label for="cmpB">Player B</label>
        <select id="cmpB"></select>
      </div>
      <div class="field">
        <label for="cmpN">Sample window</label>
        <select id="cmpN">
          <option value="5">Last 5 matches</option>
          <option value="10" selected>Last 10 matches</option>
          <option value="20">Last 20</option>
          <option value="30">Last 30</option>
          <option value="50">Last 50 (max)</option>
        </select>
      </div>
      <div class="field">
        <label for="cmpEvent">Event filter</label>
        <select id="cmpEvent">
          <option value="">All event types</option>
          <option value="PT">Pro Tour only</option>
          <option value="MJ">TV Majors only</option>
          <option value="ET">European Tour only</option>
          <option value="U">Premier League only</option>
        </select>
      </div>
    </div>

    <div class="compare-grid">
      <div class="player-card" id="cardA"></div>
      <div class="player-card" id="cardB"></div>
    </div>

    <div class="chart-card">
      <h3>Average per match (most-recent first → left)</h3>
      <div class="chart-wrap"><canvas id="cmpChart"></canvas></div>
    </div>

    <div class="h2h-card">
      <h3>Common opponents in the sample window</h3>
      <div id="commonOpponents"></div>
    </div>

    <div class="h2h-card">
      <h3>Direct head-to-head matches</h3>
      <div id="directH2H"></div>
    </div>
  </div>
</div>

<script>
const DATA = __INLINE_DATA__;
const FRESH_DAYS = 90;
const today = new Date(DATA.fetched_at_utc);

// ----- TAB SWITCHING -----
document.querySelectorAll(".tab").forEach(t => {
  t.onclick = () => {
    document.querySelectorAll(".tab").forEach(x => x.classList.toggle("active", x === t));
    const tab = t.dataset.tab;
    document.getElementById("tab-form").style.display = tab === "form" ? "" : "none";
    document.getElementById("tab-compare").style.display = tab === "compare" ? "" : "none";
    if (tab === "compare") renderCompare();
  };
});

// ============ FORM TAB ============
const COLS = [
  { key:"season_rank",     label:"Sea#",  type:"num" },
  { key:"player_name",     label:"Player" },
  { key:"country",         label:"C" },
  { key:"avg_last10",      label:"Avg L10", type:"num" },
  { key:"mean_opp_avg",    label:"Opp avg", type:"num" },
  { key:"mean_perf_vs_opp", label:"+/− vs opp", type:"trend" },
  { key:"trend",           label:"Trend",   type:"trend" },
  { key:"win_rate_last10", label:"WR L10",  type:"pct" },
  { key:"stdev_last10",    label:"± SD",    type:"num" },
  { key:"checkout_pct",    label:"CO%",     type:"num" },
  { key:"total_180s",      label:"180s",    type:"num" },
  { key:"first9_avg",      label:"F9 Avg",  type:"num" },
  { key:"season_avg",      label:"Sea Avg", type:"num" },
  { key:"matches_in_window", label:"n",     type:"num" },
  { key:"last_match_date", label:"Last played", type:"date" }
];

let sortKey = "avg_last10";
let sortDir = -1;

function fmtTrend(v) {
  if (v == null) return "—";
  const cls = v > 0.05 ? "trend-pos" : v < -0.05 ? "trend-neg" : "trend-zero";
  return `<span class="${cls}">${v > 0 ? "+" : ""}${v.toFixed(2)}</span>`;
}
function fmtPct(v) { return v == null ? "—" : (v*100).toFixed(0)+"%"; }
function fmtCO(v) { return v == null ? "—" : v.toFixed(1)+"%"; }
function fmtDate(s) {
  if (!s) return "—";
  const days = Math.floor((today - new Date(s)) / 86400000);
  const stale = days > FRESH_DAYS;
  return `<span title="${days} days ago" class="${stale ? 'stale' : ''}">${s}${stale ? ' ⚠' : ''}</span>`;
}

function buildHeader() {
  const tr = document.getElementById("thead");
  tr.innerHTML = COLS.map(c => `<th data-key="${c.key}" class="${c.key === sortKey ? 'sorted' : ''}">${c.label}<span class="arrow">${c.key === sortKey ? (sortDir < 0 ? "▼" : "▲") : "↕"}</span></th>`).join("");
  tr.querySelectorAll("th").forEach(th => {
    th.onclick = () => {
      const k = th.dataset.key;
      if (sortKey === k) sortDir = -sortDir;
      else { sortKey = k; sortDir = -1; }
      buildHeader(); renderForm();
    };
  });
}

function getRows() {
  const q = document.getElementById("search").value.toLowerCase().trim();
  const minMatches = parseInt(document.getElementById("minmatches").value, 10);
  const freshOnly = document.getElementById("freshonly").checked;
  let rows = DATA.summary.filter(r => r.matches_in_window >= minMatches);
  if (q) rows = rows.filter(r =>
    (r.player_name || "").toLowerCase().includes(q) ||
    (r.country || "").toLowerCase().includes(q));
  if (freshOnly) {
    const cutoff = new Date(today.getTime() - FRESH_DAYS*86400000);
    rows = rows.filter(r => r.last_match_date && new Date(r.last_match_date) >= cutoff);
  }
  rows.sort((a, b) => {
    const av = a[sortKey], bv = b[sortKey];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    if (typeof av === "number" && typeof bv === "number") return (av - bv) * sortDir;
    return String(av).localeCompare(String(bv)) * sortDir;
  });
  return rows;
}

function renderForm() {
  const rows = getRows();
  const tbody = document.getElementById("tbody");
  const maxAvg = Math.max(...DATA.summary.map(r => r.avg_last10 || 0));
  tbody.innerHTML = rows.map(r => {
    const barW = r.avg_last10 ? Math.round((r.avg_last10 / maxAvg) * 100) : 0;
    return `<tr data-key="${r.player_key}">
      <td class="num">${r.season_rank ?? "—"}</td>
      <td><b>${r.player_name}</b></td>
      <td><span class="flag">${r.country || ""}</span></td>
      <td class="num"><b>${r.avg_last10 ?? "—"}</b><div class="bar"><span style="width:${barW}%"></span></div></td>
      <td class="num">${r.mean_opp_avg ?? "—"}</td>
      <td class="num">${fmtTrend(r.mean_perf_vs_opp)}</td>
      <td class="num">${fmtTrend(r.trend)}</td>
      <td class="num">${fmtPct(r.win_rate_last10)}</td>
      <td class="num">${r.stdev_last10 ?? "—"}</td>
      <td class="num">${fmtCO(r.checkout_pct)}</td>
      <td class="num">${r.total_180s ?? "—"}</td>
      <td class="num">${r.first9_avg ?? "—"}</td>
      <td class="num">${r.season_avg?.toFixed(2) ?? "—"}</td>
      <td class="num">${r.matches_in_window}</td>
      <td>${fmtDate(r.last_match_date)}</td>
    </tr>`;
  }).join("");
  tbody.querySelectorAll("tr").forEach(tr => {
    tr.onclick = () => openDetail(parseInt(tr.dataset.key, 10));
  });

  document.getElementById("kpi-players").textContent = rows.length;
  document.getElementById("kpi-matches").textContent = rows.reduce((a,r) => a + r.matches_in_window, 0);
  const valid = rows.filter(r => r.avg_last10 != null);
  const mean = valid.length ? (valid.reduce((a,r)=>a+r.avg_last10,0)/valid.length) : 0;
  document.getElementById("kpi-mean").textContent = mean.toFixed(2);
  const cutoff = new Date(today.getTime() - FRESH_DAYS*86400000);
  const fresh = rows.filter(r => r.last_match_date && new Date(r.last_match_date) >= cutoff).length;
  document.getElementById("kpi-fresh").textContent = `${fresh}/${rows.length}`;
}

function openDetail(playerKey) {
  document.querySelectorAll("table.main tbody tr").forEach(tr => tr.classList.toggle("selected", parseInt(tr.dataset.key,10) === playerKey));
  const s = DATA.summary.find(r => r.player_key === playerKey);
  const matches = DATA.matches.filter(m => m.player_key === playerKey);
  document.getElementById("d-name").textContent = s.player_name;
  document.getElementById("d-meta").textContent =
    `${s.country || ""} · Season rank #${s.season_rank ?? "—"} · Season avg ${s.season_avg?.toFixed(2) ?? "—"} · Last played ${s.last_match_date ?? "—"}`;
  document.getElementById("d-summary").innerHTML = `
    <div>Avg last 10<b>${s.avg_last10 ?? "—"}</b></div>
    <div>Trend (L5−P5)<b>${s.trend == null ? "—" : (s.trend > 0 ? "+" : "") + s.trend.toFixed(2)}</b></div>
    <div>Win rate<b>${fmtPct(s.win_rate_last10)}</b></div>
    <div>Best<b>${s.best_last10 ?? "—"}</b></div>
    <div>Worst<b>${s.worst_last10 ?? "—"}</b></div>
    <div>Std dev<b>${s.stdev_last10 ?? "—"}</b></div>
  `;
  document.getElementById("d-matches").innerHTML = matches.map(m => `
    <tr>
      <td>${m.match_idx}</td><td>${m.match_date}</td>
      <td>${m.tournament || ""}</td><td>${m.round || ""}</td>
      <td class="result-${m.result === "Won" ? "W" : "L"}">${m.result === "Won" ? "W" : "L"}</td>
      <td>${m.score || ""}</td><td>${m.opponent || ""}</td>
      <td class="num">${m.three_dart_average ?? "—"}</td>
      <td class="num">${m.opponent_avg ?? "—"}</td>
      <td class="num">${m.perf_vs_opp == null ? "—" : `<span class="${m.perf_vs_opp > 0 ? 'trend-pos' : 'trend-neg'}">${m.perf_vs_opp > 0 ? '+' : ''}${m.perf_vs_opp.toFixed(2)}</span>`}</td>
    </tr>`).join("");
  document.getElementById("d-profile").href = s.profile_url || "#";
  document.getElementById("d-profile").textContent = "Open profile on dartsorakel.com →";
  document.getElementById("detail").classList.add("open");
  document.getElementById("detailBackdrop").classList.add("open");
}
function closeDetail() {
  document.getElementById("detail").classList.remove("open");
  document.getElementById("detailBackdrop").classList.remove("open");
  document.querySelectorAll("table.main tbody tr").forEach(tr => tr.classList.remove("selected"));
}

document.getElementById("filter-desc").textContent = DATA.filter;
document.getElementById("fetched").textContent = DATA.fetched_at_utc.replace("T"," ").replace("Z"," UTC");
document.getElementById("search").oninput = renderForm;
document.getElementById("minmatches").onchange = renderForm;
document.getElementById("freshonly").onchange = renderForm;

buildHeader(); renderForm();

// ============ COMPARE TAB ============
let chart = null;

// populate dropdowns sorted alphabetically
const sortedPlayers = [...DATA.summary].sort((a,b)=>a.player_name.localeCompare(b.player_name));
function populateSelect(id, defaultKey) {
  const sel = document.getElementById(id);
  sel.innerHTML = sortedPlayers.map(p =>
    `<option value="${p.player_key}" ${p.player_key === defaultKey ? "selected" : ""}>${p.player_name} (${p.country || "—"})</option>`).join("");
}
// Default: top two by avg_last10
const top2 = [...DATA.summary].filter(s=>s.avg_last10).sort((a,b)=>b.avg_last10-a.avg_last10);
populateSelect("cmpA", top2[0]?.player_key);
populateSelect("cmpB", top2[1]?.player_key);

["cmpA","cmpB","cmpN","cmpEvent"].forEach(id => {
  document.getElementById(id).onchange = renderCompare;
});

function swapPlayers() {
  const a = document.getElementById("cmpA").value;
  document.getElementById("cmpA").value = document.getElementById("cmpB").value;
  document.getElementById("cmpB").value = a;
  renderCompare();
}

function getMatches(playerKey, n, eventFilter) {
  const all = (DATA.full[playerKey] || []);
  let rows = all;
  if (eventFilter) rows = rows.filter(m => m.c === eventFilter);
  return rows.slice(0, n);
}

function stats(matches) {
  const avgs = matches.filter(m => m.a != null).map(m => m.a);
  if (!avgs.length) return null;
  const mean = avgs.reduce((a,b)=>a+b,0)/avgs.length;
  const sd = Math.sqrt(avgs.reduce((a,b)=>a+(b-mean)*(b-mean),0)/avgs.length);
  const wins = matches.filter(m => m.w === 1).length;
  return { mean, sd, wins, n: matches.length, avgs,
    best: Math.max(...avgs), worst: Math.min(...avgs),
    wr: wins/matches.length };
}

function renderCard(elId, summary, ms, mine, other) {
  const el = document.getElementById(elId);
  if (!summary) { el.innerHTML = "<div class='empty'>No data</div>"; return; }
  if (!ms || !ms.length) {
    el.innerHTML = `<h3>${summary.player_name}</h3>
      <div class="meta">${summary.country || ""} · Season rank #${summary.season_rank ?? "—"}</div>
      <div class='empty'>No matches in this filter window</div>`;
    return;
  }
  const s = stats(ms);
  const delta = (mine, other, key, higherIsBetter=true) => {
    if (!other) return "";
    const d = mine - other;
    if (Math.abs(d) < 0.01) return "";
    const better = higherIsBetter ? d > 0 : d < 0;
    return `<span class="${better ? 'delta-better' : 'delta-worse'}"> (${d > 0 ? '+' : ''}${d.toFixed(2)})</span>`;
  };
  el.innerHTML = `
    <h3>${summary.player_name}</h3>
    <div class="meta">${summary.country || ""} · Season rank #${summary.season_rank ?? "—"} · Season avg ${summary.season_avg?.toFixed(2) ?? "—"}</div>
    <div class="pa-stats">
      <div>Avg<b>${s.mean.toFixed(2)}${delta(s.mean, other?.mean, 'mean', true)}</b></div>
      <div>± SD<b>${s.sd.toFixed(2)}${delta(s.sd, other?.sd, 'sd', false)}</b></div>
      <div>Win rate<b>${(s.wr*100).toFixed(0)}%${delta(s.wr*100, other ? other.wr*100 : null, 'wr', true)}</b></div>
      <div>Best<b>${s.best.toFixed(2)}</b></div>
      <div>Worst<b>${s.worst.toFixed(2)}</b></div>
      <div>n<b>${s.n}</b></div>
    </div>
    <table>
      <thead><tr><th>Date</th><th>Event</th><th>Round</th><th>Res</th><th>Score</th><th>Opponent</th><th class="num">Avg</th><th class="num">Opp</th></tr></thead>
      <tbody>
        ${ms.map(m => `<tr>
          <td>${m.d}</td><td>${m.t || ""}</td><td>${m.r || ""}</td>
          <td class="result-${m.w ? 'W' : 'L'}">${m.w ? 'W' : 'L'}</td>
          <td>${m.s || ""}</td><td>${m.op || ""}</td>
          <td class="num">${m.a == null ? '—' : m.a.toFixed(2)}</td>
          <td class="num">${m.oa == null ? '—' : m.oa.toFixed(2)}</td>
        </tr>`).join("")}
      </tbody>
    </table>
  `;
}

function renderCompare() {
  const a = parseInt(document.getElementById("cmpA").value, 10);
  const b = parseInt(document.getElementById("cmpB").value, 10);
  const n = parseInt(document.getElementById("cmpN").value, 10);
  const ef = document.getElementById("cmpEvent").value;
  const sa = DATA.summary.find(r => r.player_key === a);
  const sb = DATA.summary.find(r => r.player_key === b);
  const ma = getMatches(a, n, ef);
  const mb = getMatches(b, n, ef);
  const stA = stats(ma);
  const stB = stats(mb);
  renderCard("cardA", sa, ma, stA, stB);
  renderCard("cardB", sb, mb, stB, stA);

  // CHART: overlay both players' per-match averages
  const labelsLen = Math.max(ma.length, mb.length);
  const labels = Array.from({length: labelsLen}, (_, i) => `M${i+1}`);
  if (chart) chart.destroy();
  chart = new Chart(document.getElementById("cmpChart").getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: sa?.player_name,
          data: ma.map(m => m.a),
          borderColor: "#ff9c00",
          backgroundColor: "rgba(255,156,0,.1)",
          tension: 0.25,
          pointRadius: 4,
        },
        {
          label: sb?.player_name,
          data: mb.map(m => m.a),
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13,110,253,.1)",
          tension: 0.25,
          pointRadius: 4,
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { suggestedMin: 75, suggestedMax: 115, title: { display: true, text: "3-dart average" } } },
      plugins: { tooltip: {
        callbacks: {
          afterLabel: function(ctx) {
            const player = ctx.datasetIndex === 0 ? ma : mb;
            const m = player[ctx.dataIndex];
            return m ? [`${m.d} · ${m.r || ""} vs ${m.op || ""}`, `Result: ${m.w ? "W" : "L"} ${m.s || ""}`] : "";
          }
        }
      }}
    }
  });

  // COMMON OPPONENTS
  const aByOpp = {}, bByOpp = {};
  ma.forEach(m => { if (m.op) (aByOpp[m.op] = aByOpp[m.op] || []).push(m); });
  mb.forEach(m => { if (m.op) (bByOpp[m.op] = bByOpp[m.op] || []).push(m); });
  const common = Object.keys(aByOpp).filter(op => bByOpp[op]);
  const co = document.getElementById("commonOpponents");
  if (!common.length) {
    co.innerHTML = "<div class='empty'>No common opponents in the current window. Widen the sample size to find more.</div>";
  } else {
    co.innerHTML = `
      <table class="common-table">
        <thead><tr><th>Opponent</th>
          <th class="num">A games</th><th class="num">A avg</th><th class="num">A wins</th>
          <th class="num">B games</th><th class="num">B avg</th><th class="num">B wins</th>
          <th class="num">Edge</th>
        </tr></thead>
        <tbody>
        ${common.map(op => {
          const aGames = aByOpp[op], bGames = bByOpp[op];
          const aAvg = aGames.filter(g=>g.a).reduce((s,g)=>s+g.a,0) / aGames.filter(g=>g.a).length;
          const bAvg = bGames.filter(g=>g.a).reduce((s,g)=>s+g.a,0) / bGames.filter(g=>g.a).length;
          const aW = aGames.filter(g=>g.w).length;
          const bW = bGames.filter(g=>g.w).length;
          const edge = aAvg - bAvg;
          const cls = edge > 0.05 ? 'delta-better' : edge < -0.05 ? 'delta-worse' : '';
          return `<tr>
            <td>${op}</td>
            <td class="num">${aGames.length}</td><td class="num">${aAvg.toFixed(2)}</td><td class="num">${aW}/${aGames.length}</td>
            <td class="num">${bGames.length}</td><td class="num">${bAvg.toFixed(2)}</td><td class="num">${bW}/${bGames.length}</td>
            <td class="num"><span class="${cls}">${edge > 0 ? '+' : ''}${edge.toFixed(2)}</span></td>
          </tr>`;
        }).join("")}
        </tbody>
      </table>
    `;
  }

  // DIRECT H2H
  const direct = ma.filter(m => m.opk === b);
  const dh = document.getElementById("directH2H");
  if (!direct.length) {
    dh.innerHTML = "<div class='empty'>No direct meetings between these two players in the current sample window.</div>";
  } else {
    const aWins = direct.filter(m => m.w).length;
    dh.innerHTML = `
      <div style="margin-bottom:8px;font-size:13px;"><b>${sa.player_name} ${aWins}–${direct.length - aWins} ${sb.player_name}</b> in their last ${direct.length} meeting${direct.length > 1 ? "s" : ""}</div>
      <table class="common-table">
        <thead><tr><th>Date</th><th>Event</th><th>Round</th><th>Result</th><th>Score</th><th class="num">${sa.player_name} avg</th></tr></thead>
        <tbody>
          ${direct.map(m => `<tr>
            <td>${m.d}</td><td>${m.t || ""}</td><td>${m.r || ""}</td>
            <td class="result-${m.w ? 'W' : 'L'}">${m.w ? sa.player_name + " won" : sb.player_name + " won"}</td>
            <td>${m.s || ""}</td>
            <td class="num">${m.a == null ? '—' : m.a.toFixed(2)}</td>
          </tr>`).join("")}
        </tbody>
      </table>
    `;
  }
}
</script>
</body>
</html>
"""


def render_html(payload: dict) -> str:
    js_data = json.dumps(payload, separators=(",", ":"))
    return HTML.replace("__INLINE_DATA__", js_data)
