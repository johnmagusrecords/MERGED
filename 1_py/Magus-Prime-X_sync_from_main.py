import shutil
from pathlib import Path

SOURCE = Path("C:/Users/djjoh/OneDrive/Desktop/MAGUS PRIME X")
TARGET = Path("C:/Users/djjoh/OneDrive/Desktop/MAGUS_PRIME_X_APP")

# Add file names you want to sync
FILES_TO_COPY = [
    "telegram_helper.py",
    "capital_com_trader.py",
    "data/assets_config.json"
]

for file in FILES_TO_COPY:
    src = SOURCE / file
    dst = TARGET / Path(file).name
    if src.exists():
        shutil.copy(src, dst)
        print(f"✅ Synced: {file}")
    else:
        print(f"❌ Missing: {file}")

print("✅ Sync complete!")
