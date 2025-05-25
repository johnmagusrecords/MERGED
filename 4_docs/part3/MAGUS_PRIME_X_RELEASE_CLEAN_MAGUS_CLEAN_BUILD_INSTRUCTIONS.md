# MAGUS PRIME X - Clean Build Guide

This document provides step-by-step instructions for creating a completely clean build of MAGUS PRIME X without any stored credentials.

## Preparation Steps

### 1. Create a New Windows User Account

1. Open Windows Settings → Accounts → Family & other users
2. Click "Add someone else to this PC"
3. Choose "I don't have this person's sign-in information"
4. Select "Add a user without a Microsoft account"
5. Enter a username like "MagusBuild" and password
6. Make sure to give the new account administrative privileges

### 2. Copy Source Files

1. Log in to the new user account
2. Create a folder like `C:\MAGUS_BUILD`
3. Copy **ONLY** these files from your original project:
   - All HTML files (except any that might contain credentials)
   - CSS files from the css folder
   - JavaScript files from the js folder
   - Python scripts (chart_analyzer.py, capital_com_trader.py, etc.)
   - Asset files (images, icons)
   - package.json and package-lock.json

### 3. Modify Credential Handling

Modify the electron.js file to prevent auto-loading credentials by replacing these lines:

```javascript
ipcMain.on('get-credentials', (event) => {
    event.reply('credentials', store.get('capital-credentials'));
});
```

With this safer version:

```javascript
ipcMain.on('get-credentials', (event) => {
    // Always return null for the distribution version
    event.reply('credentials', null);
    
    // Clear any existing credentials
    store.delete('capital-credentials');
});
```

## Building Process

### 1. Install Dependencies

1. Open Command Prompt as Administrator
2. Navigate to your project folder:
   ```
   cd C:\MAGUS_BUILD
   ```
3. Install Node.js dependencies:
   ```
   npm install
   ```

### 2. Create the Build

1. Run the build command:
   ```
   npm run build
   ```
2. Wait for the build process to complete
3. The clean build will be available in the `dist\win-unpacked` folder

## Verify Clean Build

1. Test the application by running `Magus Prime X.exe` from the build folder
2. Confirm it starts with no pre-filled credentials
3. Verify the Capital.com login screen requires entering credentials
4. Test the Chart Analyzer module with sample data or test credentials

## Prepare for Distribution

1. Copy the clean build to a distribution folder
2. Include the user documentation:
   - MAGUS_PRIME_X_FEATURES.md
   - MAGUS_PRIME_X_USER_GUIDE.md
3. Add a README.txt file explaining that users need their own Capital.com credentials

## Future Updates

For future builds, always:
1. Use a clean environment for building
2. Never store credentials in source code
3. Implement proper credential handling that isolates each user's information
4. Consider a dedicated credential manager that uses the system's secure storage

---

Following these steps will ensure your MAGUS PRIME X distribution is free from any personal credentials while maintaining all functionality, including the comprehensive Chart Analyzer module and Capital.com broker connection.
