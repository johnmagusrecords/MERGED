const Store = require("electron-store");
const fs = require("fs");
const path = require("path");

// Create a test script to verify credential handling
console.log("====== CREDENTIAL HANDLING TEST ======");

// Initialize store
const store = new Store();

// Check if any credentials are already stored
const existingCredentials = store.get("capital-credentials");
console.log("Existing credentials found:", existingCredentials ? "YES" : "NO");
if (existingCredentials) {
  console.log("Credential content type:", typeof existingCredentials);
  console.log("Keys present:", Object.keys(existingCredentials).join(", "));
}

// Clear any stored credentials
console.log("\nClearing credentials...");
store.delete("capital-credentials");

// Verify credentials were cleared
const afterClearCredentials = store.get("capital-credentials");
console.log(
  "Credentials after clearing:",
  afterClearCredentials ? "Still present" : "Successfully cleared",
);

// Test setting new credentials
console.log("\nTesting setting new credentials...");
store.set("capital-credentials", {
  key: "test-key",
  password: "test-password",
  identifier: "test-identifier",
});

// Verify new credentials were set
const newCredentials = store.get("capital-credentials");
console.log("New credentials set:", newCredentials ? "YES" : "NO");
if (newCredentials) {
  console.log(
    "New credential values:",
    JSON.stringify(newCredentials, null, 2),
  );
}

// Check localStorage simulation
console.log("\nChecking for localStorage credential files...");
const appDataPath =
  process.env.APPDATA ||
  (process.platform === "darwin"
    ? process.env.HOME + "/Library/Application Support"
    : "/var/local");
const configPath = path.join(appDataPath, "magus-prime-x");

if (fs.existsSync(configPath)) {
  console.log("Config directory exists at:", configPath);
  try {
    const files = fs.readdirSync(configPath);
    console.log("Files found:", files.join(", "));

    files.forEach((file) => {
      if (file.endsWith(".json")) {
        const filePath = path.join(configPath, file);
        const content = fs.readFileSync(filePath, "utf8");
        console.log(`\nFile ${file} content:`, content);
      }
    });
  } catch (err) {
    console.error("Error reading directory:", err);
  }
} else {
  console.log("Config directory not found at:", configPath);
}

// Final clean up
console.log("\nFinal cleanup...");
store.delete("capital-credentials");
console.log("====== TEST COMPLETED ======");
