// MAGUS PRIME X Electron Desktop App
const { app, BrowserWindow, Menu, Tray, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const url = require("url");

// Keep a global reference to prevent garbage collection
let mainWindow;
let tray = null;
let isQuitting = false;

// Path to the app HTML file (starting with the animation)
const appPath = path.join(app.getAppPath(), "..", "magus_prime_x_app.html");

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, "assets", "icon.ico"),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: true,
    },
    autoHideMenuBar: true,
    show: false, // Don't show until loaded
    backgroundColor: "#121212",
  });

  // Load the animation/login screen directly
  mainWindow.loadFile(appPath);

  // Show when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

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
});
