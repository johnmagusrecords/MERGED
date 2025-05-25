// MAGUS PRIME X - Complete Trading Application
// Main application JavaScript

// Global app state
const appState = {
    currentScreen: 'loading', // loading, login, dashboard
    isLoggedIn: false,
    user: null,
    activeSymbol: 'EURUSD',
    activeTimeframe: '1D',
    selectedMarkets: [],
    activeOrders: [],
    chartAnalyzer: null,
    brokerConnection: null,
    autoTrading: null
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('MAGUS PRIME X Initializing...');
    initializeApp();
});

// Main application initialization
function initializeApp() {
    // Create the loading screen
    renderLoadingScreen();
    
    // Check if user is already logged in (from localStorage)
    const username = localStorage.getItem('capital_username');
    const apiKey = localStorage.getItem('capital_apikey');
    
    if (username && apiKey) {
        appState.user = { username, apiKey };
        appState.isLoggedIn = true;
    }
    
    // After a short delay, transition to login or dashboard
    setTimeout(() => {
        if (appState.isLoggedIn) {
            console.log('User found in local storage, loading dashboard...');
            initializeDashboard();
        } else {
            console.log('No user found, showing login screen...');
            initializeLoginScreen();
        }
    }, 2000);
}

// Render the loading screen
function renderLoadingScreen() {
    appState.currentScreen = 'loading';
    const appContainer = document.getElementById('app-container');
    
    appContainer.innerHTML = `
        <div class="loading-overlay">
            <div class="loading-logo">
                <svg width="150" height="150" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#6a11cb" />
                            <stop offset="100%" stop-color="#2575fc" />
                        </linearGradient>
                    </defs>
                    <circle cx="100" cy="100" r="90" fill="none" stroke="url(#gradient)" stroke-width="5" />
                    <text x="100" y="120" font-size="40" text-anchor="middle" fill="url(#gradient)" font-weight="bold">MPRIME</text>
                    <path d="M100,20 L100,50" stroke="url(#gradient)" stroke-width="5" />
                    <path d="M100,150 L100,180" stroke="url(#gradient)" stroke-width="5" />
                    <path d="M20,100 L50,100" stroke="url(#gradient)" stroke-width="5" />
                    <path d="M150,100 L180,100" stroke="url(#gradient)" stroke-width="5" />
                </svg>
            </div>
            <div class="loading-text">Initializing MAGUS PRIME X</div>
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
}

// Initialize the login screen with particles animation
function initializeLoginScreen() {
    appState.currentScreen = 'login';
    const appContainer = document.getElementById('app-container');
    
    appContainer.innerHTML = `
        <div class="login-container">
            <div class="particles-container" id="particles-container"></div>
            <div class="login-content">
                <div class="login-logo">
                    <svg width="120" height="120" viewBox="0 0 200 200">
                        <defs>
                            <linearGradient id="gradient-login" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#6a11cb" />
                                <stop offset="100%" stop-color="#2575fc" />
                            </linearGradient>
                        </defs>
                        <circle cx="100" cy="100" r="90" fill="none" stroke="url(#gradient-login)" stroke-width="5" />
                        <text x="100" y="120" font-size="30" text-anchor="middle" fill="url(#gradient-login)" font-weight="bold">MPRIME</text>
                    </svg>
                </div>
                <h1 class="login-title">MAGUS PRIME X</h1>
                <form class="login-form" id="login-form">
                    <div class="form-group">
                        <label for="username" class="form-label">Capital.com Username</label>
                        <input type="text" id="username" class="form-input" placeholder="Enter your username">
                    </div>
                    <div class="form-group">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" id="password" class="form-input" placeholder="Enter your password">
                    </div>
                    <div class="form-group">
                        <label for="api-key" class="form-label">API Key</label>
                        <input type="text" id="api-key" class="form-input" placeholder="Enter your Capital.com API Key">
                    </div>
                    <button type="submit" class="login-button">Login</button>
                    <div id="login-status" class="login-status"></div>
                </form>
            </div>
        </div>
    `;
    
    // Initialize particles
    initializeParticles();
    
    // Set up login form event listener
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });
}

// Particles animation for login screen
function initializeParticles() {
    const container = document.getElementById('particles-container');
    
    // Create 50 particles
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random size between 2-6px
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        // Random starting position
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        particle.style.left = posX + '%';
        particle.style.top = posY + '%';
        
        // Set random endpoint for X direction
        const xEnd = (Math.random() * 200 - 100); // between -100 and 100
        particle.style.setProperty('--x-end', xEnd + 'px');
        
        // Random animation duration between 3-8s
        const duration = Math.random() * 5 + 3;
        particle.style.animation = `particle-movement ${duration}s infinite`;
        
        // Random delay
        particle.style.animationDelay = (Math.random() * 5) + 's';
        
        container.appendChild(particle);
    }
}

// Handle login form submission
function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const apiKey = document.getElementById('api-key').value;
    const statusElement = document.getElementById('login-status');
    
    // Reset status
    statusElement.textContent = '';
    
    // Validate form
    if (!username || !password || !apiKey) {
        statusElement.style.color = 'var(--danger-color)';
        statusElement.textContent = 'Please fill in all fields';
        return;
    }
    
    // Show connecting status
    statusElement.style.color = 'var(--text-dim)';
    statusElement.textContent = 'Connecting to Capital.com...';
    
    // Save credentials to localStorage
    localStorage.setItem('capital_username', username);
    localStorage.setItem('capital_password', password); // In a real app, don't store plain passwords
    localStorage.setItem('capital_apikey', apiKey);
    
    // Simulate API connection with the Capital.com broker
    setTimeout(() => {
        // Update status
        statusElement.textContent = 'Connected! Loading trading platform...';
        
        // Update app state
        appState.user = { username, apiKey };
        appState.isLoggedIn = true;
        
        // After a short delay, transition to dashboard
        setTimeout(() => {
            initializeDashboard();
        }, 1500);
    }, 2000);
}

// Initialize the dashboard after successful login
function initializeDashboard() {
    appState.currentScreen = 'dashboard';
    const appContainer = document.getElementById('app-container');
    
    // First show loading screen with different message
    appContainer.innerHTML = `
        <div class="loading-overlay">
            <div class="loading-logo">
                <svg width="150" height="150" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#6a11cb" />
                            <stop offset="100%" stop-color="#2575fc" />
                    </linearGradient>
                </defs>
                <circle cx="100" cy="100" r="90" fill="none" stroke="url(#gradient)" stroke-width="5" />
                <text x="100" y="120" font-size="40" text-anchor="middle" fill="url(#gradient)" font-weight="bold">MPRIME</text>
            </svg>
        </div>
        <div class="loading-text">Loading Trading Dashboard...</div>
        <div class="loading-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    
    // Initialize Chart Analyzer Module before rendering
    initializeChartAnalyzer();
    
    // Initialize Capital.com Trading Connection
    initializeCapitalComTrading();
    
    // Render the dashboard UI after a short delay
    setTimeout(() => {
        renderDashboard();
    }, 1500);
}

// Initialize Chart Analyzer Module
function initializeChartAnalyzer() {
    console.log('Initializing Chart Analyzer Module...');
    // Create chart analyzer object with technical indicators and pattern recognition
    appState.chartAnalyzer = {
        // Technical indicators
        indicators: {
            movingAverages: {
                SMA: { periods: [5, 10, 20, 50, 200], values: {}, signal: 'neutral' },
                EMA: { periods: [5, 10, 20, 50, 200], values: {}, signal: 'neutral' },
                calculate: function(data, type, period) {
                    // Implementation of moving average calculation
                    console.log(`Calculating ${type}${period} for ${appState.activeSymbol}`);
                    return Math.random() * 100 + 50; // Simulated value for demo
                },
                update: function(data) {
                    // Update all moving averages with new data
                    this.SMA.periods.forEach(period => {
                        this.SMA.values[period] = this.calculate(data, 'SMA', period);
                    });
                    this.EMA.periods.forEach(period => {
                        this.EMA.values[period] = this.calculate(data, 'EMA', period);
                    });
                    
                    // Determine signal (SMA crossovers)
                    if (this.SMA.values[5] > this.SMA.values[20]) {
                        this.signal = 'bullish';
                    } else if (this.SMA.values[5] < this.SMA.values[20]) {
                        this.signal = 'bearish';
                    } else {
                        this.signal = 'neutral';
                    }
                }
            },
            oscillators: {
                RSI: { period: 14, value: 0, signal: 'neutral' },
                MACD: { 
                    fast: 12, 
                    slow: 26, 
                    signal: 9, 
                    values: { line: 0, signal: 0, histogram: 0 },
                    indication: 'neutral'
                },
                stochastic: { K: 0, D: 0, signal: 'neutral' },
                calculate: function(data) {
                    // Calculate all oscillators
                    this.RSI.value = Math.random() * 100; // Simulated value
                    this.MACD.values.line = Math.random() * 2 - 1;
                    this.MACD.values.signal = Math.random() * 2 - 1;
                    this.MACD.values.histogram = this.MACD.values.line - this.MACD.values.signal;
                    this.stochastic.K = Math.random() * 100;
                    this.stochastic.D = Math.random() * 100;
                    
                    // RSI signal
                    if (this.RSI.value > 70) {
                        this.RSI.signal = 'overbought';
                    } else if (this.RSI.value < 30) {
                        this.RSI.signal = 'oversold';
                    } else {
                        this.RSI.signal = 'neutral';
                    }
                    
                    // MACD signal
                    if (this.MACD.values.histogram > 0 && this.MACD.values.line > 0) {
                        this.MACD.indication = 'bullish';
                    } else if (this.MACD.values.histogram < 0 && this.MACD.values.line < 0) {
                        this.MACD.indication = 'bearish';
                    } else {
                        this.MACD.indication = 'neutral';
                    }
                    
                    // Stochastic signal
                    if (this.stochastic.K > 80 && this.stochastic.D > 80) {
                        this.stochastic.signal = 'overbought';
                    } else if (this.stochastic.K < 20 && this.stochastic.D < 20) {
                        this.stochastic.signal = 'oversold';
                    } else {
                        this.stochastic.signal = 'neutral';
                    }
                }
            },
            volumeIndicators: {
                OBV: 0, // On-Balance Volume
                volumeChange: 0,
                signal: 'neutral',
                calculate: function(data) {
                    this.OBV = Math.random() * 10000;
                    this.volumeChange = Math.random() * 20 - 10;
                    
                    if (this.volumeChange > 5) {
                        this.signal = 'increasing';
                    } else if (this.volumeChange < -5) {
                        this.signal = 'decreasing';
                    } else {
                        this.signal = 'stable';
                    }
                }
            }
        },
        
        // Candlestick patterns
        candlestickPatterns: {
            patterns: [
                { name: 'Doji', signal: 'indecision', detected: false },
                { name: 'Hammer', signal: 'bullish', detected: false },
                { name: 'Hanging Man', signal: 'bearish', detected: false },
                { name: 'Engulfing', signal: 'varies', detected: false, direction: 'none' },
                { name: 'Morning Star', signal: 'bullish', detected: false },
                { name: 'Evening Star', signal: 'bearish', detected: false }
            ],
            detect: function(data) {
                // Reset all patterns
                this.patterns.forEach(pattern => {
                    pattern.detected = false;
                });
                
                // Randomly detect patterns for demonstration
                const randomIndex = Math.floor(Math.random() * this.patterns.length);
                this.patterns[randomIndex].detected = true;
                
                if (this.patterns[randomIndex].name === 'Engulfing') {
                    this.patterns[randomIndex].direction = Math.random() > 0.5 ? 'bullish' : 'bearish';
                }
                
                return this.patterns.filter(pattern => pattern.detected);
            }
        },
        
        // Chart patterns
        chartPatterns: {
            patterns: [
                { name: 'Head and Shoulders', signal: 'bearish', detected: false, completion: 0 },
                { name: 'Inverse Head and Shoulders', signal: 'bullish', detected: false, completion: 0 },
                { name: 'Double Top', signal: 'bearish', detected: false, completion: 0 },
                { name: 'Double Bottom', signal: 'bullish', detected: false, completion: 0 },
                { name: 'Triangle', signal: 'varies', detected: false, type: 'none', completion: 0 },
                { name: 'Channel', signal: 'varies', detected: false, type: 'none', completion: 0 }
            ],
            detect: function(data) {
                // Reset all patterns
                this.patterns.forEach(pattern => {
                    pattern.detected = false;
                    pattern.completion = 0;
                });
                
                // Randomly detect patterns for demonstration
                if (Math.random() > 0.7) {
                    const randomIndex = Math.floor(Math.random() * this.patterns.length);
                    this.patterns[randomIndex].detected = true;
                    this.patterns[randomIndex].completion = Math.random() * 100;
                    
                    if (this.patterns[randomIndex].name === 'Triangle') {
                        const types = ['ascending', 'descending', 'symmetrical'];
                        this.patterns[randomIndex].type = types[Math.floor(Math.random() * types.length)];
                    } else if (this.patterns[randomIndex].name === 'Channel') {
                        const types = ['ascending', 'descending', 'horizontal'];
                        this.patterns[randomIndex].type = types[Math.floor(Math.random() * types.length)];
                    }
                }
                
                return this.patterns.filter(pattern => pattern.detected);
            }
        },
        
        // Support and resistance
        supportResistance: {
            levels: [],
            calculate: function(data) {
                // Clear previous levels
                this.levels = [];
                
                // Generate a few random levels for demonstration
                const basePrice = 100 + Math.random() * 20;
                for (let i = 0; i < 3; i++) {
                    this.levels.push({
                        type: i % 2 === 0 ? 'support' : 'resistance',
                        price: basePrice + (i * 5) + (Math.random() * 2),
                        strength: Math.random()
                    });
                }
                
                return this.levels;
            }
        },
        
        // Analyze market and provide consolidated results
        analyze_market: function(symbol, timeframe) {
            console.log(`Analyzing ${symbol} on ${timeframe} timeframe...`);
            
            // Generate random data for demonstration
            const data = {
                close: Array.from({ length: 100 }, () => Math.random() * 100 + 50),
                high: Array.from({ length: 100 }, () => Math.random() * 100 + 60),
                low: Array.from({ length: 100 }, () => Math.random() * 100 + 40),
                volume: Array.from({ length: 100 }, () => Math.random() * 100000)
            };
            
            // Update indicators
            this.indicators.movingAverages.update(data);
            this.indicators.oscillators.calculate(data);
            this.indicators.volumeIndicators.calculate(data);
            
            // Detect patterns
            const candlestickPatterns = this.candlestickPatterns.detect(data);
            const chartPatterns = this.chartPatterns.detect(data);
            
            // Calculate support/resistance
            const srLevels = this.supportResistance.calculate(data);
            
            // Determine overall signal
            let maSignal = this.indicators.movingAverages.signal;
            let oscillatorSignal = 'neutral';
            
            if (this.indicators.oscillators.RSI.signal === 'oversold' && 
                this.indicators.oscillators.MACD.indication === 'bullish') {
                oscillatorSignal = 'bullish';
            } else if (this.indicators.oscillators.RSI.signal === 'overbought' && 
                       this.indicators.oscillators.MACD.indication === 'bearish') {
                oscillatorSignal = 'bearish';
            }
            
            // Final signal determination
            let overallSignal = 'neutral';
            let signalStrength = 0;
            
            if (maSignal === 'bullish' && oscillatorSignal === 'bullish') {
                overallSignal = 'strong_buy';
                signalStrength = 0.9;
            } else if (maSignal === 'bullish' || oscillatorSignal === 'bullish') {
                overallSignal = 'buy';
                signalStrength = 0.7;
            } else if (maSignal === 'bearish' && oscillatorSignal === 'bearish') {
                overallSignal = 'strong_sell';
                signalStrength = 0.9;
            } else if (maSignal === 'bearish' || oscillatorSignal === 'bearish') {
                overallSignal = 'sell';
                signalStrength = 0.7;
            }
            
            // Adjust based on detected patterns
            if (candlestickPatterns.length > 0) {
                const pattern = candlestickPatterns[0];
                if (pattern.signal === 'bullish' && overallSignal.includes('buy')) {
                    signalStrength += 0.1;
                } else if (pattern.signal === 'bearish' && overallSignal.includes('sell')) {
                    signalStrength += 0.1;
                }
            }
            
            // Compile results
            return {
                symbol: symbol,
                timeframe: timeframe,
                lastUpdated: new Date().toLocaleTimeString(),
                technicalIndicators: {
                    movingAverages: {
                        values: this.indicators.movingAverages.SMA.values,
                        signal: maSignal
                    },
                    oscillators: {
                        rsi: this.indicators.oscillators.RSI.value,
                        macd: this.indicators.oscillators.MACD.values,
                        signal: oscillatorSignal
                    },
                    volume: {
                        obv: this.indicators.volumeIndicators.OBV,
                        change: this.indicators.volumeIndicators.volumeChange,
                        signal: this.indicators.volumeIndicators.signal
                    }
                },
                patterns: {
                    candlestick: candlestickPatterns,
                    chart: chartPatterns
                },
                supportResistance: srLevels,
                tradingSignal: {
                    action: overallSignal,
                    strength: signalStrength,
                    description: this.getSignalDescription(overallSignal, signalStrength)
                }
            };
        },
        
        // Get human-readable description of signal
        getSignalDescription: function(signal, strength) {
            switch(signal) {
                case 'strong_buy':
                    return 'Strong buying opportunity with multiple indicators aligned.';
                case 'buy':
                    return 'Moderate buy signal with some positive indicators.';
                case 'neutral':
                    return 'Market conditions are neutral, no clear direction.';
                case 'sell':
                    return 'Moderate sell signal with some negative indicators.';
                case 'strong_sell':
                    return 'Strong selling opportunity with multiple indicators aligned.';
                default:
                    return 'Analyzing market conditions...';
            }
        }
    };
    
    console.log('Chart Analyzer Module initialized.');
}

// Initialize Capital.com Trading Connection
function initializeCapitalComTrading() {
    console.log('Initializing Capital.com Trading Connection...');
    
    // Get stored credentials
    const username = localStorage.getItem('capital_username');
    const apiKey = localStorage.getItem('capital_apikey');
    
    // Create broker connection object
    appState.brokerConnection = {
        broker: 'Capital.com',
        username: username,
        apiKey: apiKey,
        isConnected: false,
        account: {
            balance: 10000.00, // Demo balance
            currency: 'USD',
            leverage: 30,
            margin: 3333.33,
            equity: 10000.00,
            pnl: 0
        },
        markets: [
            { symbol: 'EURUSD', name: 'EUR/USD', bid: 1.0925, ask: 1.0927, change: 0.15 },
            { symbol: 'GBPUSD', name: 'GBP/USD', bid: 1.2654, ask: 1.2657, change: -0.22 },
            { symbol: 'USDJPY', name: 'USD/JPY', bid: 153.45, ask: 153.48, change: 0.31 },
            { symbol: 'BTCUSD', name: 'Bitcoin', bid: 68254.5, ask: 68298.2, change: 1.75 },
            { symbol: 'US500', name: 'S&P 500', bid: 5234.25, ask: 5235.75, change: 0.42 }
        ],
        activeOrders: [],
        orderHistory: [],
        
        // Connect to broker
        connect: function() {
            console.log(`Connecting to Capital.com as ${this.username}...`);
            
            // Simulate connection delay
            setTimeout(() => {
                this.isConnected = true;
                console.log('Connected to Capital.com successfully!');
                
                // Update UI elements that show connection status
                const statusElements = document.querySelectorAll('.connection-status');
                statusElements.forEach(el => {
                    el.textContent = 'Connected';
                    el.classList.remove('disconnected');
                    el.classList.add('connected');
                });
                
                // Initialize selected markets
                appState.selectedMarkets = this.markets.slice(0, 4);
            }, 1000);
        },
        
        // Disconnect from broker
        disconnect: function() {
            this.isConnected = false;
            console.log('Disconnected from Capital.com');
            
            // Update UI elements
            const statusElements = document.querySelectorAll('.connection-status');
            statusElements.forEach(el => {
                el.textContent = 'Disconnected';
                el.classList.remove('connected');
                el.classList.add('disconnected');
            });
        },
        
        // Place a new order
        placeOrder: function(orderType, symbol, amount, leverage = 30) {
            console.log(`Placing ${orderType} order for ${symbol}, Amount: ${amount}, Leverage: ${leverage}`);
            
            if (!this.isConnected) {
                console.error('Cannot place order: Not connected to broker');
                return { success: false, message: 'Not connected to broker' };
            }
            
            // Get current market data for the symbol
            const market = this.markets.find(m => m.symbol === symbol);
            if (!market) {
                console.error(`Market ${symbol} not found`);
                return { success: false, message: 'Market not found' };
            }
            
            // Calculate entry price based on order type
            const entryPrice = orderType === 'buy' ? market.ask : market.bid;
            
            // Generate a unique order ID
            const orderId = 'order_' + Date.now();
            
            // Create the new order
            const newOrder = {
                id: orderId,
                type: orderType,
                symbol: symbol,
                amount: amount,
                leverage: leverage,
                entryPrice: entryPrice,
                openTime: new Date(),
                status: 'open',
                pnl: 0,
                currentPrice: entryPrice
            };
            
            // Add to active orders
            this.activeOrders.push(newOrder);
            
            // Update appState
            appState.activeOrders = this.activeOrders;
            
            console.log(`Order placed: ${orderType} ${symbol} at ${entryPrice}`);
            
            // Return success
            return { 
                success: true, 
                message: `${orderType.toUpperCase()} order for ${symbol} placed successfully`,
                order: newOrder
            };
        },
        
        // Close an existing order
        closeOrder: function(orderId) {
            console.log(`Closing order ${orderId}...`);
            
            if (!this.isConnected) {
                console.error('Cannot close order: Not connected to broker');
                return { success: false, message: 'Not connected to broker' };
            }
            
            // Find the order
            const orderIndex = this.activeOrders.findIndex(o => o.id === orderId);
            if (orderIndex === -1) {
                console.error(`Order ${orderId} not found`);
                return { success: false, message: 'Order not found' };
            }
            
            const order = this.activeOrders[orderIndex];
            
            // Get current market data
            const market = this.markets.find(m => m.symbol === order.symbol);
            if (!market) {
                console.error(`Market ${order.symbol} not found`);
                return { success: false, message: 'Market data not available' };
            }
            
            // Calculate exit price based on order type
            const exitPrice = order.type === 'buy' ? market.bid : market.ask;
            
            // Calculate P&L
            let pnl = 0;
            if (order.type === 'buy') {
                pnl = (exitPrice - order.entryPrice) * order.amount * order.leverage;
            } else {
                pnl = (order.entryPrice - exitPrice) * order.amount * order.leverage;
            }
            
            // Update the order
            order.exitPrice = exitPrice;
            order.closeTime = new Date();
            order.status = 'closed';
            order.pnl = pnl;
            
            // Move to order history
            this.orderHistory.push(order);
            
            // Remove from active orders
            this.activeOrders.splice(orderIndex, 1);
            
            // Update account balance
            this.account.balance += pnl;
            this.account.pnl += pnl;
            
            // Update appState
            appState.activeOrders = this.activeOrders;
            
            console.log(`Order ${orderId} closed with P&L: ${pnl.toFixed(2)}`);
            
            // Return success
            return { 
                success: true, 
                message: `Order closed with ${pnl >= 0 ? 'profit' : 'loss'} of ${Math.abs(pnl).toFixed(2)}`,
                pnl: pnl
            };
        },
        
        // Update prices for all markets and active orders
        updatePrices: function() {
            if (!this.isConnected) return;
            
            // Update market prices with small random changes
            this.markets.forEach(market => {
                const changePercent = (Math.random() * 0.002) - 0.001; // -0.1% to +0.1%
                const priceChange = market.bid * changePercent;
                
                market.bid += priceChange;
                market.ask = market.bid + (market.ask - market.bid); // Maintain spread
                
                // Update daily change occasionally
                if (Math.random() > 0.7) {
                    market.change += (Math.random() * 0.2) - 0.1;
                }
            });
            
            // Update active orders P&L
            this.activeOrders.forEach(order => {
                const market = this.markets.find(m => m.symbol === order.symbol);
                if (market) {
                    // Update current price
                    order.currentPrice = order.type === 'buy' ? market.bid : market.ask;
                    
                    // Calculate P&L
                    if (order.type === 'buy') {
                        order.pnl = (order.currentPrice - order.entryPrice) * order.amount * order.leverage;
                    } else {
                        order.pnl = (order.entryPrice - order.currentPrice) * order.amount * order.leverage;
                    }
                }
            });
            
            // Update UI if needed
            if (appState.currentScreen === 'dashboard') {
                updateMarketData();
                updateActiveOrders();
            }
        }
    };
    
    // If we have credentials, connect to broker
    if (username && apiKey) {
        appState.brokerConnection.connect();
        
        // Start price updates
        setInterval(() => {
            appState.brokerConnection.updatePrices();
        }, 3000);
    } else {
        console.warn('No Capital.com credentials found. Trading features will be limited.');
    }
    
    console.log('Capital.com Trading Connection initialized.');
}

// Render the dashboard UI
function renderDashboard() {
    console.log('Rendering dashboard...');
    const appContainer = document.getElementById('app-container');
    
    appContainer.innerHTML = `
        <div class="dashboard-container">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="logo">
                        <svg width="80" height="80" viewBox="0 0 200 200">
                            <defs>
                                <linearGradient id="gradient-sidebar" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#6a11cb" />
                                    <stop offset="100%" stop-color="#2575fc" />
                                </linearGradient>
                            </defs>
                            <circle cx="100" cy="100" r="90" fill="none" stroke="url(#gradient-sidebar)" stroke-width="5" />
                            <text x="100" y="120" font-size="30" text-anchor="middle" fill="url(#gradient-sidebar)" font-weight="bold">MPRIME</text>
                        </svg>
                    </div>
                    <div class="sidebar-title">MAGUS PRIME X</div>
                </div>
                <ul class="sidebar-items">
                    <li class="sidebar-item active" data-page="dashboard">
                        <i class="fas fa-chart-line"></i> Dashboard
                    </li>
                    <li class="sidebar-item" data-page="markets">
                        <i class="fas fa-globe"></i> Markets
                    </li>
                    <li class="sidebar-item" data-page="portfolio">
                        <i class="fas fa-briefcase"></i> Portfolio
                    </li>
                    <li class="sidebar-item" data-page="analyzer">
                        <i class="fas fa-search"></i> Chart Analyzer
                    </li>
                    <li class="sidebar-item" data-page="settings">
                        <i class="fas fa-cog"></i> Settings
                    </li>
                </ul>
                
                <!-- Auto Trading Section -->
                <div class="sidebar-section">
                    <h3>Auto Trading</h3>
                    <div class="auto-trading-control">
                        <span>Auto Trading</span>
                        <label class="cyberpunk-checkbox">
                            <input type="checkbox" id="auto-trading-toggle">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="auto-trading-status">
                        <div class="trading-status">
                            <span>Status: </span>
                            <span id="trading-status-text">Off</span>
                        </div>
                        <div class="progress-bar animated" id="trading-progress">
                            <div class="fill" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <div class="dashboard-header">
                    <div>
                        <h1 class="dashboard-title">Trading Dashboard</h1>
                        <div class="dashboard-subtitle">
                            Connected to Capital.com as ${appState.user.username}
                            <span class="connection-status connected">Connected</span>
                        </div>
                    </div>
                    <div class="dashboard-actions">
                        <div class="notification-badge-modern">
                            <i class="fas fa-bell"></i>
                            <span class="badge">3</span>
                        </div>
                        <span>Balance: $${appState.brokerConnection.account.balance.toFixed(2)} ${appState.brokerConnection.account.currency}</span>
                    </div>
                </div>
                
                <!-- Market Overview -->
                <div class="market-overview" id="market-overview">
                    <!-- Market cards will be rendered here -->
                </div>
                
                <!-- Chart Section -->
                <div class="chart-section glass-card">
                    <div class="chart-header">
                        <div class="chart-title">
                            <span id="active-symbol">${appState.activeSymbol}</span>
                            <span id="active-timeframe">${appState.activeTimeframe}</span>
                        </div>
                        <div class="chart-controls">
                            <button class="neon-button" data-timeframe="1H">1H</button>
                            <button class="neon-button" data-timeframe="4H">4H</button>
                            <button class="neon-button" data-timeframe="1D">1D</button>
                            <button class="neon-button" data-timeframe="1W">1W</button>
                        </div>
                    </div>
                    <div class="chart-container card-3d-container" id="tradingview-widget">
                        <div class="card-3d">
                            <!-- TradingView Widget will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <!-- Analysis Results -->
                <div class="chart-section glass-card">
                    <div class="chart-header">
                        <div class="chart-title">Technical Analysis</div>
                        <button class="magnetic-button ripple-button" id="analyze-button">
                            <i class="fas fa-search-dollar"></i> Analyze Market
                        </button>
                    </div>
                    <div class="analysis-results" id="analysis-results">
                        <div class="futuristic-loader"></div>
                        <p>Click "Analyze Market" to perform technical analysis</p>
                    </div>
                </div>
                
                <!-- Trading Controls -->
                <div class="chart-section glass-card">
                    <div class="chart-header">
                        <div class="chart-title">Trading Controls</div>
                    </div>
                    <div class="trading-controls">
                        <div class="trading-column">
                            <div class="trade-buttons">
                                <button class="neon-button green" id="buy-button">BUY</button>
                                <button class="neon-button red" id="sell-button">SELL</button>
                            </div>
                            <div class="trading-form">
                                <div class="glowing-input">
                                    <input type="number" id="trade-amount" value="100" placeholder=" ">
                                    <label for="trade-amount">Amount (USD)</label>
                                </div>
                                <div class="glowing-input">
                                    <input type="number" id="trade-leverage" value="30" placeholder=" ">
                                    <label for="trade-leverage">Leverage</label>
                                </div>
                                <div class="tooltip">
                                    <i class="fas fa-info-circle"></i>
                                    <span class="tooltip-text">Higher leverage increases both potential profit and risk</span>
                                </div>
                            </div>
                            <div class="range-control">
                                <label>Risk Level:</label>
                                <input type="range" min="1" max="10" value="5" class="sci-fi-slider" id="risk-level">
                            </div>
                        </div>
                        <div class="trading-column">
                            <h3>Trading Signal</h3>
                            <div class="signal-box glass-card" id="trading-signal">
                                <div class="signal-strength">Analyzing Market...</div>
                                <div class="signal-description">Click "Analyze Market" to get trading signals.</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Active Trades -->
                <div class="active-trades glass-card">
                    <div class="chart-header">
                        <div class="chart-title">Active Trades</div>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Entry Price</th>
                                    <th>Current Price</th>
                                    <th>P&L</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="active-orders-table">
                                <!-- Active orders will be rendered here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Load TradingView widget
    loadTradingViewWidget();
    
    // Render initial market data
    renderMarketData();
    
    // Set up event listeners
    setupEventListeners();
    
    // Call first market analysis
    performMarketAnalysis();
}

// Load TradingView widget
function loadTradingViewWidget() {
    console.log('Loading TradingView widget...');
    const container = document.getElementById('tradingview-widget');
    
    // Clear any existing content
    container.innerHTML = '';
    
    // Create the widget in an iframe for isolation
    const iframe = document.createElement('iframe');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    container.appendChild(iframe);
    
    // Set the iframe content with the TradingView widget
    const iframeContent = `
        <html>
        <head>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }
            </style>
        </head>
        <body>
            <div class="tradingview-widget-container" style="height:100%;width:100%">
                <div id="tradingview_chart" style="height:100%;width:100%"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                    new TradingView.widget({
                        "autosize": true,
                        "symbol": "FX:${appState.activeSymbol}",
                        "interval": "${appState.activeTimeframe}",
                        "timezone": "Etc/UTC",
                        "theme": "dark",
                        "style": "1",
                        "locale": "en",
                        "toolbar_bg": "#f1f3f6",
                        "enable_publishing": false,
                        "withdateranges": true,
                        "hide_side_toolbar": false,
                        "allow_symbol_change": true,
                        "save_image": false,
                        "container_id": "tradingview_chart"
                    });
                </script>
            </div>
        </body>
        </html>
    `;
    
    iframe.onload = function() {
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(iframeContent);
        iframe.contentWindow.document.close();
    };
}

// Perform market analysis using Chart Analyzer
function performMarketAnalysis() {
    console.log('Performing market analysis...');
    
    // Show loading state
    const analysisResults = document.getElementById('analysis-results');
    if (!analysisResults) return;
    
    analysisResults.innerHTML = `
        <div class="futuristic-loader"></div>
        <p>Analyzing market data, please wait...</p>
    `;
    
    // Reset trading signal
    const tradingSignal = document.getElementById('trading-signal');
    tradingSignal.innerHTML = `
        <div class="signal-strength">Analyzing Market...</div>
        <div class="signal-description">Click "Analyze Market" to get trading signals.</div>
    `;
    
    // Call the Chart Analyzer
    setTimeout(() => {
        // Get current chart data for the active symbol
        const chartData = getChartData(appState.activeSymbol, appState.activeTimeframe);
        
        // Analyze the market using the Chart Analyzer module
        const analysisResult = appState.chartAnalyzer.analyze_market({
            symbol: appState.activeSymbol,
            timeframe: appState.activeTimeframe,
            data: chartData
        });
        
        // Display the analysis results
        displayAnalysisResults(analysisResult);
    }, 1500); // Simulate analysis delay
}

// Display analysis results in the modern UI
function displayAnalysisResults(results) {
    const analysisResults = document.getElementById('analysis-results');
    const tradingSignal = document.getElementById('trading-signal');
    
    if (!analysisResults || !tradingSignal || !results) return;
    
    // Format the results for display
    const technicalIndicators = results.indicators || {};
    const patterns = results.patterns || {};
    const supportResistance = results.levels || {};
    const overallSignal = results.signal || { direction: 'neutral', strength: 50, recommendation: 'Hold' };
    
    // Create a glassmorphism card for each section
    let analysisHTML = `
        <div class="analysis-grid">
            <div class="analysis-section glass-card">
                <h3>Technical Indicators</h3>
                <div class="indicator-list">
    `;
    
    // Add technical indicators
    for (const [indicator, value] of Object.entries(technicalIndicators)) {
        const isPositive = value.signal === 'buy';
        const isNegative = value.signal === 'sell';
        analysisHTML += `
            <div class="indicator-item">
                <span class="indicator-name">${indicator}</span>
                <span class="indicator-value ${isPositive ? 'positive' : isNegative ? 'negative' : ''}">${value.value} (${value.signal})</span>
            </div>
        `;
    }
    
    analysisHTML += `
                </div>
            </div>
            
            <div class="analysis-section glass-card">
                <h3>Chart Patterns</h3>
                <div class="pattern-list">
    `;
    
    // Add chart patterns
    if (Object.keys(patterns).length === 0) {
        analysisHTML += `<p class="no-patterns">No patterns detected</p>`;
    } else {
        for (const [pattern, value] of Object.entries(patterns)) {
            const isPositive = value.signal === 'buy';
            const isNegative = value.signal === 'sell';
            analysisHTML += `
                <div class="pattern-item">
                    <span class="pattern-name">${pattern}</span>
                    <span class="pattern-signal ${isPositive ? 'positive' : isNegative ? 'negative' : ''}">${value.signal}</span>
                </div>
            `;
        }
    }
    
    analysisHTML += `
                </div>
            </div>
            
            <div class="analysis-section glass-card">
                <h3>Support & Resistance</h3>
                <div class="levels-list">
    `;
    
    // Add support and resistance levels
    for (const [type, value] of Object.entries(supportResistance)) {
        analysisHTML += `
            <div class="level-item">
                <span class="level-name">${type}</span>
                <span class="level-value">${value.toFixed(4)}</span>
            </div>
        `;
    }
    
    analysisHTML += `
                </div>
            </div>
        </div>
    `;
    
    // Update the analysis results container
    analysisResults.innerHTML = analysisHTML;
    
    // Update the trading signal
    const signalClass = overallSignal.direction === 'buy' ? 'positive' : 
                         overallSignal.direction === 'sell' ? 'negative' : 'neutral';
                         
    const signalIcon = overallSignal.direction === 'buy' ? 'fa-arrow-up' : 
                        overallSignal.direction === 'sell' ? 'fa-arrow-down' : 'fa-minus';
    
    tradingSignal.innerHTML = `
        <div class="signal-strength ${signalClass}">
            <i class="fas ${signalIcon}"></i> ${overallSignal.recommendation}
        </div>
        <div class="signal-description">
            Signal strength: ${overallSignal.strength}%
        </div>
        <div class="signal-actions">
            <button class="neon-button ${overallSignal.direction === 'buy' ? 'green' : ''}" 
                    onclick="placeOrder('buy')" 
                    ${overallSignal.direction !== 'buy' ? 'disabled' : ''}>
                BUY
            </button>
            <button class="neon-button ${overallSignal.direction === 'sell' ? 'red' : ''}" 
                    onclick="placeOrder('sell')" 
                    ${overallSignal.direction !== 'sell' ? 'disabled' : ''}>
                SELL
            </button>
        </div>
    `;
    
    // Show notification
    showNotification(`Analysis complete: ${overallSignal.recommendation}`, 
                    overallSignal.direction === 'buy' ? 'success' : 
                    overallSignal.direction === 'sell' ? 'error' : 'info');
}

// Render market data for cards
function renderMarketData() {
    const marketOverview = document.getElementById('market-overview');
    if (!marketOverview) return;
    
    let marketCardsHTML = '';
    
    // Get the selected markets (or use the first 4 if none selected)
    const marketsToShow = appState.selectedMarkets.length > 0 ? 
        appState.selectedMarkets : 
        appState.brokerConnection.markets.slice(0, 4);
    
    marketsToShow.forEach(market => {
        const isPositive = market.change >= 0;
        marketCardsHTML += `
            <div class="card-3d-container">
                <div class="market-card-modern glass-card card-3d" data-symbol="${market.symbol}">
                    <div class="market-info">
                        <div class="symbol">${market.symbol}</div>
                        <div class="name">${market.name}</div>
                    </div>
                    <div class="market-data">
                        <div class="price">${market.bid.toFixed(market.symbol.includes('BTC') ? 1 : 4)}</div>
                        <div class="change ${isPositive ? 'positive' : 'negative'}">
                            <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
                            ${Math.abs(market.change).toFixed(2)}%
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    marketOverview.innerHTML = marketCardsHTML;
    
    // Add click events to market cards
    document.querySelectorAll('.market-card-modern').forEach(card => {
        card.addEventListener('click', function() {
            const symbol = this.getAttribute('data-symbol');
            changeActiveSymbol(symbol);
        });
    });
}

// Update market data
function updateMarketData() {
    // Update market cards
    const marketCards = document.querySelectorAll('.market-card-modern');
    marketCards.forEach(card => {
        const symbol = card.getAttribute('data-symbol');
        const market = appState.brokerConnection.markets.find(m => m.symbol === symbol);
        
        if (market) {
            const valueElement = card.querySelector('.price');
            const changeElement = card.querySelector('.change');
            
            valueElement.textContent = market.bid.toFixed(market.symbol.includes('BTC') ? 1 : 4);
            
            const isPositive = market.change >= 0;
            changeElement.className = `change ${isPositive ? 'positive' : 'negative'}`;
            changeElement.innerHTML = `
                <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
                ${Math.abs(market.change).toFixed(2)}%
            `;
        }
    });
}

// Update active orders table
function updateActiveOrders() {
    const tableBody = document.getElementById('active-orders-table');
    if (!tableBody) return;
    
    if (appState.activeOrders.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center;">No active trades</td>
            </tr>
        `;
        return;
    }
    
    let ordersHTML = '';
    
    appState.activeOrders.forEach(order => {
        const isProfitable = order.pnl >= 0;
        
        ordersHTML += `
            <tr>
                <td>${order.symbol}</td>
                <td class="${order.type === 'buy' ? 'buy' : 'sell'}">${order.type.toUpperCase()}</td>
                <td>$${order.amount}</td>
                <td>${order.entryPrice.toFixed(order.symbol.includes('BTC') ? 1 : 4)}</td>
                <td>${order.currentPrice.toFixed(order.symbol.includes('BTC') ? 1 : 4)}</td>
                <td class="${isProfitable ? 'positive' : 'negative'}">$${order.pnl.toFixed(2)}</td>
                <td>
                    <button class="button button-mini ${isProfitable ? 'button-primary' : 'button-secondary'}" data-order-id="${order.id}">
                        Close
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = ordersHTML;
    
    // Add click events to close buttons
    document.querySelectorAll('.button-mini').forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-order-id');
            closeOrder(orderId);
        });
    });
}

// Change active symbol
function changeActiveSymbol(symbol) {
    appState.activeSymbol = symbol;
    
    // Update UI
    document.getElementById('active-symbol').textContent = symbol;
    
    // Reload TradingView widget with new symbol
    loadTradingViewWidget();
    
    // Perform new market analysis
    performMarketAnalysis();
}

// Change timeframe
function changeTimeframe(timeframe) {
    appState.activeTimeframe = timeframe;
    
    // Update UI
    document.getElementById('active-timeframe').textContent = timeframe;
    
    // Update timeframe buttons
    document.querySelectorAll('[data-timeframe]').forEach(button => {
        if (button.getAttribute('data-timeframe') === timeframe) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
    
    // Reload TradingView widget with new timeframe
    loadTradingViewWidget();
    
    // Perform new market analysis
    performMarketAnalysis();
}

// Place an order
function placeOrder(type) {
    const amount = parseFloat(document.getElementById('trade-amount').value);
    const leverage = parseFloat(document.getElementById('trade-leverage').value);
    
    if (isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    if (isNaN(leverage) || leverage <= 0) {
        alert('Please enter a valid leverage');
        return;
    }
    
    const result = appState.brokerConnection.placeOrder(type, appState.activeSymbol, amount, leverage);
    
    if (result.success) {
        // Update the orders table
        updateActiveOrders();
        
        // Show success notification
        alert(result.message);
    } else {
        // Show error notification
        alert('Error: ' + result.message);
    }
}

// Close an order
function closeOrder(orderId) {
    const orderIndex = appState.activeOrders.findIndex(o => o.id === orderId);
    if (orderIndex === -1) return;
    
    const order = appState.activeOrders[orderIndex];
    
    // Get current market data
    const market = appState.brokerConnection.markets.find(m => m.symbol === order.symbol);
    if (!market) {
        console.error(`Market ${order.symbol} not found`);
        return;
    }
    
    // Calculate exit price based on order type
    const exitPrice = order.type === 'buy' ? market.bid : market.ask;
    
    // Calculate P&L
    let pnl = 0;
    if (order.type === 'buy') {
        pnl = (exitPrice - order.entryPrice) * order.amount * order.leverage;
    } else {
        pnl = (order.entryPrice - exitPrice) * order.amount * order.leverage;
    }
    
    // Update the order
    order.exitPrice = exitPrice;
    order.closeTime = new Date();
    order.status = 'closed';
    order.pnl = pnl;
    
    // Move to order history
    appState.brokerConnection.orderHistory.push(order);
    
    // Remove from active orders
    appState.activeOrders.splice(orderIndex, 1);
    
    // Update account balance
    appState.brokerConnection.account.balance += pnl;
    appState.brokerConnection.account.pnl += pnl;
    
    // Update appState
    appState.activeOrders = appState.activeOrders;
    
    console.log(`Order ${orderId} closed with P&L: ${pnl.toFixed(2)}`);
    
    // Return success
    return { 
        success: true, 
        message: `Order closed with ${pnl >= 0 ? 'profit' : 'loss'} of ${Math.abs(pnl).toFixed(2)}`,
        pnl: pnl
    };
}

// Setup event listeners
function setupEventListeners() {
    // Timeframe buttons
    document.querySelectorAll('[data-timeframe]').forEach(button => {
        button.addEventListener('click', function() {
            const timeframe = this.getAttribute('data-timeframe');
            changeTimeframe(timeframe);
        });
    });
    
    // Analyze button
    const analyzeButton = document.getElementById('analyze-button');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', performMarketAnalysis);
    }
    
    // Buy button
    const buyButton = document.getElementById('buy-button');
    if (buyButton) {
        buyButton.addEventListener('click', function() {
            placeOrder('buy');
        });
    }
    
    // Sell button
    const sellButton = document.getElementById('sell-button');
    if (sellButton) {
        sellButton.addEventListener('click', function() {
            placeOrder('sell');
        });
    }
    
    // Sidebar navigation
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            
            // Update active class
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Currently only implement dashboard page
            if (page !== 'dashboard') {
                alert('This section is coming soon!');
            }
        });
    });
    
    // Setup auto trading toggle
    setupAutoTradingToggle();
    
    // Notification badge click
    const notificationBadge = document.querySelector('.notification-badge-modern');
    if (notificationBadge) {
        notificationBadge.addEventListener('click', function() {
            // Show some sample notifications
            showNotification('Welcome to MAGUS PRIME X Trading Platform', 'success');
            setTimeout(() => {
                showNotification('Your Capital.com connection is active', 'info');
            }, 1000);
            setTimeout(() => {
                showNotification('Chart Analyzer identified potential trading opportunities', 'info');
            }, 2000);
        });
    }
}

// Setup auto trading toggle
function setupAutoTradingToggle() {
    const autoTradingToggle = document.getElementById('auto-trading-toggle');
    const tradingStatusText = document.getElementById('trading-status-text');
    const tradingProgress = document.getElementById('trading-progress').querySelector('.fill');
    
    if (!autoTradingToggle) return;
    
    autoTradingToggle.addEventListener('change', function() {
        if (this.checked) {
            tradingStatusText.textContent = 'Active';
            tradingStatusText.style.color = '#02a875';
            tradingProgress.style.width = '100%';
            
            // Start auto trading simulation
            appState.autoTrading = {
                active: true,
                startTime: new Date(),
                interval: setInterval(() => {
                    // Simulate auto trading - randomly place orders
                    if (Math.random() > 0.8) { // 20% chance to place a trade
                        const type = Math.random() > 0.5 ? 'buy' : 'sell';
                        const symbol = appState.brokerConnection.markets[
                            Math.floor(Math.random() * appState.brokerConnection.markets.length)
                        ].symbol;
                        const amount = 100 + Math.floor(Math.random() * 900);
                        const leverage = 10 + Math.floor(Math.random() * 20);
                        
                        // Place the order
                        const result = appState.brokerConnection.placeOrder(type, symbol, amount, leverage);
                        
                        if (result.success) {
                            // Show notification
                            showNotification(`Auto Trading: ${type.toUpperCase()} ${symbol} order placed`, 'success');
                            // Update orders table
                            updateActiveOrders();
                        }
                    }
                }, 10000) // Check every 10 seconds
            };
            
            showNotification('Auto Trading has been activated', 'success');
        } else {
            tradingStatusText.textContent = 'Off';
            tradingStatusText.style.color = '';
            tradingProgress.style.width = '0%';
            
            // Stop auto trading
            if (appState.autoTrading && appState.autoTrading.interval) {
                clearInterval(appState.autoTrading.interval);
                appState.autoTrading.active = false;
                showNotification('Auto Trading has been deactivated', 'info');
            }
        }
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to notification container
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);
    notificationContainer.appendChild(notification);
    
    // Add close functionality
    notification.querySelector('.notification-close').addEventListener('click', function() {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
            if (notificationContainer.children.length === 0) {
                notificationContainer.remove();
            }
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    notification.remove();
                    if (notificationContainer.children.length === 0) {
                        notificationContainer.remove();
                    }
                }
            }, 300);
        }
    }, 5000);
}

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Existing elements
    const connectBtn = document.getElementById('connectBtn');
    const themeToggle = document.getElementById('themeToggle');
    
    // New elements for authentication
    const loginBtn = document.getElementById('loginBtn');
    const loginModal = document.getElementById('loginModal');
    const closeModalBtn = document.querySelector('.close-modal');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Login functionality
    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function() {
            loginModal.classList.add('active');
        });
    }
    
    if (closeModalBtn && loginModal) {
        closeModalBtn.addEventListener('click', function() {
            loginModal.classList.remove('active');
        });
    }
    
    // Tab switching in modal
    if (tabBtns && tabContents) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                
                // Remove active class from all tabs
                tabBtns.forEach(tb => tb.classList.remove('active'));
                tabContents.forEach(tc => tc.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
    }
    
    // Form submissions
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Validate inputs
            if (!email || !password) {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would normally call your authentication API
            // For now we'll simulate a successful login
            console.log('Login attempt with:', email);
            
            // Close the modal after successful login
            loginModal.classList.remove('active');
            
            // Update UI to show logged in state
            if (loginBtn) {
                loginBtn.innerHTML = '<i class="fas fa-user-check"></i> My Account';
            }
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const name = formData.get('name');
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Validate inputs
            if (!name || !email || !password) {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would normally call your registration API
            // For now we'll simulate a successful registration
            console.log('Registration attempt with:', email);
            
            // Switch to login tab after successful registration
            tabBtns.forEach(tb => tb.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            document.querySelector('[data-tab="login"]').classList.add('active');
            document.getElementById('login-tab').classList.add('active');
            
            // Close the modal
            loginModal.classList.remove('active');
        });
    }
    
    // Analyze market button functionality
    const analyzeButton = document.querySelector('.analyze-button');
    const analyzerContent = document.getElementById('analyzer-content');
    
    if (analyzeButton && analyzerContent) {
        analyzeButton.addEventListener('click', function() {
            // Show loading state
            analyzerContent.innerHTML = '<div class="loading">Analyzing market data...</div>';
            
            // Simulate API call to the Chart Analyzer module
            setTimeout(() => {
                // Call the Chart Analyzer module
                const results = analyzeMarket();
                displayAnalysisResults(results);
            }, 1500);
        });
    }
    
    // Function to analyze market using the existing Chart Analyzer module
    function analyzeMarket() {
        // This would normally call your existing Chart Analyzer module
        // For now, return mock data that matches your existing format
        return {
            indicators: [
                { name: 'RSI', value: '32', signal: 'Oversold', type: 'bullish' },
                { name: 'MACD', value: '-0.0023', signal: 'Bearish Crossover', type: 'bearish' },
                { name: 'Bollinger Bands', value: 'Lower Band', signal: 'Potential Reversal', type: 'neutral' },
                { name: 'Moving Average (50)', value: '29,345.23', signal: 'Below Price', type: 'bullish' }
            ],
            patterns: [
                { name: 'Doji', confidence: 'High', signal: 'Indecision', type: 'neutral' },
                { name: 'Bullish Engulfing', confidence: 'Medium', signal: 'Potential Reversal', type: 'bullish' },
                { name: 'Support Level', confidence: 'High', signal: 'Strong Support', type: 'bullish' }
            ],
            overallSignal: {
                type: 'neutral',
                strength: 'Moderate',
                description: 'Mixed signals with slight bullish bias. Consider waiting for confirmation before entering a position.'
            }
        };
    }
    
    // Function to display analysis results
    function displayAnalysisResults(results) {
        if (!analyzerContent) return;
        
        const html = `
            <div class="analyzer-results">
                <div class="result-section">
                    <h3>Technical Indicators</h3>
                    <ul class="indicator-list">
                        ${results.indicators.map(indicator => `
                            <li>
                                <span class="indicator-name">${indicator.name}:</span>
                                <span class="indicator-value">${indicator.value}</span>
                                <span class="indicator-signal ${indicator.type}">${indicator.signal}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                
                <div class="result-section">
                    <h3>Chart Patterns</h3>
                    <ul class="pattern-list">
                        ${results.patterns.map(pattern => `
                            <li>
                                <span class="pattern-name">${pattern.name}</span>
                                <span class="pattern-level">${pattern.confidence}</span>
                                <span class="pattern-signal ${pattern.type}">${pattern.signal}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="signal-box ${results.overallSignal.type}">
                <div class="signal-strength">${results.overallSignal.strength} ${results.overallSignal.type.charAt(0).toUpperCase() + results.overallSignal.type.slice(1)} Signal</div>
                <div class="signal-description">${results.overallSignal.description}</div>
            </div>
        `;
        
        analyzerContent.innerHTML = html;
    }
    
    // Connect to Capital.com broker (preserving existing functionality)
    if (connectBtn) {
        connectBtn.addEventListener('click', function() {
            console.log('Connecting to Capital.com broker...');
            // API connection code would go here
            this.innerHTML = '<i class="fas fa-check"></i> Connected';
            this.classList.add('connected');
        });
    }
    
    // Load Chart with TradingView widget (preserving existing functionality)
    new TradingView.widget({
        "width": "100%",
        "height": 500,
        "symbol": "NASDAQ:AAPL",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#1a1f2e",
        "enable_publishing": false,
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_widget"
    });
    
    // Initialize tables with existing data
    initializeTables();
});

// Initialize data tables
function initializeTables() {
    // Populate active trades table with sample data
    const activeTradesTable = document.querySelector('.active-trades-table tbody');
    
    if (activeTradesTable) {
        const activeTradesData = [
            { id: 1, symbol: 'BTCUSD', type: 'Long', entry: 26985.45, size: 0.15, pnl: 3.2 },
            { id: 2, symbol: 'ETHUSD', type: 'Short', entry: 1785.30, size: 2.5, pnl: -1.4 },
            { id: 3, symbol: 'EURUSD', type: 'Long', entry: 1.0732, size: 10000, pnl: 0.8 }
        ];
        
        activeTradesData.forEach(trade => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${trade.symbol}</td>
                <td class="${trade.type.toLowerCase() === 'long' ? 'bullish' : 'bearish'}">${trade.type}</td>
                <td>${trade.entry}</td>
                <td>${trade.size}</td>
                <td class="${trade.pnl >= 0 ? 'bullish' : 'bearish'}">${trade.pnl}%</td>
                <td>
                    <button class="btn-icon" title="Edit Trade"><i class="fas fa-edit"></i></button>
                    <button class="btn-icon" title="Close Trade"><i class="fas fa-times"></i></button>
                </td>
            `;
            activeTradesTable.appendChild(row);
        });
    }
}
