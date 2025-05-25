# Running Magus Prime X Signal Dispatcher

## Setup and Installation

1. Open PowerShell or Command Prompt
2. Navigate to the project directory:

```powershell
cd "C:\Users\djjoh\OneDrive\Desktop\MAGUS PRIME X"
```

3. Create and activate a virtual environment (optional but recommended):

```powershell
# Create virtual environment (if not already created)
python -m venv tensorflow_env

# Activate virtual environment
.\tensorflow_env\Scripts\activate
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Create .env file (if not already created):

```powershell
# Copy the example file
copy .env.example .env

# Edit the .env file with your actual values
notepad .env
```

## Running the Application

Once setup is complete, run the application:

```powershell
python signal_dispatcher.py
```

The server should start and display: "Starting Magus Prime X Signal Dispatcher"

## Troubleshooting

### "No such file or directory" errors

Make sure you're in the correct directory. Always run commands from:

```
C:\Users\djjoh\OneDrive\Desktop\MAGUS PRIME X
```

### Python version issues

If you encounter Python version conflicts, make sure to specify your Python version explicitly:

```powershell
python3 signal_dispatcher.py
```

or

```powershell
py -3 signal_dispatcher.py
```

### Environment activation issues

If you can't activate the environment, you may need to adjust your execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
