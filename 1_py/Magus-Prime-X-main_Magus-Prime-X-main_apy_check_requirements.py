import importlib

# List of required packages (standard and third-party)
required_packages = [
    "os", "time", "threading", "logging", "json", "re", "datetime", "shutil", "pathlib", "sys", "argparse", "collections", "queue",  # Standard libraries
    # Third-party libraries
    "requests", "feedparser", "dotenv", "newsapi", "bs4", "flask", "telegram", "pandas", "numpy", "talib"
]

# Check each package
missing_packages = []
for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package} is installed.")
    except ImportError:
        print(f"❌ {package} is NOT installed.")
        missing_packages.append(package)

# Summary
if missing_packages:
    print("\nThe following packages are missing:")
    print("\n".join(missing_packages))
    print("\nYou can install them using:")
    print(f"pip install {' '.join(missing_packages)}")
else:
    print("\nAll required packages are installed.")
