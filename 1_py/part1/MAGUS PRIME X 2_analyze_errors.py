"""
Analyze Ruff errors to identify most common issues
"""
import re
import subprocess
import sys
from collections import Counter


def parse_error_codes(output):
    """Extract error codes from Ruff output"""
    # Pattern matches error codes like E501, F841, etc.
    pattern = r'([A-Z]\d{3})'
    return re.findall(pattern, output)

def main():
    print("Analyzing linting errors...")
    
    try:
        # Run Ruff check on all Python files
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            capture_output=True,
            text=True
        )
        
        # Parse error codes
        error_codes = parse_error_codes(result.stdout)
        
        # Count occurrences of each error code
        error_counts = Counter(error_codes)
        
        print("\nTop error categories:")
        print("=====================")
        
        for code, count in error_counts.most_common(10):
            print(f"{code}: {count} occurrences")
            
        print("\nReference for common error codes:")
        print("E501: Line too long")
        print("F401: Imported but unused")
        print("F841: Local variable assigned but never used")
        print("E741: Ambiguous variable name")
        
        # Suggest targeted fixes
        print("\nRecommended actions:")
        if 'E501' in error_counts:
            print("- For E501 (line length): Run Black with a specific line length")
            print("  python -m black --line-length 100 .")
        if 'F401' in error_counts:
            print("- For F401 (unused imports): Use 'python -m ruff check --fix .'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
