// EMERGENCY BUTTON FIX - DO NOT MODIFY 
document.addEventListener('DOMContentLoaded', function() { 
    console.log('EMERGENCY: Injecting button fixes...'); 
ECHO is off.
    // Inject the fix script directly 
    const script = document.createElement('script'); 
    script.src = './FORCE-FIX-BUTTONS.js'; 
    document.head.appendChild(script); 
ECHO is off.
    // Also copy functionality directly into page to ensure it works 
    setTimeout(function() { 
        try { 
            // Direct click handlers for all navigation buttons 
            document.querySelectorAll('.nav-item, .nav-link, [data-page]').forEach(function(button) { 
                button.addEventListener('click', function(e) { 
                    e.preventDefault(); 
                    if (page) { 
                        // Hide all pages 
                        document.querySelectorAll('.page-content, .page').forEach(function(p) { 
                            p.style.display = 'none'; 
                        }); 
ECHO is off.
                        // Show target page 
                        if (targetPage) { 
                            targetPage.style.display = 'block'; 
                        } 
ECHO is off.
                        // Update active state 
                        document.querySelectorAll('.nav-item, .nav-link').forEach(function(nav) { 
                            nav.classList.remove('active'); 
                        }); 
ECHO is off.
                        this.classList.add('active'); 
                    } 
                }); 
            }); 
            console.log('Emergency navigation fix applied!'); 
        } catch (e) { 
            console.error('Error applying emergency fix:', e); 
        } 
    }, 1000); 
}); 
