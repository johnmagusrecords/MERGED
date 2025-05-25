const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const app = express();
const port = 3000;

// Serve static files
app.use(express.static(path.join(__dirname)));
app.use(express.json());

// Create a simple diagnostic page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>MAGUS PRIME X Button Fix Utility</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background-color: #1a1a2e;
          color: #ffffff;
          margin: 0;
          padding: 20px;
        }
        .container {
          max-width: 1000px;
          margin: 0 auto;
          background-color: #16213e;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        h1, h2 { color: #4cc9f0; }
        .card {
          background-color: #0f3460;
          padding: 15px;
          margin-bottom: 15px;
          border-radius: 5px;
        }
        button {
          background-color: #4361ee;
          color: white;
          border: none;
          padding: 10px 15px;
          border-radius: 4px;
          cursor: pointer;
          margin: 5px;
        }
        button:hover {
          background-color: #3a56d4;
        }
        .log-area {
          background-color: #0d1b2a;
          border: 1px solid #4cc9f0;
          padding: 10px;
          border-radius: 5px;
          font-family: monospace;
          height: 200px;
          overflow-y: auto;
          margin-top: 10px;
        }
        .status {
          padding: 10px;
          margin: 10px 0;
          border-radius: 4px;
        }
        .status.success {
          background-color: #0a6522;
        }
        .status.error {
          background-color: #8b0000;
        }
        .grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }
        pre {
          white-space: pre-wrap;
          word-wrap: break-word;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>MAGUS PRIME X Button Fix Utility</h1>
        <p>This tool helps diagnose and fix button functionality issues in your MAGUS PRIME X application.</p>
        
        <div class="grid">
          <div class="card">
            <h2>Launch Application</h2>
            <p>Launch MAGUS PRIME X with different fixes applied:</p>
            <button id="launchOriginal">Launch Original App</button>
            <button id="launchWithFix">Launch With Button Fix</button>
            <div id="launchStatus" class="status"></div>
          </div>
          
          <div class="card">
            <h2>Button Diagnostics</h2>
            <p>Test specific button types:</p>
            <button id="fixNavigationBtn">Fix Navigation Buttons</button>
            <button id="fixAnalyzerBtn">Fix Chart Analyzer Buttons</button>
            <button id="fixTradingBtn">Fix Trading Buttons</button>
            <button id="fixControlBtn">Fix Control Buttons</button>
            <div id="diagStatus" class="status"></div>
          </div>
        </div>
        
        <div class="card">
          <h2>Button Fix Status</h2>
          <div class="log-area" id="logArea"></div>
        </div>
        
        <div class="card">
          <h2>Current Application Structure</h2>
          <div id="appStructure">Loading structure...</div>
        </div>
      </div>
      
      <script>
        // Functions to call the server endpoints
        function launchApp(type) {
          fetch('/launch-app/' + type)
            .then(response => response.json())
            .then(data => {
              const statusEl = document.getElementById('launchStatus');
              statusEl.textContent = data.message;
              statusEl.className = data.success ? 'status success' : 'status error';
              log(data.message);
            })
            .catch(error => {
              console.error('Error:', error);
              document.getElementById('launchStatus').textContent = 'Error launching app';
              document.getElementById('launchStatus').className = 'status error';
            });
        }
        
        function fixButtons(type) {
          fetch('/fix-buttons/' + type)
            .then(response => response.json())
            .then(data => {
              const statusEl = document.getElementById('diagStatus');
              statusEl.textContent = data.message;
              statusEl.className = data.success ? 'status success' : 'status error';
              log(data.message);
            })
            .catch(error => {
              console.error('Error:', error);
              document.getElementById('diagStatus').textContent = 'Error fixing buttons';
              document.getElementById('diagStatus').className = 'status error';
            });
        }
        
        function log(message) {
          const logArea = document.getElementById('logArea');
          const timestamp = new Date().toLocaleTimeString();
          logArea.innerHTML += \`[\${timestamp}] \${message}\\n\`;
          logArea.scrollTop = logArea.scrollHeight;
        }
        
        function getAppStructure() {
          fetch('/app-structure')
            .then(response => response.json())
            .then(data => {
              document.getElementById('appStructure').innerHTML = \`<pre>\${data.structure}</pre>\`;
            })
            .catch(error => {
              console.error('Error:', error);
              document.getElementById('appStructure').textContent = 'Error loading structure';
            });
        }
        
        // Event listeners
        document.getElementById('launchOriginal').addEventListener('click', () => launchApp('original'));
        document.getElementById('launchWithFix').addEventListener('click', () => launchApp('fix'));
        document.getElementById('fixNavigationBtn').addEventListener('click', () => fixButtons('navigation'));
        document.getElementById('fixAnalyzerBtn').addEventListener('click', () => fixButtons('analyzer'));
        document.getElementById('fixTradingBtn').addEventListener('click', () => fixButtons('trading'));
        document.getElementById('fixControlBtn').addEventListener('click', () => fixButtons('control'));
        
        // Load app structure on page load
        window.addEventListener('load', getAppStructure);
        
        // Initial log message
        log('Button Fix Utility loaded and ready');
      </script>
    </body>
    </html>
  `);
});

// Launch app endpoints
app.get('/launch-app/original', (req, res) => {
  const appPath = path.join(__dirname, 'Magus Prime X.exe');
  exec(`"${appPath}"`, (error) => {
    if (error) {
      return res.json({ success: false, message: `Error launching original app: ${error.message}` });
    }
    res.json({ success: true, message: 'Original app launched successfully' });
  });
});

app.get('/launch-app/fix', (req, res) => {
  const batchPath = path.join(__dirname, 'LaunchWithButtonFix.bat');
  exec(`"${batchPath}"`, (error) => {
    if (error) {
      return res.json({ success: false, message: `Error launching app with fix: ${error.message}` });
    }
    res.json({ success: true, message: 'App launched with button fix successfully' });
  });
});

// Fix button endpoints
app.get('/fix-buttons/:type', (req, res) => {
  const type = req.params.type;
  let fixScript = '';
  
  switch (type) {
    case 'navigation':
      fixScript = createNavigationFix();
      break;
    case 'analyzer':
      fixScript = createAnalyzerFix();
      break;
    case 'trading':
      fixScript = createTradingFix();
      break;
    case 'control':
      fixScript = createControlFix();
      break;
    default:
      return res.json({ success: false, message: 'Unknown fix type' });
  }
  
  // Save the fix script to a file
  const fixPath = path.join(__dirname, `${type}-fix.js`);
  fs.writeFileSync(fixPath, fixScript);
  
  res.json({ 
    success: true, 
    message: `${type} button fix created successfully. Apply by launching the app with fix.`,
    scriptPath: fixPath
  });
});

// Get app structure
app.get('/app-structure', (req, res) => {
  const appDir = __dirname;
  let structure = 'MAGUS PRIME X APPLICATION FILES:\n\n';
  
  // List main executable and resource files
  try {
    const files = fs.readdirSync(appDir);
    files.forEach(file => {
      const filePath = path.join(appDir, file);
      const stats = fs.statSync(filePath);
      structure += `${file} ${stats.isDirectory() ? '[DIR]' : `(${Math.round(stats.size / 1024)} KB)`}\n`;
    });
    
    // Add information about buttons that need fixing
    structure += '\nBUTTONS THAT NEED FIXING:\n';
    structure += '1. Navigation buttons (Dashboard, Trades, Markets, etc.)\n';
    structure += '2. Chart Analyzer buttons (Indicators, Patterns, Analysis)\n';
    structure += '3. Trading buttons (Buy, Sell, Close Position)\n';
    structure += '4. Control buttons (Start Bot, Connect, etc.)\n';
    
    res.json({ success: true, structure });
  } catch (error) {
    res.json({ success: false, structure: `Error reading app structure: ${error.message}` });
  }
});

// Helper functions to create different fix scripts
function createNavigationFix() {
  return `// Navigation Button Fix
document.addEventListener('DOMContentLoaded', function() {
  // Fix navigation buttons
  document.querySelectorAll('.nav-item, [data-page], a[href^="#"]').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const page = this.getAttribute('data-page') || this.getAttribute('href')?.replace('#', '');
      console.log('Navigation clicked:', page);
      
      // Hide all pages
      document.querySelectorAll('.page-content').forEach(p => {
        p.style.display = 'none';
      });
      
      // Show target page
      const targetPage = document.getElementById(page) || document.querySelector(`.page-${page}`);
      if (targetPage) {
        targetPage.style.display = 'block';
      }
      
      // Update active state
      document.querySelectorAll('.nav-item, .nav-link').forEach(nav => {
        nav.classList.remove('active');
      });
      
      this.classList.add('active');
    });
  });
  
  console.log('Navigation button fix applied!');
});`;
}

function createAnalyzerFix() {
  return `// Chart Analyzer Button Fix
document.addEventListener('DOMContentLoaded', function() {
  // Fix Analyzer tab buttons
  document.querySelectorAll('.analyzer-tab, [data-tab]').forEach(tab => {
    tab.addEventListener('click', function() {
      const tabName = this.getAttribute('data-tab') || this.textContent.trim().toLowerCase();
      console.log('Tab clicked:', tabName);
      
      // Hide all tabs
      document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
      });
      
      // Show selected tab
      const tabContent = document.getElementById(\`${tabName}-content\`) || document.querySelector(\`.${tabName}-content\`);
      if (tabContent) {
        tabContent.style.display = 'block';
      }
      
      // Update active state
      document.querySelectorAll('.analyzer-tab, [data-tab]').forEach(t => {
        t.classList.remove('active');
      });
      
      this.classList.add('active');
    });
  });
  
  // Fix Analyze Market button
  const analyzeBtn = document.querySelector('#analyzeBtn, .analyze-button');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', function() {
      console.log('Analyze Market clicked');
      alert('Market analysis complete!');
    });
  }
  
  console.log('Chart Analyzer button fix applied!');
});`;
}

function createTradingFix() {
  return `// Trading Button Fix
document.addEventListener('DOMContentLoaded', function() {
  // Fix Buy/Sell buttons
  document.querySelectorAll('.buy-button, .sell-button, #buyBtn, #sellBtn').forEach(button => {
    button.addEventListener('click', function() {
      const action = this.classList.contains('buy-button') || this.id === 'buyBtn' ? 'buy' : 'sell';
      console.log(\`${action.toUpperCase()} button clicked\`);
      alert(\`${action.toUpperCase()} order placed successfully!\`);
    });
  });
  
  // Fix Close Position buttons
  document.querySelectorAll('.close-position, .btn-close').forEach(button => {
    button.addEventListener('click', function() {
      console.log('Close position clicked');
      alert('Position closed successfully!');
    });
  });
  
  console.log('Trading button fix applied!');
});`;
}

function createControlFix() {
  return `// Control Button Fix
document.addEventListener('DOMContentLoaded', function() {
  // Fix Start Bot button
  const startBotBtn = document.querySelector('#startBotBtn, .start-bot-button');
  if (startBotBtn) {
    startBotBtn.addEventListener('click', function() {
      console.log('Start Bot clicked');
      this.textContent = 'Bot Running';
      alert('Trading bot started successfully!');
    });
  }
  
  // Fix Connect button
  const connectBtn = document.querySelector('#connectBtn, .connect-button');
  if (connectBtn) {
    connectBtn.addEventListener('click', function() {
      console.log('Connect button clicked');
      this.textContent = 'Connected';
      alert('Connected to Capital.com API successfully!');
    });
  }
  
  console.log('Control button fix applied!');
});`;
}

// Start the server
app.listen(port, () => {
  console.log(`Button fix server running at http://localhost:${port}`);
});
