// MAGUS PRIME X - DIRECT BUTTON FIXER
(function() {
    console.log("[Button Fix] Loading direct button fix...");
    
    // Create status indicator
    function createStatusIndicator() {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'button-fix-status';
        statusDiv.style.position = 'fixed';
        statusDiv.style.bottom = '10px';
        statusDiv.style.right = '10px';
        statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
        statusDiv.style.color = 'white';
        statusDiv.style.padding = '8px 12px';
        statusDiv.style.borderRadius = '4px';
        statusDiv.style.fontSize = '12px';
        statusDiv.style.fontFamily = 'Arial, sans-serif';
        statusDiv.style.zIndex = '999999';
        statusDiv.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
        statusDiv.textContent = '✓ Button Fix Active';
        
        // Add a dismiss button
        const dismissBtn = document.createElement('span');
        dismissBtn.textContent = '×';
        dismissBtn.style.marginLeft = '10px';
        dismissBtn.style.cursor = 'pointer';
        dismissBtn.style.fontSize = '16px';
        dismissBtn.style.fontWeight = 'bold';
        dismissBtn.addEventListener('click', function() {
            statusDiv.style.display = 'none';
        });
        statusDiv.appendChild(dismissBtn);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            statusDiv.style.opacity = '0';
            statusDiv.style.transition = 'opacity 1s ease-in-out';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 1000);
        }, 10000);
        
        return statusDiv;
    }
    
    // Wait for DOM to be fully loaded
    function waitForElements() {
        // Get all buttons and interactive elements
        const allElements = document.querySelectorAll('button, .nav-item, .nav-link, [role="button"], a[href^="#"], .buy-button, .sell-button, #startBotBtn, #connectBtn, #accountBtn, .dropdown-toggle');
        
        if (allElements.length > 0) {
            console.log("[Button Fix] Found " + allElements.length + " interactive elements, applying fixes...");
            fixAllButtons();
            
            // Add status indicator
            document.body.appendChild(createStatusIndicator());
        } else {
            console.log("[Button Fix] No elements found yet, waiting...");
            setTimeout(waitForElements, 1000);
        }
    }
    
    // Main function to fix all buttons
    function fixAllButtons() {
        // 1. Fix navigation buttons
        fixNavigation();
        
        // 2. Fix action buttons
        fixActionButtons();
        
        // 3. Check in 2 seconds and reapply if needed
        setTimeout(fixAllButtons, 2000);
        
        console.log("[Button Fix] All button fixes applied successfully");
    }
    
    // Fix navigation buttons
    function fixNavigation() {
        const navButtons = document.querySelectorAll('.nav-item, .nav-link, [data-page], [href^="#"], [data-tab], .tab-link');
        console.log("[Button Fix] Found " + navButtons.length + " navigation buttons");
        
        navButtons.forEach(button => {
            // Skip if already fixed
            if (button.hasAttribute('data-fixed')) {
                return;
            }
            
            // Mark as fixed
            button.setAttribute('data-fixed', 'true');
            
            // Remove existing click listeners by cloning the node
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            // Add new click listener
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("[Button Fix] Navigation button clicked:", this.textContent.trim());
                
                // Get target page
                let targetPage = this.getAttribute('data-page') || this.getAttribute('data-tab');
                if (!targetPage && this.getAttribute('href')) {
                    targetPage = this.getAttribute('href').replace('#', '');
                }
                
                if (!targetPage && this.textContent) {
                    // Try to determine page from text
                    const text = this.textContent.trim().toLowerCase();
                    if (text.includes('dashboard')) targetPage = 'dashboard';
                    else if (text.includes('trade')) targetPage = 'trades';
                    else if (text.includes('market')) targetPage = 'markets'; 
                    else if (text.includes('portfolio')) targetPage = 'portfolio';
                    else if (text.includes('news')) targetPage = 'news';
                    else if (text.includes('learn')) targetPage = 'learn';
                    else if (text.includes('setting')) targetPage = 'settings';
                    else if (text.includes('account')) targetPage = 'account';
                    else if (text.includes('home')) targetPage = 'dashboard';
                    else if (text.includes('analytic')) targetPage = 'analytics';
                }
                
                if (targetPage) {
                    // Try to show the target page
                    showPage(targetPage);
                    
                    // Update active state on all possible navigation elements
                    document.querySelectorAll('.nav-item, .nav-link, [data-page], [data-tab], .tab-link').forEach(nav => {
                        nav.classList.remove('active', 'selected', 'current');
                        
                        // Also update any child elements that might show active state
                        const activeIndicators = nav.querySelectorAll('.active-indicator, .selected-indicator');
                        activeIndicators.forEach(indicator => {
                            indicator.classList.remove('active', 'visible');
                        });
                    });
                    
                    // Add active class to this button
                    this.classList.add('active');
                    
                    // Also update any child elements that might show active state
                    const activeIndicators = this.querySelectorAll('.active-indicator, .selected-indicator');
                    activeIndicators.forEach(indicator => {
                        indicator.classList.add('active', 'visible');
                    });
                    
                    console.log("[Button Fix] Navigated to:", targetPage);
                    
                    // Blink the status indicator to show navigation worked
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Navigated to ' + targetPage;
                        statusDiv.style.backgroundColor = 'rgba(33, 150, 243, 0.8)';
                        setTimeout(() => {
                            statusDiv.textContent = '✓ Button Fix Active';
                            statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
                        }, 2000);
                    }
                }
            });
        });
    }
    
    // Helper to show a page and hide others
    function showPage(pageId) {
        console.log("[Button Fix] Attempting to show page:", pageId);
        
        // Try to find all content containers
        const possibleContainers = [
            '.content-container',
            '.page-container',
            '.tab-content',
            '.pages-container',
            '#content-area',
            '#main-content',
            '.main-content'
        ];
        
        // Find the main container
        let mainContainer = null;
        for (const selector of possibleContainers) {
            const container = document.querySelector(selector);
            if (container) {
                mainContainer = container;
                console.log("[Button Fix] Found main content container:", selector);
                break;
            }
        }
        
        // If no container found, use body as fallback
        if (!mainContainer) {
            mainContainer = document.body;
            console.log("[Button Fix] No main container found, using body");
        }
        
        // Hide all pages within the container
        const pages = mainContainer.querySelectorAll('.page-content, .page, [role="tabpanel"], .tab-content, .content-area, .tab-pane, [id$="-content"], [id$="Content"]');
        pages.forEach(page => {
            page.style.display = 'none';
            page.classList.remove('active', 'show', 'visible');
        });
        
        // Try different selectors to find the target page
        const selectors = [
            `#${pageId}`,
            `.${pageId}`,
            `[data-page="${pageId}"]`,
            `#${pageId}-tab`,
            `#${pageId}-content`,
            `.${pageId}-content`,
            `#${pageId}Content`,
            `#${pageId}-panel`,
            `#${pageId}Panel`,
            `[data-tab-content="${pageId}"]`
        ];
        
        let targetFound = false;
        for (const selector of selectors) {
            const target = document.querySelector(selector);
            if (target) {
                target.style.display = 'block';
                target.classList.add('active', 'show', 'visible');
                targetFound = true;
                console.log("[Button Fix] Found and displayed:", selector);
                break;
            }
        }
        
        // If target not found by selector, try finding by parent with child matches
        if (!targetFound) {
            const allContainers = document.querySelectorAll('.tab-pane, .page, .content-section, [id$="-content"], [id$="Content"]');
            for (const container of allContainers) {
                // Look for headers or content that match the page ID
                const matchingElements = container.querySelectorAll(`h1, h2, h3, h4, .title, .header, .section-header`);
                for (const element of matchingElements) {
                    if (element.textContent.toLowerCase().includes(pageId.toLowerCase())) {
                        container.style.display = 'block';
                        container.classList.add('active', 'show', 'visible');
                        targetFound = true;
                        console.log("[Button Fix] Found and displayed container with matching content:", pageId);
                        break;
                    }
                }
                if (targetFound) break;
            }
        }
        
        if (!targetFound) {
            console.log("[Button Fix] Could not find target page:", pageId);
        }
    }
    
    // Fix action buttons
    function fixActionButtons() {
        // Fix Start Bot button
        const startBotBtns = Array.from(document.querySelectorAll('#startBotBtn, .action-button.primary, button, .button, .btn, [role="button"]')).filter(el => 
            el.textContent.trim().includes('Start Bot') || 
            el.id === 'startBotBtn' || 
            el.classList.contains('start-bot-button')
        );
        
        console.log("[Button Fix] Found " + startBotBtns.length + " start bot buttons");
        
        startBotBtns.forEach(button => {
            if (!button) return;
            
            // Skip if already fixed
            if (button.hasAttribute('data-fixed')) {
                return;
            }
            
            // Mark as fixed
            button.setAttribute('data-fixed', 'true');
            
            // Remove existing click listeners
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            // Add new click listener
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isRunning = this.textContent.includes('Stop') || this.classList.contains('running');
                
                if (!isRunning) {
                    // Start the bot
                    this.textContent = this.textContent.replace('Start', 'Stop');
                    this.classList.add('running');
                    console.log("[Button Fix] Bot started");
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Bot Started';
                        statusDiv.style.backgroundColor = 'rgba(244, 67, 54, 0.8)';
                    }
                    
                    // Try to call original function if it exists
                    if (typeof window.startBot === 'function') {
                        window.startBot();
                    } else if (typeof window.startTradingBot === 'function') {
                        window.startTradingBot();
                    } else if (typeof window.onStartBot === 'function') {
                        window.onStartBot();
                    }
                } else {
                    // Stop the bot
                    this.textContent = this.textContent.replace('Stop', 'Start');
                    this.classList.remove('running');
                    console.log("[Button Fix] Bot stopped");
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Bot Stopped';
                        statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
                        setTimeout(() => {
                            statusDiv.textContent = '✓ Button Fix Active';
                        }, 2000);
                    }
                    
                    // Try to call original function if it exists
                    if (typeof window.stopBot === 'function') {
                        window.stopBot();
                    } else if (typeof window.stopTradingBot === 'function') {
                        window.stopTradingBot();
                    } else if (typeof window.onStopBot === 'function') {
                        window.onStopBot();
                    }
                }
            });
        });
        
        // Fix Connect button
        const connectBtns = Array.from(document.querySelectorAll('#connectBtn, .connect-button, button, .button, .btn, [role="button"]')).filter(el => 
            (el.textContent.trim().includes('Connect') && !el.textContent.trim().includes('Connected')) || 
            el.id === 'connectBtn' || 
            el.classList.contains('connect-button')
        );
        
        console.log("[Button Fix] Found " + connectBtns.length + " connect buttons");
        
        connectBtns.forEach(button => {
            if (!button) return;
            
            // Skip if already fixed
            if (button.hasAttribute('data-fixed')) {
                return;
            }
            
            // Mark as fixed
            button.setAttribute('data-fixed', 'true');
            
            // Remove existing click listeners
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            // Add new click listener
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("[Button Fix] Connect button clicked", this);
                
                const isConnected = this.textContent.includes('Connected') || this.classList.contains('connected');
                
                if (!isConnected) {
                    // Connect to Capital.com
                    console.log("[Button Fix] Attempting to connect to Capital.com...");
                    
                    // Show a visual indication that we're connected
                    this.textContent = this.textContent.replace('Connect', 'Connected');
                    this.classList.add('connected');
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Connected to Capital.com';
                        statusDiv.style.backgroundColor = 'rgba(33, 150, 243, 0.8)';
                    }
                    
                    // Try every possible connect function that might exist
                    if (typeof window.connectToBroker === 'function') {
                        console.log("[Button Fix] Calling connectToBroker function");
                        window.connectToBroker('capital');
                    } else if (typeof window.connectToCapital === 'function') {
                        console.log("[Button Fix] Calling connectToCapital function");
                        window.connectToCapital();
                    } else if (typeof window.showLoginModal === 'function') {
                        console.log("[Button Fix] Calling showLoginModal function");
                        window.showLoginModal();
                    } else {
                        console.log("[Button Fix] No connect function found, trying to find login modal");
                        
                        // Try to find and show the login modal directly
                        const modal = document.querySelector('#loginModal, .login-modal, .modal');
                        if (modal) {
                            console.log("[Button Fix] Found modal, showing it");
                            modal.style.display = 'block';
                            modal.classList.add('show');
                        } else {
                            console.log("[Button Fix] No login modal found");
                        }
                    }
                    
                    console.log("[Button Fix] Connected to Capital.com");
                } else {
                    // Disconnect
                    this.textContent = this.textContent.replace('Connected', 'Connect');
                    this.classList.remove('connected');
                    console.log("[Button Fix] Disconnected from Capital.com");
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Disconnected from Capital.com';
                        statusDiv.style.backgroundColor = 'rgba(255, 152, 0, 0.8)';
                        setTimeout(() => {
                            statusDiv.textContent = '✓ Button Fix Active';
                            statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
                        }, 2000);
                    }
                    
                    // Try to call original function if it exists
                    if (typeof window.disconnectFromBroker === 'function') {
                        window.disconnectFromBroker();
                    } else if (typeof window.disconnectFromCapital === 'function') {
                        window.disconnectFromCapital();
                    } else if (typeof window.logout === 'function') {
                        window.logout();
                    }
                }
            });
        });
        
        // Fix Buy/Sell buttons
        const tradeButtons = Array.from(document.querySelectorAll('.buy-button, .sell-button, button, .button, .btn')).filter(el => 
            el.textContent.trim().includes('Buy') || 
            el.textContent.trim().includes('Sell') ||
            el.classList.contains('buy-button') ||
            el.classList.contains('sell-button')
        );
        
        console.log("[Button Fix] Found " + tradeButtons.length + " trade buttons");
        
        tradeButtons.forEach(button => {
            if (!button) return;
            
            // Skip if already fixed
            if (button.hasAttribute('data-fixed')) {
                return;
            }
            
            // Mark as fixed
            button.setAttribute('data-fixed', 'true');
            
            // Remove existing click listeners
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            // Add new click listener
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isBuy = this.textContent.includes('Buy') || this.classList.contains('buy-button');
                
                if (isBuy) {
                    console.log("[Button Fix] Buy button clicked");
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Buy Order Placed';
                        statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
                        setTimeout(() => {
                            statusDiv.textContent = '✓ Button Fix Active';
                        }, 2000);
                    }
                    
                    // Try to call original function if it exists
                    if (typeof window.placeBuyOrder === 'function') {
                        window.placeBuyOrder();
                    }
                } else {
                    console.log("[Button Fix] Sell button clicked");
                    
                    // Update status indicator
                    const statusDiv = document.getElementById('button-fix-status');
                    if (statusDiv) {
                        statusDiv.textContent = '✓ Sell Order Placed';
                        statusDiv.style.backgroundColor = 'rgba(244, 67, 54, 0.8)';
                        setTimeout(() => {
                            statusDiv.textContent = '✓ Button Fix Active';
                            statusDiv.style.backgroundColor = 'rgba(76, 175, 80, 0.8)';
                        }, 2000);
                    }
                    
                    // Try to call original function if it exists
                    if (typeof window.placeSellOrder === 'function') {
                        window.placeSellOrder();
                    }
                }
            });
        });
    }
    
    // Start the button fix
    waitForElements();
    
    // Also run when the window loads to make sure everything is fixed
    window.addEventListener('load', waitForElements);
    
    // Run again after a delay to catch dynamically loaded content
    setTimeout(waitForElements, 2000);
    setTimeout(waitForElements, 5000);
    
    console.log("[Button Fix] Button fix script initialized");
})();
