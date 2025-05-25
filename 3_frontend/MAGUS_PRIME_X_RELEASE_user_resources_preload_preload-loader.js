// Preload Loader with EMERGENCY BUTTON FIX 
document.addEventListener('DOMContentLoaded', function() { 
  // Load original preload 
  const iframe1 = document.createElement('iframe'); 
  iframe1.src = 'file://' + __dirname + '/preload/preload.html'; 
  iframe1.style.display = 'none'; 
  document.body.appendChild(iframe1); 
ECHO is off.
  // Load emergency fix 
  const iframe2 = document.createElement('iframe'); 
  iframe2.src = 'file://' + __dirname + '/preload/force-fix.html'; 
  iframe2.style.display = 'none'; 
  document.body.appendChild(iframe2); 
ECHO is off.
  // Direct script injection 
  const script = document.createElement('script'); 
  script.src = 'file://' + __dirname + '/preload/FORCE-FIX-BUTTONS.js'; 
  document.body.appendChild(script); 
}); 
