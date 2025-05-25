// MAGUS PRIME X Bot Test Dashboard JavaScript

// Configuration and state
const config = {
  logToFile: true,
  logFilePath: "bot-test-logs.txt",
  saveInterval: 30000, // 30 seconds
  simulationMode: true,
  defaultBalance: 10000,
  apiCheckInterval: 5000, // 5 seconds
};

const state = {
  connected: false,
  botRunning: false,
  accountBalance: config.defaultBalance,
  accountEquity: config.defaultBalance,
  dailyPL: 0,
  openPositions: [],
  tradeHistory: [],
  logs: [],
  strategyMode: "Balanced",
  riskPercent: 2,
  tpMovePercent: 0.5,
  breakEvenTrigger: 1.0,
  tradeInterval: 300,
  markets: [],
  lastApiCheck: null,
};

// DOM Elements
const elements = {
  connectionStatus: document.getElementById("connectionStatus"),
  connectionText: document.getElementById("connectionText"),
  botStatus: document.getElementById("botStatus"),
  botStatusText: document.getElementById("botStatusText"),
  connectBtn: document.getElementById("connectBtn"),
  startBotBtn: document.getElementById("startBotBtn"),
  stopBotBtn: document.getElementById("stopBotBtn"),
  testTradeBtn: document.getElementById("testTradeBtn"),
  clearLogsBtn: document.getElementById("clearLogsBtn"),
  accountBalance: document.getElementById("accountBalance"),
  accountEquity: document.getElementById("accountEquity"),
  dailyPL: document.getElementById("dailyPL"),
  openPositions: document.getElementById("openPositions"),
  strategyMode: document.getElementById("strategyMode"),
  customStrategySettings: document.getElementById("customStrategySettings"),
  riskPercent: document.getElementById("riskPercent"),
  tpMove: document.getElementById("tpMove"),
  tradeInterval: document.getElementById("tradeInterval"),
  applyStrategyBtn: document.getElementById("applyStrategyBtn"),
  activeTradesContainer: document.getElementById("activeTradesContainer"),
  tradeHistoryBody: document.getElementById("tradeHistoryBody"),
  logContainer: document.getElementById("logContainer"),
  logLevel: document.getElementById("logLevel"),
  symbolInput: document.getElementById("symbolInput"),
  manualBuyBtn: document.getElementById("manualBuyBtn"),
  manualSellBtn: document.getElementById("manualSellBtn"),
  marketSearch: document.getElementById("marketSearch"),
  refreshMarketsBtn: document.getElementById("refreshMarketsBtn"),
  marketAnalysisBody: document.getElementById("marketAnalysisBody"),
  winRate: document.getElementById("winRate"),
  avgProfit: document.getElementById("avgProfit"),
  avgLoss: document.getElementById("avgLoss"),
  profitFactor: document.getElementById("profitFactor"),
};

// Charts
let profitLossChart;
let winLossChart;

// Initialize the dashboard
function initDashboard() {
  initCharts();
  attachEventListeners();
  loadSavedState();
  updateUI();

  // Add initial log entry
  addLog("Dashboard initialized", "info");

  // Load example data for testing
  if (config.simulationMode) {
    loadExampleData();
  }

  // Start regular updates
  setInterval(updateUI, 1000);
  setInterval(saveState, config.saveInterval);
  setInterval(checkApiStatus, config.apiCheckInterval);
}

// Initialize charts
function initCharts() {
  // Profit/Loss Chart
  const plCtx = document.getElementById("profitLossChart").getContext("2d");
  profitLossChart = new Chart(plCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Cumulative P/L",
          data: [],
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.1)",
          borderWidth: 2,
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
          labels: {
            color: "#e0e0e0",
          },
        },
        title: {
          display: true,
          text: "Profit/Loss History",
          color: "#e0e0e0",
        },
      },
      scales: {
        x: {
          ticks: { color: "#999" },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
        },
        y: {
          ticks: { color: "#999" },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
        },
      },
    },
  });

  // Win/Loss Ratio Chart
  const wlCtx = document.getElementById("winLossChart").getContext("2d");
  winLossChart = new Chart(wlCtx, {
    type: "doughnut",
    data: {
      labels: ["Wins", "Losses"],
      datasets: [
        {
          data: [0, 0],
          backgroundColor: ["#4CAF50", "#F44336"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
          labels: {
            color: "#e0e0e0",
          },
        },
        title: {
          display: true,
          text: "Win/Loss Ratio",
          color: "#e0e0e0",
        },
      },
    },
  });
}

// Attach event listeners
function attachEventListeners() {
  // Connection buttons
  elements.connectBtn.addEventListener("click", toggleConnection);

  // Bot control
  elements.startBotBtn.addEventListener("click", startBot);
  elements.stopBotBtn.addEventListener("click", stopBot);
  elements.testTradeBtn.addEventListener("click", createTestTrade);

  // Strategy settings
  elements.strategyMode.addEventListener(
    "change",
    toggleCustomStrategySettings,
  );
  elements.applyStrategyBtn.addEventListener("click", applyStrategy);

  // Log controls
  elements.clearLogsBtn.addEventListener("click", clearLogs);
  elements.logLevel.addEventListener("change", filterLogs);

  // Manual trading
  elements.manualBuyBtn.addEventListener("click", () =>
    createManualTrade("BUY"),
  );
  elements.manualSellBtn.addEventListener("click", () =>
    createManualTrade("SELL"),
  );

  // Markets tab
  elements.refreshMarketsBtn.addEventListener("click", refreshMarkets);
  elements.marketSearch.addEventListener("input", filterMarkets);
}

// Load saved state
function loadSavedState() {
  const savedState = localStorage.getItem("botTestDashboardState");
  if (savedState) {
    try {
      const parsed = JSON.parse(savedState);
      // Merge saved state but keep current connection status
      Object.assign(state, parsed, {
        connected: state.connected,
        botRunning: state.botRunning,
      });
      addLog("Saved state loaded", "info");
    } catch (error) {
      addLog("Error loading saved state: " + error.message, "error");
    }
  }
}

// Save current state
function saveState() {
  try {
    localStorage.setItem("botTestDashboardState", JSON.stringify(state));
    if (config.logToFile) {
      saveLogsToFile();
    }
  } catch (error) {
    console.error("Error saving state:", error);
  }
}

// Save logs to file
function saveLogsToFile() {
  // In a real implementation, this would use fetch to call a server endpoint
  // that would save the logs to a file.
  // For this simulator, we'll just print a message
  console.log("Logs would be saved to:", config.logFilePath);
}

// Toggle connection status
function toggleConnection() {
  if (state.connected) {
    // Disconnect
    state.connected = false;
    if (state.botRunning) {
      stopBot();
    }
    addLog("Disconnected from Capital.com API", "info");
  } else {
    // Connect
    state.connected = true;
    addLog("Connected to Capital.com API", "info");
    // Simulate fetching account info
    setTimeout(() => {
      state.accountBalance = config.defaultBalance;
      state.accountEquity = config.defaultBalance;
      state.dailyPL = 0;
      updateUI();
      addLog("Account information fetched", "info");
    }, 1000);
  }
  updateUI();
}

// Start the bot
function startBot() {
  if (!state.connected) {
    addLog("Cannot start bot: Not connected to API", "error");
    return;
  }

  state.botRunning = true;
  addLog("Bot started", "info");

  // Start the simulation loop if in simulation mode
  if (config.simulationMode) {
    addLog("Running in simulation mode", "info");
    runSimulation();
  }

  updateUI();
}

// Stop the bot
function stopBot() {
  state.botRunning = false;
  addLog("Bot stopped", "info");
  updateUI();
}

// Apply strategy settings
function applyStrategy() {
  const mode = elements.strategyMode.value;
  state.strategyMode = mode;

  if (mode === "Custom") {
    state.riskPercent = parseFloat(elements.riskPercent.value);
    state.tpMovePercent = parseFloat(elements.tpMove.value);
    state.tradeInterval = parseInt(elements.tradeInterval.value);
  } else {
    // Apply preset values
    if (mode === "Safe") {
      state.riskPercent = 1;
      state.tpMovePercent = 0.3;
      state.breakEvenTrigger = 0.5;
      state.tradeInterval = 600;
    } else if (mode === "Aggressive") {
      state.riskPercent = 3;
      state.tpMovePercent = 1.0;
      state.breakEvenTrigger = 1.5;
      state.tradeInterval = 120;
    } else {
      // Balanced
      state.riskPercent = 2;
      state.tpMovePercent = 0.5;
      state.breakEvenTrigger = 1.0;
      state.tradeInterval = 300;
    }
  }

  addLog(`Strategy changed to ${mode} mode`, "info");
  updateUI();
}

// Toggle custom strategy settings
function toggleCustomStrategySettings() {
  const isCustom = elements.strategyMode.value === "Custom";
  elements.customStrategySettings.style.display = isCustom ? "block" : "none";
}

// Create a test trade
function createTestTrade() {
  if (!state.connected) {
    addLog("Cannot execute test trade: Not connected to API", "error");
    return;
  }

  const symbols = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "BTCUSD", "ETHUSD"];
  const symbol = symbols[Math.floor(Math.random() * symbols.length)];
  const direction = Math.random() > 0.5 ? "BUY" : "SELL";

  executeTrade(symbol, direction, true);
}

// Create a manual trade
function createManualTrade(direction) {
  if (!state.connected) {
    addLog("Cannot execute manual trade: Not connected to API", "error");
    return;
  }

  const symbol = elements.symbolInput.value.trim();
  if (!symbol) {
    addLog("Please enter a symbol for manual trade", "error");
    return;
  }

  executeTrade(symbol, direction, false);
}

// Execute a trade (simulated or real)
function executeTrade(symbol, direction, isTest) {
  const tradeId = Date.now().toString();
  const currentPrice = getRandomPrice(symbol);
  const size = calculatePositionSize(symbol, state.riskPercent);
  const stopLoss = calculateStopLoss(currentPrice, direction);
  const takeProfit = calculateTakeProfit(currentPrice, direction);

  // Create new trade object
  const trade = {
    id: tradeId,
    symbol: symbol,
    direction: direction,
    openPrice: currentPrice,
    currentPrice: currentPrice,
    size: size,
    stopLoss: stopLoss,
    takeProfit: takeProfit,
    openTime: new Date(),
    pnl: 0,
    pnlPercent: 0,
    status: "OPEN",
  };

  // Add to open positions
  state.openPositions.push(trade);

  // Log the trade
  addLog(
    `${direction} order executed: ${symbol} ${size} units at ${currentPrice}`,
    "trade",
  );
  if (isTest) {
    addLog("This is a test trade and will be simulated", "info");
  }

  // Update UI
  updateUI();
  renderActiveTrades();

  return trade;
}

// Calculate position size based on risk
function calculatePositionSize(symbol, riskPercent) {
  const accountSize = state.accountBalance;
  const riskAmount = accountSize * (riskPercent / 100);

  // In a real implementation, this would use proper math based on pip value
  // For simulation, we'll use a simplified approach
  return Math.round((riskAmount / 10) * 100) / 100;
}

// Calculate stop loss level
function calculateStopLoss(price, direction) {
  // Simple calculation for simulation
  const atrValue = price * 0.001; // Simulated ATR as 0.1% of price

  if (direction === "BUY") {
    return Math.round((price - atrValue * 1.5) * 100000) / 100000;
  } else {
    return Math.round((price + atrValue * 1.5) * 100000) / 100000;
  }
}

// Calculate take profit level
function calculateTakeProfit(price, direction) {
  // Simple calculation for simulation
  const atrValue = price * 0.001; // Simulated ATR as 0.1% of price

  if (direction === "BUY") {
    return Math.round((price + atrValue * 2.5) * 100000) / 100000;
  } else {
    return Math.round((price - atrValue * 2.5) * 100000) / 100000;
  }
}

// Get a random price for a symbol (for simulation)
function getRandomPrice(symbol) {
  const basePrices = {
    EURUSD: 1.185,
    GBPUSD: 1.365,
    AUDUSD: 0.745,
    USDJPY: 110.5,
    BTCUSD: 55000,
    ETHUSD: 3500,
  };

  const basePrice = basePrices[symbol] || 100;
  const fluctuation = basePrice * 0.002 * (Math.random() - 0.5);
  return Math.round((basePrice + fluctuation) * 100000) / 100000;
}

// Update the UI based on current state
function updateUI() {
  // Update connection status
  elements.connectionStatus.className = state.connected
    ? "status-indicator status-active"
    : "status-indicator status-inactive";
  elements.connectionText.textContent = state.connected
    ? "Connected"
    : "Disconnected";
  elements.connectBtn.textContent = state.connected ? "Disconnect" : "Connect";

  // Update bot status
  elements.botStatus.className = state.botRunning
    ? "status-indicator status-active"
    : "status-indicator status-inactive";
  elements.botStatusText.textContent = state.botRunning
    ? "Bot Active"
    : "Bot Inactive";

  // Button states
  elements.startBotBtn.disabled = state.botRunning || !state.connected;
  elements.stopBotBtn.disabled = !state.botRunning;
  elements.testTradeBtn.disabled = !state.connected;
  elements.manualBuyBtn.disabled = !state.connected;
  elements.manualSellBtn.disabled = !state.connected;

  // Account info
  elements.accountBalance.textContent = formatMoney(state.accountBalance);
  elements.accountEquity.textContent = formatMoney(state.accountEquity);
  elements.dailyPL.textContent = formatMoney(state.dailyPL);
  elements.dailyPL.className = state.dailyPL >= 0 ? "profit" : "loss";
  elements.openPositions.textContent = state.openPositions.length;

  // Update performance metrics
  updatePerformanceMetrics();
}

// Render active trades
function renderActiveTrades() {
  const container = elements.activeTradesContainer;

  if (state.openPositions.length === 0) {
    container.innerHTML =
      '<div class="text-center text-muted">No active trades</div>';
    return;
  }

  container.innerHTML = "";
  state.openPositions.forEach((trade) => {
    const tradeEl = document.createElement("div");
    tradeEl.className = `card trade-card mb-3 ${trade.direction === "BUY" ? "trade-buy" : "trade-sell"}`;

    tradeEl.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5>${trade.symbol} ${trade.direction}</h5>
                    <span class="${trade.pnl >= 0 ? "profit" : "loss"}">${formatMoney(trade.pnl)}</span>
                </div>
                <div class="row mb-1">
                    <div class="col-6">Open: ${trade.openPrice}</div>
                    <div class="col-6">Current: ${trade.currentPrice}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-6">SL: ${trade.stopLoss}</div>
                    <div class="col-6">TP: ${trade.takeProfit}</div>
                </div>
                <div class="d-flex justify-content-between">
                    <small>${formatTime(trade.openTime)}</small>
                    <button class="btn btn-sm btn-danger close-trade-btn" data-trade-id="${trade.id}">Close</button>
                </div>
            </div>
        `;

    container.appendChild(tradeEl);

    // Add event listener to close button
    const closeBtn = tradeEl.querySelector(".close-trade-btn");
    closeBtn.addEventListener("click", () => closeTrade(trade.id));
  });
}

// Render trade history
function renderTradeHistory() {
  const tbody = elements.tradeHistoryBody;
  tbody.innerHTML = "";

  state.tradeHistory
    .slice()
    .reverse()
    .forEach((trade) => {
      const row = document.createElement("tr");

      const duration = trade.closeTime
        ? Math.floor((trade.closeTime - trade.openTime) / 1000)
        : "-";

      row.innerHTML = `
            <td>${formatTime(trade.openTime)}</td>
            <td>${trade.symbol}</td>
            <td>${trade.direction}</td>
            <td>${trade.size}</td>
            <td>${trade.openPrice}</td>
            <td>${trade.closePrice || "-"}</td>
            <td class="${trade.pnl >= 0 ? "profit" : "loss"}">${formatMoney(trade.pnl)}</td>
            <td>${duration}s</td>
        `;

      tbody.appendChild(row);
    });
}

// Add a log entry
function addLog(message, type = "info") {
  const log = {
    time: new Date(),
    message: message,
    type: type,
  };

  state.logs.unshift(log);

  // Keep logs to a reasonable size
  if (state.logs.length > 1000) {
    state.logs.pop();
  }

  renderLogs();
}

// Render logs
function renderLogs() {
  const container = elements.logContainer;
  const filterType = elements.logLevel.value;

  // Filter logs if needed
  let logsToShow = state.logs;
  if (filterType !== "all") {
    logsToShow = state.logs.filter((log) => log.type === filterType);
  }

  // Clear container
  container.innerHTML = "";

  // Add logs
  logsToShow.forEach((log) => {
    const logEl = document.createElement("div");
    logEl.className = `log-entry log-${log.type}`;
    logEl.innerHTML = `<span class="text-muted">${formatTime(log.time)}</span> ${log.message}`;
    container.appendChild(logEl);
  });
}

// Filter logs by level
function filterLogs() {
  renderLogs();
}

// Clear logs
function clearLogs() {
  state.logs = [];
  renderLogs();
  addLog("Logs cleared", "info");
}

// Close a trade
function closeTrade(tradeId) {
  const tradeIndex = state.openPositions.findIndex((t) => t.id === tradeId);
  if (tradeIndex === -1) return;

  const trade = state.openPositions[tradeIndex];

  // Set closing price (with some slippage for realism)
  const slippage = (Math.random() - 0.5) * 0.0001 * trade.openPrice;
  const closePrice = trade.currentPrice + slippage;

  // Calculate final P/L
  const priceDiff =
    trade.direction === "BUY"
      ? closePrice - trade.openPrice
      : trade.openPrice - closePrice;
  const pnl =
    priceDiff * trade.size * (trade.symbol.includes("JPY") ? 100 : 10000);

  // Create closed trade record
  const closedTrade = {
    ...trade,
    closePrice: closePrice,
    closeTime: new Date(),
    pnl: pnl,
    status: "CLOSED",
  };

  // Update account
  state.accountBalance += pnl;
  state.accountEquity += pnl;
  state.dailyPL += pnl;

  // Remove from open positions and add to history
  state.openPositions.splice(tradeIndex, 1);
  state.tradeHistory.push(closedTrade);

  // Log
  addLog(
    `${trade.direction} position closed: ${trade.symbol} at ${closePrice} (${pnl >= 0 ? "Profit" : "Loss"}: ${formatMoney(pnl)})`,
    "trade",
  );

  // Update UI
  updateUI();
  renderActiveTrades();
  renderTradeHistory();
  updatePerformanceMetrics();
}

// Update performance metrics
function updatePerformanceMetrics() {
  if (state.tradeHistory.length === 0) return;

  // Calculate statistics
  const wins = state.tradeHistory.filter((t) => t.pnl > 0).length;
  const losses = state.tradeHistory.filter((t) => t.pnl <= 0).length;

  const winRate = (wins / state.tradeHistory.length) * 100;

  const profits = state.tradeHistory.filter((t) => t.pnl > 0).map((t) => t.pnl);
  const avgProfit =
    profits.length > 0
      ? profits.reduce((a, b) => a + b, 0) / profits.length
      : 0;

  const losses2 = state.tradeHistory
    .filter((t) => t.pnl <= 0)
    .map((t) => t.pnl);
  const avgLoss =
    losses2.length > 0
      ? losses2.reduce((a, b) => a + b, 0) / losses2.length
      : 0;

  const profitFactor =
    Math.abs(avgLoss) > 0 ? avgProfit / Math.abs(avgLoss) : 0;

  // Update display
  elements.winRate.textContent = winRate.toFixed(1) + "%";
  elements.avgProfit.textContent = formatMoney(avgProfit);
  elements.avgLoss.textContent = formatMoney(avgLoss);
  elements.profitFactor.textContent = profitFactor.toFixed(2);

  // Update charts
  updateCharts();
}

// Update charts with current data
function updateCharts() {
  // P/L Chart
  const plData = [];
  let cumulative = 0;
  const dates = [];

  state.tradeHistory.forEach((trade) => {
    cumulative += trade.pnl;
    plData.push(cumulative);
    dates.push(formatDate(trade.closeTime));
  });

  profitLossChart.data.labels = dates;
  profitLossChart.data.datasets[0].data = plData;
  profitLossChart.update();

  // Win/Loss Chart
  const wins = state.tradeHistory.filter((t) => t.pnl > 0).length;
  const losses = state.tradeHistory.filter((t) => t.pnl <= 0).length;

  winLossChart.data.datasets[0].data = [wins, losses];
  winLossChart.update();
}

// Refresh market analysis
function refreshMarkets() {
  if (!state.connected) {
    addLog("Cannot refresh markets: Not connected to API", "error");
    return;
  }

  addLog("Refreshing market analysis...", "info");

  // Simulated market data
  const markets = [
    { symbol: "EURUSD", price: getRandomPrice("EURUSD") },
    { symbol: "GBPUSD", price: getRandomPrice("GBPUSD") },
    { symbol: "AUDUSD", price: getRandomPrice("AUDUSD") },
    { symbol: "USDJPY", price: getRandomPrice("USDJPY") },
    { symbol: "BTCUSD", price: getRandomPrice("BTCUSD") },
    { symbol: "ETHUSD", price: getRandomPrice("ETHUSD") },
  ];

  // Add random technical indicators
  markets.forEach((market) => {
    market.ema200 = market.price * (1 + (Math.random() - 0.5) * 0.01);
    market.rsi = Math.round(Math.random() * 100);
    market.macd = (Math.random() - 0.5) * 0.01;

    // Signal based on indicators
    if (market.rsi > 70) {
      market.signal = "Overbought";
    } else if (market.rsi < 30) {
      market.signal = "Oversold";
    } else if (market.price > market.ema200 && market.macd > 0) {
      market.signal = "Bullish";
    } else if (market.price < market.ema200 && market.macd < 0) {
      market.signal = "Bearish";
    } else {
      market.signal = "Neutral";
    }
  });

  state.markets = markets;
  renderMarketAnalysis();
}

// Filter market analysis table
function filterMarkets() {
  const searchTerm = elements.marketSearch.value.toLowerCase();
  renderMarketAnalysis(searchTerm);
}

// Render market analysis table
function renderMarketAnalysis(searchTerm = "") {
  const tbody = elements.marketAnalysisBody;
  const filteredMarkets = searchTerm
    ? state.markets.filter((m) => m.symbol.toLowerCase().includes(searchTerm))
    : state.markets;

  tbody.innerHTML = "";
  filteredMarkets.forEach((market) => {
    const row = document.createElement("tr");

    let signalClass = "";
    if (market.signal === "Bullish" || market.signal === "Oversold") {
      signalClass = "profit";
    } else if (market.signal === "Bearish" || market.signal === "Overbought") {
      signalClass = "loss";
    }

    row.innerHTML = `
            <td>${market.symbol}</td>
            <td>${market.price}</td>
            <td>${market.ema200.toFixed(5)}</td>
            <td>${market.rsi}</td>
            <td>${market.macd.toFixed(5)}</td>
            <td class="${signalClass}">${market.signal}</td>
            <td>
                <button class="btn btn-sm btn-success me-1 analyze-btn" data-symbol="${market.symbol}">Analyze</button>
            </td>
        `;

    tbody.appendChild(row);

    // Add event listener to buttons
    const analyzeBtn = row.querySelector(".analyze-btn");
    analyzeBtn.addEventListener("click", () => analyzeMarket(market.symbol));
  });
}

// Analyze a specific market
function analyzeMarket(symbol) {
  if (!state.connected) {
    addLog("Cannot analyze market: Not connected to API", "error");
    return;
  }

  addLog(`Analyzing ${symbol}...`, "info");

  // Set the symbol in the input field
  elements.symbolInput.value = symbol;

  // Simulate analysis with random recommendations
  setTimeout(() => {
    const random = Math.random();
    let recommendation;

    if (random > 0.6) {
      recommendation = "BUY";
      addLog(
        `Analysis complete: ${symbol} - Strong ${recommendation} signal detected`,
        "info",
      );
    } else if (random < 0.4) {
      recommendation = "SELL";
      addLog(
        `Analysis complete: ${symbol} - Strong ${recommendation} signal detected`,
        "info",
      );
    } else {
      recommendation = "NEUTRAL";
      addLog(
        `Analysis complete: ${symbol} - ${recommendation} conditions, no clear signal`,
        "info",
      );
    }
  }, 1000);
}

// Run bot simulation
function runSimulation() {
  if (!state.botRunning) return;

  // Check if we have available markets
  if (state.markets.length === 0) {
    refreshMarkets();
  }

  // Randomly decide if a trade should be taken
  const shouldTrade = Math.random() < 0.3;

  if (shouldTrade) {
    // Pick a random market
    const marketIndex = Math.floor(Math.random() * state.markets.length);
    const market = state.markets[marketIndex];

    // Decide direction based on signal
    let direction;
    if (market.signal === "Bullish" || market.signal === "Oversold") {
      direction = "BUY";
    } else if (market.signal === "Bearish" || market.signal === "Overbought") {
      direction = "SELL";
    } else {
      direction = Math.random() > 0.5 ? "BUY" : "SELL";
    }

    // Execute the trade
    addLog(
      `Bot analyzing ${market.symbol}: ${market.signal} conditions detected`,
      "info",
    );
    setTimeout(() => {
      addLog(`Bot generated ${direction} signal for ${market.symbol}`, "trade");
      executeTrade(market.symbol, direction, false);
    }, 1000);
  }

  // Update existing positions
  updatePositions();

  // Schedule next run
  const interval = 5000 + Math.random() * 10000;
  setTimeout(runSimulation, interval);
}

// Update existing positions (simulated price movements)
function updatePositions() {
  if (state.openPositions.length === 0) return;

  let equityChange = 0;

  // Update each position
  state.openPositions.forEach((position) => {
    // Generate a small random price movement
    const priceMove = position.openPrice * 0.0005 * (Math.random() - 0.5);
    position.currentPrice = parseFloat(
      (position.currentPrice + priceMove).toFixed(5),
    );

    // Calculate P/L
    const priceDiff =
      position.direction === "BUY"
        ? position.currentPrice - position.openPrice
        : position.openPrice - position.currentPrice;

    position.pnl =
      priceDiff *
      position.size *
      (position.symbol.includes("JPY") ? 100 : 10000);
    position.pnlPercent = (priceDiff / position.openPrice) * 100;

    equityChange += position.pnl;

    // Check for stop loss or take profit
    if (position.direction === "BUY") {
      if (position.currentPrice <= position.stopLoss) {
        addLog(
          `Stop Loss triggered for ${position.symbol} BUY position`,
          "trade",
        );
        closeTrade(position.id);
      } else if (position.currentPrice >= position.takeProfit) {
        addLog(
          `Take Profit reached for ${position.symbol} BUY position`,
          "trade",
        );
        closeTrade(position.id);
      }
    } else {
      // SELL
      if (position.currentPrice >= position.stopLoss) {
        addLog(
          `Stop Loss triggered for ${position.symbol} SELL position`,
          "trade",
        );
        closeTrade(position.id);
      } else if (position.currentPrice <= position.takeProfit) {
        addLog(
          `Take Profit reached for ${position.symbol} SELL position`,
          "trade",
        );
        closeTrade(position.id);
      }
    }
  });

  // Update account equity
  state.accountEquity = state.accountBalance + equityChange;

  // Update UI
  renderActiveTrades();
  updateUI();
}

// Check API status (simulated)
function checkApiStatus() {
  if (!state.connected) return;

  // Simulate occasional API issues
  const now = Date.now();
  if (!state.lastApiCheck || now - state.lastApiCheck > 60000) {
    if (Math.random() < 0.1) {
      // Simulate temporary connection issue
      addLog("Warning: API response delayed, retry in progress...", "warning");
      setTimeout(() => {
        addLog("API connection restored", "info");
      }, 3000);
    }
    state.lastApiCheck = now;
  }
}

// Helper: Format money value
function formatMoney(value) {
  return "$" + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, "$&,");
}

// Helper: Format time
function formatTime(date) {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// Helper: Format date
function formatDate(date) {
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
}

// Load sample data for testing
function loadExampleData() {
  // Add some sample trade history
  const symbols = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "BTCUSD"];
  const now = new Date();

  for (let i = 0; i < 15; i++) {
    const direction = Math.random() > 0.5 ? "BUY" : "SELL";
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const basePrice = getRandomPrice(symbol);
    const size = Math.round(Math.random() * 4 + 1);

    // Random PnL
    const isWin = Math.random() > 0.4;
    const priceDiff =
      basePrice * (isWin ? 0.003 : -0.002) * (Math.random() + 0.5);
    const closePrice =
      direction === "BUY" ? basePrice + priceDiff : basePrice - priceDiff;
    const pnl =
      direction === "BUY"
        ? (closePrice - basePrice) * size * 10000
        : (basePrice - closePrice) * size * 10000;

    // Random dates (past few days)
    const openTime = new Date(
      now.getTime() - Math.random() * 5 * 24 * 60 * 60 * 1000,
    );
    const closeTime = new Date(
      openTime.getTime() + Math.random() * 12 * 60 * 60 * 1000,
    );

    state.tradeHistory.push({
      id: "hist-" + i,
      symbol: symbol,
      direction: direction,
      openPrice: basePrice,
      closePrice: closePrice,
      size: size,
      openTime: openTime,
      closeTime: closeTime,
      pnl: pnl,
      status: "CLOSED",
    });
  }

  // Update metrics
  updatePerformanceMetrics();
  renderTradeHistory();
}

// Initialize dashboard on page load
document.addEventListener("DOMContentLoaded", initDashboard);
