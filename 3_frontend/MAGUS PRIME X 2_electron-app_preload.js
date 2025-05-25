const { contextBridge, ipcRenderer } = require("electron");

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld("electron", {
  login: (credentials) => ipcRenderer.send("login", credentials),
  startBot: (symbol, timeframe) =>
    ipcRenderer.send("start-bot", symbol, timeframe),
  stopBot: () => ipcRenderer.send("stop-bot"),
  getMarketData: () => ipcRenderer.invoke("get-market-data"),
  getAccountInfo: () => ipcRenderer.invoke("get-account-info"),
  executeTrade: (tradeData) => ipcRenderer.invoke("execute-trade", tradeData),
  closePosition: (positionId) =>
    ipcRenderer.invoke("close-position", positionId),
  modifyPosition: (positionId, data) =>
    ipcRenderer.invoke("modify-position", positionId, data),
  getChartAnalysis: (symbol, timeframe) =>
    ipcRenderer.invoke("get-chart-analysis", symbol, timeframe),
  getPatterns: (symbol, timeframe) =>
    ipcRenderer.invoke("get-patterns", symbol, timeframe),
  getSupportResistance: (symbol, timeframe) =>
    ipcRenderer.invoke("get-support-resistance", symbol, timeframe),
  sendTelegramNotification: (message) =>
    ipcRenderer.invoke("send-telegram", message),
  getChatGPTAnalysis: (symbol) =>
    ipcRenderer.invoke("get-chatgpt-analysis", symbol),
  // Add new methods for Capital.com integration
  getEnvVariables: (keys) => ipcRenderer.invoke("get-env-variables", keys),
  saveEnvVariables: (variables) =>
    ipcRenderer.invoke("save-env-variables", variables),
  connectToCapital: (credentials) =>
    ipcRenderer.invoke("connect-to-capital", credentials),
  getPositions: () => ipcRenderer.invoke("get-positions"),
  getOrders: () => ipcRenderer.invoke("get-orders"),
  getTradeHistory: () => ipcRenderer.invoke("get-trade-history"),
  updateBotConfig: (config) => ipcRenderer.invoke("update-bot-config", config),
  getBotStats: () => ipcRenderer.invoke("get-bot-stats"),
});
