"""
Reinstall packages that are commonly affected by syntax corruption
"""
import subprocess
import sys


def main():
    packages_to_reinstall = [
        "platformdirs",
        "black",
        "pre-commit",
        "pip",
    ]
    
    print("Reinstalling potentially corrupted packages...")
    
    for package in packages_to_reinstall:
        print(f"\nReinstalling {package}...")
        try:
            # Force reinstall the package
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--force-reinstall", package]
            )
            print(f"✅ Successfully reinstalled {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to reinstall {package}: {e}")
    
    print("\nPackage reinstallation complete.")
    print("\nTo format your code with Black, run:")
    print("    python -m black .")
    
    print("\nTo install pre-commit, run:")
    print("    python -m pip install pre-commit")
    print("    python -m pre_commit install")

if __name__ == "__main__":
    main()
