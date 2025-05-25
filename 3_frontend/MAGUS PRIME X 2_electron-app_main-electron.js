const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const dotenv = require("dotenv");
const axios = require("axios");

// Load environment variables
dotenv.config({ path: path.join(__dirname, "..", ".env") });

let mainWindow = null;
let splashWindow = null;
let flaskProcess = null;
let botRunning = false;
let botStatus = {
  active: false,
  strategy: "Balanced",
  trades: [],
  startTime: null,
  stats: {
    totalTrades: 0,
    winningTrades: 0,
    losingTrades: 0,
    profitToday: 0,
    tradesPerDay: [],
  },
};

// Start Flask backend process
function startFlaskBackend() {
  // Path to your Python executable (use the virtual environment if available)
  const pythonPath = path.join(
    __dirname,
    "..",
    "venv",
    "Scripts",
    "python.exe",
  );

  // Path to your Flask app.py file
  const appPath = path.join(__dirname, "..", "app.py");

  // Check if paths exist
  if (!fs.existsSync(pythonPath)) {
    console.error("Python executable not found at:", pythonPath);
    return null;
  }

  if (!fs.existsSync(appPath)) {
    console.error("Flask app not found at:", appPath);
    return null;
  }

  // Start Flask app
  const process = spawn(pythonPath, [appPath]);

  process.stdout.on("data", (data) => {
    console.log(`Flask: ${data}`);
  });

  process.stderr.on("data", (data) => {
    console.error(`Flask Error: ${data}`);
  });

  process.on("close", (code) => {
    console.log(`Flask process exited with code ${code}`);
  });

  return process;
}

function createSplashWindow() {
  // Get screen size
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  splashWindow = new BrowserWindow({
    width: width,
    height: height,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    kiosk: true, // Forces fullscreen without system UI
    center: true,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  // Set to true fullscreen mode
  splashWindow.setFullScreen(true);

  // Ensure the window is always on top
  splashWindow.setAlwaysOnTop(true, "screen-saver");

  splashWindow.loadFile(path.join(__dirname, "..", "mockup_startup.html"));
}

function createMainWindow() {
  // Get exact screen dimensions
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.bounds; // Use bounds instead of workAreaSize to get full screen

  mainWindow = new BrowserWindow({
    width: width,
    height: height,
    show: false,
    frame: false, // Remove window chrome
    titleBarStyle: "hidden",
    fullscreen: true,
    kiosk: true, // Enforces fullscreen mode
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  // Set to true fullscreen mode
  mainWindow.setFullScreen(true);

  // Load the new dashboard interface
  mainWindow.loadFile(path.join(__dirname, "..", "dashboard.html"));

  // Maximize the window to ensure it's full-screen
  mainWindow.maximize();

  // Make borderless
  mainWindow.setMenuBarVisibility(false);

  // CSS to ensure the content takes the full screen
  mainWindow.webContents.insertCSS(`
    html, body {
      margin: 0;
      padding: 0;
      width: 100vw !important;
      height: 100vh !important;
      overflow: hidden;
    }
    #tradingview-container {
      width: 100% !important;
      height: 500px !important;
    }
  `);

  mainWindow.on("closed", () => {
    mainWindow = null;
    if (flaskProcess) {
      flaskProcess.kill();
    }
    app.quit();
  });
}

// Transition from splash to main window after successful login
function transitionToMainWindow() {
  if (splashWindow) {
    splashWindow.close();
    splashWindow = null;
  }

  if (mainWindow) {
    mainWindow.show();
    mainWindow.setFullScreen(true);
    mainWindow.maximize(); // Ensure it's maximized
  } else {
    createMainWindow();
  }
}

// Handle IPC messages from renderer process
ipcMain.on("login", (event, credentials) => {
  // Here you would verify credentials against Capital.com API
  // For now, we'll just simulate a successful login
  console.log("Login attempt with credentials:", credentials);

  // Simulate API verification delay
  setTimeout(() => {
    // Store credentials securely for API requests
    // (For a real app, use a more secure storage method)
    global.credentials = credentials;

    // Transition to main window
    transitionToMainWindow();
  }, 2000);
});

// Add IPC handlers for Capital.com API integration
ipcMain.handle("get-env-variables", async (event, keys) => {
  const result = {};
  keys.forEach((key) => {
    result[key] = process.env[key] || "";
  });
  return result;
});

ipcMain.handle("save-env-variables", async (event, variables) => {
  try {
    let envContent = fs.readFileSync(
      path.join(__dirname, "..", ".env"),
      "utf8",
    );

    Object.keys(variables).forEach((key) => {
      const regex = new RegExp(`^${key}=.*$`, "m");
      if (envContent.match(regex)) {
        // Update existing variable
        envContent = envContent.replace(regex, `${key}=${variables[key]}`);
      } else {
        // Add new variable
        envContent += `\n${key}=${variables[key]}`;
      }
    });

    fs.writeFileSync(path.join(__dirname, "..", ".env"), envContent);

    // Reload environment variables
    Object.keys(variables).forEach((key) => {
      process.env[key] = variables[key];
    });

    return { success: true };
  } catch (error) {
    console.error("Error saving environment variables:", error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle("connect-to-capital", async (event, credentials) => {
  try {
    // Use the credentials to authenticate with Capital.com
    const response = await axios.post(
      "https://demo-api-capital.backend-capital.com/api/v1/session",
      {
        identifier: credentials.identifier,
        password: credentials.password,
      },
      {
        headers: {
          "X-CAP-API-KEY": credentials.key,
          "Content-Type": "application/json",
        },
      },
    );

    // Store the session token for future requests
    global.capitalSession = {
      token: response.data.session.token,
      accountId: response.data.accounts[0].accountId,
    };

    return { success: true, accountId: global.capitalSession.accountId };
  } catch (error) {
    console.error(
      "Error connecting to Capital.com:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

ipcMain.handle("get-account-info", async (event) => {
  try {
    if (!global.capitalSession) {
      return { success: false, error: "Not connected to Capital.com" };
    }

    const response = await axios.get(
      `https://demo-api-capital.backend-capital.com/api/v1/accounts/${global.capitalSession.accountId}`,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
        },
      },
    );

    return {
      success: true,
      accountInfo: {
        accountId: response.data.accountId,
        accountName: response.data.accountName,
        accountType: response.data.accountType,
        balance: response.data.balance,
        currency: response.data.currency,
        profitLoss: response.data.profitLoss,
        available: response.data.available,
      },
    };
  } catch (error) {
    console.error(
      "Error getting account info:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

ipcMain.handle("get-positions", async (event) => {
  try {
    if (!global.capitalSession) {
      return { success: false, error: "Not connected to Capital.com" };
    }

    const response = await axios.get(
      `https://demo-api-capital.backend-capital.com/api/v1/positions?accountId=${global.capitalSession.accountId}`,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
        },
      },
    );

    return { success: true, positions: response.data.positions || [] };
  } catch (error) {
    console.error(
      "Error getting positions:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

ipcMain.handle("get-orders", async (event) => {
  try {
    if (!global.capitalSession) {
      return { success: false, error: "Not connected to Capital.com" };
    }

    const response = await axios.get(
      `https://demo-api-capital.backend-capital.com/api/v1/workingorders?accountId=${global.capitalSession.accountId}`,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
        },
      },
    );

    return { success: true, orders: response.data.workingOrders || [] };
  } catch (error) {
    console.error(
      "Error getting orders:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

ipcMain.handle("execute-trade", async (event, tradeData) => {
  try {
    if (!global.capitalSession) {
      return { success: false, error: "Not connected to Capital.com" };
    }

    const response = await axios.post(
      `https://demo-api-capital.backend-capital.com/api/v1/positions`,
      tradeData,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
          "Content-Type": "application/json",
        },
      },
    );

    return { success: true, dealReference: response.data.dealReference };
  } catch (error) {
    console.error(
      "Error executing trade:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

ipcMain.handle("close-position", async (event, positionId) => {
  try {
    if (!global.capitalSession) {
      return { success: false, error: "Not connected to Capital.com" };
    }

    // Get the position first to determine the direction
    const posResponse = await axios.get(
      `https://demo-api-capital.backend-capital.com/api/v1/positions/${positionId}`,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
        },
      },
    );

    const position = posResponse.data;

    // Create close request (opposite direction to open)
    const closeData = {
      dealId: positionId,
      direction: position.direction === "BUY" ? "SELL" : "BUY",
      size: position.size,
      orderType: "MARKET",
    };

    const response = await axios.delete(
      `https://demo-api-capital.backend-capital.com/api/v1/positions/${positionId}`,
      {
        headers: {
          "X-SECURITY-TOKEN": global.capitalSession.token,
          CST: global.capitalSession.accountId,
          "Content-Type": "application/json",
        },
        data: closeData,
      },
    );

    return { success: true, dealReference: response.data.dealReference };
  } catch (error) {
    console.error(
      "Error closing position:",
      error.response?.data || error.message,
    );
    return {
      success: false,
      error: error.response?.data?.errorCode || error.message,
    };
  }
});

// Bot control
ipcMain.on("start-bot", (event, symbol, timeframe) => {
  if (botRunning) return;

  botRunning = true;
  botStatus.active = true;
  botStatus.startTime = new Date();
  botStatus.currentSymbol = symbol;
  botStatus.currentTimeframe = timeframe;

  console.log(`Bot started trading ${symbol} on ${timeframe} timeframe`);

  // In a real implementation, this would start a background trading process
  // For now, we'll just update the status
});

ipcMain.on("stop-bot", (event) => {
  botRunning = false;
  botStatus.active = false;
  console.log("Bot stopped");
});

ipcMain.handle("get-bot-stats", (event) => {
  return botStatus;
});

// Add keyboard shortcut to toggle fullscreen (F11)
app.on("browser-window-created", (event, window) => {
  window.on("ready-to-show", () => {
    window.webContents.on("before-input-event", (event, input) => {
      if (input.key === "F11") {
        window.setFullScreen(!window.isFullScreen());
      }
      // Allow Escape key to exit fullscreen but not close the app
      if (input.key === "Escape" && window.isFullScreen()) {
        window.setFullScreen(false);
        event.preventDefault();
      }
    });
  });
});

// Prevent accidental exits with Alt+F4 or other system shortcuts
app.on("before-quit", (event) => {
  if (mainWindow && mainWindow.isFullScreen()) {
    // Show a confirmation dialog
    const { dialog } = require("electron");
    const choice = dialog.showMessageBoxSync(mainWindow, {
      type: "question",
      buttons: ["Yes", "No"],
      title: "Confirm Exit",
      message: "Are you sure you want to exit MAGUS PRIME X?",
    });

    if (choice === 1) {
      event.preventDefault();
    }
  }
});

app.on("ready", () => {
  // Start the Flask backend
  flaskProcess = startFlaskBackend();

  // Dev tools in development environment
  if (process.env.NODE_ENV === "development") {
    const {
      default: installExtension,
      REACT_DEVELOPER_TOOLS,
    } = require("electron-devtools-installer");
    installExtension(REACT_DEVELOPER_TOOLS)
      .then((name) => console.log(`Added Extension: ${name}`))
      .catch((err) => console.log("An error occurred: ", err));
  }

  // Skip the splash screen and go directly to the dashboard for testing
  createMainWindow();
  mainWindow.show();

  // Uncomment this to use the splash screen in production
  // createSplashWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow === null) {
    createMainWindow();
  }
});
