const scanButton = document.querySelector("#scanButton");
const limitInput = document.querySelector("#limitInput");
const maxMarketsInput = document.querySelector("#maxMarketsInput");
const profitInput = document.querySelector("#profitInput");
const opportunityCount = document.querySelector("#opportunityCount");
const bestEdge = document.querySelector("#bestEdge");
const scanTime = document.querySelector("#scanTime");
const statusText = document.querySelector("#statusText");
const lastUpdated = document.querySelector("#lastUpdated");
const resultsBody = document.querySelector("#resultsBody");
const arbMonitorButton = document.querySelector("#arbMonitorButton");
const arbAlertStatus = document.querySelector("#arbAlertStatus");
const arbAlerts = document.querySelector("#arbAlerts");
const traderButton = document.querySelector("#traderButton");
const categoryInput = document.querySelector("#categoryInput");
const periodInput = document.querySelector("#periodInput");
const orderInput = document.querySelector("#orderInput");
const traderLimitInput = document.querySelector("#traderLimitInput");
const tradesPerTraderInput = document.querySelector("#tradesPerTraderInput");
const closedPositionsInput = document.querySelector("#closedPositionsInput");
const minWinRateInput = document.querySelector("#minWinRateInput");
const minClosedInput = document.querySelector("#minClosedInput");
const minRecentTradesInput = document.querySelector("#minRecentTradesInput");
const traderCount = document.querySelector("#traderCount");
const topScore = document.querySelector("#topScore");
const traderLoadTime = document.querySelector("#traderLoadTime");
const traderStatusText = document.querySelector("#traderStatusText");
const traderLastUpdated = document.querySelector("#traderLastUpdated");
const traderResults = document.querySelector("#traderResults");
const smartIngestButton = document.querySelector("#smartIngestButton");
const smartLoadButton = document.querySelector("#smartLoadButton");
const smartCategoryInput = document.querySelector("#smartCategoryInput");
const smartPeriodInput = document.querySelector("#smartPeriodInput");
const candidateLimitInput = document.querySelector("#candidateLimitInput");
const smartTradesInput = document.querySelector("#smartTradesInput");
const smartPositionsInput = document.querySelector("#smartPositionsInput");
const markoutTradesInput = document.querySelector("#markoutTradesInput");
const smartMinTradesInput = document.querySelector("#smartMinTradesInput");
const smartMinClosedInput = document.querySelector("#smartMinClosedInput");
const smartMinWinRateInput = document.querySelector("#smartMinWinRateInput");
const smartWalletCount = document.querySelector("#smartWalletCount");
const smartTopScore = document.querySelector("#smartTopScore");
const smartUpdateStat = document.querySelector("#smartUpdateStat");
const smartStatusText = document.querySelector("#smartStatusText");
const smartLastUpdated = document.querySelector("#smartLastUpdated");
const smartResults = document.querySelector("#smartResults");
const watchlistLoadButton = document.querySelector("#watchlistLoadButton");
const traderMonitorButton = document.querySelector("#traderMonitorButton");
const watchlistRefreshButton = document.querySelector("#watchlistRefreshButton");
const watchlistCount = document.querySelector("#watchlistCount");
const watchlistStatusText = document.querySelector("#watchlistStatusText");
const watchlistLastLoad = document.querySelector("#watchlistLastLoad");
const watchlistResults = document.querySelector("#watchlistResults");
const watchlistAlertStatus = document.querySelector("#watchlistAlertStatus");
const watchlistAlerts = document.querySelector("#watchlistAlerts");
const paperLoadButton = document.querySelector("#paperLoadButton");
const paperReconcileButton = document.querySelector("#paperReconcileButton");
const paperSaveBalanceButton = document.querySelector("#paperSaveBalanceButton");
const paperResetButton = document.querySelector("#paperResetButton");
const paperSaveExecutionButton = document.querySelector("#paperSaveExecutionButton");
const paperBalanceInput = document.querySelector("#paperBalanceInput");
const paperEntrySlippageInput = document.querySelector("#paperEntrySlippageInput");
const paperExitSlippageInput = document.querySelector("#paperExitSlippageInput");
const paperFeeInput = document.querySelector("#paperFeeInput");
const paperMaxChaseInput = document.querySelector("#paperMaxChaseInput");
const paperCapitalModeInput = document.querySelector("#paperCapitalModeInput");
const paperMinCashReserveInput = document.querySelector("#paperMinCashReserveInput");
const paperExecutionStatus = document.querySelector("#paperExecutionStatus");
const paperCashBalance = document.querySelector("#paperCashBalance");
const paperActiveCost = document.querySelector("#paperActiveCost");
const paperRunningPnl = document.querySelector("#paperRunningPnl");
const paperEquity = document.querySelector("#paperEquity");
const paperWinLoss = document.querySelector("#paperWinLoss");
const paperWinRate = document.querySelector("#paperWinRate");
const paperRiskEvents = document.querySelector("#paperRiskEvents");
const paperAccountChart = document.querySelector("#paperAccountChart");
const paperAccountChartSummary = document.querySelector("#paperAccountChartSummary");
const paperLastUpdated = document.querySelector("#paperLastUpdated");
const paperClosedSummary = document.querySelector("#paperClosedSummary");
const paperActiveResults = document.querySelector("#paperActiveResults");
const paperClosedResults = document.querySelector("#paperClosedResults");
const paperTabButtons = document.querySelectorAll(".paper-tab-button");
const paperSubpanels = document.querySelectorAll("#paperActivePanel, #paperFinishedPanel");
const accountRefreshButton = document.querySelector("#accountRefreshButton");
const accountConnectionStatus = document.querySelector("#accountConnectionStatus");
const accountBalance = document.querySelector("#accountBalance");
const accountAllowance = document.querySelector("#accountAllowance");
const accountOpenPositions = document.querySelector("#accountOpenPositions");
const accountRecentTrades = document.querySelector("#accountRecentTrades");
const accountLiveTrading = document.querySelector("#accountLiveTrading");
const accountLastUpdated = document.querySelector("#accountLastUpdated");
const accountConnectionDetails = document.querySelector("#accountConnectionDetails");
const accountReadOnlyData = document.querySelector("#accountReadOnlyData");
const accountConnectionForm = document.querySelector("#accountConnectionForm");
const accountConnectionSaveStatus = document.querySelector("#accountConnectionSaveStatus");
const saveAccountConnectionButton = document.querySelector("#saveAccountConnectionButton");
const testAccountConnectionButton = document.querySelector("#testAccountConnectionButton");
const deriveAccountCredentialsButton = document.querySelector("#deriveAccountCredentialsButton");
const accountAddressInput = document.querySelector("#accountAddressInput");
const accountFunderInput = document.querySelector("#accountFunderInput");
const accountSignatureTypeInput = document.querySelector("#accountSignatureTypeInput");
const accountApiKeyInput = document.querySelector("#accountApiKeyInput");
const accountApiSecretInput = document.querySelector("#accountApiSecretInput");
const accountApiPassphraseInput = document.querySelector("#accountApiPassphraseInput");
const accountPrivateKeyInput = document.querySelector("#accountPrivateKeyInput");
const liveTradingStatus = document.querySelector("#liveTradingStatus");
const liveArmButton = document.querySelector("#liveArmButton");
const liveKillButton = document.querySelector("#liveKillButton");
const liveModeMetric = document.querySelector("#liveModeMetric");
const liveBalanceMetric = document.querySelector("#liveBalanceMetric");
const liveCashReserveMetric = document.querySelector("#liveCashReserveMetric");
const liveEquityMetric = document.querySelector("#liveEquityMetric");
const liveOpenCostMetric = document.querySelector("#liveOpenCostMetric");
const liveRealizedMetric = document.querySelector("#liveRealizedMetric");
const liveRunningPnlMetric = document.querySelector("#liveRunningPnlMetric");
const liveCopytraderList = document.querySelector("#liveCopytraderList");
const liveOpenPositions = document.querySelector("#liveOpenPositions");
const liveClosedPositions = document.querySelector("#liveClosedPositions");
const linkedClosedSummary = document.querySelector("#linkedClosedSummary");
const linkedClosedPositions = document.querySelector("#linkedClosedPositions");
const liveOrderLog = document.querySelector("#liveOrderLog");
const liveTabButtons = document.querySelectorAll(".live-tab-button");
const liveSubpanels = document.querySelectorAll("#liveOpenPanel, #liveClosedPanel");
const liveCapitalModeInput = document.querySelector("#liveCapitalModeInput");
const liveMinCashReserveInput = document.querySelector("#liveMinCashReserveInput");
const liveMinTradeInput = document.querySelector("#liveMinTradeInput");
const liveMaxChaseInput = document.querySelector("#liveMaxChaseInput");
const liveSaveRiskButton = document.querySelector("#liveSaveRiskButton");
const liveAccountChart = document.querySelector("#liveAccountChart");
const liveAccountChartSummary = document.querySelector("#liveAccountChartSummary");
let scannerHasRun = false;
let tradersHaveLoaded = false;
let smartHasLoaded = false;
let smartHasIngested = false;
let arbMonitorId = null;
let traderMonitorId = null;
let traderMonitorRefreshInFlight = false;
let lastSeenPaperEventId = 0;
const monitorIntervalMs = 30000;
let copytradeSettings = {};
let liveCopytradeSettings = {};
let activeTabName = "scanner";
let liveRefreshInFlight = false;
let liveRefreshTimer = null;
let liveRiskSettingsDirty = false;
let liveRiskSettingsSaving = false;

function debounce(fn, wait = 450) {
  let timeoutId;
  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => fn(...args), wait);
  };
}

function formatMoney(value) {
  return Number(value).toFixed(4);
}

function formatUsd(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function formatUsdPrecise(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatBps(value) {
  return `${Number(value).toFixed(2)} bps`;
}

function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function formatSignedUsd(value) {
  const amount = Number(value || 0);
  const prefix = amount > 0 ? "+" : "";
  return `${prefix}${formatUsdPrecise(amount)}`;
}

function formatOptionalUsd(value) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "string") return value;
  return formatUsdPrecise(value);
}

function formatDate(timestamp) {
  if (!timestamp) return "-";
  return new Date(Number(timestamp) * 1000).toLocaleString();
}

async function ensureNotificationPermission() {
  if (!("Notification" in window)) {
    return false;
  }
  if (Notification.permission === "granted") {
    return true;
  }
  if (Notification.permission === "denied") {
    return false;
  }
  const permission = await Notification.requestPermission();
  return permission === "granted";
}

function showBrowserNotification(title, body) {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, { body });
  }
}

function setLoading(isLoading) {
  scanButton.disabled = isLoading;
  scanButton.textContent = isLoading ? "Scanning..." : "Run Scan";
  if (isLoading) {
    statusText.textContent = "Scanning";
  }
}

function renderEmpty(message) {
  resultsBody.innerHTML = `<tr class="empty-row"><td colspan="7">${message}</td></tr>`;
}

function renderError(message) {
  resultsBody.innerHTML = `<tr class="error-row"><td colspan="7">${message}</td></tr>`;
}

function renderArbAlerts(alerts) {
  if (!alerts.length) {
    arbAlerts.innerHTML = `<div class="empty-state">No arbitrage alerts stored yet.</div>`;
    return;
  }

  arbAlerts.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-row">
          <div>
            <strong>${formatBps(alert.net_profit_bps)}</strong>
            <div class="trade-meta">profit edge</div>
          </div>
          <div class="trade-title">
            <strong>${escapeHtml(alert.question || "Untitled market")}</strong>
            <span>YES ${formatMoney(alert.yes_price)} | NO ${formatMoney(alert.no_price)}</span>
          </div>
          <div>
            <strong>${formatMoney(alert.max_size)}</strong>
            <div class="trade-meta">max size</div>
          </div>
          <div>
            <strong>${new Date(alert.created_at).toLocaleTimeString()}</strong>
            <div class="trade-meta">alert</div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderTraderError(message) {
  traderResults.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function renderSmartError(message) {
  smartResults.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function renderWatchlistError(message) {
  watchlistResults.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function renderOpportunities(opportunities) {
  if (!opportunities.length) {
    renderEmpty("No binary arbitrage opportunities found for this scan.");
    return;
  }

  resultsBody.innerHTML = opportunities
    .map(
      (item) => `
        <tr>
          <td class="market-cell">
            <strong>${escapeHtml(item.question)}</strong>
            <span>${escapeHtml(item.condition_id)}</span>
          </td>
          <td>${formatMoney(item.yes_price)}</td>
          <td>${formatMoney(item.no_price)}</td>
          <td>${formatMoney(item.estimated_fee_per_set)}</td>
          <td>${formatMoney(item.net_cost_per_set)}</td>
          <td class="profit">${formatMoney(item.net_profit_per_set)}<br>${formatBps(item.net_profit_bps)}</td>
          <td>${formatMoney(item.max_size)}</td>
        </tr>
      `
    )
    .join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderTradeValueGraph({ startValue, endValue, startLabel, endLabel, history = [] }) {
  const points = [
    { value: Number(startValue || 0), label: startLabel },
    ...history.map((item) => ({ value: Number(item.mark_value_usdc || 0), label: "" })),
    { value: Number(endValue || 0), label: endLabel },
  ];
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const graphPoints = points.map((point, index) => {
    const x = points.length === 1 ? 160 : 42 + (index / (points.length - 1)) * 236;
    const y = 74 - ((point.value - min) / span) * 48;
    return { ...point, x, y };
  });
  const startPoint = graphPoints[0];
  const endPoint = graphPoints[graphPoints.length - 1];
  const up = endPoint.value >= startPoint.value;
  const lineClass = up ? "profit-stroke" : "loss-stroke";
  const endClass = up ? "profit-fill" : "loss-fill";
  const polylinePoints = graphPoints.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");

  return `
    <div class="paper-trade-graph" aria-hidden="true">
      <svg viewBox="0 0 320 104" role="img">
        <line class="graph-axis" x1="28" y1="80" x2="292" y2="80"></line>
        <polyline class="${lineClass}" points="${polylinePoints}"></polyline>
        ${graphPoints.map((point, index) => `<circle class="${index === graphPoints.length - 1 ? endClass : "neutral-fill"}" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="${index === graphPoints.length - 1 ? 6 : 4}"></circle>`).join("")}
        <text x="42" y="98" text-anchor="middle">${escapeHtml(startLabel)}</text>
        <text x="278" y="98" text-anchor="middle">${escapeHtml(endLabel)}</text>
      </svg>
      <div class="trade-meta">${Math.max(0, history.length)} mark snapshot${history.length === 1 ? "" : "s"}</div>
    </div>
  `;
}

function renderPaperAccountHistoryChart(snapshots) {
  renderAccountHistoryChart({
    snapshots,
    chartEl: paperAccountChart,
    summaryEl: paperAccountChartSummary,
    emptyText: "Account snapshots will appear as the bot runs.",
    ariaLabel: "Paper account balance over time",
    equityKey: "equity_estimate",
    cashKey: "cash_balance",
    pnlKey: "running_pnl",
    equityLabel: "Equity",
    cashLabel: "Cash",
    pnlLabel: "Running PnL",
  });
}

function renderLiveAccountHistoryChart(snapshots) {
  renderAccountHistoryChart({
    snapshots,
    chartEl: liveAccountChart,
    summaryEl: liveAccountChartSummary,
    emptyText: "Live balance snapshots will appear as the bot runs.",
    ariaLabel: "Linked account balance over time",
    equityKey: "equity_estimate_usdc",
    cashKey: "balance_usdc",
    pnlKey: "realized_pnl_usdc",
    equityLabel: "Estimate",
    cashLabel: "Balance",
    pnlLabel: "Realized PnL",
  });
}

function renderAccountHistoryChart({ snapshots, chartEl, summaryEl, emptyText, ariaLabel, equityKey, cashKey, pnlKey, equityLabel, cashLabel, pnlLabel }) {
  if (!chartEl || !summaryEl) return;
  if (!snapshots.length) {
    chartEl.innerHTML = `<div class="empty-state">${escapeHtml(emptyText)}</div>`;
    summaryEl.textContent = "No account history yet";
    return;
  }

  const values = snapshots.flatMap((item) => [Number(item[equityKey] || 0), Number(item[cashKey] || 0)]);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const width = 640;
  const height = 220;
  const left = 54;
  const right = 18;
  const top = 18;
  const bottom = 34;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const xFor = (index) => left + (snapshots.length === 1 ? plotWidth : (index / (snapshots.length - 1)) * plotWidth);
  const yFor = (value) => top + plotHeight - ((Number(value || 0) - min) / span) * plotHeight;
  const equityPoints = snapshots.map((item, index) => `${xFor(index).toFixed(1)},${yFor(item[equityKey]).toFixed(1)}`).join(" ");
  const cashPoints = snapshots.map((item, index) => `${xFor(index).toFixed(1)},${yFor(item[cashKey]).toFixed(1)}`).join(" ");
  const first = snapshots[0];
  const last = snapshots[snapshots.length - 1];
  const equityChange = Number(last[equityKey] || 0) - Number(first[equityKey] || 0);
  const runningPnl = Number(last[pnlKey] || 0);

  summaryEl.textContent = `${snapshots.length} snapshots | ${formatSignedUsd(equityChange)} change | ${formatSignedUsd(runningPnl)} PnL`;
  chartEl.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(ariaLabel)}">
      <line class="account-chart-grid" x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}"></line>
      <line class="account-chart-grid" x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}"></line>
      <text x="10" y="${top + 5}">${escapeHtml(formatUsdPrecise(max))}</text>
      <text x="10" y="${height - bottom}">${escapeHtml(formatUsdPrecise(min))}</text>
      <polyline class="cash-stroke" points="${cashPoints}"></polyline>
      <polyline class="equity-stroke" points="${equityPoints}"></polyline>
      <circle class="profit-fill" cx="${xFor(snapshots.length - 1).toFixed(1)}" cy="${yFor(last[equityKey]).toFixed(1)}" r="5"></circle>
      <text x="${left}" y="${height - 10}">${escapeHtml(new Date(first.observed_at).toLocaleTimeString())}</text>
      <text x="${width - right}" y="${height - 10}" text-anchor="end">${escapeHtml(new Date(last.observed_at).toLocaleTimeString())}</text>
    </svg>
    <div class="account-chart-legend">
      <span><i class="legend-dot legend-equity"></i>${escapeHtml(equityLabel)} ${escapeHtml(formatUsdPrecise(last[equityKey]))}</span>
      <span><i class="legend-dot legend-cash"></i>${escapeHtml(cashLabel)} ${escapeHtml(formatUsdPrecise(last[cashKey]))}</span>
      <span>${escapeHtml(pnlLabel)} ${escapeHtml(formatSignedUsd(last[pnlKey]))}</span>
    </div>
  `;
}

function renderDetailStat(label, value, className = "") {
  return `
    <div class="paper-detail-stat">
      <span>${escapeHtml(label)}</span>
      <strong class="${className}">${escapeHtml(value)}</strong>
    </div>
  `;
}

function renderStatusPill(label, enabled) {
  return `
    <div class="paper-detail-stat">
      <span>${escapeHtml(label)}</span>
      <strong class="${enabled ? "profit" : "loss"}">${enabled ? "Configured" : "Missing"}</strong>
    </div>
  `;
}

function formatWallet(value) {
  if (!value) return "-";
  const text = String(value);
  return text.length > 14 ? `${text.slice(0, 8)}...${text.slice(-6)}` : text;
}

async function loadConfig() {
  const response = await fetch("/api/config");
  if (!response.ok) return;
  const config = await response.json();
  limitInput.value = config.scanLimit ?? 50;
  maxMarketsInput.value = Math.min(config.scanLimit ?? 50, 25);
  profitInput.value = config.minProfitBps ?? 10;
}

function switchTab(tabName) {
  activeTabName = tabName;
  document.querySelectorAll(".nav-item[data-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${tabName}Panel`);
  });

  if (tabName === "traders" && !tradersHaveLoaded) {
    loadTraders();
  }
  if (tabName === "smart" && !smartHasLoaded) {
    loadSmartWallets();
  }
  if (tabName === "watchlist") {
    loadWatchlist(false);
  }
  if (tabName === "paper") {
    loadPaperOrders();
  }
  if (tabName === "execution") {
    loadAccountConnection();
    loadAccountStatus();
    loadLiveTrading();
  }
}

async function runScan() {
  scannerHasRun = true;
  setLoading(true);
  statusText.textContent = "Scanning";

  const params = new URLSearchParams({
    limit: limitInput.value || "50",
    maxMarkets: maxMarketsInput.value || "",
    minProfitBps: profitInput.value || "10",
  });

  try {
    const response = await fetch(`/api/scan?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Scanner returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const opportunities = data.opportunities || [];
    const best = opportunities[0]?.net_profit_bps ?? 0;

    opportunityCount.textContent = String(data.opportunityCount ?? opportunities.length);
    bestEdge.textContent = formatBps(best);
    scanTime.textContent = `${data.durationSeconds}s`;
    statusText.textContent = "Complete";
    lastUpdated.textContent = `Last scan: ${new Date(data.finishedAt).toLocaleString()}`;
    renderOpportunities(opportunities);
  } catch (error) {
    statusText.textContent = "Error";
    renderError(error.message || "Scan failed.");
  } finally {
    setLoading(false);
  }
}

async function loadArbitrageAlerts() {
  const response = await fetch("/api/alerts/arbitrage?limit=50");
  if (!response.ok) return;
  const data = await response.json();
  renderArbAlerts(data.alerts || []);
}

async function checkArbitrageAlerts() {
  const response = await fetch("/api/alerts/arbitrage/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      limit: limitInput.value || "50",
      maxMarkets: maxMarketsInput.value || "25",
      minProfitBps: profitInput.value || "10",
    }),
  });
  if (!response.ok) {
    throw new Error(`Arbitrage alert check returned HTTP ${response.status}`);
  }

  const data = await response.json();
  const newAlerts = data.newAlerts || [];
  arbAlertStatus.textContent = `${newAlerts.length} new | ${data.opportunityCount} opportunities checked | ${data.paperOrdersCreated || 0} paper orders`;
  if (newAlerts.length) {
    renderArbAlerts(newAlerts);
    for (const alert of newAlerts) {
      showBrowserNotification("Arbitrage opportunity", `${formatBps(alert.net_profit_bps)} | ${alert.question}`);
    }
    await loadPaperOrders(false);
  } else {
    await loadArbitrageAlerts();
  }
}

async function toggleArbMonitor() {
  if (arbMonitorId) {
    window.clearInterval(arbMonitorId);
    arbMonitorId = null;
    arbMonitorButton.textContent = "Start Arb Alerts";
    arbAlertStatus.textContent = "Monitor stopped";
    return;
  }

  await ensureNotificationPermission();
  arbMonitorButton.textContent = "Stop Arb Alerts";
  arbAlertStatus.textContent = "Monitor running";
  await checkArbitrageAlerts();
  arbMonitorId = window.setInterval(() => {
    checkArbitrageAlerts().catch((error) => {
      arbAlertStatus.textContent = error.message || "Arbitrage monitor error";
    });
  }, monitorIntervalMs);
}

function setTraderLoading(isLoading) {
  traderButton.disabled = isLoading;
  traderButton.textContent = isLoading ? "Loading..." : "Load Traders";
  if (isLoading) {
    traderStatusText.textContent = "Loading";
  }
}

function renderTraders(traders) {
  if (!traders.length) {
    traderResults.innerHTML = `<div class="empty-state">No traders returned for these filters.</div>`;
    return;
  }

  traderResults.innerHTML = traders.map(renderTraderCard).join("");
}

function renderTraderCard(trader) {
  const initials = (trader.username || trader.proxy_wallet || "?").slice(0, 2).toUpperCase();
  const avatar = trader.profile_image
    ? `<img src="${escapeHtml(trader.profile_image)}" alt="">`
    : escapeHtml(initials);
  const xUsername = trader.x_username ? `@${escapeHtml(trader.x_username)}` : "No X linked";
  const trades = trader.recent_trades || [];
  const stats = trader.stats || {};

  return `
    <article class="trader-card">
      <div class="trader-summary">
        <div class="trader-name">
          <div class="avatar">${avatar}</div>
          <div>
            <strong>#${escapeHtml(trader.rank)} ${escapeHtml(trader.username)}</strong>
            <span>${xUsername}${trader.verified_badge ? " | Verified" : ""}</span>
          </div>
        </div>
        <div class="wallet">${escapeHtml(trader.proxy_wallet)}</div>
        <button class="small-button save-wallet-button" type="button"
          data-wallet="${escapeHtml(trader.proxy_wallet)}"
          data-username="${escapeHtml(trader.username)}"
          data-x-username="${escapeHtml(trader.x_username)}"
          data-profile-image="${escapeHtml(trader.profile_image)}"
          data-verified="${trader.verified_badge ? "1" : "0"}">Save Trader</button>
        <div class="trader-stats">
          <div class="stat-box">
            <span>PnL</span>
            <strong class="profit">${formatUsd(trader.pnl)}</strong>
          </div>
          <div class="stat-box">
            <span>Volume</span>
            <strong>${formatUsd(trader.volume)}</strong>
          </div>
          <div class="stat-box">
            <span>Score</span>
            <strong>${Number(stats.consistency_score || 0).toFixed(1)}</strong>
          </div>
          <div class="stat-box">
            <span>Win rate</span>
            <strong>${formatPercent(stats.win_rate)}</strong>
          </div>
          <div class="stat-box">
            <span>Closed W/L</span>
            <strong>${Number(stats.winning_positions || 0)} / ${Number(stats.losing_positions || 0)}</strong>
          </div>
          <div class="stat-box">
            <span>Active days</span>
            <strong>${Number(stats.active_days || 0)}</strong>
          </div>
        </div>
      </div>
      <div class="trade-list">
        ${
          trades.length
            ? trades.map(renderTradeRow).join("")
            : `<div class="empty-state">No recent trades returned for this wallet.</div>`
        }
      </div>
    </article>
  `;
}

function renderTradeRow(trade) {
  const sideClass = trade.side === "SELL" ? "side-sell" : "side-buy";
  return `
    <div class="trade-row">
      <div>
        <span class="${sideClass}">${escapeHtml(trade.side || "-")}</span>
        <div class="trade-meta">${formatDate(trade.timestamp)}</div>
      </div>
      <div class="trade-title">
        <strong>${escapeHtml(trade.title || "Untitled market")}</strong>
        <span>${escapeHtml(trade.outcome || "-")} | ${escapeHtml(trade.slug || "")}</span>
        <div class="trade-hash">${escapeHtml(trade.transaction_hash || "")}</div>
      </div>
      <div>
        <strong>${formatUsd(trade.usdc_size)}</strong>
        <div class="trade-meta">${formatMoney(trade.size)} shares</div>
      </div>
      <div>
        <strong>${formatMoney(trade.price)}</strong>
        <div class="trade-meta">price</div>
      </div>
    </div>
  `;
}

async function loadTraders() {
  tradersHaveLoaded = true;
  setTraderLoading(true);

  const params = new URLSearchParams({
    category: categoryInput.value || "OVERALL",
    timePeriod: periodInput.value || "DAY",
    orderBy: orderInput.value || "PNL",
    limit: traderLimitInput.value || "10",
    tradesPerTrader: tradesPerTraderInput.value || "5",
    closedPositionsPerTrader: closedPositionsInput.value || "50",
    minWinRate: String(Number(minWinRateInput.value || 0) / 100),
    minClosedPositions: minClosedInput.value || "10",
    minRecentTrades: minRecentTradesInput.value || "3",
  });

  if (orderInput.value === "CONSISTENCY") {
    params.set("orderBy", "PNL");
    params.set("rankBy", "CONSISTENCY");
  }

  try {
    const response = await fetch(`/api/traders?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Trader tracker returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const traders = data.traders || [];
    traderCount.textContent = String(data.traderCount ?? traders.length);
    topScore.textContent = Number(traders[0]?.stats?.consistency_score ?? 0).toFixed(1);
    traderLoadTime.textContent = `${data.durationSeconds}s`;
    traderStatusText.textContent = "Complete";
    traderLastUpdated.textContent = `Last load: ${new Date(data.finishedAt).toLocaleString()}`;
    renderTraders(traders);
  } catch (error) {
    traderStatusText.textContent = "Error";
    renderTraderError(error.message || "Trader load failed.");
  } finally {
    setTraderLoading(false);
  }
}

function setSmartLoading(isLoading, label = "Working") {
  smartIngestButton.disabled = isLoading;
  smartLoadButton.disabled = isLoading;
  if (isLoading) {
    smartStatusText.textContent = label;
  }
  smartIngestButton.textContent = isLoading ? "Updating..." : "Update Memory";
  smartLoadButton.textContent = isLoading ? "Loading..." : "Rank Wallets";
}

async function ingestSmartWallets() {
  smartHasIngested = true;
  setSmartLoading(true, "Updating");

  try {
    const response = await fetch("/api/smart-wallets/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: smartCategoryInput.value || "OVERALL",
        timePeriod: smartPeriodInput.value || "MONTH",
        orderBy: "PNL",
        candidateLimit: candidateLimitInput.value || "25",
        tradesPerWallet: smartTradesInput.value || "25",
        closedPositionsPerWallet: smartPositionsInput.value || "50",
        markoutTradesPerWallet: markoutTradesInput.value || "5",
      }),
    });
    if (!response.ok) {
      throw new Error(`Smart wallet ingest returned HTTP ${response.status}`);
    }

    const data = await response.json();
    smartStatusText.textContent = "Updated";
    smartUpdateStat.textContent = `${data.walletsSeen} wallets`;
    smartLastUpdated.textContent = `Memory update: ${data.walletsSeen} wallets, ${data.tradesSeen} trades, ${data.closedPositionsSeen} positions`;
    await loadSmartWallets();
  } catch (error) {
    smartStatusText.textContent = "Error";
    renderSmartError(error.message || "Smart wallet ingest failed.");
  } finally {
    setSmartLoading(false);
  }
}

async function loadSmartWallets() {
  smartHasLoaded = true;
  setSmartLoading(true, "Ranking");

  const params = new URLSearchParams({
    category: smartCategoryInput.value || "OVERALL",
    timePeriod: smartPeriodInput.value || "MONTH",
    limit: "25",
    minTrades: smartMinTradesInput.value || "10",
    minClosedPositions: smartMinClosedInput.value || "10",
    minWinRate: String(Number(smartMinWinRateInput.value || 0) / 100),
    minAverageMarkout: "-1",
  });

  try {
    const response = await fetch(`/api/smart-wallets?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Smart wallet ranking returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const wallets = data.wallets || [];
    smartWalletCount.textContent = String(data.walletCount ?? wallets.length);
    smartTopScore.textContent = Number(wallets[0]?.insider_score ?? 0).toFixed(1);
    smartStatusText.textContent = "Complete";
    smartLastUpdated.textContent = `Ranked: ${new Date(data.finishedAt).toLocaleString()}`;
    renderSmartWallets(wallets);
  } catch (error) {
    smartStatusText.textContent = "Error";
    renderSmartError(error.message || "Smart wallet ranking failed.");
  } finally {
    setSmartLoading(false);
  }
}

async function refreshSmartForFilterChange(shouldIngest = false) {
  if (shouldIngest) {
    await ingestSmartWallets();
    return;
  }

  if (smartHasLoaded || smartHasIngested) {
    await loadSmartWallets();
  }
}

function renderSmartWallets(wallets) {
  if (!wallets.length) {
    smartResults.innerHTML = `<div class="empty-state">No wallets match the current filters yet. Update memory or loosen filters.</div>`;
    return;
  }

  smartResults.innerHTML = wallets.map(renderSmartWalletCard).join("");
}

function renderSmartWalletCard(wallet) {
  const initials = (wallet.username || wallet.proxy_wallet || "?").slice(0, 2).toUpperCase();
  const avatar = wallet.profile_image
    ? `<img src="${escapeHtml(wallet.profile_image)}" alt="">`
    : escapeHtml(initials);
  const xUsername = wallet.x_username ? `@${escapeHtml(wallet.x_username)}` : "No X linked";
  const trades = wallet.recent_trades || [];
  const reasons = wallet.reasons || [];

  return `
    <article class="trader-card">
      <div class="trader-summary">
        <div class="trader-name">
          <div class="avatar">${avatar}</div>
          <div>
            <strong>${escapeHtml(wallet.username || wallet.proxy_wallet)}</strong>
            <span>${xUsername}${wallet.verified_badge ? " | Verified" : ""}</span>
          </div>
        </div>
        <div class="wallet">${escapeHtml(wallet.proxy_wallet)}</div>
        <button class="small-button save-wallet-button" type="button"
          data-wallet="${escapeHtml(wallet.proxy_wallet)}"
          data-username="${escapeHtml(wallet.username)}"
          data-x-username="${escapeHtml(wallet.x_username)}"
          data-profile-image="${escapeHtml(wallet.profile_image)}"
          data-verified="${wallet.verified_badge ? "1" : "0"}">Save Trader</button>
        <div class="trader-stats">
          <div class="stat-box">
            <span>Signal score</span>
            <strong>${Number(wallet.insider_score || 0).toFixed(1)}</strong>
          </div>
          <div class="stat-box">
            <span>Win rate</span>
            <strong>${formatPercent(wallet.win_rate)}</strong>
          </div>
          <div class="stat-box">
            <span>Realized PnL</span>
            <strong class="profit">${formatUsd(wallet.total_realized_pnl)}</strong>
          </div>
          <div class="stat-box">
            <span>Avg markout</span>
            <strong>${formatMoney(wallet.average_markout)}</strong>
          </div>
          <div class="stat-box">
            <span>Observed trades</span>
            <strong>${Number(wallet.observed_trade_count || 0)}</strong>
          </div>
          <div class="stat-box">
            <span>Closed W/L</span>
            <strong>${Number(wallet.winning_positions || 0)} / ${Number(wallet.losing_positions || 0)}</strong>
          </div>
        </div>
        <ul class="reason-list">
          ${reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}
        </ul>
      </div>
      <div class="trade-list">
        ${
          trades.length
            ? trades.map(renderTradeRow).join("")
            : `<div class="empty-state">No stored recent trades for this wallet yet.</div>`
        }
      </div>
    </article>
  `;
}

async function saveWalletFromButton(button) {
  const payload = {
    proxyWallet: button.dataset.wallet,
    username: button.dataset.username || "",
    xUsername: button.dataset.xUsername || "",
    profileImage: button.dataset.profileImage || "",
    verifiedBadge: button.dataset.verified === "1",
    label: button.dataset.username || button.dataset.wallet,
  };

  button.disabled = true;
  const oldText = button.textContent;
  button.textContent = "Saving...";
  try {
    const response = await fetch("/api/watchlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Save returned HTTP ${response.status}`);
    }
    button.textContent = "Saved";
    await loadWatchlist(false);
  } catch (error) {
    button.textContent = "Save failed";
  } finally {
    setTimeout(() => {
      button.disabled = false;
      button.textContent = oldText;
    }, 1200);
  }
}

async function loadWatchlist(showLoading = true) {
  if (showLoading) {
    watchlistLoadButton.disabled = true;
    watchlistLoadButton.textContent = "Loading...";
    watchlistStatusText.textContent = "Loading";
  }

  try {
    const response = await fetch("/api/watchlist");
    if (!response.ok) {
      throw new Error(`Watchlist returned HTTP ${response.status}`);
    }
    const data = await response.json();
    const wallets = data.wallets || [];
    watchlistCount.textContent = String(data.walletCount ?? wallets.length);
    watchlistStatusText.textContent = "Complete";
    watchlistLastLoad.textContent = new Date().toLocaleTimeString();
    renderWatchlist(wallets);
    await loadWatchlistAlerts();
  } catch (error) {
    watchlistStatusText.textContent = "Error";
    renderWatchlistError(error.message || "Watchlist load failed.");
  } finally {
    watchlistLoadButton.disabled = false;
    watchlistLoadButton.textContent = "Load Watchlist";
  }
}

async function refreshWatchlistTrades() {
  if (traderMonitorRefreshInFlight) {
    return;
  }
  traderMonitorRefreshInFlight = true;
  watchlistRefreshButton.disabled = true;
  watchlistRefreshButton.textContent = "Refreshing...";
  watchlistStatusText.textContent = "Refreshing";

  try {
    const response = await fetch("/api/watchlist/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tradesPerWallet: 20 }),
    });
    if (!response.ok) {
      throw new Error(`Watchlist refresh returned HTTP ${response.status}`);
    }
    const data = await response.json();
    watchlistStatusText.textContent = "Complete";
    watchlistAlertStatus.textContent = `${data.newAlerts} new alerts from ${data.walletsChecked} wallets`;
    if (data.copytradeAutostops > 0) {
      showBrowserNotification("Copytrade autostopped", `${data.copytradeAutostops} trader copytrade setting${data.copytradeAutostops === 1 ? "" : "s"} turned off because paper cash was too low.`);
      watchlistAlertStatus.textContent += ` | ${data.copytradeAutostops} autostopped`;
      await loadCopytradeSettings();
    }
    if (data.newAlerts > 0) {
      const paperText = data.paperOrdersCreated ? `, ${data.paperOrdersCreated} paper order${data.paperOrdersCreated === 1 ? "" : "s"}` : "";
      showBrowserNotification("Saved trader activity", `${data.newAlerts} new trade alert${data.newAlerts === 1 ? "" : "s"}${paperText}`);
    }
    await loadWatchlist(false);
    await loadWatchlistAlerts();
    await loadPaperOrders(false);
  } catch (error) {
    watchlistStatusText.textContent = "Error";
    watchlistAlertStatus.textContent = error.message || "Refresh failed.";
  } finally {
    traderMonitorRefreshInFlight = false;
    watchlistRefreshButton.disabled = false;
    watchlistRefreshButton.textContent = "Refresh Trades";
  }
}

async function startTraderMonitor(requestNotifications = false) {
  if (traderMonitorId) {
    return;
  }

  if (requestNotifications) {
    await ensureNotificationPermission();
  }
  traderMonitorButton.textContent = "Trade Alerts On";
  watchlistAlertStatus.textContent = "Trade monitor running";
  await refreshWatchlistTrades();
  traderMonitorId = window.setInterval(() => {
    refreshWatchlistTrades().catch((error) => {
      watchlistAlertStatus.textContent = error.message || "Trade monitor error";
    });
  }, monitorIntervalMs);
}

async function handleTraderMonitorButton() {
  await startTraderMonitor(true);
  await refreshWatchlistTrades();
}

async function loadWatchlistMonitorStatus() {
  const response = await fetch("/api/watchlist/monitor");
  if (!response.ok) return;
  const data = await response.json();
  traderMonitorButton.textContent = data.running ? "Trade Alerts On" : "Start Trade Alerts";
  if (data.lastError) {
    watchlistAlertStatus.textContent = data.lastError;
  } else if (data.lastRunAt) {
    const result = data.lastResult || {};
    watchlistAlertStatus.textContent = `${Number(result.newAlerts || 0)} new alerts from ${Number(result.walletsChecked || 0)} wallets`;
  }
}

async function loadWatchlistAlerts() {
  const response = await fetch("/api/watchlist/alerts?limit=50");
  if (!response.ok) return;
  const data = await response.json();
  renderWatchlistAlerts(data.alerts || []);
}

function renderWatchlistAlerts(alerts) {
  if (!alerts.length) {
    watchlistAlerts.innerHTML = `<div class="empty-state">No saved-wallet trade alerts yet.</div>`;
    return;
  }

  watchlistAlerts.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-row">
          <div>
            <strong>${escapeHtml(alert.username || alert.proxy_wallet)}</strong>
            <div class="trade-meta">${formatDate(alert.trade_timestamp)}</div>
          </div>
          <div class="trade-title">
            <strong>${escapeHtml(alert.title || "Untitled market")}</strong>
            <span>${escapeHtml(alert.outcome || "-")}</span>
          </div>
          <div>
            <span class="${alert.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(alert.side || "-")}</span>
            <div class="trade-meta">${formatUsd(alert.usdc_size)}</div>
          </div>
          <div>
            <strong>${formatMoney(alert.price)}</strong>
            <div class="trade-meta">price</div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderWatchlist(wallets) {
  if (!wallets.length) {
    watchlistResults.innerHTML = `<div class="empty-state">No saved traders yet.</div>`;
    return;
  }

  watchlistResults.innerHTML = wallets.map(renderWatchlistCard).join("");
}

function renderWatchlistCard(item) {
  const wallet = item.smart_wallet || {};
  const username = item.username || wallet.username || item.proxy_wallet;
  const profileImage = item.profile_image || wallet.profile_image || "";
  const initials = (username || item.proxy_wallet || "?").slice(0, 2).toUpperCase();
  const avatar = profileImage ? `<img src="${escapeHtml(profileImage)}" alt="">` : escapeHtml(initials);
  const trades = wallet.recent_trades || [];
  const reasons = wallet.reasons || [];
  const alertsEnabled = item.alerts_enabled !== false;
  const copySetting = copytradeSettings[(item.proxy_wallet || "").toLowerCase()] || {};
  const copyEnabled = copySetting.enabled === true;

  return `
    <article class="trader-card">
      <div class="trader-summary">
        <div class="trader-name">
          <div class="avatar">${avatar}</div>
          <div>
            <strong>${escapeHtml(username)}</strong>
            <span>Saved ${escapeHtml(item.added_at || "")}</span>
          </div>
        </div>
        <div class="wallet">${escapeHtml(item.proxy_wallet)}</div>
        <button class="small-button danger-button remove-wallet-button" type="button"
          data-wallet="${escapeHtml(item.proxy_wallet)}">Remove</button>
        <button class="small-button toggle-wallet-alerts-button" type="button"
          data-wallet="${escapeHtml(item.proxy_wallet)}"
          data-enabled="${alertsEnabled ? "1" : "0"}">${alertsEnabled ? "Alerts On" : "Alerts Off"}</button>
        <div class="copytrade-controls">
        <button class="small-button toggle-paper-copytrade-button" type="button"
          data-wallet="${escapeHtml(item.proxy_wallet)}"
          data-enabled="${copyEnabled ? "1" : "0"}">${copyEnabled ? "Copytrade On" : "Copytrade Off"}</button>
          <select class="paper-copy-sizing-mode" data-wallet="${escapeHtml(item.proxy_wallet)}">
            <option value="PERCENT" ${copySetting.sizing_mode !== "FIXED" ? "selected" : ""}>Percent</option>
            <option value="FIXED" ${copySetting.sizing_mode === "FIXED" ? "selected" : ""}>Fixed USDC</option>
          </select>
          <input class="paper-copy-size-value" data-wallet="${escapeHtml(item.proxy_wallet)}" type="number" min="0" step="1" placeholder="Size" value="${Number(copySetting.size_value ?? 10)}">
          <input class="paper-copy-max-usdc" data-wallet="${escapeHtml(item.proxy_wallet)}" type="number" min="0" step="1" placeholder="Max USDC" value="${Number(copySetting.max_usdc ?? 100)}">
        </div>
        <div class="trader-stats">
          <div class="stat-box">
            <span>Signal score</span>
            <strong>${Number(wallet.insider_score || 0).toFixed(1)}</strong>
          </div>
          <div class="stat-box">
            <span>Win rate</span>
            <strong>${formatPercent(wallet.win_rate)}</strong>
          </div>
          <div class="stat-box">
            <span>Realized PnL</span>
            <strong class="profit">${formatUsd(wallet.total_realized_pnl)}</strong>
          </div>
          <div class="stat-box">
            <span>Observed trades</span>
            <strong>${Number(wallet.observed_trade_count || 0)}</strong>
          </div>
          <div class="stat-box">
            <span>Closed W/L</span>
            <strong>${Number(wallet.winning_positions || 0)} / ${Number(wallet.losing_positions || 0)}</strong>
          </div>
          <div class="stat-box">
            <span>Avg markout</span>
            <strong>${formatMoney(wallet.average_markout || 0)}</strong>
          </div>
        </div>
        <ul class="reason-list">
          ${reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}
        </ul>
      </div>
      <div class="trade-list">
        ${
          trades.length
            ? trades.map(renderTradeRow).join("")
            : `<div class="empty-state">No stored trades for this saved wallet yet. Run Smart Wallets update to enrich it.</div>`
        }
      </div>
    </article>
  `;
}

async function loadCopytradeSettings() {
  const response = await fetch("/api/paper/copytrade");
  if (!response.ok) return;
  const data = await response.json();
  copytradeSettings = data.settings || {};
}

async function saveCopytradeSettings(wallet, enabled) {
  const mode = getCopySettingValue(wallet, ".paper-copy-sizing-mode", "PERCENT");
  const sizeValue = getCopySettingValue(wallet, ".paper-copy-size-value", "10");
  const maxUsdc = getCopySettingValue(wallet, ".paper-copy-max-usdc", "100");
  const response = await fetch(`/api/paper/copytrade/${encodeURIComponent(wallet)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      enabled,
      sizingMode: mode,
      sizeValue,
      maxUsdc,
    }),
  });
  if (!response.ok) {
    throw new Error(`Copytrade settings returned HTTP ${response.status}`);
  }
  await loadCopytradeSettings();
  await loadWatchlist(false);
}

async function saveLiveCopytradeSettings(wallet, enabled) {
  const mode = getCopySettingValue(wallet, ".live-copy-sizing-mode", "PERCENT");
  const sizeValue = getCopySettingValue(wallet, ".live-copy-size-value", "10");
  const maxUsdc = getCopySettingValue(wallet, ".live-copy-max-usdc", "100");
  const response = await fetch(`/api/live/copytrade/${encodeURIComponent(wallet)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      enabled,
      sizingMode: mode,
      sizeValue,
      maxUsdc,
    }),
  });
  if (!response.ok) {
    throw new Error(`Live copytrade settings returned HTTP ${response.status}`);
  }
  await loadLiveTrading();
}

function getCopySettingValue(wallet, selector, fallback) {
  const escapedWallet = CSS.escape(wallet);
  const controls = Array.from(document.querySelectorAll(`${selector}[data-wallet="${escapedWallet}"]`));
  const activeControl = controls.find((control) => control.offsetParent !== null) || controls[0];
  return activeControl?.value || fallback;
}

async function toggleCopytrade(button) {
  const wallet = button.dataset.wallet;
  const nextEnabled = button.dataset.enabled !== "1";
  button.disabled = true;
  button.textContent = nextEnabled ? "Turning on..." : "Turning off...";
  try {
    await saveCopytradeSettings(wallet, nextEnabled);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Toggle failed";
  }
}

async function toggleLiveCopytrade(button) {
  const wallet = button.dataset.wallet;
  const nextEnabled = button.dataset.enabled !== "1";
  button.disabled = true;
  button.textContent = nextEnabled ? "Turning on..." : "Turning off...";
  try {
    await saveLiveCopytradeSettings(wallet, nextEnabled);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Toggle failed";
  }
}

async function loadPaperOrders(showLoading = true) {
  if (showLoading) {
    paperLoadButton.disabled = true;
  }
  try {
    const [accountResponse, activeResponse, closedResponse] = await Promise.all([
      fetch("/api/paper/account"),
      fetch("/api/paper/positions?status=OPEN&limit=100"),
      fetch("/api/paper/positions?status=CLOSED&limit=5000"),
    ]);
    if (!accountResponse.ok || !activeResponse.ok || !closedResponse.ok) {
      throw new Error("Paper portfolio request failed.");
    }
    const account = await accountResponse.json();
    const active = await activeResponse.json();
    const closed = await closedResponse.json();
    renderPaperAccount(account);
    renderPaperActivePositions(active.positions || []);
    renderPaperClosedPositions(closed.positions || []);
    await loadPaperAccountHistory();
    await loadPaperEvents();
    paperLastUpdated.textContent = new Date().toLocaleString();
  } catch (error) {
    paperActiveResults.innerHTML = `<div class="empty-state">${escapeHtml(error.message || "Paper portfolio failed.")}</div>`;
  } finally {
    paperLoadButton.disabled = false;
  }
}

async function loadPaperAccountHistory() {
  const response = await fetch("/api/paper/account/history?limit=500");
  if (!response.ok) return;
  const data = await response.json();
  renderPaperAccountHistoryChart(data.snapshots || []);
}

async function loadPaperEvents() {
  const response = await fetch("/api/paper/events?limit=20");
  if (!response.ok) return;
  const data = await response.json();
  const events = data.events || [];
  paperRiskEvents.textContent = String(data.eventCount || 0);
  for (const event of [...events].reverse()) {
    const id = Number(event.id || 0);
    if (id <= lastSeenPaperEventId) continue;
    if (event.event_type === "COPYTRADE_AUTOSTOP_LOW_BALANCE") {
      showBrowserNotification("Copytrade autostopped", event.message || "Paper cash was too low for a copytrade.");
    }
    lastSeenPaperEventId = Math.max(lastSeenPaperEventId, id);
  }
}

function renderPaperAccount(account) {
  paperBalanceInput.value = Number(account.startingBalance || 1000).toFixed(0);
  paperCashBalance.textContent = formatUsd(account.cashBalance);
  paperActiveCost.textContent = formatUsd(account.activeCost);
  const runningPnl = Number(account.runningPnl || account.realizedPnl || 0);
  paperRunningPnl.textContent = formatUsdPrecise(runningPnl);
  paperRunningPnl.classList.toggle("profit", runningPnl >= 0);
  paperRunningPnl.classList.toggle("loss", runningPnl < 0);
  paperEquity.textContent = formatUsdPrecise(account.equityEstimate);
  paperWinLoss.textContent = `${Number(account.wins || 0)} / ${Number(account.losses || 0)}`;
  paperWinRate.textContent = formatPercent(account.winRate);
  const unpricedText = Number(account.unpricedOpenPositions || 0) > 0 ? ` | ${Number(account.unpricedOpenPositions)} unpriced open` : "";
  paperClosedSummary.textContent = `${Number(account.closedTrades || 0)} closed | ${formatUsdPrecise(account.realizedPnl)} realized PnL${unpricedText}`;
}

function renderPaperActivePositions(positions) {
  const openPositions = positions.filter((position) => position.status === "OPEN");
  if (!openPositions.length) {
    paperActiveResults.innerHTML = `<div class="empty-state">No active paper trades.</div>`;
    return;
  }

  paperActiveResults.innerHTML = openPositions
    .map(
      (position) => {
        const unrealizedPnl = Number(position.unrealized_pnl_usdc || 0);
        const invested = Number(position.cost_usdc || 0);
        const markValue = Number(position.mark_value_usdc || position.cost_usdc || 0);
        const markText = position.mark_price === null || position.mark_price === undefined ? "unpriced" : `mark ${formatMoney(position.mark_price)}`;
        const manualExitPrice = position.mark_price === null || position.mark_price === undefined ? position.entry_price : position.mark_price;
        const closeInputId = `manualClosePrice-${position.id}`;
        const pnlClass = unrealizedPnl >= 0 ? "profit" : "loss";
        return `
        <div class="paper-trade-card" data-expanded="0">
          <div class="alert-row paper-trade-summary" role="button" tabindex="0">
            <div>
              <strong>${escapeHtml(position.strategy)}</strong>
              <div class="trade-meta">${new Date(position.opened_at).toLocaleString()}</div>
            </div>
            <div class="trade-title">
              <strong>${escapeHtml(position.title || "Untitled market")}</strong>
              <span>${escapeHtml(position.outcome || "-")} | ${escapeHtml(position.source_wallet || "")}</span>
            </div>
            <div>
              <span class="${position.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(position.side || "-")}</span>
              <div class="trade-meta">${formatUsdPrecise(invested)} invested</div>
              <strong class="${pnlClass}">${formatSignedUsd(unrealizedPnl)}</strong>
              <div class="trade-meta">open PnL</div>
            </div>
            <div>
              <strong>${formatMoney(position.entry_price)}</strong>
              <div class="trade-meta">${markText}</div>
              <div class="trade-meta">${formatMoney(position.size)} shares</div>
              <button
                class="small-button close-paper-position-button"
                type="button"
                data-position-id="${position.id}"
                data-entry-price="${position.entry_price}"
                data-exit-price="${manualExitPrice}"
              >Manual Close</button>
            </div>
          </div>
          <div class="paper-trade-details">
            <div class="paper-detail-grid">
              ${renderDetailStat("Money invested", formatUsdPrecise(invested))}
              ${renderDetailStat("Current value", formatUsdPrecise(markValue))}
              ${renderDetailStat("Unrealized PnL", formatSignedUsd(unrealizedPnl), pnlClass)}
              ${renderDetailStat("Shares", formatMoney(position.size))}
              ${renderDetailStat("Entry price", formatMoney(position.entry_price))}
              ${renderDetailStat("Observed entry", position.observed_entry_price === null || position.observed_entry_price === undefined ? "-" : formatMoney(position.observed_entry_price))}
              ${renderDetailStat("Entry fee", formatUsdPrecise(position.entry_fee_usdc || 0))}
              ${renderDetailStat("Current mark", position.mark_price === null || position.mark_price === undefined ? "Unpriced" : formatMoney(position.mark_price))}
            </div>
            <div class="manual-close-panel">
              <label>
                <span>Manual exit price</span>
                <input id="${closeInputId}" type="number" min="0" max="1" step="0.0001" value="${formatMoney(manualExitPrice)}">
              </label>
              <button
                class="secondary-button close-paper-position-button"
                type="button"
                data-position-id="${position.id}"
                data-entry-price="${position.entry_price}"
                data-price-input-id="${closeInputId}"
              >Close Trade</button>
            </div>
            ${renderTradeValueGraph({
              startValue: invested,
              endValue: markValue,
              startLabel: "Invested",
              endLabel: position.mark_price === null || position.mark_price === undefined ? "Cost basis" : "Current",
              history: position.mark_history || [],
            })}
          </div>
        </div>
      `;
      }
    )
    .join("");
}

function renderPaperClosedPositions(positions) {
  if (!positions.length) {
    paperClosedResults.innerHTML = `<div class="empty-state">No closed paper trades.</div>`;
    return;
  }

  paperClosedResults.innerHTML = positions
    .map(
      (position) => {
        const pnl = Number(position.pnl_usdc || 0);
        const invested = Number(position.cost_usdc || 0);
        const exitValue = Number(position.exit_value_usdc || 0);
        const pnlClass = pnl >= 0 ? "profit" : "loss";
        return `
        <div class="paper-trade-card" data-expanded="0">
          <div class="paper-finished-row paper-trade-summary" role="button" tabindex="0">
            <div>
              <strong class="paper-money ${pnlClass}">${formatSignedUsd(pnl)}</strong>
              <div class="trade-meta">money made</div>
            </div>
            <div class="trade-title">
              <strong>${escapeHtml(position.title || "Untitled market")}</strong>
              <span>${escapeHtml(position.outcome || "-")} | ${escapeHtml(position.strategy || "-")}</span>
            </div>
            <div>
              <strong>${formatUsdPrecise(exitValue)}</strong>
              <div class="trade-meta">exit value</div>
              <span class="trade-meta">Entry ${formatMoney(position.entry_price)} -> Exit ${formatMoney(position.exit_price)}</span>
            </div>
            <div>
              <strong>${formatMoney(position.size)}</strong>
              <div class="trade-meta">shares</div>
              <div class="trade-meta">${new Date(position.closed_at).toLocaleString()}</div>
            </div>
          </div>
          <div class="paper-trade-details">
            <div class="paper-detail-grid">
              ${renderDetailStat("Money invested", formatUsdPrecise(invested))}
              ${renderDetailStat("Exit value", formatUsdPrecise(exitValue))}
              ${renderDetailStat("Realized PnL", formatSignedUsd(pnl), pnlClass)}
              ${renderDetailStat("Shares", formatMoney(position.size))}
              ${renderDetailStat("Entry price", formatMoney(position.entry_price))}
              ${renderDetailStat("Observed entry", position.observed_entry_price === null || position.observed_entry_price === undefined ? "-" : formatMoney(position.observed_entry_price))}
              ${renderDetailStat("Exit price", formatMoney(position.exit_price))}
              ${renderDetailStat("Observed exit", position.observed_exit_price === null || position.observed_exit_price === undefined ? "-" : formatMoney(position.observed_exit_price))}
              ${renderDetailStat("Fees paid", formatUsdPrecise(Number(position.entry_fee_usdc || 0) + Number(position.exit_fee_usdc || 0)))}
            </div>
            ${renderTradeValueGraph({
              startValue: invested,
              endValue: exitValue,
              startLabel: "Invested",
              endLabel: "Exited",
              history: position.mark_history || [],
            })}
            <div class="paper-close-note">${escapeHtml(position.close_reason || "Closed paper trade")}</div>
          </div>
        </div>
      `;
      }
    )
    .join("");
}

async function loadAccountStatus() {
  if (!accountRefreshButton) return;
  accountRefreshButton.disabled = true;
  accountRefreshButton.textContent = "Refreshing...";
  try {
    const response = await fetch("/api/account/status");
    const data = await parseApiJson(response, "Account status");
    renderAccountStatus(data);
  } catch (error) {
    accountConnectionStatus.textContent = "Error";
    accountConnectionDetails.innerHTML = `<div class="empty-state">${escapeHtml(error.message || "Account status failed.")}</div>`;
  } finally {
    accountRefreshButton.disabled = false;
    accountRefreshButton.textContent = "Refresh Account";
  }
}

async function loadAccountConnection() {
  if (!accountConnectionForm) return;
  try {
    const response = await fetch("/api/account/connection");
    const data = await parseApiJson(response, "Account connection");
    renderAccountConnection(data);
  } catch (error) {
    accountConnectionSaveStatus.textContent = error.message || "Could not load saved connection.";
  }
}

async function parseApiJson(response, label) {
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (error) {
    const hint = text.trim().startsWith("<")
      ? "The app server returned an HTML page instead of JSON. Restart the desktop app/server so the new API routes are loaded."
      : "The app server returned invalid JSON.";
    throw new Error(`${label} failed: ${hint}`);
  }
  if (!response.ok) {
    throw new Error(data.error || `${label} returned HTTP ${response.status}`);
  }
  return data;
}

function renderAccountConnection(data) {
  accountAddressInput.value = data.accountAddress || "";
  accountFunderInput.value = data.funderAddress || "";
  accountSignatureTypeInput.value = data.signatureType || "3";
  accountApiKeyInput.value = "";
  accountApiSecretInput.value = "";
  accountApiPassphraseInput.value = "";
  accountPrivateKeyInput.value = "";
  accountApiKeyInput.placeholder = data.apiKeyConfigured ? `Saved ${data.apiKeyMasked || ""} - leave blank to keep` : "Leave blank to keep saved value";
  accountApiSecretInput.placeholder = data.apiSecretConfigured ? `Saved ${data.apiSecretMasked || ""} - leave blank to keep` : "Leave blank to keep saved value";
  accountApiPassphraseInput.placeholder = data.apiPassphraseConfigured ? `Saved ${data.apiPassphraseMasked || ""} - leave blank to keep` : "Leave blank to keep saved value";
  accountPrivateKeyInput.placeholder = data.privateKeyConfigured ? `Saved ${data.privateKeyMasked || ""} - leave blank to keep` : "Use a separate small bot wallet. Leave blank to keep saved value.";
  accountConnectionSaveStatus.textContent = "Connection values loaded from local .env";
}

function collectAccountConnectionPayload() {
  const funderAddress = accountFunderInput.value.trim();
  const accountAddress = accountAddressInput.value.trim() || funderAddress;
  return {
    accountAddress,
    funderAddress,
    signatureType: accountSignatureTypeInput.value.trim() || "3",
    apiKey: accountApiKeyInput.value.trim(),
    apiSecret: accountApiSecretInput.value.trim(),
    apiPassphrase: accountApiPassphraseInput.value.trim(),
    privateKey: accountPrivateKeyInput.value.trim(),
  };
}

async function saveAccountConnection({ testAfterSave = false } = {}) {
  if (!accountConnectionForm) return;
  saveAccountConnectionButton.disabled = true;
  testAccountConnectionButton.disabled = true;
  deriveAccountCredentialsButton.disabled = true;
  accountConnectionSaveStatus.textContent = "Saving connection...";
  try {
    const response = await fetch("/api/account/connection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectAccountConnectionPayload()),
    });
    const data = await parseApiJson(response, "Save connection");
    renderAccountConnection(data);
    accountConnectionSaveStatus.textContent = testAfterSave ? "Saved. Testing read-only connection..." : "Saved locally.";
    if (testAfterSave) {
      await loadAccountStatus();
      accountConnectionSaveStatus.textContent = "Saved and tested.";
    }
  } catch (error) {
    accountConnectionSaveStatus.textContent = error.message || "Connection save failed.";
  } finally {
    saveAccountConnectionButton.disabled = false;
    testAccountConnectionButton.disabled = false;
    deriveAccountCredentialsButton.disabled = false;
  }
}

async function deriveAccountCredentials() {
  if (!accountConnectionForm) return;
  saveAccountConnectionButton.disabled = true;
  testAccountConnectionButton.disabled = true;
  deriveAccountCredentialsButton.disabled = true;
  accountConnectionSaveStatus.textContent = "Deriving CLOB API credentials...";
  try {
    const response = await fetch("/api/account/derive-credentials", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectAccountConnectionPayload()),
    });
    const data = await parseApiJson(response, "Derive credentials");
    renderAccountConnection(data);
    accountConnectionSaveStatus.textContent = "API credentials derived and saved locally.";
  } catch (error) {
    accountConnectionSaveStatus.textContent = error.message || "Credential derivation failed.";
  } finally {
    saveAccountConnectionButton.disabled = false;
    testAccountConnectionButton.disabled = false;
    deriveAccountCredentialsButton.disabled = false;
  }
}

function renderAccountStatus(data) {
  accountConnectionStatus.textContent = data.accountConfigured ? "Read-only" : "Disconnected";
  accountBalance.textContent = formatOptionalUsd(data.collateralBalanceUsdc);
  accountAllowance.textContent = formatOptionalUsd(data.collateralAllowanceUsdc);
  accountOpenPositions.textContent = String(data.openPositionCount || 0);
  accountRecentTrades.textContent = String(data.recentTradeCount || 0);
  accountLiveTrading.textContent = data.liveTradingEnabled ? "Enabled" : "Disabled";
  accountLastUpdated.textContent = new Date().toLocaleString();

  accountConnectionDetails.innerHTML = `
    <div class="paper-detail-grid">
      ${renderDetailStat("Mode", data.connectionMode || "READ_ONLY")}
      ${renderDetailStat("Account", formatWallet(data.accountAddress))}
      ${renderDetailStat("Signer", data.signerAddress ? formatWallet(data.signerAddress) : "-")}
      ${renderDetailStat("Funder", data.funderAddress ? formatWallet(data.funderAddress) : "-")}
      ${renderDetailStat("Signature type", data.signatureType || "-")}
      ${renderStatusPill("API credentials", data.apiCredentialsConfigured)}
      ${renderStatusPill("Private key", data.privateKeyConfigured)}
      ${renderStatusPill("Authenticated CLOB", data.authenticatedConnected)}
      ${renderDetailStat("USDC / pUSD balance", formatOptionalUsd(data.collateralBalanceUsdc))}
      ${renderDetailStat("USDC / pUSD allowance", formatOptionalUsd(data.collateralAllowanceUsdc))}
      ${renderDetailStat("Trading status", data.tradingBlockedReason || "Live trading disabled", "loss")}
    </div>
  `;

  const errors = data.errors || [];
  const positions = data.positions || [];
  const trades = data.recentTrades || [];
  const closed = data.closedPositions || [];
  const closedPnl = closed.reduce((total, item) => total + Number(item.realized_pnl || 0), 0);
  const openOrders = data.openOrders || [];
  const authenticatedTrades = data.authenticatedTrades || [];
  const balanceAllowance = data.balanceAllowance || {};
  const rawAllowance = balanceAllowance.allowance ?? balanceAllowance.allowances ?? "-";
  accountReadOnlyData.innerHTML = `
    ${errors.length ? `<div class="empty-state">${escapeHtml(errors.join(" | "))}</div>` : ""}
    <div class="account-snapshot-card">
      <div class="account-snapshot-header">
        <div class="trader-name">
          <div class="avatar">RO</div>
          <div>
            <strong>Read-only account snapshot</strong>
            <span>${escapeHtml(formatWallet(data.accountAddress))}</span>
          </div>
        </div>
        <div class="trader-stats">
          <div class="stat-box"><span>Open positions</span><strong>${Number(data.openPositionCount || 0)}</strong></div>
          <div class="stat-box"><span>Closed PnL</span><strong class="${closedPnl >= 0 ? "profit" : "loss"}">${formatSignedUsd(closedPnl)}</strong></div>
          <div class="stat-box"><span>Open orders</span><strong>${Number(openOrders.length || 0)}</strong></div>
          <div class="stat-box"><span>Balance</span><strong>${formatOptionalUsd(data.collateralBalanceUsdc)}</strong></div>
          <div class="stat-box"><span>Allowance</span><strong>${formatOptionalUsd(data.collateralAllowanceUsdc)}</strong></div>
        </div>
      </div>
      <div class="paper-close-note">Raw CLOB collateral: balance ${escapeHtml(String(balanceAllowance.balance ?? "-"))} | allowance ${escapeHtml(typeof rawAllowance === "object" ? JSON.stringify(rawAllowance) : String(rawAllowance))}</div>
      <div class="account-data-sections">
        <div class="account-data-section">
          <h4>Open Orders</h4>
          <div class="account-row-list">
        ${openOrders.slice(0, 8).map((order) => `
          <div class="account-data-row">
            <span class="${order.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(order.side || "ORDER")}</span>
            <div class="trade-title">
              <strong>${escapeHtml(order.market || order.id || "Open order")}</strong>
              <span>${escapeHtml(order.asset_id || order.assetId || order.token_id || "")}</span>
            </div>
            <div><strong>${formatMoney(order.price || 0)}</strong><div class="trade-meta">price</div></div>
            <div><strong>${formatMoney(order.original_size || order.size || 0)}</strong><div class="trade-meta">size</div></div>
          </div>
        `).join("") || `<div class="empty-state">No open orders returned for this account.</div>`}
          </div>
        </div>
        <div class="account-data-section">
          <h4>Open Positions</h4>
          <div class="account-row-list">
        ${positions.slice(0, 20).map((position) => `
          <div class="account-data-row">
            <span class="side-buy">POS</span>
            <div class="trade-title">
              <strong>${escapeHtml(position.title || position.market || position.conditionId || "Open position")}</strong>
              <span>${escapeHtml(position.outcome || position.asset || "")}</span>
            </div>
            <div><strong>${formatMoney(position.size || position.shares || position.amount || 0)}</strong><div class="trade-meta">size</div></div>
            <div><strong>${formatUsdPrecise(position.currentValue || position.value || position.usdcValue || 0)}</strong><div class="trade-meta">value</div></div>
          </div>
        `).join("") || `<div class="empty-state">No open positions returned for this account.</div>`}
          </div>
        </div>
        <div class="account-data-section">
          <h4>Authenticated Trades</h4>
          <div class="account-row-list">
        ${authenticatedTrades.slice(0, 5).map((trade) => `
          <div class="account-data-row">
            <span class="${trade.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(trade.side || "TRADE")}</span>
            <div class="trade-title">
              <strong>${escapeHtml(trade.market || trade.id || "Authenticated trade")}</strong>
              <span>${escapeHtml(trade.asset_id || trade.assetId || "")}</span>
            </div>
            <div><strong>${formatMoney(trade.price || 0)}</strong><div class="trade-meta">price</div></div>
            <div><strong>${formatMoney(trade.size || 0)}</strong><div class="trade-meta">size</div></div>
          </div>
        `).join("") || `<div class="empty-state">No authenticated trades returned for this account.</div>`}
          </div>
        </div>
        <div class="account-data-section">
          <h4>Public Recent Trades</h4>
          <div class="account-row-list">
        ${trades.slice(0, 12).map((trade) => `
          <div class="account-data-row">
            <span class="${trade.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(trade.side || "-")}</span>
            <div class="trade-title">
              <strong>${escapeHtml(trade.title || "Recent trade")}</strong>
              <span>${escapeHtml(trade.outcome || "")}</span>
            </div>
            <div><strong>${formatMoney(trade.price || 0)}</strong><div class="trade-meta">price</div></div>
            <div><strong>${formatUsdPrecise(trade.usdc_size || 0)}</strong><div class="trade-meta">USDC</div></div>
          </div>
        `).join("") || `<div class="empty-state">No public trades returned for this account.</div>`}
          </div>
        </div>
        <div class="account-data-section">
          <h4>Closed Positions</h4>
          <div class="paper-close-note">${Number(data.closedPositionCount || closed.length)} closed positions from linked account | ${formatSignedUsd(closedPnl)} total realized PnL</div>
          <div class="account-row-list">
        ${closed.slice(0, 20).map((item) => `
          <div class="account-data-row">
            <span class="${Number(item.realized_pnl || 0) >= 0 ? "side-buy" : "side-sell"}">CLOSED</span>
            <div class="trade-title">
              <strong>${escapeHtml(item.title || "Closed position")}</strong>
              <span>${escapeHtml(item.outcome || "")} | ${item.timestamp ? new Date(Number(item.timestamp) * 1000).toLocaleString() : ""}</span>
            </div>
            <div><strong>${formatMoney(item.avg_price || 0)}</strong><div class="trade-meta">avg</div></div>
            <div><strong>${formatSignedUsd(item.realized_pnl || 0)}</strong><div class="trade-meta">PnL</div></div>
          </div>
        `).join("") || `<div class="empty-state">No closed positions returned for this account.</div>`}
          </div>
        </div>
      </div>
    </div>
  `;
}

async function loadLiveTrading() {
  if (!liveTradingStatus) return;
  if (liveRefreshInFlight) return;
  liveRefreshInFlight = true;
  try {
    const [settingsResponse, copytradersResponse, positionsResponse, closedPositionsResponse, linkedClosedResponse, ordersResponse] = await Promise.all([
      fetch("/api/live/settings"),
      fetch("/api/live/copytraders"),
      fetch("/api/live/positions?status=OPEN&limit=50"),
      fetch("/api/live/positions?status=CLOSED&limit=200"),
      fetch("/api/live/linked-closed-positions?limit=100"),
      fetch("/api/live/orders?limit=50"),
    ]);
    const settingsData = await parseApiJson(settingsResponse, "Live settings");
    const copytradersData = await parseApiJson(copytradersResponse, "Live copytraders");
    const positionsData = await parseApiJson(positionsResponse, "Live positions");
    const closedPositionsData = await parseApiJson(closedPositionsResponse, "Closed live positions");
    const linkedClosedData = await parseApiJson(linkedClosedResponse, "Linked closed positions");
    const ordersData = await parseApiJson(ordersResponse, "Live orders");
    renderLiveTrading(
      settingsData,
      copytradersData.copytraders || [],
      positionsData.positions || [],
      closedPositionsData.positions || [],
      linkedClosedData,
      ordersData.orders || []
    );
    await loadLiveAccountHistory();
  } catch (error) {
    liveTradingStatus.textContent = error.message || "Live trading status failed.";
  } finally {
    liveRefreshInFlight = false;
  }
}

async function loadLiveAccountHistory() {
  if (!liveAccountChart) return;
  const response = await fetch("/api/live/account/history?limit=500");
  if (!response.ok) return;
  const data = await response.json();
  renderLiveAccountHistoryChart(data.snapshots || []);
}

function renderLiveTrading(data, copytraders, positions, closedPositions, linkedClosedData, orders) {
  const settings = data.settings || {};
  const account = data.account || {};
  const enabled = settings.enabled === true;
  liveTradingStatus.textContent = enabled
    ? "Live copytrading is ARMED. Kill switch is off."
    : "Kill switch is ON. Live trading is stopped.";
  liveModeMetric.textContent = enabled ? "Armed" : "Stopped";
  liveModeMetric.className = enabled ? "profit" : "loss";
  liveBalanceMetric.textContent = formatUsdPrecise(settings.minCashReserveUsdc || 0);
  liveCashReserveMetric.textContent = formatOptionalUsd(account.balanceUsdc);
  liveEquityMetric.textContent = formatOptionalUsd(account.equityEstimateUsdc);
  liveOpenCostMetric.textContent = formatUsdPrecise(account.openCostUsdc || 0);
  liveRealizedMetric.textContent = formatSignedUsd(account.realizedPnlUsdc || 0);
  liveRunningPnlMetric.textContent = formatSignedUsd(account.runningPnlUsdc || 0);
  liveRunningPnlMetric.className = Number(account.runningPnlUsdc || 0) >= 0 ? "profit" : "loss";
  liveArmButton.disabled = enabled;
  liveKillButton.disabled = !enabled;
  renderLiveCopytraders(copytraders);
  loadLiveRiskSettings();

  liveOpenPositions.innerHTML = positions.map((position) => `
    <div class="account-data-row">
      <span class="side-buy">LIVE</span>
      <div class="trade-title">
        <strong>${escapeHtml(position.title || "Live position")}</strong>
        <span>${escapeHtml(position.outcome || "")}</span>
      </div>
      <div><strong>${formatMoney(position.entry_price || 0)}</strong><div class="trade-meta">entry</div></div>
      <div><strong>${formatSignedUsd(position.unrealized_pnl_usdc || 0)}</strong><div class="trade-meta">live PnL</div></div>
    </div>
  `).join("") || `<div class="empty-state">No live positions opened by this bot.</div>`;

  liveClosedPositions.innerHTML = closedPositions.map((position) => {
    const pnl = Number(position.pnl_usdc || 0);
    const feesPaid = Number(position.entry_fee_usdc || 0) + Number(position.exit_fee_usdc || 0);
    return `
    <div class="account-data-row">
      <span class="${pnl >= 0 ? "side-buy" : "side-sell"}">CLOSED</span>
      <div class="trade-title">
        <strong>${escapeHtml(position.title || "Closed live trade")}</strong>
        <span>${escapeHtml(position.outcome || "")} | ${escapeHtml(position.close_reason || "Closed")}</span>
      </div>
      <div><strong>${formatUsdPrecise(position.cost_usdc || 0)}</strong><div class="trade-meta">invested</div></div>
      <div><strong>${formatUsdPrecise(position.exit_value_usdc || 0)}</strong><div class="trade-meta">exit value</div></div>
      <div><strong>${formatUsdPrecise(feesPaid)}</strong><div class="trade-meta">fees paid</div></div>
      <div><strong class="${pnl >= 0 ? "profit" : "loss"}">${formatSignedUsd(pnl)}</strong><div class="trade-meta">${position.closed_at ? new Date(position.closed_at).toLocaleString() : "closed"}</div></div>
    </div>
  `;
  }).join("") || `<div class="empty-state">No closed live trades yet.</div>`;

  const linkedClosed = linkedClosedData.positions || [];
  const linkedPnl = Number(linkedClosedData.realizedPnl || 0);
  linkedClosedSummary.textContent = `${Number(linkedClosedData.positionCount || linkedClosed.length)} linked closed positions | ${formatSignedUsd(linkedPnl)} total realized PnL`;
  linkedClosedSummary.className = `paper-close-note ${linkedPnl >= 0 ? "profit" : "loss"}`;
  linkedClosedPositions.innerHTML = linkedClosed.map((position) => {
    const pnl = Number(position.realized_pnl || 0);
    return `
      <div class="account-data-row">
        <span class="${pnl >= 0 ? "side-buy" : "side-sell"}">CLOSED</span>
        <div class="trade-title">
          <strong>${escapeHtml(position.title || "Linked closed position")}</strong>
          <span>${escapeHtml(position.outcome || "")} | ${position.timestamp ? new Date(Number(position.timestamp) * 1000).toLocaleString() : ""}</span>
        </div>
        <div><strong>${formatMoney(position.avg_price || 0)}</strong><div class="trade-meta">avg</div></div>
        <div><strong>${formatMoney(position.total_bought || 0)}</strong><div class="trade-meta">bought</div></div>
        <div><strong class="${pnl >= 0 ? "profit" : "loss"}">${formatSignedUsd(pnl)}</strong><div class="trade-meta">PnL</div></div>
      </div>
    `;
  }).join("") || `<div class="empty-state">No linked closed positions returned.</div>`;

  liveOrderLog.innerHTML = orders.map((order) => `
    <div class="account-data-row">
      <span class="${order.side === "SELL" ? "side-sell" : "side-buy"}">${escapeHtml(order.side || "LIVE")}</span>
      <div class="trade-title">
        <strong>${escapeHtml(order.title || "Live order")}</strong>
        <span>${escapeHtml(order.status || "")} | ${escapeHtml(order.reason || "")}</span>
      </div>
      <div><strong>${formatMoney(order.limit_price || 0)}</strong><div class="trade-meta">limit</div></div>
      <div><strong>${formatUsdPrecise(order.requested_usdc || 0)}</strong><div class="trade-meta">USDC</div></div>
    </div>
  `).join("") || `<div class="empty-state">Live copy orders will appear here after you give go.</div>`;
}

async function loadLiveRiskSettings() {
  if (!liveCapitalModeInput) return;
  if (liveRiskSettingsDirty || liveRiskSettingsSaving) return;
  const response = await fetch("/api/live/settings");
  if (!response.ok) return;
  const data = await response.json();
  const settings = data.settings || {};
  if (liveRiskSettingsDirty || liveRiskSettingsSaving) return;
  liveCapitalModeInput.value = settings.copytradeCapitalMode || "CONSERVATIVE";
  liveMinCashReserveInput.value = Number(settings.minCashReserveUsdc || 0).toFixed(0);
  liveMinTradeInput.value = Number(settings.minTradeUsdc || 1).toFixed(0);
  liveMaxChaseInput.value = Number(settings.maxChaseBps || 0).toFixed(0);
}

async function saveLiveRiskSettings() {
  if (!liveSaveRiskButton) return;
  liveSaveRiskButton.disabled = true;
  liveRiskSettingsSaving = true;
  liveTradingStatus.textContent = "Saving live risk settings...";
  try {
    const currentResponse = await fetch("/api/live/settings");
    const current = currentResponse.ok ? await currentResponse.json() : {};
    const currentSettings = current.settings || {};
    const response = await fetch("/api/live/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        entrySlippageBps: currentSettings.entrySlippageBps ?? "25",
        exitSlippageBps: currentSettings.exitSlippageBps ?? "25",
        maxChaseBps: liveMaxChaseInput.value || "0",
        copytradeCapitalMode: liveCapitalModeInput.value || "CONSERVATIVE",
        minCashReserveUsdc: liveMinCashReserveInput.value || "0",
        minTradeUsdc: liveMinTradeInput.value || "1",
      }),
    });
    const saved = await parseApiJson(response, "Save live risk");
    const savedSettings = saved.settings || {};
    liveCapitalModeInput.value = savedSettings.copytradeCapitalMode || liveCapitalModeInput.value || "CONSERVATIVE";
    liveMinCashReserveInput.value = Number(savedSettings.minCashReserveUsdc ?? liveMinCashReserveInput.value ?? 0).toFixed(0);
    liveMinTradeInput.value = Number(savedSettings.minTradeUsdc ?? liveMinTradeInput.value ?? 1).toFixed(0);
    liveMaxChaseInput.value = Number(savedSettings.maxChaseBps ?? liveMaxChaseInput.value ?? 0).toFixed(0);
    liveRiskSettingsDirty = false;
    await loadLiveTrading();
    liveTradingStatus.textContent = "Live risk settings saved.";
  } catch (error) {
    liveTradingStatus.textContent = error.message || "Live risk settings failed.";
  } finally {
    liveRiskSettingsSaving = false;
    liveSaveRiskButton.disabled = false;
  }
}

function renderLiveCopytraders(copytraders) {
  if (!liveCopytraderList) return;
  liveCopytradeSettings = {};
  if (!copytraders.length) {
    liveCopytraderList.innerHTML = `<div class="empty-state">No saved traders yet. Add traders to the Watchlist first.</div>`;
    return;
  }
  liveCopytraderList.innerHTML = copytraders.map((item) => {
    const setting = item.copytrade || {};
    const wallet = item.proxy_wallet || "";
    liveCopytradeSettings[wallet.toLowerCase()] = setting;
    const enabled = setting.enabled === true;
    const username = item.username || wallet;
    return `
      <div class="live-copytrader-row">
        <div class="trader-name">
          <div class="avatar">${escapeHtml((username || "?").slice(0, 2).toUpperCase())}</div>
          <div>
            <strong>${escapeHtml(username)}</strong>
            <span>${escapeHtml(formatWallet(wallet))}</span>
          </div>
        </div>
        <button class="small-button toggle-live-copytrade-button" type="button"
          data-wallet="${escapeHtml(wallet)}"
          data-enabled="${enabled ? "1" : "0"}">${enabled ? "Live Copy On" : "Live Copy Off"}</button>
        <select class="live-copy-sizing-mode" data-wallet="${escapeHtml(wallet)}">
          <option value="PERCENT" ${setting.sizing_mode !== "FIXED" ? "selected" : ""}>Percent</option>
          <option value="FIXED" ${setting.sizing_mode === "FIXED" ? "selected" : ""}>Fixed USDC</option>
        </select>
        <input class="live-copy-size-value" data-wallet="${escapeHtml(wallet)}" type="number" min="0" step="1" value="${Number(setting.size_value ?? 10)}">
        <input class="live-copy-max-usdc" data-wallet="${escapeHtml(wallet)}" type="number" min="0" step="1" value="${Number(setting.max_usdc ?? 100)}">
        <div class="${enabled ? "profit" : "loss"}">${enabled ? "Eligible for live copy" : "Not copied"}</div>
      </div>
    `;
  }).join("");
}

async function setLiveTradingEnabled(enabled) {
  if (!liveTradingStatus) return;
  liveTradingStatus.textContent = enabled ? "Arming live copytrading..." : "Stopping live copytrading...";
  liveArmButton.disabled = true;
  liveKillButton.disabled = true;
  try {
    const response = await fetch(enabled ? "/api/live/settings" : "/api/live/kill-switch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    });
    await parseApiJson(response, enabled ? "Arm live trading" : "Kill switch");
    await loadLiveTrading();
  } catch (error) {
    liveTradingStatus.textContent = error.message || "Live trading update failed.";
    liveArmButton.disabled = false;
    liveKillButton.disabled = false;
  }
}

function switchPaperTab(tabName) {
  paperTabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.paperTab === tabName);
  });
  paperSubpanels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === `paper${tabName[0].toUpperCase()}${tabName.slice(1)}Panel`);
  });
}

function switchLiveTab(tabName) {
  liveTabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.liveTab === tabName);
  });
  liveSubpanels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === `live${tabName === "open" ? "Open" : "Closed"}Panel`);
  });
}

async function savePaperBalance() {
  paperSaveBalanceButton.disabled = true;
  try {
    const response = await fetch("/api/paper/account/balance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ balance: paperBalanceInput.value || "1000" }),
    });
    if (!response.ok) {
      throw new Error(`Balance update returned HTTP ${response.status}`);
    }
    await loadPaperOrders(false);
  } finally {
    paperSaveBalanceButton.disabled = false;
  }
}

async function resetPaperAccount() {
  const confirmed = window.confirm(
    "Reset paper trading? This clears paper positions, orders, charts and events, restores starting balance, and turns off copytrading for every trader."
  );
  if (!confirmed) return;

  paperResetButton.disabled = true;
  paperResetButton.textContent = "Resetting...";
  try {
    const response = await fetch("/api/paper/reset", { method: "POST" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || `Reset returned HTTP ${response.status}`);
    }
    lastSeenPaperEventId = 0;
    paperLastUpdated.textContent = `Reset complete | ${formatUsdPrecise(data.cashBalance || 0)} cash`;
    await loadCopytradeSettings();
    await loadWatchlist(false);
    await loadPaperOrders(false);
  } catch (error) {
    paperLastUpdated.textContent = error.message || "Paper reset failed.";
  } finally {
    paperResetButton.disabled = false;
    paperResetButton.textContent = "Reset Paper";
  }
}

async function loadPaperExecutionSettings() {
  const response = await fetch("/api/paper/execution-settings");
  if (!response.ok) return;
  const settings = await response.json();
  paperEntrySlippageInput.value = Number(settings.entrySlippageBps || 0).toFixed(0);
  paperExitSlippageInput.value = Number(settings.exitSlippageBps || 0).toFixed(0);
  paperFeeInput.value = Number(settings.feeBps || 0).toFixed(0);
  paperMaxChaseInput.value = Number(settings.maxChaseBps || 0).toFixed(0);
  paperCapitalModeInput.value = settings.copytradeCapitalMode || "CONSERVATIVE";
  paperMinCashReserveInput.value = Number(settings.minCashReserveUsdc || 0).toFixed(0);
  paperExecutionStatus.textContent = `${paperCapitalModeInput.value.toLowerCase()} | Reserve ${formatUsdPrecise(settings.minCashReserveUsdc || 0)} | Entry ${formatBps(settings.entrySlippageBps || 0)} | Exit ${formatBps(settings.exitSlippageBps || 0)} | Fee ${formatBps(settings.feeBps || 0)}`;
}

async function savePaperExecutionSettings() {
  paperSaveExecutionButton.disabled = true;
  paperExecutionStatus.textContent = "Saving assumptions...";
  try {
    const response = await fetch("/api/paper/execution-settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        entrySlippageBps: paperEntrySlippageInput.value || "0",
        exitSlippageBps: paperExitSlippageInput.value || "0",
        feeBps: paperFeeInput.value || "0",
        maxChaseBps: paperMaxChaseInput.value || "0",
        copytradeCapitalMode: paperCapitalModeInput.value || "CONSERVATIVE",
        minCashReserveUsdc: paperMinCashReserveInput.value || "0",
      }),
    });
    if (!response.ok) {
      throw new Error(`Execution settings returned HTTP ${response.status}`);
    }
    const data = await response.json();
    const enforcement = data.cashReserveEnforcement || {};
    await loadPaperExecutionSettings();
    if (Number(enforcement.closedPositionCount || 0) > 0) {
      paperExecutionStatus.textContent = `Reserve restored: auto-closed ${Number(enforcement.closedPositionCount)} position${Number(enforcement.closedPositionCount) === 1 ? "" : "s"} | Cash ${formatUsdPrecise(enforcement.cashBalance || 0)}`;
      await loadPaperOrders(false);
      await loadPaperAccountHistory();
    } else if (Number(enforcement.remainingShortfall || 0) > 0) {
      paperExecutionStatus.textContent = `Reserve still short by ${formatUsdPrecise(enforcement.remainingShortfall || 0)} after auto-close check.`;
      await loadPaperOrders(false);
    }
  } catch (error) {
    paperExecutionStatus.textContent = error.message || "Execution settings failed.";
  } finally {
    paperSaveExecutionButton.disabled = false;
  }
}

async function reconcilePaperPositions() {
  paperReconcileButton.disabled = true;
  paperReconcileButton.textContent = "Settling...";
  try {
    const response = await fetch("/api/paper/reconcile", { method: "POST" });
    if (!response.ok) {
      throw new Error(`Settlement check returned HTTP ${response.status}`);
    }
    const data = await response.json();
    paperClosedSummary.textContent = `${Number(data.settledPositions || 0)} settled | ${formatUsd(data.realizedPnl)} PnL`;
    await loadPaperOrders(false);
  } catch (error) {
    paperClosedSummary.textContent = error.message || "Settlement check failed.";
  } finally {
    paperReconcileButton.disabled = false;
    paperReconcileButton.textContent = "Settle Ended";
  }
}

async function closePaperPosition(button) {
  const positionId = button.dataset.positionId;
  const input = button.dataset.priceInputId ? document.getElementById(button.dataset.priceInputId) : null;
  const exitPrice = input?.value || button.dataset.exitPrice || button.dataset.entryPrice || "1";
  const parsedExitPrice = Number(exitPrice);
  if (!Number.isFinite(parsedExitPrice) || parsedExitPrice < 0 || parsedExitPrice > 1) {
    paperLastUpdated.textContent = "Manual close failed: exit price must be between 0 and 1.";
    return;
  }
  button.disabled = true;
  button.textContent = "Closing...";
  try {
    const response = await fetch(`/api/paper/positions/${encodeURIComponent(positionId)}/close`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exitPrice, reason: "Manual close" }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || `Close returned HTTP ${response.status}`);
    }
    if (data.closed === false) {
      throw new Error(data.reason || "Position was not closed.");
    }
    paperLastUpdated.textContent = `Manual close saved | ${formatSignedUsd(data.pnlUsdc || 0)} PnL`;
    await loadPaperOrders(false);
  } catch (error) {
    paperLastUpdated.textContent = error.message || "Manual close failed.";
  } finally {
    button.disabled = false;
    button.textContent = "Close";
  }
}

async function removeWatchlistWallet(button) {
  const wallet = button.dataset.wallet;
  button.disabled = true;
  button.textContent = "Removing...";
  try {
    const response = await fetch(`/api/watchlist/${encodeURIComponent(wallet)}`, { method: "DELETE" });
    if (!response.ok) {
      throw new Error(`Remove returned HTTP ${response.status}`);
    }
    await loadWatchlist(false);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Remove failed";
  }
}

async function toggleWalletAlerts(button) {
  const wallet = button.dataset.wallet;
  const currentlyEnabled = button.dataset.enabled === "1";
  const nextEnabled = !currentlyEnabled;

  button.disabled = true;
  button.textContent = nextEnabled ? "Turning on..." : "Turning off...";
  try {
    const response = await fetch(`/api/watchlist/${encodeURIComponent(wallet)}/alerts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: nextEnabled }),
    });
    if (!response.ok) {
      throw new Error(`Alert toggle returned HTTP ${response.status}`);
    }
    await loadWatchlist(false);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Toggle failed";
  }
}

scanButton.addEventListener("click", runScan);
arbMonitorButton.addEventListener("click", toggleArbMonitor);
traderButton.addEventListener("click", loadTraders);
smartIngestButton.addEventListener("click", ingestSmartWallets);
smartLoadButton.addEventListener("click", loadSmartWallets);
watchlistLoadButton.addEventListener("click", () => loadWatchlist(true));
traderMonitorButton.addEventListener("click", handleTraderMonitorButton);
watchlistRefreshButton.addEventListener("click", refreshWatchlistTrades);
paperLoadButton.addEventListener("click", () => loadPaperOrders(true));
paperReconcileButton.addEventListener("click", reconcilePaperPositions);
paperSaveBalanceButton.addEventListener("click", savePaperBalance);
paperResetButton.addEventListener("click", resetPaperAccount);
paperSaveExecutionButton.addEventListener("click", savePaperExecutionSettings);
accountRefreshButton.addEventListener("click", loadAccountStatus);
paperTabButtons.forEach((button) => {
  button.addEventListener("click", () => switchPaperTab(button.dataset.paperTab));
});
liveTabButtons.forEach((button) => {
  button.addEventListener("click", () => switchLiveTab(button.dataset.liveTab));
});

const autoRunScan = debounce(() => {
  if (scannerHasRun) {
    runScan();
  }
});

const autoLoadTraders = debounce(() => {
  if (tradersHaveLoaded) {
    loadTraders();
  }
});

const autoLoadSmart = debounce(() => refreshSmartForFilterChange(false));
const autoIngestSmart = debounce(() => refreshSmartForFilterChange(true), 700);

[limitInput, maxMarketsInput, profitInput].forEach((input) => {
  input.addEventListener("input", autoRunScan);
});

[
  categoryInput,
  periodInput,
  orderInput,
  traderLimitInput,
  tradesPerTraderInput,
  closedPositionsInput,
  minWinRateInput,
  minClosedInput,
  minRecentTradesInput,
].forEach((input) => {
  input.addEventListener("input", autoLoadTraders);
  input.addEventListener("change", autoLoadTraders);
});

[smartCategoryInput, smartPeriodInput, candidateLimitInput, smartTradesInput, smartPositionsInput, markoutTradesInput].forEach(
  (input) => {
    input.addEventListener("input", autoIngestSmart);
    input.addEventListener("change", autoIngestSmart);
  }
);

[smartMinTradesInput, smartMinClosedInput, smartMinWinRateInput].forEach((input) => {
  input.addEventListener("input", autoLoadSmart);
});
document.addEventListener("click", (event) => {
  const saveButton = event.target.closest(".save-wallet-button");
  if (saveButton) {
    saveWalletFromButton(saveButton);
    return;
  }

  const removeButton = event.target.closest(".remove-wallet-button");
  if (removeButton) {
    removeWatchlistWallet(removeButton);
    return;
  }

  const toggleAlertsButton = event.target.closest(".toggle-wallet-alerts-button");
  if (toggleAlertsButton) {
    toggleWalletAlerts(toggleAlertsButton);
    return;
  }

  const toggleCopytradeButton = event.target.closest(".toggle-paper-copytrade-button");
  if (toggleCopytradeButton) {
    toggleCopytrade(toggleCopytradeButton);
    return;
  }

  const toggleLiveCopytradeButton = event.target.closest(".toggle-live-copytrade-button");
  if (toggleLiveCopytradeButton) {
    toggleLiveCopytrade(toggleLiveCopytradeButton);
    return;
  }

  const closePaperButton = event.target.closest(".close-paper-position-button");
  if (closePaperButton) {
    event.preventDefault();
    event.stopPropagation();
    closePaperPosition(closePaperButton);
    return;
  }

  const paperTradeSummary = event.target.closest(".paper-trade-summary");
  if (paperTradeSummary) {
    const card = paperTradeSummary.closest(".paper-trade-card");
    if (card) {
      card.dataset.expanded = card.dataset.expanded === "1" ? "0" : "1";
    }
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const paperTradeSummary = event.target.closest(".paper-trade-summary");
  if (!paperTradeSummary) return;
  event.preventDefault();
  const card = paperTradeSummary.closest(".paper-trade-card");
  if (card) {
    card.dataset.expanded = card.dataset.expanded === "1" ? "0" : "1";
  }
});
document.addEventListener("change", (event) => {
  const control = event.target.closest(".paper-copy-sizing-mode, .paper-copy-size-value, .paper-copy-max-usdc");
  if (control) {
    const wallet = control.dataset.wallet;
    const setting = copytradeSettings[(wallet || "").toLowerCase()] || {};
    saveCopytradeSettings(wallet, setting.enabled === true).catch(() => {});
    return;
  }
  const liveControl = event.target.closest(".live-copy-sizing-mode, .live-copy-size-value, .live-copy-max-usdc");
  if (!liveControl) return;
  const wallet = liveControl.dataset.wallet;
  const setting = liveCopytradeSettings[(wallet || "").toLowerCase()] || {};
  saveLiveCopytradeSettings(wallet, setting.enabled === true).catch(() => {});
});
document.querySelectorAll(".nav-item[data-tab]").forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tab));
});
if (accountConnectionForm) {
  accountConnectionForm.addEventListener("submit", (event) => {
    event.preventDefault();
    saveAccountConnection({ testAfterSave: false });
  });
}
if (testAccountConnectionButton) {
  testAccountConnectionButton.addEventListener("click", () => {
    saveAccountConnection({ testAfterSave: true });
  });
}
if (deriveAccountCredentialsButton) {
  deriveAccountCredentialsButton.addEventListener("click", () => {
    deriveAccountCredentials();
  });
}
if (liveArmButton) {
  liveArmButton.addEventListener("click", () => {
    const confirmed = window.confirm("Arm live copytrading now? This allows the bot to submit real FOK copy orders for saved traders with Copytrade enabled.");
    if (!confirmed) return;
    setLiveTradingEnabled(true);
  });
}
if (liveKillButton) {
  liveKillButton.addEventListener("click", () => {
    setLiveTradingEnabled(false);
  });
}
if (liveSaveRiskButton) {
  liveSaveRiskButton.addEventListener("click", () => {
    saveLiveRiskSettings();
  });
}
[liveCapitalModeInput, liveMinCashReserveInput, liveMinTradeInput, liveMaxChaseInput].forEach((input) => {
  if (!input) return;
  input.addEventListener("input", () => {
    liveRiskSettingsDirty = true;
  });
  input.addEventListener("change", () => {
    liveRiskSettingsDirty = true;
  });
});
liveRefreshTimer = window.setInterval(() => {
  loadLiveTrading().catch(() => {});
}, 5000);
loadConfig().catch(() => {});
loadCopytradeSettings().catch(() => {});
loadPaperExecutionSettings().catch(() => {});
loadWatchlistMonitorStatus().catch(() => {});
startTraderMonitor(false).catch(() => {});
