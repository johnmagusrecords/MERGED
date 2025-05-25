const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Initialize store
const store = new Store();

let mainWindow;
let pythonProcess;
let isDevMode = process.env.NODE_ENV === 'development';

function createWindow() {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 1024,
        minHeight: 768,
        icon: path.join(__dirname, 'assets/icon.png'),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        frame: false,
        backgroundColor: '#0a0a0a'
    });

    // Load the startup animation
    mainWindow.loadFile('startup_animation.html');

    // After animation completes, load the main application
    setTimeout(() => {
        mainWindow.loadFile('magus_prime_x_unified.html');
    }, 5000); // 5 seconds delay for the animation

    // Open DevTools in development mode
    if (isDevMode) {
        mainWindow.webContents.openDevTools();
    }

    // Start Python backend
    startPythonBackend();

    // Check for updates
    autoUpdater.checkForUpdatesAndNotify();
}

function startPythonBackend() {
    // Start the Python trading bot
    pythonProcess = spawn('python', ['trading_bot.py'], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data}`);
        mainWindow.webContents.send('python-output', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
        mainWindow.webContents.send('python-error', data.toString());
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        mainWindow.webContents.send('python-exit', code);
    });
}

// Window controls
ipcMain.on('minimize-window', () => {
    mainWindow.minimize();
});

ipcMain.on('maximize-window', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});

ipcMain.on('close-window', () => {
    mainWindow.close();
});

// Trading bot controls
ipcMain.on('start-bot', () => {
    if (!pythonProcess) {
        startPythonBackend();
    }
});

ipcMain.on('stop-bot', () => {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
});

// Capital.com API credentials
ipcMain.on('save-credentials', (event, credentials) => {
    store.set('capital-credentials', credentials);
});

ipcMain.on('get-credentials', (event) => {
    event.reply('credentials', store.get('capital-credentials'));
});

// Auto-updater events
autoUpdater.on('update-available', () => {
    mainWindow.webContents.send('update-available');
});

autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-downloaded');
});

ipcMain.on('install-update', () => {
    autoUpdater.quitAndInstall();
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (pythonProcess) {
            pythonProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Error handling
process.on('uncaughtException', (error) => {
    dialog.showErrorBox('Error', error.message);
});

// Custom protocol for deep linking
if (process.defaultApp) {
    if (process.argv.length >= 2) {
        app.setAsDefaultProtocolClient('magusprimex', process.execPath, [path.resolve(process.argv[1])]);
    }
} else {
    app.setAsDefaultProtocolClient('magusprimex');
}

// Handle deep linking
app.on('open-url', (event, url) => {
    event.preventDefault();
    mainWindow.webContents.send('deep-link', url);
});
