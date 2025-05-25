# MAGUS PRIME X - Distribution Checklist

## Important Security Steps Before Distribution

To ensure your personal Capital.com credentials are completely removed before distributing the application:

### Step 1: Clear Application Data
1. Delete the following folders if they exist:
   - `%APPDATA%\magus-prime-x`
   - Any user-data folders in the application directory

### Step 2: Create a Clean Distribution Package
1. Copy **ONLY** the files from the `user` folder to a new ZIP file or folder
2. **DO NOT** run the application before distributing it (this prevents your credentials from being saved)
3. Make sure the README instructions clearly state that users need their own Capital.com credentials

### Step 3: Test on a Separate Computer
1. Before final distribution, test the application on a different computer
2. Verify that it starts with no pre-filled credentials
3. Ensure the Chart Analyzer module works with test credentials
4. Confirm the Capital.com connection works properly

## What to Include in Distribution

The distribution package should contain:
- The Magus Prime X.exe executable
- All supporting files in the `user` folder
- Documentation files (README.md, QUICK_START_GUIDE.md)
- The CLEAR_CREDENTIALS.bat script (for users to clear their own credentials if needed)

## What to Exclude from Distribution

Do not include:
- The `main` folder with source code
- Any configuration files containing credentials
- The `.env` file
- Any folders containing cached data or user settings

## Critical Notes for Users

Ensure your documentation reminds users:
1. They must use their own Capital.com API credentials
2. All technical indicators, candlestick pattern detection, and chart pattern recognition features are included
3. The broker connection is fully functional but requires proper API credentials
4. Their credentials will be stored securely on their local machine only

---

Following these steps will ensure your personal trading account remains secure while providing users with the full functionality of MAGUS PRIME X.
