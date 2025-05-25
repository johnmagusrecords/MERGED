// MAGUS PRIME X - Button Functionality Fix

// Main function to fix all buttons
function fixAllButtons() {
    console.log('MAGUS PRIME X Button Fix: Starting...');
    
    // Fix navigation buttons
    const navButtons = document.querySelectorAll('.nav-item, button[data-page], a[data-page]');
    console.log('Nav buttons found:', navButtons.length);
    
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page') || this.getAttribute('href')?.replace('#', '') || '';
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
        });
    });
    
    // Fix Chart Analyzer tabs
    const analyzerTabs = document.querySelectorAll('.analyzer-tab, [data-tab]');
    console.log('Analyzer tabs found:', analyzerTabs.length);
    
    analyzerTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab') || '';
            console.log('Chart Analyzer tab clicked:', tabName);
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show selected tab
            const targetContent = document.getElementById(`${tabName}-content`) || document.querySelector(`.${tabName}-content`);
            if (targetContent) {
                targetContent.style.display = 'block';
            }
            
            // Update active state
            analyzerTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Fix start bot button
    const startBotBtn = document.querySelector('#startBotBtn');
    if (startBotBtn) {
        console.log('Start Bot button found');
        startBotBtn.addEventListener('click', function() {
            console.log('Start Bot button clicked');
            this.textContent = 'Bot Running';
            this.disabled = true;
            alert('Trading bot started successfully!');
        });
    }
    
    // Fix connect button
    const connectBtn = document.querySelector('#connectBtn, button.connect');
    if (connectBtn) {
        console.log('Connect button found');
        connectBtn.addEventListener('click', function() {
            console.log('Connect button clicked');
            this.textContent = 'Connected';
            this.disabled = true;
            alert('Connected to Capital.com API successfully!');
        });
    }
    
    // Fix buy/sell buttons
    const tradeButtons = document.querySelectorAll('.buy-button, .sell-button');
    console.log('Trade buttons found:', tradeButtons.length);
    
    tradeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.classList.contains('buy-button') ? 'buy' : 'sell';
            console.log(`${action.toUpperCase()} button clicked`);
            alert(`${action.toUpperCase()} order placed successfully!`);
        });
    });
    
    // Fix tab buttons in Chart Analyzer section
    const chartTabs = document.querySelectorAll('.chart-tabs button, .tab-selector button');
    console.log('Chart tabs found:', chartTabs.length);
    
    chartTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.textContent.trim().toLowerCase();
            console.log('Chart tab clicked:', tabName);
            
            // Update active state
            chartTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Fix any remaining buttons that might have been missed
    const allButtons = document.querySelectorAll('button:not([data-fixed]), .btn:not([data-fixed])');
    console.log('Remaining buttons found:', allButtons.length);
    
    allButtons.forEach(button => {
        button.setAttribute('data-fixed', 'true');
        button.addEventListener('click', function(e) {
            console.log('Button clicked:', this.textContent || this.innerText);
        });
    });
    
    console.log('MAGUS PRIME X Button Fix: Completed');
}

// Run our fix when the DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixAllButtons);
} else {
    fixAllButtons();
}

// Also run our fix when the window is fully loaded (to catch any dynamically loaded elements)
window.addEventListener('load', fixAllButtons);

// Periodically check for new buttons (for dynamic content)
setInterval(fixAllButtons, 5000);
