// MAGUS PRIME X button fix preload 
const fs = require('fs'); 
const path = require('path'); 
 
// Wait for document to be loaded 
document.addEventListener('DOMContentLoaded', function() { 
  // Read the button fix script 
  const buttonFixPath = path.join(__dirname, 'DirectButtonFix.js'); 
  if (fs.existsSync(buttonFixPath)) { 
    const buttonFixScript = fs.readFileSync(buttonFixPath, 'utf8'); 
 
    // Inject it into the page 
    const scriptElement = document.createElement('script'); 
    scriptElement.textContent = buttonFixScript; 
    document.head.appendChild(scriptElement); 
    console.log('MAGUS PRIME X button fix injected successfully!'); 
  } else { 
    console.error('Button fix script not found at:', buttonFixPath); 
  } 
}); 
