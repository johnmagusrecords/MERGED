// MAGUS PRIME X Electron Desktop App
const { app, BrowserWindow, Menu, Tray, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const url = require("url");

// Keep a global reference to prevent garbage collection
let mainWindow;
let tray = null;
let flaskProcess = null;
let isQuitting = false;

// Flask server URL
const serverUrl = "http://localhost:5000";

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, "assets", "icon.ico"),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
    },
    autoHideMenuBar: true,
    show: false, // Don't show until loaded
    backgroundColor: "#121212",
  });

  // Load the splash screen first
  mainWindow.loadFile(path.join(__dirname, "splash.html"));

  // Show when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  // Start Flask backend
  startFlaskServer();

  // Create tray icon
  createTray();

  // Emitted when the window is closed
  mainWindow.on("closed", function () {
    mainWindow = null;
  });

  // Handle window close event - minimize to tray instead of quitting
  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
    return true;
  });
}

// Start the Flask server as a child process
function startFlaskServer() {
  // Find Python path
  const pythonPath = "python"; // Using system Python

  // Path to the Flask app
  const flaskAppPath = path.join(app.getAppPath(), "..", "web_interface.py");

  console.log(`Starting Flask server from: ${flaskAppPath}`);

  // Spawn the Flask process
  flaskProcess = spawn(pythonPath, [flaskAppPath], {
    stdio: "pipe",
  });

  // Handle stdout
  flaskProcess.stdout.on("data", (data) => {
    console.log(`Flask stdout: ${data}`);

    // If we see the "Running on" message, the server is ready
    if (data.toString().includes("Running on http://")) {
      setTimeout(() => {
        // Wait a bit to make sure the server is fully ready
        loadDashboard();
      }, 2000);
    }
  });

  // Handle stderr
  flaskProcess.stderr.on("data", (data) => {
    console.error(`Flask stderr: ${data}`);
  });

  // Handle process exit
  flaskProcess.on("exit", (code, signal) => {
    console.log(`Flask process exited with code ${code} and signal ${signal}`);
    if (code !== 0 && !isQuitting) {
      dialog.showErrorBox(
        "Server Error",
        "The MAGUS PRIME X server has stopped unexpectedly. The application will now close.",
      );
      app.quit();
    }
  });
}

// Load the actual dashboard after the Flask server starts
function loadDashboard() {
  mainWindow.loadURL(serverUrl);

  // Handle load errors
  mainWindow.webContents.on("did-fail-load", () => {
    console.log("Failed to load dashboard, retrying...");
    // Retry after a short delay
    setTimeout(() => {
      mainWindow.loadURL(serverUrl);
    }, 1000);
  });
}

// Create the tray icon and context menu
function createTray() {
  tray = new Tray(path.join(__dirname, "assets", "icon.ico"));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: "Open Dashboard",
      click: () => {
        mainWindow.show();
      },
    },
    {
      label: "Restart Server",
      click: () => {
        restartFlaskServer();
      },
    },
    { type: "separator" },
    {
      label: "Quit",
      click: () => {
        isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setToolTip("MAGUS PRIME X Trading Bot");
  tray.setContextMenu(contextMenu);

  // Double-click on tray icon to show the window
  tray.on("double-click", () => {
    mainWindow.show();
  });
}

// Restart the Flask server if needed
function restartFlaskServer() {
  if (flaskProcess) {
    flaskProcess.kill();
    startFlaskServer();
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.on("ready", createWindow);

// Quit when all windows are closed.
app.on("window-all-closed", function () {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", function () {
  if (mainWindow === null) {
    createWindow();
  }
});

// Clean up before quitting
app.on("before-quit", () => {
  isQuitting = true;
  // Kill the Flask server
  if (flaskProcess) {
    flaskProcess.kill();
  }
});
