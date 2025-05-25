// Constants and Configuration
const CONFIG = {
    DEFAULT_TIMEFRAME: '15m',
    TIMEFRAMES: ['1m', '5m', '15m', '1h', '4h', '1d'],
    COLORS: {
        upColor: '#FFD700',  // Gold
        upBorderColor: '#DAA520',  // Golden rod
        downColor: '#E74C3C',
        downBorderColor: '#C0392B',
        gridColor: 'rgba(255, 255, 255, 0.05)',
        textColor: '#888888',
        backgroundColor: '#1a1a1a',
        borderColor: '#333333'
    }
};

let botRunning = false;
let tradingViewWidget = null;

// Initialize TradingView Widget
function initTradingViewWidget() {
    tradingViewWidget = new TradingView.widget({
        "container_id": "tradingview_chart",
        "autosize": true,
        "symbol": "CAPITALCOM:BTCUSD",
        "interval": "15",
        "timezone": "exchange",
        "theme": "dark",
        "style": "1",
        "toolbar_bg": "#1a1a1a",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "save_image": true,
        "studies": [
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
            "AwesomeOscillator@tv-basicstudies"
        ],
        "show_popup_button": true,
        "popup_width": "1000",
        "popup_height": "650",
        "locale": "en"
    });
}

// Chart Size Controls
function toggleChartSize(action) {
    const chartContainer = document.getElementById('tradingview_chart');
    if (action === 'maximize') {
        chartContainer.style.height = 'calc(100vh - 200px)';
    } else {
        chartContainer.style.height = '600px';
    }
    if (tradingViewWidget) {
        tradingViewWidget.resize();
    }
}

// Bot Controls
function toggleBot() {
    const startBtn = document.getElementById('startBot');
    const stopBtn = document.getElementById('stopBot');
    
    if (!botRunning) {
        fetch('/api/bot/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    botRunning = true;
                    startBtn.classList.add('hidden');
                    stopBtn.classList.remove('hidden');
                    showNotification('Bot started successfully', 'success');
                }
            })
            .catch(error => showNotification('Failed to start bot', 'error'));
    } else {
        fetch('/api/bot/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    botRunning = false;
                    stopBtn.classList.add('hidden');
                    startBtn.classList.remove('hidden');
                    showNotification('Bot stopped successfully', 'success');
                }
            })
            .catch(error => showNotification('Failed to stop bot', 'error'));
    }
}

// Capital.com Integration
function showLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
}

function hideLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
}

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const apiKey = document.getElementById('apiKey').value;
    const apiPassword = document.getElementById('apiPassword').value;
    
    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey, apiPassword })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideLoginModal();
            showNotification('Successfully connected to Capital.com', 'success');
            updateConnectionStatus(true);
        } else {
            showNotification('Failed to connect: ' + data.error, 'error');
        }
    })
    .catch(error => showNotification('Connection failed', 'error'));
});

// Notification System
function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `fixed bottom-4 right-4 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center ${
        type === 'success' ? 'border-l-4 border-green-500' :
        type === 'error' ? 'border-l-4 border-red-500' :
        'border-l-4 border-blue-500'
    }`;
    
    container.innerHTML = `
        <i class="fas fa-${
            type === 'success' ? 'check-circle text-green-500' :
            type === 'error' ? 'exclamation-circle text-red-500' :
            'info-circle text-blue-500'
        } mr-3"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 5000);
}

// Real-time Data Updates
async function fetchBotData() {
    try {
        const [positionsRes, signalsRes, newsRes] = await Promise.all([
            fetch('http://localhost:5001/api/dashboard/positions'),
            fetch('http://localhost:5001/api/dashboard/signals'),
            fetch('http://localhost:5001/api/dashboard/market_news')
        ]);

        const [positions, signals, news] = await Promise.all([
            positionsRes.json(),
            signalsRes.json(),
            newsRes.json()
        ]);

        updatePositions(positions.positions);
        updateSignals(signals.signals);
        updateNews(news.news);
    } catch (error) {
        console.error('Error fetching bot data:', error);
    }
}

function updatePositions(positions) {
    const tradesContainer = document.getElementById('tradesContent');
    if (!tradesContainer) return;

    const tradesHTML = positions.map(position => `
        <div class="bg-gray-800 rounded-lg p-4 mb-4">
            <div class="flex justify-between items-center">
                <div>
                    <span class="text-lg font-semibold">${position.symbol}</span>
                    <span class="ml-2 px-2 py-1 rounded ${position.direction === 'BUY' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}">
                        ${position.direction}
                    </span>
                    <span class="ml-2 text-sm text-gray-400">${position.trading_mode}</span>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-400">Entry: ${position.entry_price}</div>
                    <div class="text-sm ${position.profit_loss >= 0 ? 'text-yellow-400' : 'text-red-400'}">
                        P/L: ${position.profit_loss.toFixed(2)}
                    </div>
                </div>
            </div>
            <div class="mt-2 flex justify-between items-center">
                <div class="text-sm">
                    <div>TP: ${position.take_profit}</div>
                    <div>SL: ${position.stop_loss}</div>
                </div>
                <div>
                    <button onclick="editTrade(this)" class="px-3 py-1 bg-blue-500/20 text-blue-400 rounded mr-2">Edit</button>
                    <button onclick="closeTrade(this)" class="px-3 py-1 bg-red-500/20 text-red-400 rounded">Close</button>
                </div>
            </div>
        </div>
    `).join('');

    tradesContainer.innerHTML = tradesHTML;
}

function updateSignals(signals) {
    const signalsContainer = document.getElementById('signalsContainer');
    if (!signalsContainer) return;

    const signalsHTML = signals.map(signal => `
        <div class="bg-gray-800 rounded-lg p-4 mb-4">
            <div class="flex justify-between items-center">
                <div>
                    <span class="text-lg font-semibold">${signal.symbol}</span>
                    <span class="ml-2 px-2 py-1 rounded ${signal.action === 'BUY' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}">
                        ${signal.action}
                    </span>
                </div>
                <div class="text-sm text-gray-400">
                    ${signal.mode}
                </div>
            </div>
            <div class="mt-2 text-sm text-gray-400">
                ${signal.reason}
            </div>
        </div>
    `).join('');

    signalsContainer.innerHTML = signalsHTML;
}

function updateNews(news) {
    const newsContainer = document.getElementById('notificationsContent');
    if (!newsContainer) return;

    const newsHTML = news.map(item => `
        <div class="bg-gray-800 rounded-lg p-4 mb-4">
            <div class="flex justify-between items-center">
                <div class="text-lg font-semibold">${item.title}</div>
                <div class="text-sm">
                    <span class="px-2 py-1 rounded ${item.sentiment === 'positive' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}">
                        ${item.sentiment}
                    </span>
                </div>
            </div>
            <div class="mt-2 text-sm text-gray-400">
                ${item.content}
            </div>
            <div class="mt-2 text-xs text-gray-500">
                ${new Date(item.timestamp).toLocaleString()}
            </div>
        </div>
    `).join('');

    newsContainer.innerHTML = newsHTML;
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize TradingView widget
    initTradingViewWidget();
    
    // Start data polling
    fetchBotData();
    setInterval(fetchBotData, 5000);

    // Initialize bot controls
    document.getElementById('startBot').addEventListener('click', toggleBot);
    document.getElementById('stopBot').addEventListener('click', toggleBot);

    // Initialize event listeners
    document.addEventListener('click', (e) => {
        const notificationContainer = document.getElementById('notificationContainer');
        const dropdown = document.getElementById('notificationDropdown');
        
        if (!notificationContainer.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
});

// Navigation Management
function switchTab(tabName) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('hidden');
    });
    
    const selectedContent = document.getElementById(`${tabName}Content`);
    if (selectedContent) {
        selectedContent.classList.remove('hidden');
    }

    if (tabName === 'dashboard' && tradingViewWidget) {
        tradingViewWidget.resize();
    }
}

// Notifications
function toggleNotifications(e) {
    e.stopPropagation();
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.classList.toggle('hidden');
}

function markAllAsRead() {
    const notifications = document.querySelectorAll('#notificationDropdown .notification');
    notifications.forEach(notification => {
        notification.classList.remove('unread');
    });
    document.querySelector('.notification-badge').textContent = '0';
}

// Currency Switcher
function switchCurrency(currency) {
    const currencySymbol = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'AED': 'د.إ'
    }[currency] || '$';
    
    document.querySelectorAll('.currency-value').forEach(element => {
        const value = parseFloat(element.dataset.value);
        const rate = getCurrencyRate(currency);
        const converted = value * rate;
        element.textContent = `${currencySymbol}${converted.toFixed(2)}`;
    });
}

function getCurrencyRate(currency) {
    const rates = {
        'USD': 1,
        'EUR': 0.85,
        'GBP': 0.73,
        'AED': 3.67
    };
    return rates[currency] || 1;
}
