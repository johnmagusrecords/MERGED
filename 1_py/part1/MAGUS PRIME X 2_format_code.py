"""
Format code directly using Black without relying on batch files
"""
import argparse
import subprocess
import sys


def run_black(files=None, line_length=100):
    """Run Black formatter directly without batch files"""
    cmd = [sys.executable, "-m", "black", f"--line-length={line_length}"]
    
    if files:
        # Add specific files to the command
        cmd.extend(files)
    else:
        # Default to current directory
        cmd.append(".")
    
    print(f"Running Black with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\n✅ Black formatting completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Black formatting failed: {e}")
        return False
    
def run_ruff(files=None, fix=True, unsafe=False):
    """Run Ruff linter directly without batch files"""
    cmd = [sys.executable, "-m", "ruff", "check"]
    
    if fix:
        cmd.append("--fix")
    
    if unsafe:
        cmd.append("--unsafe-fixes")
    
    if files:
        # Add specific files to the command
        cmd.extend(files)
    else:
        # Default to current directory
        cmd.append(".")
    
    print(f"Running Ruff with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\n✅ Ruff linting completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ruff linting failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Format code with Black and Ruff")
    parser.add_argument("--black-only", action="store_true", help="Only run Black formatter")
    parser.add_argument("--ruff-only", action="store_true", help="Only run Ruff linter")
    parser.add_argument("--unsafe", action="store_true", help="Use unsafe fixes with Ruff")
    parser.add_argument("--check", action="store_true", help="Check only, don't make changes")
    parser.add_argument("--line-length", type=int, default=100, help="Line length for Black")
    parser.add_argument("files", nargs="*", help="Files to format (default: all Python files)")
    
    args = parser.parse_args()
    
    # Run the tools based on arguments
    success = True
    
    if not args.ruff_only:
        success = run_black(args.files, args.line_length) and success
    
    if not args.black_only:
        success = run_ruff(args.files, not args.check, args.unsafe) and success
    
    if success:
        print("\n✅ All formatting tasks completed successfully!")
    else:
        print("\n⚠️ Some formatting tasks failed. Check the output above for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
