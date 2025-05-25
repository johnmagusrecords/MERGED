// Socket.io connection
const socket = io();

// Global variables
let tradingViewWidget = null;
let botRunning = false;
let currentSymbol = "BTCUSD";
let currentTimeframe = "15";
let isConnected = false;
let performanceChart = null;
let botStartTime = null;
let runningTimeInterval = null;

// DOM Elements
const connectBtn = document.getElementById("connectBtn");
const configureBtn = document.getElementById("configureBtn");
const botDashboardBtn = document.getElementById("botDashboardBtn");
const startBotBtn = document.getElementById("startBotBtn");
const stopBotBtn = document.getElementById("stopBotBtn");
const connectionStatus = document.getElementById("connectionStatus");
const connectionModal = document.getElementById("connectionModal");
const botDashboardModal = document.getElementById("botDashboardModal");
const testConnectionBtn = document.getElementById("testConnectionBtn");
const saveConnectionBtn = document.getElementById("saveConnectionBtn");
const botStatus = document.getElementById("botStatus");
const botRunningTime = document.getElementById("botRunningTime");
const activeStrategy = document.getElementById("activeStrategy");

// Initialize TradingView widget
function initTradingViewWidget() {
  if (tradingViewWidget) return;

  tradingViewWidget = new TradingView.widget({
    container_id: "tradingViewChart",
    symbol: "CAPITALCOM:" + currentSymbol,
    interval: currentTimeframe,
    theme: "dark",
    style: "1",
    toolbar_bg: "#2b2f36",
    enable_publishing: false,
    hide_side_toolbar: false,
    allow_symbol_change: true,
    save_image: false,
    height: "100%",
    width: "100%",
  });
}

// Initialize performance chart
function initPerformanceChart() {
  const ctx = document.getElementById("performanceChart").getContext("2d");
  performanceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "P/L",
          data: [],
          borderColor: "#0ecb81",
          tension: 0.4,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          grid: {
            color: "rgba(255, 255, 255, 0.1)",
          },
          ticks: {
            color: "#848e9c",
          },
        },
        x: {
          grid: {
            color: "rgba(255, 255, 255, 0.1)",
          },
          ticks: {
            color: "#848e9c",
          },
        },
      },
      plugins: {
        legend: {
          labels: {
            color: "#eaecef",
          },
        },
      },
    },
  });
}

// Modal handling
function showModal(modal) {
  modal.classList.remove("hidden");
}

function hideModal(modal) {
  modal.classList.add("hidden");
}

// Event listeners
connectBtn.addEventListener("click", () => showModal(connectionModal));
botDashboardBtn.addEventListener("click", () => showModal(botDashboardModal));

document.querySelectorAll(".modal-close").forEach((button) => {
  button.addEventListener("click", (e) => {
    const modal = e.target.closest(".modal");
    hideModal(modal);
  });
});

testConnectionBtn.addEventListener("click", async () => {
  const credentials = getCredentials();
  const result = await testConnection(credentials);
  if (result.success) {
    showNotification("Connection test successful!", "success");
  } else {
    showNotification(result.message || "Connection test failed", "error");
  }
});

saveConnectionBtn.addEventListener("click", async () => {
  const credentials = getCredentials();
  const result = await connect(credentials);
  if (result.success) {
    isConnected = true;
    updateConnectionStatus(true);
    showNotification("Successfully connected to Capital.com", "success");
    hideModal(connectionModal);
    configureBtn.classList.remove("hidden");
    botDashboardBtn.classList.remove("hidden");
  } else {
    showNotification(result.message || "Connection failed", "error");
  }
});

startBotBtn.addEventListener("click", () => {
  if (!isConnected) {
    showNotification("Please connect to Capital.com first", "error");
    return;
  }
  startBot();
});

stopBotBtn.addEventListener("click", () => {
  stopBot();
});

// Helper functions
function getCredentials() {
  return {
    apiKey: document.getElementById("apiKey").value,
    apiPassword: document.getElementById("apiPassword").value,
    identifier: document.getElementById("identifier").value,
  };
}

async function testConnection(credentials) {
  try {
    const response = await fetch("/api/test_connection", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: error.message };
  }
}

async function connect(credentials) {
  try {
    const response = await fetch("/api/connect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: error.message };
  }
}

function updateConnectionStatus(connected) {
  connectionStatus.className = `px-2 py-1 rounded text-sm ${connected ? "bg-success" : "bg-warning"}`;
  connectionStatus.textContent = connected ? "Connected" : "Disconnected";
  connectBtn.classList.toggle("hidden", connected);
  configureBtn.classList.toggle("hidden", !connected);
  botDashboardBtn.classList.toggle("hidden", !connected);
}

function startBot() {
  botRunning = true;
  botStartTime = new Date();
  updateBotStatus(true);
  startRunningTimeCounter();
  socket.emit("start_bot");
  showNotification("Bot started successfully", "success");
}

function stopBot() {
  botRunning = false;
  botStartTime = null;
  updateBotStatus(false);
  stopRunningTimeCounter();
  socket.emit("stop_bot");
  showNotification("Bot stopped successfully", "success");
}

function updateBotStatus(running) {
  botStatus.className = `px-2 py-1 rounded text-sm ${running ? "bg-success" : "bg-warning"}`;
  botStatus.textContent = running ? "Running" : "Stopped";
  startBotBtn.classList.toggle("hidden", running);
  stopBotBtn.classList.toggle("hidden", !running);
}

function startRunningTimeCounter() {
  if (runningTimeInterval) clearInterval(runningTimeInterval);
  runningTimeInterval = setInterval(updateRunningTime, 1000);
}

function stopRunningTimeCounter() {
  if (runningTimeInterval) {
    clearInterval(runningTimeInterval);
    runningTimeInterval = null;
  }
  botRunningTime.textContent = "00:00:00";
}

function updateRunningTime() {
  if (!botStartTime) return;
  const now = new Date();
  const diff = now - botStartTime;
  const hours = Math.floor(diff / 3600000);
  const minutes = Math.floor((diff % 3600000) / 60000);
  const seconds = Math.floor((diff % 60000) / 1000);
  botRunningTime.textContent = `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;
}

function padZero(num) {
  return num.toString().padStart(2, "0");
}

function showNotification(message, type = "success") {
  const notification = document.createElement("div");
  notification.className = `notification ${type}`;
  notification.textContent = message;
  document.getElementById("notificationContainer").appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

// Socket event handlers
socket.on("connect", () => {
  console.log("Connected to server");
  if (isConnected) {
    updateConnectionStatus(true);
  }
});

socket.on("disconnect", () => {
  console.log("Disconnected from server");
  updateConnectionStatus(false);
  if (botRunning) {
    stopBot();
  }
});

socket.on("market_data", (data) => {
  updateMarketData(data);
});

socket.on("bot_update", (data) => {
  updateBotMetrics(data);
});

function updateMarketData(data) {
  // Update market data in the interface
  if (!data) return;

  document.getElementById("accountBalance").textContent = formatCurrency(
    data.balance || 0,
  );
  document.getElementById("accountEquity").textContent = formatCurrency(
    data.equity || 0,
  );
  document.getElementById("openPL").textContent = formatCurrency(
    data.openPL || 0,
  );

  // Update active trades
  const activeTradesContainer = document.getElementById("activeTrades");
  activeTradesContainer.innerHTML = "";

  if (data.activeTrades) {
    data.activeTrades.forEach((trade) => {
      const tradeElement = document.createElement("div");
      tradeElement.className = "trade-card";
      tradeElement.innerHTML = `
                <div class="flex justify-between items-center">
                    <span>${trade.symbol}</span>
                    <span class="${trade.pl >= 0 ? "text-success" : "text-danger"}">${formatCurrency(trade.pl)}</span>
                </div>
                <div class="flex justify-between text-sm text-secondary">
                    <span>${trade.type}</span>
                    <span>${trade.size}</span>
                </div>
            `;
      activeTradesContainer.appendChild(tradeElement);
    });
  }
}

function updateBotMetrics(data) {
  if (!data) return;

  // Update trading statistics
  document.getElementById("winRate").textContent =
    `${(data.winRate || 0).toFixed(2)}%`;
  document.getElementById("totalTrades").textContent = data.totalTrades || 0;
  document.getElementById("profitFactor").textContent = (
    data.profitFactor || 0
  ).toFixed(2);

  // Update performance chart
  if (performanceChart && data.performanceHistory) {
    performanceChart.data.labels = data.performanceHistory.map((p) => p.time);
    performanceChart.data.datasets[0].data = data.performanceHistory.map(
      (p) => p.pl,
    );
    performanceChart.update();
  }

  // Update recent trades table
  const recentTradesBody = document.getElementById("recentTradesBody");
  if (recentTradesBody && data.recentTrades) {
    recentTradesBody.innerHTML = "";
    data.recentTrades.forEach((trade) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td class="p-2">${formatDate(trade.time)}</td>
                <td class="p-2">${trade.symbol}</td>
                <td class="p-2">${trade.type}</td>
                <td class="p-2">${trade.entry}</td>
                <td class="p-2">${trade.exit}</td>
                <td class="p-2 ${trade.pl >= 0 ? "text-success" : "text-danger"}">${formatCurrency(trade.pl)}</td>
            `;
      recentTradesBody.appendChild(row);
    });
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(timestamp));
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTradingViewWidget();
  initPerformanceChart();
});
