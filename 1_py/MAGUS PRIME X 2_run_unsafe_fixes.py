"""
Apply unsafe fixes to resolve more linting issues automatically
"""
import subprocess
import sys


def main():
    print("Running Ruff with unsafe fixes enabled...")
    
    try:
        # Run Ruff with unsafe fixes on all Python files
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--fix", "--unsafe-fixes", "."],
            capture_output=True,
            text=True
        )
        
        print("\nRuff output:")
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
        print("\nUnsafe fixes applied. Run normal check to see remaining issues:")
        print("    python -m ruff check bot.py")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
