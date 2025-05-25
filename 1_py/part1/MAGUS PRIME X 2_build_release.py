import os
import shutil
import time
import argparse
import datetime
from pathlib import Path

# Use Path for directory handling
SOURCE_DIR = Path.cwd()
RELEASE_DIR = SOURCE_DIR / "MAGUS_PRIME_X_APP"

# Default files and folders to include
INCLUDE_FILES = [
    "bot.py",
    "fix-all-buttons.js",
    ".env",  # Added to include environment variables
    "requirements.txt",
    "README.md",
    "setup_env.bat",
    "telegram_helper.py",
    "api_helper.py",
    "config.py",
    "commentary_generator.py",
    "market_status_checker.py",
    "gpt_commentary.py",
    "enhanced_signal_sender.py",
    "assets_config.json"
]

INCLUDE_FOLDERS = {
    "templates": "templates",
    "static": "static",
    "tools": "tools",
    "tests": "tests",
}


def clean_and_create_release_folder():
    """Remove old build and create a fresh directory"""
    if RELEASE_DIR.exists():
        print(f"Removing old build at {RELEASE_DIR}...")
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(exist_ok=True)
    print("✅ Created new clean build folder: MAGUS_PRIME_X_APP")


def copy_files():
    """Copy individual files to the release folder"""
    copied = []
    missing = []

    for file in INCLUDE_FILES:
        src = SOURCE_DIR / file
        dst = RELEASE_DIR / file
        if src.exists():
            shutil.copy2(src, dst)
            copied.append(file)
            print(f"✓ Copied {file}")
        else:
            missing.append(file)
            print(f"⚠️ File not found: {file}")

    return copied, missing


def copy_folders():
    """Copy entire folders to the release folder"""
    copied = []
    missing = []

    for folder, target in INCLUDE_FOLDERS.items():
        src = SOURCE_DIR / folder
        dst = RELEASE_DIR / target
        if src.exists():
            shutil.copytree(src, dst)
            copied.append(folder)
            print(f"✓ Copied folder: {folder}")
        else:
            missing.append(folder)
            print(f"⚠️ Folder not found: {folder}")

    return copied, missing


def create_build_info(copied_files, missing_files, copied_folders, missing_folders):
    """Create a build info file with details about the build"""
    build_info = RELEASE_DIR / "build_info.txt"
    with open(build_info, "w") as f:
        f.write("MAGUS PRIME X BUILD INFORMATION\n")
        f.write("==============================\n\n")
        f.write(
            f"Build Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Copied Files:\n")
        for file in copied_files:
            f.write(f" - {file}\n")

        f.write("\nCopied Folders:\n")
        for folder in copied_folders:
            f.write(f" - {folder}\n")

        if missing_files or missing_folders:
            f.write("\nWARNING: The following items were not found:\n")

            if missing_files:
                f.write("\nMissing Files:\n")
                for file in missing_files:
                    f.write(f" - {file}\n")

            if missing_folders:
                f.write("\nMissing Folders:\n")
                for folder in missing_folders:
                    f.write(f" - {folder}\n")

    print(f"✓ Created build info file")


def create_zip_archive(zip_name=None):
    """Create a zip archive of the build folder"""
    if zip_name is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        zip_name = f"MAGUS_PRIME_X_APP-{timestamp}.zip"

    archive_path = SOURCE_DIR / zip_name.replace(".zip", "")
    shutil.make_archive(
        str(archive_path),
        'zip',
        str(SOURCE_DIR),
        "MAGUS_PRIME_X_APP"
    )
    print(f"✓ Created zip archive: {zip_name}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Build release package for MAGUS PRIME X")
    parser.add_argument("--zip", action="store_true",
                        help="Create a zip archive of the build")
    parser.add_argument(
        "--zip-name", help="Name for the zip file (default: MAGUS_PRIME_X_APP-{timestamp}.zip)")
    args = parser.parse_args()

    start_time = time.time()
    print("🚀 Starting MAGUS PRIME X build...")

    # Build process
    clean_and_create_release_folder()
    copied_files, missing_files = copy_files()
    copied_folders, missing_folders = copy_folders()
    create_build_info(copied_files, missing_files,
                      copied_folders, missing_folders)

    # Create zip if requested
    if args.zip:
        create_zip_archive(args.zip_name)

    # Print summary
    end_time = time.time()
    duration = end_time - start_time

    print("\n📋 Build Summary:")
    print(f"- Copied {len(copied_files)} files")
    print(f"- Copied {len(copied_folders)} folders")
    if missing_files:
        print(f"- {len(missing_files)} files not found")
    if missing_folders:
        print(f"- {len(missing_folders)} folders not found")
    print(f"- Build completed in {duration:.2f} seconds")
    print("\n🎉 Build complete! Your new app is in MAGUS_PRIME_X_APP")


if __name__ == "__main__":
    main()
