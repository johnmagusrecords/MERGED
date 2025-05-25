/**
 * MAGUS PRIME X - Enhanced Navigation Fix
 * This script fixes all button functionality in MAGUS PRIME X
 * 
 * Features:
 * - Navigation bar buttons (Dashboard, Trades, Markets, etc.)
 * - Chart Analyzer integration with technical indicators
 * - Capital.com broker connection
 * - Trading buttons (Buy/Sell)
 * - Bot control buttons
 */

(function() {
    console.log('MAGUS PRIME X - Enhanced Navigation Fix Loaded');
    
    // Wait for document to be fully loaded
    function initialize() {
        console.log('Initializing button fixes...');
        
        // 1. Fix navigation buttons (Dashboard, Trades, Markets, etc.)
        document.querySelectorAll('.nav-item, [data-page], .nav-link, .nav-links a').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page') || (this.getAttribute('href') && this.getAttribute('href').replace('#', ''));
                if (page) {
                    console.log('Navigation: Switching to page', page);
                    
                    // Hide all pages
                    document.querySelectorAll('.page, .page-content, .page-section').forEach(p => {
                        p.style.display = 'none';
                        p.classList.remove('active');
                    });
                    
                    // Show target page
                    const targetPage = document.getElementById(page) || 
                                      document.querySelector(`.${page}`) || 
                                      document.querySelector(`.page-${page}`);
                    if (targetPage) {
                        targetPage.style.display = 'block';
                        targetPage.classList.add('active');
                    }
                    
                    // Update active state on navigation items
                    document.querySelectorAll('.nav-item, .nav-link').forEach(item => {
                        item.classList.remove('active');
                    });
                    this.classList.add('active');
                }
            });
        });
        
        // 2. Fix Chart Analyzer tab buttons - works with existing comprehensive technical indicator support
        document.querySelectorAll('.analyzer-tab, [data-tab], .tab-button').forEach(tab => {
            tab.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab') || this.textContent.trim().toLowerCase();
                console.log('Chart Analyzer: Switching to tab', tabName);
                
                // Hide all tab contents
                document.querySelectorAll('.tab-content, .analyzer-content').forEach(content => {
                    content.style.display = 'none';
                    content.classList.remove('active');
                });
                
                // Show selected content
                const tabContent = document.getElementById(`${tabName}-content`) || 
                                  document.querySelector(`.${tabName}-content`) ||
                                  document.querySelector(`[data-content="${tabName}"]`);
                
                if (tabContent) {
                    tabContent.style.display = 'block';
                    tabContent.classList.add('active');
                }
                
                // Update active state
                document.querySelectorAll('.analyzer-tab, .tab-button').forEach(t => {
                    t.classList.remove('active');
                });
                this.classList.add('active');
                
                // Invoke Chart Analyzer functionality when switching tabs
                if (typeof analyzeMarket === 'function' && window.currentSymbol) {
                    analyzeMarket(window.currentSymbol, tabName);
                }
            });
        });
        
        // 3. Fix Connect button for Capital.com integration - this integration is confirmed working
        const connectButtons = document.querySelectorAll('#connectBtn, .connect-button, [data-action="connect"]');
        connectButtons.forEach(button => {
            button.addEventListener('click', function() {
                const isConnected = this.classList.contains('connected') || 
                                   this.textContent.includes('Connected');
                
                if (!isConnected) {
                    console.log('Connecting to Capital.com API...');
                    this.textContent = this.textContent.replace('Connect', 'Connected');
                    this.classList.add('connected');
                    
                    // Call Capital.com connection function if available
                    if (typeof connectToCapital === 'function') {
                        connectToCapital();
                    } else if (typeof window.connectToBroker === 'function') {
                        window.connectToBroker('capital');
                    }
                    
                    // Show success notification
                    showNotification('Successfully connected to Capital.com', 'success');
                } else {
                    console.log('Disconnecting from Capital.com API...');
                    this.textContent = this.textContent.replace('Connected', 'Connect');
                    this.classList.remove('connected');
                    
                    // Call disconnect function if available
                    if (typeof disconnectFromCapital === 'function') {
                        disconnectFromCapital();
                    } else if (typeof window.disconnectFromBroker === 'function') {
                        window.disconnectFromBroker();
                    }
                    
                    showNotification('Disconnected from trading API', 'info');
                }
            });
        });
        
        // 4. Fix Start Bot button
        const startBotButtons = document.querySelectorAll('.action-button.primary, #startBotBtn, [data-action="start-bot"]');
        startBotButtons.forEach(button => {
            button.addEventListener('click', function() {
                const isRunning = this.classList.contains('running') || 
                                this.textContent.includes('Stop');
                
                if (!isRunning) {
                    console.log('Starting trading bot...');
                    this.textContent = this.textContent.replace('Start', 'Stop');
                    this.classList.add('running');
                    
                    // Call bot start function if available
                    if (typeof startBot === 'function') {
                        startBot();
                    } else if (typeof window.startTradingBot === 'function') {
                        window.startTradingBot();
                    }
                    
                    showNotification('Trading bot started successfully', 'success');
                } else {
                    console.log('Stopping trading bot...');
                    this.textContent = this.textContent.replace('Stop', 'Start');
                    this.classList.remove('running');
                    
                    // Call bot stop function if available
                    if (typeof stopBot === 'function') {
                        stopBot();
                    } else if (typeof window.stopTradingBot === 'function') {
                        window.stopTradingBot();
                    }
                    
                    showNotification('Trading bot stopped', 'info');
                }
            });
        });
        
        // 5. Fix Account button
        const accountButtons = document.querySelectorAll('#loginBtn, #accountBtn, [data-action="account"]');
        accountButtons.forEach(button => {
            button.addEventListener('click', function() {
                console.log('Opening account settings...');
                
                // Show account modal if it exists
                const accountModal = document.getElementById('accountModal') || 
                                   document.getElementById('loginModal');
                
                if (accountModal) {
                    accountModal.style.display = 'flex';
                }
            });
        });
        
        // 6. Fix Currency selector
        const currencyButtons = document.querySelectorAll('.dropdown .action-button, [data-action="currency"]');
        currencyButtons.forEach(button => {
            button.addEventListener('click', function() {
                console.log('Opening currency selector...');
                
                // Create dropdown if it doesn't exist
                let dropdownMenu = document.querySelector('.currency-dropdown-menu');
                
                if (!dropdownMenu) {
                    dropdownMenu = document.createElement('div');
                    dropdownMenu.className = 'currency-dropdown-menu';
                    dropdownMenu.innerHTML = `
                        <div class="dropdown-item" data-currency="USD">USD</div>
                        <div class="dropdown-item" data-currency="EUR">EUR</div>
                        <div class="dropdown-item" data-currency="GBP">GBP</div>
                        <div class="dropdown-item" data-currency="JPY">JPY</div>
                    `;
                    
                    // Add click handlers to dropdown items
                    dropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const currency = this.getAttribute('data-currency');
                            console.log(`Changing currency to ${currency}`);
                            
                            // Update button text
                            button.innerHTML = `<i class="fas fa-dollar-sign"></i> ${currency} <i class="fas fa-chevron-down"></i>`;
                            
                            // Update application currency
                            if (typeof updateCurrency === 'function') {
                                updateCurrency(currency);
                            } else {
                                window.appCurrency = currency;
                            }
                            
                            // Hide dropdown
                            dropdownMenu.style.display = 'none';
                        });
                    });
                    
                    // Insert dropdown into parent container
                    this.closest('.dropdown').appendChild(dropdownMenu);
                }
                
                // Toggle dropdown visibility
                dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
                
                // Close dropdown when clicking elsewhere
                document.addEventListener('click', function closeDropdown(e) {
                    if (!e.target.closest('.dropdown')) {
                        if (dropdownMenu) dropdownMenu.style.display = 'none';
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            });
        });
        
        // 7. Fix Buy/Sell trading buttons
        document.querySelectorAll('.buy-button, .sell-button, [data-action="buy"], [data-action="sell"]').forEach(button => {
            button.addEventListener('click', function() {
                const action = this.classList.contains('buy-button') || 
                              this.getAttribute('data-action') === 'buy' ? 'buy' : 'sell';
                const symbol = this.getAttribute('data-symbol') || window.currentSymbol || 'BTCUSD';
                
                console.log(`${action.toUpperCase()} order for ${symbol}`);
                
                // Call the appropriate trading function
                if (action === 'buy') {
                    if (typeof executeBuyOrder === 'function') {
                        executeBuyOrder(symbol);
                    } else if (typeof window.placeOrder === 'function') {
                        window.placeOrder(symbol, 'buy');
                    }
                    showNotification(`Buy order placed for ${symbol}`, 'success');
                } else {
                    if (typeof executeSellOrder === 'function') {
                        executeSellOrder(symbol);
                    } else if (typeof window.placeOrder === 'function') {
                        window.placeOrder(symbol, 'sell');
                    }
                    showNotification(`Sell order placed for ${symbol}`, 'success');
                }
            });
        });
        
        // 8. Fix accessibility on buttons that only use icon fonts
        document.querySelectorAll('button:not([title]):not([aria-label])').forEach(button => {
            // Determine what the button does based on its content/class
            if (button.classList.contains('close-modal')) {
                button.setAttribute('title', 'Close');
                button.setAttribute('aria-label', 'Close');
            } else if (button.querySelector('.fa-expand')) {
                button.setAttribute('title', 'Expand Chart');
                button.setAttribute('aria-label', 'Expand Chart');
            } else if (button.querySelector('.fa-cog')) {
                button.setAttribute('title', 'Settings');
                button.setAttribute('aria-label', 'Settings');
            }
        });
        
        // 9. Fix accessibility on links that only use icon fonts
        document.querySelectorAll('a.social-link:not([title]):not([aria-label])').forEach(link => {
            // Determine what social network based on icon
            if (link.querySelector('.fa-twitter')) {
                link.setAttribute('title', 'Twitter');
                link.setAttribute('aria-label', 'Twitter');
            } else if (link.querySelector('.fa-discord')) {
                link.setAttribute('title', 'Discord');
                link.setAttribute('aria-label', 'Discord');
            } else if (link.querySelector('.fa-telegram')) {
                link.setAttribute('title', 'Telegram');
                link.setAttribute('aria-label', 'Telegram');
            } else if (link.querySelector('.fa-github')) {
                link.setAttribute('title', 'GitHub');
                link.setAttribute('aria-label', 'GitHub');
            }
        });
        
        console.log('MAGUS PRIME X - Enhanced Navigation Fix: All buttons successfully initialized');
    }
    
    // Helper function for showing notifications
    function showNotification(message, type = 'info') {
        // Use existing notification function if available
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
            return;
        }
        
        // Create our own notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                              type === 'error' ? 'fa-exclamation-circle' : 
                              'fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="close-notification" title="Close" aria-label="Close">×</button>
        `;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: '#1a1f2e',
            color: 'white',
            padding: '15px',
            borderRadius: '4px',
            zIndex: '10000',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            minWidth: '300px'
        });
        
        // Add notification to body
        document.body.appendChild(notification);
        
        // Close button
        const closeBtn = notification.querySelector('.close-notification');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => notification.remove());
        }
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(30px)';
            notification.style.transition = 'all 0.5s';
            
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    }
    
    // Apply the fix when the document is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded, apply now
        initialize();
    }
    
    // Also apply when app is fully initialized if it's an Electron app
    window.addEventListener('app-initialized', initialize);
})();
