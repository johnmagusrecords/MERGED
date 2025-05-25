// Direct injection script 
document.addEventListener('DOMContentLoaded', function() { 
    console.log("Loading button fix injection..."); 
    var script = document.createElement('script'); 
    script.src = '../main/fix-all-buttons.js'; 
    document.head.appendChild(script); 
    console.log("Button fix injection loaded"); 
}); 
