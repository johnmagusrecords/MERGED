document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const connectBtn = document.getElementById('connectBtn');
    const startBotBtn = document.getElementById('startBotBtn');
    const modal = document.getElementById('modal');
    const closeModal = document.querySelector('.close');
    const loginForm = document.getElementById('loginForm');
    const loginStatus = document.getElementById('loginStatus');
    const portfolioValue = document.getElementById('portfolioValue');
    const portfolioChange = document.getElementById('portfolioChange');
    const tradesCount = document.getElementById('tradesCount');
    const tradesBreakdown = document.getElementById('tradesBreakdown');
    const winrateValue = document.getElementById('winrateValue');
    const timeButtons = document.querySelectorAll('.time-btn');
    const signalsList = document.getElementById('signalsList');
    const positionsList = document.getElementById('positionsList');
    const ordersList = document.getElementById('ordersList');

    // App state
    let appState = {
        connected: false,
        botRunning: false,
        currentSymbol: 'BTCUSD',
        currentInterval: '15m',
        accountInfo: null,
        positions: [],
        orders: [],
        signals: []
    };

    // Event Listeners
    connectBtn.addEventListener('click', () => {
        if (appState.connected) {
            // Disconnect logic
            disconnectFromCapital();
        } else {
            // Show login modal
            modal.style.display = 'block';
            
            // Pre-fill form with values from .env if available
            if (window.electron) {
                window.electron.getEnvVariables(['CAPITAL_API_KEY', 'CAPITAL_API_PASSWORD', 'CAPITAL_API_IDENTIFIER'])
                    .then(envVars => {
                        document.getElementById('apiKey').value = envVars.CAPITAL_API_KEY || '';
                        document.getElementById('apiPassword').value = envVars.CAPITAL_API_PASSWORD || '';
                        document.getElementById('apiIdentifier').value = envVars.CAPITAL_API_IDENTIFIER || '';
                    });
            }
        }
    });

    startBotBtn.addEventListener('click', () => {
        if (!appState.connected) {
            showNotification('Please connect to Capital.com first', 'error');
            return;
        }

        if (appState.botRunning) {
            stopBot();
        } else {
            startBot();
        }
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const apiKey = document.getElementById('apiKey').value;
        const apiPassword = document.getElementById('apiPassword').value; 
        const apiIdentifier = document.getElementById('apiIdentifier').value;
        
        loginStatus.className = 'login-status';
        loginStatus.textContent = 'Connecting...';
        loginStatus.style.display = 'block';
        
        try {
            // Connect to Capital.com using the provided API credentials
            const connected = await connectToCapital(apiKey, apiPassword, apiIdentifier);
            
            if (connected) {
                loginStatus.className = 'login-status success';
                loginStatus.textContent = 'Successfully connected!';
                
                setTimeout(() => {
                    modal.style.display = 'none';
                    updateConnectionStatus(true);
                }, 1500);
            } else {
                loginStatus.className = 'login-status error';
                loginStatus.textContent = 'Failed to connect. Please check your credentials.';
            }
        } catch (error) {
            loginStatus.className = 'login-status error';
            loginStatus.textContent = `Error: ${error.message}`;
        }
    });

    timeButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            timeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Update the chart timeframe
            const interval = button.getAttribute('data-interval');
            updateChartTimeframe(interval);
        });
    });

    // Functions to handle Capital.com API
    async function connectToCapital(apiKey, apiPassword, apiIdentifier) {
        try {
            const success = await window.capitalApi.connect(apiKey, apiPassword, apiIdentifier);
            
            if (success) {
                // Fetch account information
                const accountInfo = await window.capitalApi.getAccountInfo();
                appState.accountInfo = accountInfo;
                
                // Update UI with account info
                updateAccountInfo(accountInfo);
                
                // Start fetching positions and orders
                fetchPositionsAndOrders();
                
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error connecting to Capital.com:', error);
            return false;
        }
    }

    function disconnectFromCapital() {
        window.capitalApi.disconnect();
        updateConnectionStatus(false);
        
        // Clear account info
        appState.accountInfo = null;
        appState.positions = [];
        appState.orders = [];
        
        // Update UI
        updateAccountInfo(null);
        renderPositions([]);
        renderOrders([]);
        
        // Stop the bot if it's running
        if (appState.botRunning) {
            stopBot();
        }
    }

    function updateConnectionStatus(connected) {
        appState.connected = connected;
        
        if (connected) {
            connectBtn.innerHTML = '<i class="fa fa-plug"></i> Disconnect';
            connectBtn.style.backgroundColor = '#ff3b30';
        } else {
            connectBtn.innerHTML = '<i class="fa fa-plug"></i> Connect';
            connectBtn.style.backgroundColor = '';
        }
    }

    function updateAccountInfo(accountInfo) {
        if (accountInfo) {
            // Update portfolio value
            portfolioValue.textContent = `$${accountInfo.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            
            // Update portfolio change (if available)
            if (accountInfo.dailyChange) {
                const changeClass = accountInfo.dailyChange >= 0 ? 'var(--green-color)' : 'var(--red-color)';
                const changePrefix = accountInfo.dailyChange >= 0 ? '+' : '';
                portfolioChange.textContent = `${changePrefix}${accountInfo.dailyChange.toFixed(2)}% today`;
                portfolioChange.style.color = changeClass;
            }
        } else {
            // Reset UI when not connected
            portfolioValue.textContent = '$0.00';
            portfolioChange.textContent = '+0.00% today';
            portfolioChange.style.color = 'var(--green-color)';
        }
    }

    async function fetchPositionsAndOrders() {
        if (!appState.connected) return;
        
        try {
            // Fetch positions
            const positions = await window.capitalApi.getPositions();
            appState.positions = positions;
            renderPositions(positions);
            
            // Update active trades count
            updateTradesCount(positions);
            
            // Fetch orders
            const orders = await window.capitalApi.getOrders();
            appState.orders = orders;
            renderOrders(orders);
            
            // Fetch signals
            const signals = await window.capitalApi.getSignals(appState.currentSymbol, appState.currentInterval);
            appState.signals = signals;
            renderSignals(signals);
            
            // Schedule next update
            setTimeout(fetchPositionsAndOrders, 5000);
        } catch (error) {
            console.error('Error fetching data:', error);
            setTimeout(fetchPositionsAndOrders, 10000); // Retry after longer delay on error
        }
    }

    function updateTradesCount(positions) {
        const totalTrades = positions.length;
        tradesCount.textContent = totalTrades;
        
        // Count by type (example distinction between scalping and swing trades)
        const scalpingTrades = positions.filter(p => isScalpingTrade(p)).length;
        const swingTrades = totalTrades - scalpingTrades;
        tradesBreakdown.textContent = `${scalpingTrades} Scalping + ${swingTrades} Swing`;
    }

    function isScalpingTrade(position) {
        // This is a simplified example - real logic would depend on your trading strategy
        // For example, scalping trades might have closer take profits or be on shorter timeframes
        return position.timeframe && ['1m', '5m', '15m', '30m'].includes(position.timeframe);
    }

    // Render trading positions in the UI
    function renderPositions(positions) {
        // Clear current positions
        positionsList.innerHTML = '';
        
        if (!positions || positions.length === 0) {
            positionsList.innerHTML = '<div class="empty-message">No active positions</div>';
            return;
        }
        
        // Sort positions by profit percentage (descending)
        positions.sort((a, b) => parseFloat(b.profitPercent) - parseFloat(a.profitPercent));
        
        // Render each position
        positions.forEach(position => {
            const isProfitable = parseFloat(position.profit) > 0;
            const posItem = document.createElement('div');
            posItem.className = 'position-item';
            
            posItem.innerHTML = `
                <div class="position-header">
                    <span class="position-symbol">${position.symbol}</span>
                    <span class="position-direction ${position.direction === 'BUY' ? 'long' : 'short'}">${position.direction}</span>
                </div>
                <div class="position-details">
                    <div class="position-price">
                        <span>Entry: ${parseFloat(position.entryPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                        <span>Current: ${parseFloat(position.currentPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>
                    <div class="position-profit ${isProfitable ? 'profit' : 'loss'}">
                        ${isProfitable ? '+' : ''}${position.profit} (${isProfitable ? '+' : ''}${position.profitPercent}%)
                    </div>
                </div>
                <div class="position-footer">
                    <span class="position-size">Size: ${position.size}</span>
                    <span class="position-time">${formatDate(position.openDate)}</span>
                    <button class="close-position-btn" data-dealid="${position.dealId}">Close</button>
                </div>
            `;
            
            positionsList.appendChild(posItem);
            
            // Add event listener to close position button
            const closeBtn = posItem.querySelector('.close-position-btn');
            closeBtn.addEventListener('click', () => {
                closePosition(position.dealId);
            });
        });
        
        // Update the position count in the Active Trades section
        const buyCount = positions.filter(p => p.direction === 'BUY').length;
        const sellCount = positions.filter(p => p.direction === 'SELL').length;
        
        tradesCount.textContent = positions.length;
        tradesBreakdown.textContent = `${buyCount} Long • ${sellCount} Short`;
    }
    
    // Render pending orders in the UI
    function renderOrders(orders) {
        // Clear current orders
        ordersList.innerHTML = '';
        
        if (!orders || orders.length === 0) {
            ordersList.innerHTML = '<div class="empty-message">No pending orders</div>';
            return;
        }
        
        // Render each order
        orders.forEach(order => {
            const orderItem = document.createElement('div');
            orderItem.className = 'order-item';
            
            orderItem.innerHTML = `
                <div class="order-header">
                    <span class="order-symbol">${order.symbol}</span>
                    <span class="order-type">${order.type}</span>
                </div>
                <div class="order-details">
                    <span class="order-direction ${order.direction === 'BUY' ? 'long' : 'short'}">${order.direction}</span>
                    <span class="order-price">${parseFloat(order.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </div>
                <div class="order-footer">
                    <span class="order-size">Size: ${order.size}</span>
                    <span class="order-time">${formatDate(order.created)}</span>
                    <button class="cancel-order-btn" data-id="${order.id}">Cancel</button>
                </div>
            `;
            
            ordersList.appendChild(orderItem);
            
            // Add event listener to cancel order button
            const cancelBtn = orderItem.querySelector('.cancel-order-btn');
            cancelBtn.addEventListener('click', () => {
                cancelOrder(order.id);
            });
        });
    }
    
    // Render trading signals in the UI
    function renderSignals(signals) {
        // Clear current signals
        signalsList.innerHTML = '';
        
        if (!signals || signals.length === 0) {
            signalsList.innerHTML = '<div class="empty-message">No trading signals</div>';
            return;
        }
        
        // Sort signals by time (newest first)
        signals.sort((a, b) => new Date(b.time) - new Date(a.time));
        
        // Render each signal
        signals.forEach(signal => {
            const signalItem = document.createElement('div');
            signalItem.className = 'signal-item';
            
            signalItem.innerHTML = `
                <div class="signal-header">
                    <span class="signal-symbol">${signal.symbol}</span>
                    <span class="signal-timeframe">${signal.timeframe}</span>
                </div>
                <div class="signal-details">
                    <span class="signal-direction ${signal.direction === 'BUY' ? 'long' : 'short'}">${signal.direction} - ${signal.type}</span>
                    <span class="signal-confidence">Confidence: ${signal.confidence}</span>
                </div>
                <div class="signal-footer">
                    <span class="signal-price">Price: ${parseFloat(signal.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    <span class="signal-time">${formatDate(signal.time)}</span>
                    <button class="take-signal-btn" data-id="${signal.id}">Trade</button>
                </div>
            `;
            
            signalsList.appendChild(signalItem);
            
            // Add event listener to trade signal button
            const tradeBtn = signalItem.querySelector('.take-signal-btn');
            tradeBtn.addEventListener('click', () => {
                executeTrade(signal);
            });
        });
    }
    
    // Execute a trade based on a signal
    async function executeTrade(signal) {
        if (!appState.connected) {
            showNotification('Please connect to Capital.com first', 'error');
            return;
        }
        
        try {
            showNotification(`Executing ${signal.direction} trade for ${signal.symbol}...`, 'info');
            
            // In a real implementation, this would call the API to place a trade
            // For demo, we'll add a simulated position
            const position = {
                dealId: `pos-${Math.floor(Math.random() * 10000)}`,
                symbol: signal.symbol,
                direction: signal.direction,
                size: parseFloat((Math.random() * 2 + 0.1).toFixed(2)),
                entryPrice: parseFloat(signal.price),
                currentPrice: parseFloat(signal.price),
                stopLevel: parseFloat(signal.price) * (signal.direction === 'BUY' ? 0.98 : 1.02),
                profitLevel: parseFloat(signal.price) * (signal.direction === 'BUY' ? 1.05 : 0.95),
                openDate: new Date().toISOString(),
                profit: 0,
                profitPercent: 0,
                status: 'OPEN',
                timeframe: signal.timeframe,
                strategy: signal.type
            };
            
            // Add to positions and update UI
            appState.positions.push(position);
            updateTradesCount(appState.positions);
            renderPositions(appState.positions);
            
            showNotification(`${signal.direction} trade executed for ${signal.symbol}`, 'success');
        } catch (error) {
            console.error('Error executing trade:', error);
            showNotification('Failed to execute trade', 'error');
        }
    }
    
    // Close a position
    async function closePosition(dealId) {
        if (!appState.connected) {
            showNotification('Please connect to Capital.com first', 'error');
            return;
        }
        
        try {
            showNotification('Closing position...', 'info');
            
            // In a real implementation, this would call the API to close the position
            // For demo, we'll remove the position from our local state
            const positionIndex = appState.positions.findIndex(p => p.dealId === dealId);
            
            if (positionIndex !== -1) {
                appState.positions.splice(positionIndex, 1);
                updateTradesCount(appState.positions);
                renderPositions(appState.positions);
                
                showNotification('Position closed successfully', 'success');
            }
        } catch (error) {
            console.error('Error closing position:', error);
            showNotification('Failed to close position', 'error');
        }
    }
    
    // Cancel an order
    async function cancelOrder(orderId) {
        if (!appState.connected) {
            showNotification('Please connect to Capital.com first', 'error');
            return;
        }
        
        try {
            showNotification('Cancelling order...', 'info');
            
            // In a real implementation, this would call the API to cancel the order
            // For demo, we'll remove the order from our local state
            const orderIndex = appState.orders.findIndex(o => o.id === orderId);
            
            if (orderIndex !== -1) {
                appState.orders.splice(orderIndex, 1);
                renderOrders(appState.orders);
                
                showNotification('Order cancelled successfully', 'success');
            }
        } catch (error) {
            console.error('Error cancelling order:', error);
            showNotification('Failed to cancel order', 'error');
        }
    }

    // Functions to handle bot control
    async function startBot() {
        try {
            startBotBtn.classList.add('running');
            startBotBtn.querySelector('span').textContent = 'Stop Bot';
            startBotBtn.querySelector('i').className = 'fas fa-stop';
            
            appState.botRunning = true;
            
            // Simulate starting the bot
            console.log('Starting trading bot...');
            
            if (window.electron) {
                const result = await window.electron.startBot();
                console.log('Bot start result:', result);
            }
            
            // Start simulation for demo purposes
            startTradingSimulation();
            
            showNotification('Trading bot started successfully', 'success');
        } catch (error) {
            console.error('Error starting bot:', error);
            showNotification('Failed to start trading bot', 'error');
            stopBot();
        }
    }
    
    async function stopBot() {
        try {
            startBotBtn.classList.remove('running');
            startBotBtn.querySelector('span').textContent = 'Start Bot';
            startBotBtn.querySelector('i').className = 'fas fa-play';
            
            appState.botRunning = false;
            
            // Simulate stopping the bot
            console.log('Stopping trading bot...');
            
            if (window.electron) {
                const result = await window.electron.stopBot();
                console.log('Bot stop result:', result);
            }
            
            // Stop simulation
            stopTradingSimulation();
            
            showNotification('Trading bot stopped', 'info');
        } catch (error) {
            console.error('Error stopping bot:', error);
            showNotification('Failed to stop trading bot', 'error');
        }
    }

    // Trading simulation variables
    let simulationInterval = null;
    const tradingSymbols = ['BTCUSD', 'ETHUSD', 'XRPUSD', 'SOLUSD', 'ADAUSD', 'XAUUSD', 'XAGUSD', 'US100', 'GER40'];
    
    // Start trading simulation for demo purposes
    function startTradingSimulation() {
        // Clear any existing intervals
        if (simulationInterval) {
            clearInterval(simulationInterval);
        }
        
        // Update positions and signals immediately
        updateSimulatedPositions();
        updateSimulatedSignals();
        updateSimulatedOrders();
        
        // Set up periodic updates every 15 seconds
        simulationInterval = setInterval(() => {
            updateSimulatedPositions();
            updateSimulatedSignals();
            updateSimulatedOrders();
            updatePortfolioValue();
        }, 15000);
    }
    
    // Stop trading simulation
    function stopTradingSimulation() {
        if (simulationInterval) {
            clearInterval(simulationInterval);
            simulationInterval = null;
        }
    }
    
    // Update portfolio value with random fluctuations
    function updatePortfolioValue() {
        if (!appState.accountInfo) return;
        
        // Simulate small random changes to portfolio value
        const currentBalance = parseFloat(appState.accountInfo.balance);
        const change = (Math.random() * 2 - 1) * currentBalance * 0.003; // ±0.3% change
        
        appState.accountInfo.balance = (currentBalance + change).toFixed(2);
        appState.accountInfo.dailyChange = (parseFloat(appState.accountInfo.dailyChange) + (change / currentBalance) * 100).toFixed(2);
        
        // Update UI
        portfolioValue.textContent = `$${appState.accountInfo.balance}`;
        portfolioChange.textContent = `${appState.accountInfo.dailyChange > 0 ? '+' : ''}${appState.accountInfo.dailyChange}% today`;
        portfolioChange.className = appState.accountInfo.dailyChange >= 0 ? 'green' : 'red';
    }
    
    // Update simulated trading positions
    function updateSimulatedPositions() {
        if (!appState.connected || !appState.botRunning) return;
        
        // If bot is running, randomly add new positions or update existing ones
        window.capitalApi.getPositions().then(positions => {
            // If bot is running and we have less than 5 positions, randomly add a new one
            if (appState.botRunning && positions.length < 5 && Math.random() < 0.3) {
                const newPosition = generateRandomPosition();
                positions.push(newPosition);
            }
            
            // Update existing positions with random price changes
            positions = positions.map(pos => {
                // Random price change up to ±0.5%
                const priceChange = pos.currentPrice * (Math.random() * 0.01 - 0.005);
                const newPrice = pos.currentPrice + priceChange;
                
                // Calculate new profit based on direction and price change
                const priceDirection = pos.direction === 'BUY' ? 
                    newPrice - pos.entryPrice : 
                    pos.entryPrice - newPrice;
                
                const newProfit = priceDirection * pos.size;
                const newProfitPercent = (priceDirection / pos.entryPrice) * 100;
                
                return {
                    ...pos,
                    currentPrice: newPrice.toFixed(2),
                    profit: newProfit.toFixed(2),
                    profitPercent: newProfitPercent.toFixed(2)
                };
            });
            
            // Randomly close a position if we have some and bot is running
            if (appState.botRunning && positions.length > 0 && Math.random() < 0.1) {
                positions.splice(Math.floor(Math.random() * positions.length), 1);
            }
            
            appState.positions = positions;
            updateTradesCount(positions);
            renderPositions(positions);
        });
    }
    
    // Generate a random trading position for simulation
    function generateRandomPosition() {
        const symbol = tradingSymbols[Math.floor(Math.random() * tradingSymbols.length)];
        const direction = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const entryPrice = getRandomPrice(symbol);
        const size = parseFloat((Math.random() * 2 + 0.1).toFixed(2));
        const profit = (Math.random() * 200 - 100).toFixed(2);
        const profitPercent = (Math.random() * 5 - 2.5).toFixed(2);
        const dealId = `pos-${Math.floor(Math.random() * 10000)}`;
        const strategies = ['MACD Crossover', 'RSI Divergence', 'Trend Following', 'Breakout', 'Mean Reversion'];
        const timeframes = ['1m', '5m', '15m', '1h', '4h'];
        
        return {
            dealId,
            symbol,
            direction,
            size,
            entryPrice,
            currentPrice: (entryPrice + (direction === 'BUY' ? 1 : -1) * entryPrice * 0.01).toFixed(2),
            stopLevel: (entryPrice - (direction === 'BUY' ? 1 : -1) * entryPrice * 0.02).toFixed(2),
            profitLevel: (entryPrice + (direction === 'BUY' ? 1 : -1) * entryPrice * 0.03).toFixed(2),
            openDate: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            profit,
            profitPercent,
            status: 'OPEN',
            timeframe: timeframes[Math.floor(Math.random() * timeframes.length)],
            strategy: strategies[Math.floor(Math.random() * strategies.length)]
        };
    }
    
    // Get a random price for a symbol
    function getRandomPrice(symbol) {
        const basePrices = {
            'BTCUSD': 52000,
            'ETHUSD': 3100,
            'XRPUSD': 0.55,
            'SOLUSD': 145,
            'ADAUSD': 0.45,
            'XAUUSD': 2325,
            'XAGUSD': 28,
            'US100': 18500,
            'GER40': 17900
        };
        
        const basePrice = basePrices[symbol] || 100;
        return (basePrice + basePrice * (Math.random() * 0.1 - 0.05)).toFixed(2);
    }
    
    // Update simulated trading signals
    function updateSimulatedSignals() {
        if (!appState.connected) return;
        
        const signals = [];
        
        // Generate 5-10 random signals
        const count = Math.floor(Math.random() * 6) + 5;
        
        for (let i = 0; i < count; i++) {
            const symbol = tradingSymbols[Math.floor(Math.random() * tradingSymbols.length)];
            const direction = Math.random() > 0.5 ? 'BUY' : 'SELL';
            const signalTypes = ['Reversal', 'Breakout', 'Trend Continuation', 'Divergence', 'Support/Resistance'];
            const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];
            const confidence = Math.floor(Math.random() * 35) + 65; // 65-99% confidence
            
            signals.push({
                id: `signal-${Math.floor(Math.random() * 10000)}`,
                symbol,
                direction,
                price: getRandomPrice(symbol),
                confidence: `${confidence}%`,
                type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
                timeframe: timeframes[Math.floor(Math.random() * timeframes.length)],
                time: new Date(Date.now() - Math.random() * 3600000).toISOString() // Up to 1 hour ago
            });
        }
        
        appState.signals = signals;
        renderSignals(signals);
    }
    
    // Update simulated pending orders
    function updateSimulatedOrders() {
        if (!appState.connected) return;
        
        const orders = [];
        
        // Only generate orders if bot is running and with low probability
        if (appState.botRunning && Math.random() < 0.4) {
            const count = Math.floor(Math.random() * 3) + 1; // 1-3 orders
            
            for (let i = 0; i < count; i++) {
                const symbol = tradingSymbols[Math.floor(Math.random() * tradingSymbols.length)];
                const direction = Math.random() > 0.5 ? 'BUY' : 'SELL';
                const price = getRandomPrice(symbol);
                const orderTypes = ['LIMIT', 'STOP'];
                
                orders.push({
                    id: `order-${Math.floor(Math.random() * 10000)}`,
                    symbol,
                    direction,
                    price,
                    size: parseFloat((Math.random() * 2 + 0.1).toFixed(2)),
                    type: orderTypes[Math.floor(Math.random() * orderTypes.length)],
                    created: new Date(Date.now() - Math.random() * 3600000).toISOString() // Up to 1 hour ago
                });
            }
        }
        
        appState.orders = orders;
        renderOrders(orders);
    }

    // Utility functions
    function showNotification(message, type = 'info') {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('MAGUS PRIME X', {
                body: message,
                icon: 'images/logo.png'
            });
        }
        
        // For this demo, also log to console
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: 'numeric', 
            minute: 'numeric', 
            hour12: true 
        });
    }

    // Initialize dashboard
    function initDashboard() {
        // Set up win rate (demo data)
        winrateValue.textContent = '76%';
        
        // Initialize TradingView chart
        if (window.initTradingViewWidget) {
            window.initTradingViewWidget('tradingview-container', appState.currentSymbol, appState.currentInterval);
        }
        
        // Request permissions for notifications
        if ('Notification' in window) {
            Notification.requestPermission();
        }
        
        // Check if we have stored credentials and connect automatically
        if (window.electron) {
            window.electron.getEnvVariables(['CAPITAL_API_KEY', 'CAPITAL_API_PASSWORD', 'CAPITAL_API_IDENTIFIER'])
                .then(envVars => {
                    if (envVars.CAPITAL_API_KEY && envVars.CAPITAL_API_PASSWORD && envVars.CAPITAL_API_IDENTIFIER) {
                        // Auto-connect with stored credentials
                        connectToCapital(envVars.CAPITAL_API_KEY, envVars.CAPITAL_API_PASSWORD, envVars.CAPITAL_API_IDENTIFIER)
                            .then(connected => {
                                if (connected) {
                                    updateConnectionStatus(true);
                                }
                            });
                    }
                });
        }
    }

    // Initialize the dashboard
    initDashboard();

    // Bot simulation functions
    let botInterval = null;

    // Simulate market data updates
    function simulateMarketUpdates() {
        // Generate random market data
        if (appState.connected && appState.botRunning) {
            // Update portfolio value with slight fluctuations
            const change = (Math.random() - 0.5) * 200; // Random change between -100 and +100
            const currentValue = parseFloat(appState.accountInfo.balance);
            appState.accountInfo.balance = (currentValue + change).toFixed(2);
            
            // Update portfolio performance
            const percentChange = (change / currentValue * 100).toFixed(2);
            const dailyChangeEl = document.getElementById('daily-change');
            if (dailyChangeEl) {
                const isPositive = change >= 0;
                dailyChangeEl.className = isPositive ? 'positive-change' : 'negative-change';
                dailyChangeEl.textContent = `${isPositive ? '+' : ''}${percentChange}% (${isPositive ? '+' : ''}$${Math.abs(change).toFixed(2)})`;
            }
            
            // Update UI
            updateAccountInfo(appState.accountInfo);
            
            // Update existing positions if any
            if (appState.positions.length > 0) {
                appState.positions.forEach(position => {
                    // Simulate price movement
                    const priceChange = (Math.random() - 0.45) * (parseFloat(position.entryPrice) * 0.01); // Slightly biased towards profit
                    position.currentPrice = (parseFloat(position.currentPrice) + priceChange).toFixed(2);
                    
                    // Calculate profit
                    const priceDirection = position.direction === 'BUY' ? 
                        1 : 
                        -1;
                    
                    const priceDiff = (parseFloat(position.currentPrice) - parseFloat(position.entryPrice)) * priceDirection;
                    position.profit = (priceDiff * parseFloat(position.size)).toFixed(2);
                    position.profitPercent = ((priceDiff / parseFloat(position.entryPrice)) * 100).toFixed(2);
                });
                
                // Randomly close a position (5% chance)
                if (Math.random() < 0.05 && appState.positions.length > 0) {
                    const randomIndex = Math.floor(Math.random() * appState.positions.length);
                    appState.positions.splice(randomIndex, 1);
                }
                
                renderPositions(appState.positions);
            }
            
            // Randomly generate new trading signals (10% chance)
            if (Math.random() < 0.1) {
                generateRandomSignal();
            }
            
            // Randomly open new positions based on signals (15% chance if we have signals)
            if (Math.random() < 0.15 && appState.signals.length > 0) {
                const randomSignalIndex = Math.floor(Math.random() * appState.signals.length);
                const signal = appState.signals[randomSignalIndex];
                executeTrade(signal);
                
                // Remove the used signal
                appState.signals.splice(randomSignalIndex, 1);
                renderSignals(appState.signals);
            }
        }
    }

    // Generate random trading signals
    function generateRandomSignal() {
        const assets = ['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'];
        const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', 'D'];
        const strategies = ['Trend Following', 'Mean Reversion', 'Breakout', 'RSI Divergence', 'MACD Crossover', 'Support/Resistance'];
        
        const asset = assets[Math.floor(Math.random() * assets.length)];
        const timeframe = timeframes[Math.floor(Math.random() * timeframes.length)];
        const direction = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const strategy = strategies[Math.floor(Math.random() * strategies.length)];
        const price = parseFloat((Math.random() * 1000 + 50).toFixed(2));
        
        const signal = {
            id: `sig-${Math.floor(Math.random() * 100000)}`,
            symbol: asset,
            direction: direction,
            timeframe: timeframe,
            type: strategy,
            price: price,
            confidence: `${Math.floor(Math.random() * 30 + 70)}%`, // 70-99%
            time: new Date().toISOString()
        };
        
        appState.signals.push(signal);
        renderSignals(appState.signals);
        showNotification(`New ${direction} signal for ${asset} detected`, 'info');
    }

    // Functions to handle bot control
    async function startBot() {
        try {
            startBotBtn.classList.add('running');
            startBotBtn.innerHTML = 'Stop Bot <i class="fas fa-stop-circle"></i>';
            botStatusIndicator.classList.remove('status-disconnected');
            botStatusIndicator.classList.add('status-connected');
            botStatusText.textContent = 'Trading Bot: Active';
            
            // Update app state
            appState.botRunning = true;
            
            // Initialize with some data for testing
            if (appState.positions.length === 0) {
                // Add some initial positions
                for (let i = 0; i < 2; i++) {
                    generateRandomPosition();
                }
            }
            
            if (appState.signals.length === 0) {
                // Add some initial signals
                for (let i = 0; i < 3; i++) {
                    generateRandomSignal();
                }
            }
            
            // Set up interval to simulate market data updates
            botInterval = setInterval(simulateMarketUpdates, 3000);
            
            showNotification('Trading bot has been started', 'success');
        } catch (error) {
            console.error('Error starting bot:', error);
            botStatusIndicator.classList.remove('status-connected');
            botStatusIndicator.classList.add('status-disconnected');
            botStatusText.textContent = 'Trading Bot: Error';
            showNotification('Failed to start trading bot', 'error');
        }
    }

    // Generate a random position for simulation
    function generateRandomPosition() {
        const assets = ['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'];
        const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', 'D'];
        const strategies = ['Trend Following', 'Mean Reversion', 'Breakout', 'RSI Divergence', 'MACD Crossover'];
        
        const asset = assets[Math.floor(Math.random() * assets.length)];
        const direction = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const entryPrice = parseFloat((Math.random() * 1000 + 50).toFixed(2));
        const currentPrice = parseFloat((entryPrice * (1 + (Math.random() * 0.04 - 0.02))).toFixed(2));
        const size = parseFloat((Math.random() * 2 + 0.1).toFixed(2));
        
        // Calculate profit
        const priceDirection = direction === 'BUY' ? 1 : -1;
        const priceDiff = (currentPrice - entryPrice) * priceDirection;
        const profit = (priceDiff * size).toFixed(2);
        const profitPercent = ((priceDiff / entryPrice) * 100).toFixed(2);
        
        const position = {
            dealId: `pos-${Math.floor(Math.random() * 10000)}`,
            symbol: asset,
            direction: direction,
            size: size,
            entryPrice: entryPrice,
            currentPrice: currentPrice,
            stopLevel: entryPrice * (direction === 'BUY' ? 0.98 : 1.02),
            profitLevel: entryPrice * (direction === 'BUY' ? 1.05 : 0.95),
            openDate: new Date(Date.now() - Math.floor(Math.random() * 86400000)).toISOString(), // Random time in the last 24 hours
            profit: profit,
            profitPercent: profitPercent,
            status: 'OPEN',
            timeframe: timeframes[Math.floor(Math.random() * timeframes.length)],
            strategy: strategies[Math.floor(Math.random() * strategies.length)]
        };
        
        appState.positions.push(position);
        renderPositions(appState.positions);
    }

    async function stopBot() {
        try {
            startBotBtn.classList.remove('running');
            startBotBtn.innerHTML = 'Start Bot <i class="fas fa-play-circle"></i>';
            botStatusIndicator.classList.remove('status-connected');
            botStatusIndicator.classList.add('status-disconnected');
            botStatusText.textContent = 'Trading Bot: Stopped';
            
            // Update app state
            appState.botRunning = false;
            
            // Clear the interval
            if (botInterval) {
                clearInterval(botInterval);
                botInterval = null;
            }
            
            showNotification('Trading bot has been stopped', 'info');
        } catch (error) {
            console.error('Error stopping bot:', error);
            showNotification('Failed to stop trading bot', 'error');
        }
    }
});
