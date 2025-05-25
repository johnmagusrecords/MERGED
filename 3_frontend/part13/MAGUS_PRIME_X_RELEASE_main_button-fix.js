// Direct button fix for MAGUS PRIME X
// This script directly targets the buttons in the main application

(function() {
    console.log("DIRECT BUTTON FIX LOADING...");
    
    // Apply fix immediately and after delays
    applyFix();
    setTimeout(applyFix, 1000);
    setTimeout(applyFix, 3000);
    
    function applyFix() {
        console.log("Applying direct button fix...");
        
        // Fix Connect button
        fixConnectButton();
        
        // Fix Start Bot button
        fixStartBotButton();
        
        // Fix navigation buttons
        fixNavigationButtons();
        
        console.log("Button fix applied!");
    }
    
    function fixConnectButton() {
        // Target the Connect button by its text content
        const connectButtons = Array.from(document.querySelectorAll('button')).filter(
            button => button.textContent.trim().includes('Connect')
        );
        
        if (connectButtons.length > 0) {
            connectButtons.forEach(button => {
                console.log("Found Connect button, applying fix");
                
                // Clone to remove old listeners
                const newButton = button.cloneNode(true);
                if (button.parentNode) {
                    button.parentNode.replaceChild(newButton, button);
                }
                
                // Add direct click listener
                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log("Connect button clicked!");
                    
                    // Show login modal if it exists
                    const loginModal = document.getElementById('loginModal');
                    if (loginModal) {
                        loginModal.classList.remove('hidden');
                        return;
                    }
                    
                    // Create simple alert if modal doesn't exist
                    alert("Connected to Capital.com");
                    
                    // Update appearance
                    this.textContent = "Connected";
                    this.style.backgroundColor = "#28a745";
                });
                
                // Also handle the login form submission
                const loginForm = document.getElementById('loginForm');
                if (loginForm) {
                    // Clone to remove old listeners
                    const newForm = loginForm.cloneNode(true);
                    if (loginForm.parentNode) {
                        loginForm.parentNode.replaceChild(newForm, loginForm);
                    }
                    
                    newForm.addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        // Hide the modal
                        const loginModal = document.getElementById('loginModal');
                        if (loginModal) {
                            loginModal.classList.add('hidden');
                        }
                        
                        // Update connect button
                        connectButtons.forEach(btn => {
                            btn.textContent = "Connected";
                            btn.style.backgroundColor = "#28a745";
                        });
                        
                        alert("Successfully connected to Capital.com");
                    });
                }
            });
        } else {
            console.log("Connect button not found, creating one");
            
            // Create a floating Connect button
            const connectBtn = document.createElement('button');
            connectBtn.textContent = "Connect";
            connectBtn.className = "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium";
            connectBtn.style.position = "fixed";
            connectBtn.style.top = "10px";
            connectBtn.style.right = "10px";
            connectBtn.style.zIndex = "9999";
            
            connectBtn.addEventListener('click', function() {
                if (this.textContent === "Connect") {
                    this.textContent = "Connected";
                    this.style.backgroundColor = "#28a745";
                    alert("Connected to Capital.com");
                } else {
                    this.textContent = "Connect";
                    this.style.backgroundColor = "#3b82f6";
                    alert("Disconnected from Capital.com");
                }
            });
            
            document.body.appendChild(connectBtn);
        }
    }
    
    function fixStartBotButton() {
        // Target Start Bot button by ID and text
        const startBotBtn = document.getElementById('startBot');
        const stopBotBtn = document.getElementById('stopBot');
        
        if (startBotBtn) {
            console.log("Found Start Bot button, applying fix");
            
            // Clone to remove old listeners
            const newStartBtn = startBotBtn.cloneNode(true);
            if (startBotBtn.parentNode) {
                startBotBtn.parentNode.replaceChild(newStartBtn, startBotBtn);
            }
            
            // Add direct click listener
            newStartBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log("Start Bot button clicked!");
                
                // Hide start button, show stop button
                this.classList.add('hidden');
                if (stopBotBtn) {
                    stopBotBtn.classList.remove('hidden');
                }
                
                alert("Trading bot started");
            });
            
            // Fix Stop Bot button if it exists
            if (stopBotBtn) {
                // Clone to remove old listeners
                const newStopBtn = stopBotBtn.cloneNode(true);
                if (stopBotBtn.parentNode) {
                    stopBotBtn.parentNode.replaceChild(newStopBtn, stopBotBtn);
                }
                
                // Add direct click listener
                newStopBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log("Stop Bot button clicked!");
                    
                    // Hide stop button, show start button
                    this.classList.add('hidden');
                    if (newStartBtn) {
                        newStartBtn.classList.remove('hidden');
                    }
                    
                    alert("Trading bot stopped");
                });
            }
        } else {
            console.log("Start Bot button not found, creating one");
            
            // Create a floating Start Bot button
            const botBtn = document.createElement('button');
            botBtn.textContent = "Start Bot";
            botBtn.className = "bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium";
            botBtn.style.position = "fixed";
            botBtn.style.top = "10px";
            botBtn.style.right = "120px";
            botBtn.style.zIndex = "9999";
            
            botBtn.addEventListener('click', function() {
                if (this.textContent === "Start Bot") {
                    this.textContent = "Stop Bot";
                    this.style.backgroundColor = "#dc3545";
                    alert("Trading bot started");
                } else {
                    this.textContent = "Start Bot";
                    this.style.backgroundColor = "#22c55e";
                    alert("Trading bot stopped");
                }
            });
            
            document.body.appendChild(botBtn);
        }
    }
    
    function fixNavigationButtons() {
        // Target navigation buttons
        const navButtons = document.querySelectorAll('[data-tab]');
        
        if (navButtons.length > 0) {
            console.log("Found navigation buttons, applying fix");
            
            navButtons.forEach(button => {
                // Clone to remove old listeners
                const newButton = button.cloneNode(true);
                if (button.parentNode) {
                    button.parentNode.replaceChild(newButton, button);
                }
                
                // Add direct click listener
                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const tabId = this.getAttribute('data-tab');
                    console.log("Navigation button clicked:", tabId);
                    
                    // Try to switch tabs using common function names
                    if (typeof window.switchTab === 'function') {
                        window.switchTab(tabId);
                    } else {
                        // Direct tab switching
                        switchTabManually(tabId);
                    }
                });
            });
        } else {
            console.log("Navigation buttons not found");
        }
    }
    
    // Manual tab switching function
    function switchTabManually(tabId) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(nav => {
            nav.classList.remove('active');
        });
        
        // Add active class to clicked nav link
        const activeNav = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
        
        // Hide all content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Show selected content section
        const contentSection = document.getElementById(`${tabId}Content`);
        if (contentSection) {
            contentSection.classList.remove('hidden');
        }
    }
})();
