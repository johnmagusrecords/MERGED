const { spawn } = require("child_process");

const mainWindow = new BrowserWindow({
  webPreferences: {
    nodeIntegration: true,
    contextIsolation: false,
    webviewTag: true, // Enable webview
  },
});

// Run bot.py when the app starts
const pythonProcess = spawn("python", ["bot.py"], {
  cwd: __dirname,
  stdio: "inherit",
});

// Optional: handle process exit
pythonProcess.on("close", (code) => {
  console.log(`bot.py exited with code ${code}`);
});
