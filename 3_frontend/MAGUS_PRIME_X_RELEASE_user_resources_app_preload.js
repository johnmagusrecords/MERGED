// MAGUS PRIME X Enhanced Preload Script 
window.addEventListener('DOMContentLoaded', () =
    console.log('MAGUS PRIME X - Loading navigation fixes...'); 
    // Inject our navigation fix script 
    const fixScript = document.createElement('script'); 
    fixScript.src = './magus_prime_navfix.js'; 
    document.head.appendChild(fixScript); 
ECHO is off.
    // Ensure accessibility attributes are set on icon-only buttons and links 
    setTimeout(() =
        document.querySelectorAll('button:not([title]):not([aria-label])').forEach(btn =
            if (btn.querySelector('.fa-times')) { 
                btn.setAttribute('title', 'Close'); 
                btn.setAttribute('aria-label', 'Close'); 
            } 
        }); 
    }, 1000); 
}); 
