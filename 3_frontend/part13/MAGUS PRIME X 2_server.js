const express = require("express");
const path = require("path");
const app = express();
const port = 3000;

// Serve static files from the current directory
app.use(express.static(path.join(__dirname)));

// Start the server
app.listen(port, () => {
  console.log(`MAGUS PRIME X test server running at http://localhost:${port}`);
  console.log(
    `Open your browser to http://localhost:${port}/test-navbar-buttons.html`,
  );
});
