const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// Serve static files
app.use(express.static(__dirname));

// Serve the visual guide on the root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'visual-guide.html'));
});

// Start the server
app.listen(port, () => {
  console.log(`Button fix guide server running at http://localhost:${port}`);
});
