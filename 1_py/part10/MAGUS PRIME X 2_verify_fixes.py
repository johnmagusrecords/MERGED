"""
Simple verification script to check if syntax errors were fixed in bot.py
"""
import os
import subprocess
import sys


def check_file_syntax(file_path):
    """Check if a Python file contains syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Attempt to compile the file to check for syntax errors
        compile(content, file_path, 'exec')
        print(f"✅ No syntax errors found in {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path} at line {e.lineno}, column {e.offset}: {e.msg}")
        print(f"   {e.text.strip()}")
        return False
    except Exception as e:
        print(f"❌ Error checking {file_path}: {e}")
        return False


def check_ruff_errors(file_path):
    """Run Ruff to check for linting errors"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ No Ruff errors found in {file_path}")
            return True
        else:
            print(f"⚠️ Ruff found issues in {file_path}:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running Ruff on {file_path}: {e}")
        return False


def main():
    print("=== Verifying Fixes ===")
    
    # Check bot.py for syntax errors
    bot_path = os.path.join(os.getcwd(), "bot.py")
    syntax_ok = check_file_syntax(bot_path)
    
    # If syntax is OK, check for Ruff errors
    if syntax_ok:
        ruff_ok = check_ruff_errors(bot_path)
        
        if ruff_ok:
            print("\n🎉 All fixes have been successfully applied!")
        else:
            print("\n⚠️ Some linting issues remain, but syntax is correct.")
    else:
        print("\n❌ Syntax errors still exist. Please fix them before proceeding.")
    
    print("\nNext steps:")
    print("1. Run black to format your code: python -m black bot.py")
    print("2. Run ruff to fix remaining linting issues: python -m ruff check --fix bot.py")


if __name__ == "__main__":
    main()
