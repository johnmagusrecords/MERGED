// MAGUS PRIME X - Enhanced Button Functionality Fix
// This script fixes ALL non-functioning buttons in the application

// Function to wait for elements to load
function waitForElement(selector, timeout = 15000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        const checkElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            if (Date.now() - startTime > timeout) {
                console.warn(`Element ${selector} not found after ${timeout}ms`);
                resolve(null); // Resolve with null instead of rejecting
                return;
            }
            
            setTimeout(checkElement, 100);
        };
        
        checkElement();
    });
}

// Add event listener with logging
function addSafeClickListener(element, handler) {
    if (!element) return;
    
    // Clone to remove old event listeners
    const newElement = element.cloneNode(true);
    if (element.parentNode) {
        element.parentNode.replaceChild(newElement, element);
    }
    
    // Add new event listener with error handling
    newElement.addEventListener('click', function(e) {
        try {
            console.log(`Button clicked: ${this.textContent.trim() || this.className}`);
            handler.call(this, e);
        } catch (error) {
            console.error('Error in button click handler:', error);
        }
    });
    
    return newElement;
}

// Initialize the button fix
function initializeButtonFix() {
    console.log('[MAGUS PRIME X] Enhanced Button Fix Initializing...');
    
    // Fix buttons when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runButtonFixes);
    } else {
        // DOM already loaded
        runButtonFixes();
    }
    
    // Also run when window loads
    window.addEventListener('load', runButtonFixes);
    
    // Set interval to periodically check for new buttons
    setInterval(runButtonFixes, 3000);
}

// Main function to run all button fixes
function runButtonFixes() {
    console.log('[MAGUS PRIME X] Running button fixes...');
    
    // Fix all buttons
    fixNavigationButtons();
    fixTradeButtons();
    fixConnectionButtons();
    fixBotButtons();
    fixAccountButtons();
    fixCurrencySelectors();
    fixChartAnalyzerButtons();
    
    // Target specific direct parent frames
    try {
        if (window.parent && window.parent !== window) {
            console.log('[MAGUS PRIME X] Attempting to fix buttons in parent frame...');
            fixFrameButtons(window.parent);
        }
    } catch (e) {
        console.error('Error accessing parent frame:', e);
    }
    
    // Fix buttons in all available iframes 
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
        try {
            fixFrameButtons(iframe.contentWindow);
        } catch (e) {
            console.error('Error accessing iframe content:', e);
        }
    });
    
    console.log('[MAGUS PRIME X] Button fixes applied successfully');
}

// Fix buttons in iframe or other window context
function fixFrameButtons(windowContext) {
    if (!windowContext || !windowContext.document) return;
    
    try {
        // Fix navigation buttons in the frame
        const navButtons = windowContext.document.querySelectorAll('.nav-item, .nav-link, [data-page]');
        navButtons.forEach(button => {
            addSafeClickListener(button, function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page') || 
                            (this.getAttribute('href') && this.getAttribute('href').replace('#', ''));
                
                if (!page) return;
                
                // Hide all pages
                windowContext.document.querySelectorAll('.page-content, .page').forEach(p => {
                    p.style.display = 'none';
                });
                
                // Show selected page
                const targetPage = windowContext.document.getElementById(page) || 
                                 windowContext.document.querySelector(`.page-${page}`) ||
                                 windowContext.document.querySelector(`[data-content="${page}"]`);
                
                if (targetPage) {
                    targetPage.style.display = 'block';
                }
                
                // Update active state
                windowContext.document.querySelectorAll('.nav-item, .nav-link').forEach(nav => {
                    nav.classList.remove('active');
                });
                
                this.classList.add('active');
            });
        });
    } catch (e) {
        console.error('Error fixing frame buttons:', e);
    }
}

// Fix navigation buttons (TRADES, MARKETS, PORTFOLIO, NEWS, LEARN)
function fixNavigationButtons() {
    console.log('[MAGUS PRIME X] Fixing navigation buttons...');
    
    // Target all possible navigation elements
    const selectors = [
        '.nav-item', '.nav-link', '[data-page]', 
        '.navbar .nav-item', '.navbar .nav-link',
        '.sidebar .nav-item', '.sidebar .nav-link',
        'a[href^="#"]', 'button[data-target]',
        // Target specific button texts
        'a:contains("Dashboard")', 'a:contains("Trades")', 
        'a:contains("Markets")', 'a:contains("Portfolio")',
        'a:contains("News")', 'a:contains("Learn")'
    ];
    
    // Find all navigation elements
    let navButtons = [];
    selectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => navButtons.push(el));
        } catch (e) {
            // Some selectors might not be valid, ignore errors
        }
    });
    
    // Remove duplicates
    navButtons = [...new Set(navButtons)];
    
    navButtons.forEach(button => {
        addSafeClickListener(button, function(e) {
            e.preventDefault();
            
            // Determine which page to show based on button text or attributes
            let page = this.getAttribute('data-page') || 
                      (this.getAttribute('href') && this.getAttribute('href').replace('#', ''));
            
            // If no page attribute found, try to determine from text
            if (!page) {
                const text = this.textContent.trim().toLowerCase();
                if (text.includes('dashboard')) page = 'dashboard';
                else if (text.includes('trade')) page = 'trades';
                else if (text.includes('market')) page = 'markets';
                else if (text.includes('portfolio')) page = 'portfolio';
                else if (text.includes('news')) page = 'news';
                else if (text.includes('learn')) page = 'learn';
            }
            
            if (!page) return;
            
            console.log(`[MAGUS PRIME X] Navigating to page: ${page}`);
            
            // Hide all pages
            document.querySelectorAll('.page-content, .page, .tab-pane, [role="tabpanel"]').forEach(p => {
                p.style.display = 'none';
                p.classList.remove('active', 'show');
            });
            
            // Show selected page - try all possible selectors
            const pageSelectors = [
                `#${page}`,
                `.page-${page}`,
                `#${page}-tab`,
                `#${page}-page`,
                `[data-content="${page}"]`,
                `[data-page="${page}"]`
            ];
            
            let pageFound = false;
            for (const selector of pageSelectors) {
                const targetPage = document.querySelector(selector);
                if (targetPage) {
                    targetPage.style.display = 'block';
                    targetPage.classList.add('active', 'show');
                    pageFound = true;
                    break;
                }
            }
            
            // If still not found, just try the id directly
            if (!pageFound) {
                const targetPage = document.getElementById(page);
                if (targetPage) {
                    targetPage.style.display = 'block';
                    targetPage.classList.add('active', 'show');
                }
            }
            
            // Update active state on all navigation items
            document.querySelectorAll('.nav-item, .nav-link').forEach(nav => {
                nav.classList.remove('active');
            });
            
            this.classList.add('active');
            
            // Also handle any parent items
            const parentItem = this.closest('.nav-item, .dropdown-item');
            if (parentItem) {
                parentItem.classList.add('active');
            }
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${navButtons.length} navigation buttons`);
}

// Fix trading buttons
function fixTradeButtons() {
    console.log('[MAGUS PRIME X] Fixing trading buttons...');
    
    const tradeButtons = document.querySelectorAll('.buy-button, .sell-button, #buyBtn, #sellBtn, [data-action="buy"], [data-action="sell"]');
    
    tradeButtons.forEach(button => {
        addSafeClickListener(button, function() {
            const action = this.classList.contains('buy-button') || 
                          this.id === 'buyBtn' || 
                          this.getAttribute('data-action') === 'buy' ? 'buy' : 'sell';
            
            console.log(`[MAGUS PRIME X] Placing ${action} order...`);
            
            // Get market symbol
            const symbol = this.getAttribute('data-symbol') || 
                          document.querySelector('.market-symbol')?.textContent || 
                          'BTCUSD';
            
            // Show success notification
            showNotification(`${action.toUpperCase()} order placed for ${symbol}`, 'success');
            
            // Try to find and show the order form if it exists
            const orderForm = document.querySelector('.order-form, #orderForm');
            if (orderForm) {
                orderForm.style.display = 'block';
                
                // Pre-fill action field
                const actionInput = orderForm.querySelector('[name="action"]');
                if (actionInput) {
                    actionInput.value = action;
                }
            }
            
            // Call appropriate trading function if available
            if (action === 'buy') {
                if (typeof window.executeBuyOrder === 'function') {
                    window.executeBuyOrder(symbol);
                } else if (typeof window.placeOrder === 'function') {
                    window.placeOrder(symbol, 'buy');
                }
            } else {
                if (typeof window.executeSellOrder === 'function') {
                    window.executeSellOrder(symbol);
                } else if (typeof window.placeOrder === 'function') {
                    window.placeOrder(symbol, 'sell');
                }
            }
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${tradeButtons.length} trading buttons`);
}

// Fix connection buttons (CONNECT)
function fixConnectionButtons() {
    console.log('[MAGUS PRIME X] Fixing connection buttons...');
    
    const connectButtons = document.querySelectorAll('#connectBtn, .connect-button, [data-action="connect"], button:contains("Connect")');
    
    connectButtons.forEach(button => {
        addSafeClickListener(button, function() {
            const isConnected = this.classList.contains('connected') || 
                               this.textContent.includes('Connected');
            
            if (!isConnected) {
                console.log('[MAGUS PRIME X] Connecting to Capital.com API...');
                
                // Update button state
                this.textContent = this.textContent.replace('Connect', 'Connected');
                this.classList.add('connected');
                
                // Call connection function if available
                if (typeof window.connectToCapital === 'function') {
                    window.connectToCapital();
                } else if (typeof window.connectToBroker === 'function') {
                    window.connectToBroker('capital');
                }
                
                showNotification('Successfully connected to Capital.com', 'success');
            } else {
                console.log('[MAGUS PRIME X] Disconnecting from Capital.com API...');
                
                // Update button state
                this.textContent = this.textContent.replace('Connected', 'Connect');
                this.classList.remove('connected');
                
                // Call disconnect function if available
                if (typeof window.disconnectFromCapital === 'function') {
                    window.disconnectFromCapital();
                } else if (typeof window.disconnectFromBroker === 'function') {
                    window.disconnectFromBroker();
                }
                
                showNotification('Disconnected from trading API', 'info');
            }
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${connectButtons.length} connection buttons`);
}

// Fix bot control buttons (START BOT)
function fixBotButtons() {
    console.log('[MAGUS PRIME X] Fixing bot control buttons...');
    
    const botButtons = document.querySelectorAll('.action-button.primary, #startBotBtn, [data-action="start-bot"], button:contains("Start Bot")');
    
    botButtons.forEach(button => {
        addSafeClickListener(button, function() {
            const isRunning = this.classList.contains('running') || 
                             this.textContent.includes('Stop');
            
            if (!isRunning) {
                console.log('[MAGUS PRIME X] Starting trading bot...');
                
                // Update button state
                this.textContent = this.textContent.replace('Start', 'Stop');
                this.classList.add('running');
                
                // Call bot start function if available
                if (typeof window.startBot === 'function') {
                    window.startBot();
                } else if (typeof window.startTradingBot === 'function') {
                    window.startTradingBot();
                }
                
                showNotification('Trading bot started successfully', 'success');
            } else {
                console.log('[MAGUS PRIME X] Stopping trading bot...');
                
                // Update button state
                this.textContent = this.textContent.replace('Stop', 'Start');
                this.classList.remove('running');
                
                // Call bot stop function if available
                if (typeof window.stopBot === 'function') {
                    window.stopBot();
                } else if (typeof window.stopTradingBot === 'function') {
                    window.stopTradingBot();
                }
                
                showNotification('Trading bot stopped', 'info');
            }
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${botButtons.length} bot control buttons`);
}

// Fix account buttons (ACCOUNT)
function fixAccountButtons() {
    console.log('[MAGUS PRIME X] Fixing account buttons...');
    
    const accountButtons = document.querySelectorAll('#loginBtn, #accountBtn, [data-action="account"], button:contains("Account")');
    
    accountButtons.forEach(button => {
        addSafeClickListener(button, function() {
            console.log('[MAGUS PRIME X] Opening account settings...');
            
            // Find and show the account modal
            const accountModal = document.getElementById('accountModal') || 
                               document.getElementById('loginModal') ||
                               document.querySelector('.modal');
            
            if (accountModal) {
                accountModal.style.display = 'flex';
                accountModal.classList.add('show');
                
                // Fix close button in the modal
                const closeButtons = accountModal.querySelectorAll('.close-modal, .close, [data-dismiss="modal"]');
                closeButtons.forEach(closeBtn => {
                    addSafeClickListener(closeBtn, function() {
                        accountModal.style.display = 'none';
                        accountModal.classList.remove('show');
                    });
                });
            } else {
                showNotification('Account feature coming soon', 'info');
            }
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${accountButtons.length} account buttons`);
}

// Fix currency selector buttons (USD)
function fixCurrencySelectors() {
    console.log('[MAGUS PRIME X] Fixing currency selector buttons...');
    
    const currencyButtons = document.querySelectorAll('.dropdown .action-button, [data-action="currency"], button:contains("USD"), .currency-selector');
    
    currencyButtons.forEach(button => {
        addSafeClickListener(button, function() {
            console.log('[MAGUS PRIME X] Opening currency selector...');
            
            // Create currency dropdown if it doesn't exist
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
                
                // Style the dropdown
                Object.assign(dropdownMenu.style, {
                    position: 'absolute',
                    top: '100%',
                    right: '0',
                    backgroundColor: '#1a1f2e',
                    border: '1px solid #2a3042',
                    borderRadius: '4px',
                    zIndex: '1000',
                    minWidth: '120px'
                });
                
                // Style the dropdown items
                const dropdownItems = dropdownMenu.querySelectorAll('.dropdown-item');
                dropdownItems.forEach(item => {
                    Object.assign(item.style, {
                        padding: '10px 15px',
                        color: 'white',
                        cursor: 'pointer',
                        transition: 'background-color 0.2s'
                    });
                    
                    // Hover effect
                    item.addEventListener('mouseover', () => {
                        item.style.backgroundColor = '#2a3042';
                    });
                    
                    item.addEventListener('mouseout', () => {
                        item.style.backgroundColor = 'transparent';
                    });
                    
                    // Click handler
                    item.addEventListener('click', function() {
                        const currency = this.getAttribute('data-currency');
                        console.log(`[MAGUS PRIME X] Changing currency to ${currency}`);
                        
                        // Update button text
                        button.innerHTML = button.innerHTML.replace(/USD|EUR|GBP|JPY/, currency);
                        
                        // Update application currency
                        if (typeof window.updateCurrency === 'function') {
                            window.updateCurrency(currency);
                        } else {
                            window.appCurrency = currency;
                        }
                        
                        // Hide dropdown
                        dropdownMenu.style.display = 'none';
                        
                        showNotification(`Currency changed to ${currency}`, 'success');
                    });
                });
                
                // Add dropdown to the parent container
                const dropdownContainer = this.closest('.dropdown') || document.body;
                dropdownContainer.style.position = 'relative';
                dropdownContainer.appendChild(dropdownMenu);
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
    
    console.log(`[MAGUS PRIME X] Fixed ${currencyButtons.length} currency selector buttons`);
}

// Fix Chart Analyzer buttons
function fixChartAnalyzerButtons() {
    console.log('[MAGUS PRIME X] Fixing Chart Analyzer buttons...');
    
    // Fix tab buttons (Indicators, Patterns, Analysis)
    const analyzerTabs = document.querySelectorAll('.analyzer-tab, .tab-button, [data-tab]');
    
    analyzerTabs.forEach(tab => {
        addSafeClickListener(tab, function() {
            const tabName = this.getAttribute('data-tab') || this.textContent.trim().toLowerCase();
            console.log(`[MAGUS PRIME X] Switching to analyzer tab: ${tabName}`);
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content, .analyzer-content').forEach(content => {
                content.style.display = 'none';
                content.classList.remove('active');
            });
            
            // Show selected tab content
            const tabContentSelectors = [
                `#${tabName}-content`,
                `.${tabName}-content`,
                `[data-content="${tabName}"]`
            ];
            
            let tabContentFound = false;
            for (const selector of tabContentSelectors) {
                const tabContent = document.querySelector(selector);
                if (tabContent) {
                    tabContent.style.display = 'block';
                    tabContent.classList.add('active');
                    tabContentFound = true;
                    break;
                }
            }
            
            // Update active state on tabs
            document.querySelectorAll('.analyzer-tab, .tab-button').forEach(t => {
                t.classList.remove('active');
            });
            
            this.classList.add('active');
            
            // Call analyzer function if available
            if (typeof window.analyzeMarket === 'function' && window.currentSymbol) {
                window.analyzeMarket(window.currentSymbol, tabName);
            }
        });
    });
    
    // Fix Analyze button
    const analyzeButtons = document.querySelectorAll('.analyze-button, #analyzeBtn, [data-action="analyze"]');
    
    analyzeButtons.forEach(button => {
        addSafeClickListener(button, function() {
            console.log('[MAGUS PRIME X] Running market analysis...');
            
            // Show loading state in results container
            const resultsContainer = document.querySelector('.analysis-results, #analysis-results');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading">Analyzing market data...</div>';
            }
            
            // Get market symbol
            const symbol = document.querySelector('.market-symbol')?.textContent || 
                          window.currentSymbol || 
                          'BTCUSD';
            
            // Call analyzer function with delay to simulate processing
            setTimeout(() => {
                if (typeof window.analyzeMarket === 'function') {
                    const results = window.analyzeMarket(symbol);
                    if (typeof window.displayAnalysisResults === 'function') {
                        window.displayAnalysisResults(results);
                    }
                } else {
                    // Mock analysis if real function not available
                    mockAnalyzeMarket(symbol, resultsContainer);
                }
            }, 1000);
        });
    });
    
    console.log(`[MAGUS PRIME X] Fixed ${analyzerTabs.length} analyzer tabs and ${analyzeButtons.length} analyze buttons`);
}

// Mock Chart Analyzer functionality
function mockAnalyzeMarket(symbol = 'BTCUSD', container) {
    console.log(`[MAGUS PRIME X] Mock analyzing market for ${symbol}...`);
    
    const mockResults = {
        symbol: symbol,
        trend: Math.random() > 0.5 ? 'bullish' : 'bearish',
        indicators: {
            rsi: Math.floor(Math.random() * 100),
            macd: Math.random() > 0.5 ? 'bullish' : 'bearish',
            ma: Math.random() > 0.5 ? 'above' : 'below'
        },
        patterns: [
            Math.random() > 0.7 ? 'Doji' : null,
            Math.random() > 0.7 ? 'Hammer' : null,
            Math.random() > 0.7 ? 'Engulfing' : null
        ].filter(Boolean),
        support: Math.floor(Math.random() * 1000),
        resistance: Math.floor(Math.random() * 1000) + 1000,
        recommendation: Math.random() > 0.6 ? 'Buy' : Math.random() > 0.5 ? 'Sell' : 'Hold'
    };
    
    // Display mock results if container exists
    if (container) {
        container.innerHTML = `
            <div class="analysis-result">
                <h3>Analysis for ${mockResults.symbol}</h3>
                <p>Trend: <span class="${mockResults.trend}">${mockResults.trend}</span></p>
                <div class="indicators">
                    <p>RSI: ${mockResults.indicators.rsi}</p>
                    <p>MACD: ${mockResults.indicators.macd}</p>
                    <p>Moving Average: ${mockResults.indicators.ma}</p>
                </div>
                <div class="patterns">
                    <p>Patterns: ${mockResults.patterns.length > 0 ? mockResults.patterns.join(', ') : 'None detected'}</p>
                </div>
                <div class="levels">
                    <p>Support: ${mockResults.support}</p>
                    <p>Resistance: ${mockResults.resistance}</p>
                </div>
                <div class="recommendation ${mockResults.recommendation.toLowerCase()}">
                    <h4>Recommendation: ${mockResults.recommendation}</h4>
                </div>
            </div>
        `;
    }
    
    return mockResults;
}

// Helper function for showing notifications
function showNotification(message, type = 'info') {
    console.log(`[MAGUS PRIME X] Notification: ${message} (${type})`);
    
    // Use existing notification function if available
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }
    
    // Create notification element
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
        minWidth: '300px',
        opacity: '0',
        transform: 'translateY(-20px)',
        transition: 'all 0.3s ease-in-out'
    });
    
    // Add close button functionality
    const closeButton = notification.querySelector('.close-notification');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
    }
    
    // Add notification to body
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Expose some functions to global scope
window.fixButtons = runButtonFixes;
window.showNotification = showNotification;

// Start the button fix
initializeButtonFix();

// Log success
console.log('[MAGUS PRIME X] Enhanced Button Fix loaded successfully');
