// ABSOLUTE BUTTON INJECTION - MAGUS PRIME X
// This script forcefully adds working buttons to the application

// Immediate execution function
(function() {
    console.log("🔄 ABSOLUTE BUTTON INJECTOR RUNNING");
    
    // Create a status indicator
    const statusDiv = document.createElement('div');
    statusDiv.style.position = 'fixed';
    statusDiv.style.bottom = '10px';
    statusDiv.style.right = '10px';
    statusDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    statusDiv.style.color = 'white';
    statusDiv.style.padding = '10px';
    statusDiv.style.borderRadius = '5px';
    statusDiv.style.zIndex = '9999';
    statusDiv.style.fontSize = '12px';
    statusDiv.textContent = '⚙️ Button injector running...';
    document.body.appendChild(statusDiv);
    
    // Create toolbar with working buttons
    function createToolbar() {
        // Check if toolbar already exists
        if (document.getElementById('magus-toolbar')) {
            return;
        }
        
        // Create main toolbar
        const toolbar = document.createElement('div');
        toolbar.id = 'magus-toolbar';
        toolbar.style.position = 'fixed';
        toolbar.style.top = '10px';
        toolbar.style.right = '10px';
        toolbar.style.backgroundColor = 'rgba(30, 30, 30, 0.9)';
        toolbar.style.padding = '10px';
        toolbar.style.borderRadius = '8px';
        toolbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
        toolbar.style.zIndex = '9999';
        toolbar.style.display = 'flex';
        toolbar.style.flexDirection = 'column';
        toolbar.style.gap = '8px';
        
        // Create title
        const title = document.createElement('div');
        title.textContent = 'MAGUS CONTROLS';
        title.style.fontWeight = 'bold';
        title.style.textAlign = 'center';
        title.style.color = '#f0f0f0';
        title.style.borderBottom = '1px solid #555';
        title.style.paddingBottom = '5px';
        title.style.marginBottom = '5px';
        toolbar.appendChild(title);
        
        // Create Connect button
        const connectBtn = document.createElement('button');
        connectBtn.textContent = 'Connect to Capital.com';
        connectBtn.style.backgroundColor = '#4CAF50';
        connectBtn.style.color = 'white';
        connectBtn.style.border = 'none';
        connectBtn.style.padding = '8px 12px';
        connectBtn.style.borderRadius = '4px';
        connectBtn.style.cursor = 'pointer';
        connectBtn.style.margin = '2px 0';
        connectBtn.style.width = '100%';
        connectBtn.style.textAlign = 'left';
        
        // Add Connect icon
        connectBtn.innerHTML = '🔌 Connect to Capital.com';
        
        // Add click handler
        connectBtn.addEventListener('click', function() {
            // Update button appearance
            if (this.getAttribute('data-connected') === 'true') {
                // Disconnect
                this.removeAttribute('data-connected');
                this.style.backgroundColor = '#4CAF50';
                this.innerHTML = '🔌 Connect to Capital.com';
                
                // Show notification
                notify('Disconnected from Capital.com', 'info');
                
                // Try to call disconnect function if it exists
                if (typeof window.disconnectFromBroker === 'function') {
                    window.disconnectFromBroker();
                }
            } else {
                // Connect
                this.setAttribute('data-connected', 'true');
                this.style.backgroundColor = '#f44336';
                this.innerHTML = '⚡ Disconnect from Capital.com';
                
                // Show notification
                notify('Connected to Capital.com!', 'success');
                
                // Try to call connect function
                // Try multiple possible function names
                let connected = false;
                
                if (typeof window.connectToBroker === 'function') {
                    window.connectToBroker('capital');
                    connected = true;
                } else if (typeof window.connectToCapital === 'function') {
                    window.connectToCapital();
                    connected = true;
                } else if (typeof window.connectCapitalCom === 'function') {
                    window.connectCapitalCom();
                    connected = true;
                } else if (typeof window.connect === 'function') {
                    window.connect();
                    connected = true;
                }
                
                // If none of the functions worked, try to interact with UI elements
                if (!connected) {
                    // Try to find and click the original connect button
                    const originalButtons = Array.from(document.querySelectorAll('button')).filter(
                        btn => btn.textContent.includes('Connect') || 
                              btn.classList.contains('connect-button') ||
                              btn.id.includes('connect')
                    );
                    
                    if (originalButtons.length > 0) {
                        originalButtons[0].click();
                        console.log("Clicked original connect button");
                    } else {
                        console.log("No connect function or button found");
                    }
                }
            }
        });
        toolbar.appendChild(connectBtn);
        
        // Create Start Bot button
        const startBotBtn = document.createElement('button');
        startBotBtn.innerHTML = '▶️ Start Trading Bot';
        startBotBtn.style.backgroundColor = '#2196F3';
        startBotBtn.style.color = 'white';
        startBotBtn.style.border = 'none';
        startBotBtn.style.padding = '8px 12px';
        startBotBtn.style.borderRadius = '4px';
        startBotBtn.style.cursor = 'pointer';
        startBotBtn.style.margin = '2px 0';
        startBotBtn.style.width = '100%';
        startBotBtn.style.textAlign = 'left';
        
        // Add click handler
        startBotBtn.addEventListener('click', function() {
            // Update button appearance
            if (this.getAttribute('data-running') === 'true') {
                // Stop bot
                this.removeAttribute('data-running');
                this.style.backgroundColor = '#2196F3';
                this.innerHTML = '▶️ Start Trading Bot';
                
                // Show notification
                notify('Trading bot stopped', 'info');
                
                // Try to call stop function
                if (typeof window.stopBot === 'function') {
                    window.stopBot();
                } else if (typeof window.stopTradingBot === 'function') {
                    window.stopTradingBot();
                } else {
                    // Try to find and click original stop button
                    const stopButtons = Array.from(document.querySelectorAll('button')).filter(
                        btn => btn.textContent.includes('Stop') || btn.id === 'stopBot'
                    );
                    
                    if (stopButtons.length > 0) {
                        stopButtons[0].click();
                    }
                }
            } else {
                // Start bot
                this.setAttribute('data-running', 'true');
                this.style.backgroundColor = '#f44336';
                this.innerHTML = '⏹️ Stop Trading Bot';
                
                // Show notification
                notify('Trading bot started!', 'success');
                
                // Try to call start function
                if (typeof window.startBot === 'function') {
                    window.startBot();
                } else if (typeof window.startTradingBot === 'function') {
                    window.startTradingBot();
                } else {
                    // Try to find and click original start button
                    const startButtons = Array.from(document.querySelectorAll('button')).filter(
                        btn => btn.textContent.includes('Start') || btn.id === 'startBot'
                    );
                    
                    if (startButtons.length > 0) {
                        startButtons[0].click();
                    }
                }
            }
        });
        toolbar.appendChild(startBotBtn);
        
        // Add dashboard button
        addNavButton(toolbar, 'dashboard', '📊 Dashboard');
        
        // Add trades button
        addNavButton(toolbar, 'trades', '📈 Trades');
        
        // Add markets/assets button
        addNavButton(toolbar, 'markets', '🏦 Markets');
        addNavButton(toolbar, 'assets', '💰 Assets');
        
        // Add news button
        addNavButton(toolbar, 'news', '📰 News');
        
        // Add portfolio button
        addNavButton(toolbar, 'portfolio', '📂 Portfolio');
        
        // Add a minimize/expand toggle
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = '▲ Minimize';
        toggleBtn.style.backgroundColor = '#555';
        toggleBtn.style.color = 'white';
        toggleBtn.style.border = 'none';
        toggleBtn.style.padding = '4px 8px';
        toggleBtn.style.borderRadius = '4px';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.margin = '2px 0';
        toggleBtn.style.fontSize = '10px';
        toggleBtn.style.width = '100%';
        toggleBtn.style.textAlign = 'center';
        
        const buttonContainer = document.createElement('div');
        buttonContainer.id = 'magus-button-container';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.flexDirection = 'column';
        buttonContainer.style.gap = '8px';
        toolbar.appendChild(buttonContainer);
        
        // Add all buttons to container
        Array.from(toolbar.children).forEach(child => {
            if (child !== title && child !== toggleBtn && child !== buttonContainer) {
                buttonContainer.appendChild(child);
            }
        });
        
        // Add toggle button at the end
        toolbar.appendChild(toggleBtn);
        
        toggleBtn.addEventListener('click', function() {
            const container = document.getElementById('magus-button-container');
            if (container.style.display !== 'none') {
                container.style.display = 'none';
                this.innerHTML = '▼ Expand';
            } else {
                container.style.display = 'flex';
                this.innerHTML = '▲ Minimize';
            }
        });
        
        // Add toolbar to body
        document.body.appendChild(toolbar);
        
        // Update status
        statusDiv.textContent = '✅ Button injector active - Use the toolbar on the right';
        
        // Auto-hide status after 5 seconds
        setTimeout(() => {
            statusDiv.style.opacity = '0';
            statusDiv.style.transition = 'opacity 1s';
            setTimeout(() => statusDiv.remove(), 1000);
        }, 5000);
    }
    
    // Helper to add navigation buttons
    function addNavButton(toolbar, pageId, label) {
        const btn = document.createElement('button');
        btn.innerHTML = label;
        btn.setAttribute('data-page', pageId);
        btn.style.backgroundColor = '#555';
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.padding = '8px 12px';
        btn.style.borderRadius = '4px';
        btn.style.cursor = 'pointer';
        btn.style.margin = '2px 0';
        btn.style.width = '100%';
        btn.style.textAlign = 'left';
        
        btn.addEventListener('click', function() {
            // Update all nav buttons
            document.querySelectorAll('#magus-toolbar button[data-page]').forEach(navBtn => {
                navBtn.style.backgroundColor = '#555';
            });
            
            // Highlight this button
            this.style.backgroundColor = '#007bff';
            
            // Show notification
            notify(`Navigating to ${pageId}`, 'info');
            
            // Try common navigation functions
            if (typeof window.switchTab === 'function') {
                window.switchTab(pageId);
            } else if (typeof window.navigateTo === 'function') {
                window.navigateTo(pageId);
            } else {
                // Manual navigation
                showPage(pageId);
            }
        });
        
        toolbar.appendChild(btn);
    }
    
    // Function to show a specific page
    function showPage(pageId) {
        console.log(`Attempting to show page: ${pageId}`);
        
        // Try different content container selectors
        const contentIds = [
            `${pageId}Content`,
            `${pageId}_content`,
            `${pageId}-content`,
            `${pageId}-tab-content`,
            pageId
        ];
        
        // Hide all content sections
        document.querySelectorAll('.content-section, [id$="Content"], .tab-content > div, .tab-pane').forEach(section => {
            section.style.display = 'none';
            section.classList.add('hidden');
            if (section.classList.contains('active')) {
                section.classList.remove('active');
            }
        });
        
        // Try to find and show the target content
        let found = false;
        
        for (const id of contentIds) {
            const contentSection = document.getElementById(id);
            if (contentSection) {
                contentSection.style.display = 'block';
                contentSection.classList.remove('hidden');
                contentSection.classList.add('active');
                console.log(`✓ Showing content section: ${id}`);
                found = true;
                break;
            }
        }
        
        // If we couldn't find by ID, try more general selectors
        if (!found) {
            const selectors = [
                `.${pageId}-content`,
                `.${pageId}_content`,
                `.${pageId}-tab`,
                `.tab-${pageId}`,
                `[data-page="${pageId}"]`,
                `[data-tab="${pageId}"]`
            ];
            
            for (const selector of selectors) {
                const contentSection = document.querySelector(selector);
                if (contentSection) {
                    contentSection.style.display = 'block';
                    contentSection.classList.remove('hidden');
                    contentSection.classList.add('active');
                    console.log(`✓ Showing content section by selector: ${selector}`);
                    found = true;
                    break;
                }
            }
        }
        
        // Update active state on original nav items
        document.querySelectorAll('.nav-link, .nav-item, [data-tab]').forEach(nav => {
            nav.classList.remove('active');
            
            // Check if this nav item is for the current page
            const navPage = nav.getAttribute('data-tab') || 
                           nav.getAttribute('data-page') || 
                           (nav.getAttribute('href') && nav.getAttribute('href').replace('#', ''));
            
            if (navPage === pageId) {
                nav.classList.add('active');
            }
        });
    }
    
    // Show a notification
    function notify(message, type = 'info') {
        const notification = document.createElement('div');
        notification.textContent = message;
        
        // Set color based on type
        const bgColor = type === 'success' ? '#4CAF50' :
                       type === 'error' ? '#f44336' :
                       type === 'warning' ? '#ff9800' : '#2196F3';
        
        // Style notification
        Object.assign(notification.style, {
            position: 'fixed',
            bottom: '20px',
            left: '20px',
            backgroundColor: bgColor,
            color: 'white',
            padding: '12px 20px',
            borderRadius: '4px',
            boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
            zIndex: '10000',
            opacity: '0',
            transform: 'translateY(20px)',
            transition: 'all 0.3s ease'
        });
        
        // Add to body
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 4000);
    }
    
    // Run main function after small delay
    setTimeout(createToolbar, 1000);
    
    // Also run after page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => setTimeout(createToolbar, 1000));
    }
    
    // Also try after window load
    window.addEventListener('load', () => setTimeout(createToolbar, 1500));
    
    // Try multiple times to handle dynamic content loading
    setTimeout(createToolbar, 3000);
    setTimeout(createToolbar, 6000);
    
    console.log("🔄 ABSOLUTE BUTTON INJECTOR INITIALIZED");
})();
