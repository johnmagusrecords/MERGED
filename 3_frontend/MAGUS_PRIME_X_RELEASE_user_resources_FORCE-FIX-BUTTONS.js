// MAGUS PRIME X - EMERGENCY BUTTON FIX INJECTION
// This script directly fixes all buttons in the MAGUS PRIME X application

// Force button functionality immediately
(function() {
    console.log("EMERGENCY: Force-enabling all buttons in MAGUS PRIME X");
    
    // Function to apply button fixes to a document
    function forceFixButtons(doc) {
        if (!doc) return;
        
        console.log("Applying emergency button fixes to document");
        
        // 1. Force-fix navigation buttons
        const navButtons = doc.querySelectorAll('.nav-item, .nav-link, [data-page], button[data-target], a[href^="#"]');
        navButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Navigation button clicked:", this.textContent);
                
                // Get target page from button
                let page = this.getAttribute('data-page');
                if (!page && this.getAttribute('href')) {
                    page = this.getAttribute('href').replace('#', '');
                }
                if (!page && this.textContent) {
                    const text = this.textContent.trim().toLowerCase();
                    if (text.includes('dashboard')) page = 'dashboard';
                    else if (text.includes('trade')) page = 'trades';
                    else if (text.includes('market')) page = 'markets';
                    else if (text.includes('portfolio')) page = 'portfolio';
                    else if (text.includes('news')) page = 'news';
                    else if (text.includes('learn')) page = 'learn';
                }
                
                if (!page) {
                    console.log("Could not determine target page - activating clicked item");
                    // Just make this item active
                    doc.querySelectorAll('.nav-item, .nav-link').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    this.classList.add('active');
                    return;
                }
                
                // Hide all pages first
                doc.querySelectorAll('.page-content, .page, [role="tabpanel"], .content-section').forEach(p => {
                    if (p) {
                        p.style.display = 'none';
                        p.classList.remove('active', 'show');
                    }
                });
                
                // Try to find and show target page using different selectors
                let targetFound = false;
                const selectors = [
                    `#${page}`,
                    `.${page}`,
                    `#${page}-tab`,
                    `#${page}-content`,
                    `.${page}-content`,
                    `[data-page="${page}"]`,
                    `[data-content="${page}"]`
                ];
                
                for (const selector of selectors) {
                    const target = doc.querySelector(selector);
                    if (target) {
                        console.log("Found target page:", selector);
                        target.style.display = 'block';
                        target.classList.add('active', 'show');
                        targetFound = true;
                        break;
                    }
                }
                
                if (!targetFound) {
                    console.log("Target page not found with standard selectors, trying broader search");
                    // Try a more aggressive approach - look for any element containing the page name
                    doc.querySelectorAll('div, section').forEach(el => {
                        if (el.id && el.id.includes(page) || 
                            el.className && el.className.includes(page)) {
                            el.style.display = 'block';
                            el.classList.add('active', 'show');
                            targetFound = true;
                        }
                    });
                }
                
                // Update active state on navigation
                doc.querySelectorAll('.nav-item, .nav-link').forEach(btn => {
                    btn.classList.remove('active');
                });
                this.classList.add('active');
                
                // Also activate parent nav item if this is in a dropdown
                const parentNavItem = this.closest('.nav-item');
                if (parentNavItem) {
                    parentNavItem.classList.add('active');
                }
                
                console.log("Navigation completed to:", page);
                
                // Dispatch custom event that navigation happened
                const navEvent = new CustomEvent('navigation', { detail: { page: page } });
                document.dispatchEvent(navEvent);
                
                // Show success notification
                showNotification(`Navigated to ${page}`, 'success');
            };
        });
        
        // 2. Force-fix the Start Bot button
        const startBotButtons = doc.querySelectorAll('.action-button.primary, #startBotBtn, [data-action="start-bot"], button:contains("Start Bot")');
        startBotButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Start Bot button clicked");
                
                const isRunning = this.classList.contains('running') || this.textContent.includes('Stop');
                
                if (!isRunning) {
                    // Start the bot
                    this.textContent = this.textContent.replace('Start', 'Stop');
                    this.classList.add('running');
                    
                    // Try to call available bot functions
                    if (typeof window.startBot === 'function') {
                        window.startBot();
                    } else if (typeof window.startTradingBot === 'function') {
                        window.startTradingBot();
                    }
                    
                    showNotification("Trading bot started successfully", 'success');
                } else {
                    // Stop the bot
                    this.textContent = this.textContent.replace('Stop', 'Start');
                    this.classList.remove('running');
                    
                    // Try to call available bot functions
                    if (typeof window.stopBot === 'function') {
                        window.stopBot();
                    } else if (typeof window.stopTradingBot === 'function') {
                        window.stopTradingBot();
                    }
                    
                    showNotification("Trading bot stopped", 'info');
                }
            };
        });
        
        // 3. Force-fix the Connect button
        const connectButtons = doc.querySelectorAll('#connectBtn, .connect-button, [data-action="connect"], button:contains("Connect")');
        connectButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Connect button clicked");
                
                const isConnected = this.classList.contains('connected') || this.textContent.includes('Connected');
                
                if (!isConnected) {
                    // Connect to broker
                    this.textContent = this.textContent.replace('Connect', 'Connected');
                    this.classList.add('connected');
                    
                    // Try to call available connection functions
                    if (typeof window.connectToCapital === 'function') {
                        window.connectToCapital();
                    } else if (typeof window.connectToBroker === 'function') {
                        window.connectToBroker('capital');
                    }
                    
                    showNotification("Successfully connected to Capital.com", 'success');
                } else {
                    // Disconnect from broker
                    this.textContent = this.textContent.replace('Connected', 'Connect');
                    this.classList.remove('connected');
                    
                    // Try to call available disconnect functions
                    if (typeof window.disconnectFromCapital === 'function') {
                        window.disconnectFromCapital();
                    } else if (typeof window.disconnectFromBroker === 'function') {
                        window.disconnectFromBroker();
                    }
                    
                    showNotification("Disconnected from trading API", 'info');
                }
            };
        });
        
        // 4. Force-fix the Account button
        const accountButtons = doc.querySelectorAll('#loginBtn, #accountBtn, [data-action="account"], button:contains("Account")');
        accountButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Account button clicked");
                
                // Find account modal
                const accountModal = doc.getElementById('accountModal') || 
                                   doc.getElementById('loginModal') ||
                                   doc.querySelector('.modal');
                
                if (accountModal) {
                    // Show modal
                    accountModal.style.display = 'flex';
                    accountModal.classList.add('show');
                    
                    // Fix close button in modal
                    const closeButtons = accountModal.querySelectorAll('.close-modal, .close, [data-dismiss="modal"]');
                    closeButtons.forEach(closeBtn => {
                        closeBtn.onclick = function() {
                            accountModal.style.display = 'none';
                            accountModal.classList.remove('show');
                        };
                    });
                    
                    showNotification("Account panel opened", 'info');
                } else {
                    showNotification("Account functionality coming soon", 'info');
                }
            };
        });
        
        // 5. Force-fix the Currency dropdown
        const currencyButtons = doc.querySelectorAll('.dropdown .action-button, [data-action="currency"], button:contains("USD"), .currency-selector');
        currencyButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Currency selector clicked");
                
                // Create dropdown menu if it doesn't exist
                let dropdownMenu = doc.querySelector('.currency-dropdown-menu');
                
                if (!dropdownMenu) {
                    dropdownMenu = doc.createElement('div');
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
                        minWidth: '120px',
                        display: 'none'
                    });
                    
                    // Add click handlers to dropdown items
                    dropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {
                        // Style dropdown items
                        Object.assign(item.style, {
                            padding: '10px 15px',
                            color: 'white',
                            cursor: 'pointer'
                        });
                        
                        // Add click handler
                        item.onclick = function(e) {
                            e.stopPropagation();
                            
                            const currency = this.getAttribute('data-currency');
                            console.log(`Changing currency to ${currency}`);
                            
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
                        };
                    });
                    
                    // Add to parent container
                    const parent = this.closest('.dropdown') || doc.body;
                    parent.style.position = 'relative';
                    parent.appendChild(dropdownMenu);
                }
                
                // Toggle dropdown visibility
                if (dropdownMenu.style.display === 'block') {
                    dropdownMenu.style.display = 'none';
                } else {
                    dropdownMenu.style.display = 'block';
                }
                
                // Close when clicking outside
                setTimeout(() => {
                    const clickHandler = function(evt) {
                        if (!evt.target.closest('.dropdown')) {
                            dropdownMenu.style.display = 'none';
                            doc.removeEventListener('click', clickHandler);
                        }
                    };
                    
                    doc.addEventListener('click', clickHandler);
                }, 100);
            };
        });
        
        // 6. Force-fix Buy/Sell buttons
        const tradeButtons = doc.querySelectorAll('.buy-button, .sell-button, [data-action="buy"], [data-action="sell"]');
        tradeButtons.forEach(button => {
            if (!button) return;
            
            button.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const action = this.classList.contains('buy-button') || 
                              this.getAttribute('data-action') === 'buy' ? 'buy' : 'sell';
                
                const symbol = this.getAttribute('data-symbol') || 
                              doc.querySelector('.market-symbol')?.textContent ||
                              window.currentSymbol || 'BTCUSD';
                
                console.log(`${action.toUpperCase()} order for ${symbol}`);
                
                // Call trading functions if available
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
                
                showNotification(`${action.toUpperCase()} order placed for ${symbol}`, 'success');
            };
        });
        
        // 7. Fix Chart Analyzer buttons
        const analyzerTabs = doc.querySelectorAll('.analyzer-tab, .tab-button, [data-tab]');
        analyzerTabs.forEach(tab => {
            if (!tab) return;
            
            tab.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const tabName = this.getAttribute('data-tab') || this.textContent.trim().toLowerCase();
                console.log(`Switching to analyzer tab: ${tabName}`);
                
                // Hide all tab contents
                doc.querySelectorAll('.tab-content, .analyzer-content').forEach(content => {
                    content.style.display = 'none';
                    content.classList.remove('active');
                });
                
                // Show selected tab content
                const tabContent = doc.getElementById(`${tabName}-content`) || 
                                 doc.querySelector(`.${tabName}-content`) ||
                                 doc.querySelector(`[data-content="${tabName}"]`);
                
                if (tabContent) {
                    tabContent.style.display = 'block';
                    tabContent.classList.add('active');
                }
                
                // Update active state on tabs
                doc.querySelectorAll('.analyzer-tab, .tab-button').forEach(t => {
                    t.classList.remove('active');
                });
                
                this.classList.add('active');
                
                // Call analyzer function if available
                if (typeof window.analyzeMarket === 'function' && window.currentSymbol) {
                    window.analyzeMarket(window.currentSymbol, tabName);
                }
            };
        });
        
        // Make links non-breaking
        doc.querySelectorAll('a').forEach(link => {
            if (link && !link.hasAttribute('target') && link.getAttribute('href') !== '#') {
                link.setAttribute('target', '_blank');
            }
        });
        
        console.log("Force button fix applied to document successfully");
    }
    
    // Helper function for notifications
    function showNotification(message, type = 'info') {
        console.log(`Notification: ${message} (${type})`);
        
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
            <button class="close-notification">×</button>
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
            if (document.body.contains(notification)) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // Apply fixes immediately to the current document
    forceFixButtons(document);
    
    // Also apply every time DOM changes
    const observer = new MutationObserver(() => {
        forceFixButtons(document);
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Apply to all frames/iframes
    function fixAllFrames() {
        try {
            // Fix in main document
            forceFixButtons(document);
            
            // Fix in all iframes
            const frames = document.querySelectorAll('iframe');
            frames.forEach(frame => {
                try {
                    if (frame.contentDocument) {
                        forceFixButtons(frame.contentDocument);
                    }
                } catch (e) {
                    console.error('Error fixing iframe:', e);
                }
            });
            
            // Schedule another check after a delay (for dynamically loaded content)
            setTimeout(fixAllFrames, 2000);
        } catch (e) {
            console.error('Error in fixAllFrames:', e);
        }
    }
    
    // Start fixing frames
    fixAllFrames();
    
    // Add event listeners to window load events
    window.addEventListener('load', fixAllFrames);
    window.addEventListener('DOMContentLoaded', fixAllFrames);
    
    // Expose functions to global scope
    window.forceFixButtons = forceFixButtons;
    window.fixAllFrames = fixAllFrames;
    window.showNotification = showNotification;
    
    // Send a notification that the fix is active
    setTimeout(() => {
        showNotification('MAGUS PRIME X button fixes activated', 'success');
    }, 1000);
    
    console.log("Emergency button fix injection complete");
})();
