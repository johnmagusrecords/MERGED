"""
Error fixing utility for MAGUS PRIME X
Automatically fixes Ruff errors and provides guidance on manual fixes
"""

import argparse
import os
import platform
import subprocess
import sys


def print_colored(text, color="white", bold=False):
    """Print text with ANSI color codes on compatible terminals"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }

    bold_code = "\033[1m" if bold else ""
    color_code = colors.get(color.lower(), "\033[97m")
    reset_code = "\033[0m"

    # Windows CMD doesn't support ANSI by default
    if (
        platform.system() == "Windows"
        and "ANSICON" not in os.environ
        and "WT_SESSION" not in os.environ
    ):
        print(text)
    else:
        print(f"{bold_code}{color_code}{text}{reset_code}")


def run_command(cmd, silent=False):
    """Run a shell command and return the output"""
    try:
        if silent:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        else:
            result = subprocess.run(cmd, text=True, check=False)
        return result
    except Exception as e:
        print_colored(f"Error running command: {e}", "red", True)
        return None


def get_file_list():
    """Get a list of Python files in the project"""
    python_files = []
    for root, _, files in os.walk("."):
        if any(excluded in root for excluded in [".git", "__pycache__", "venv", "env"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def run_ruff_check(files, fix=False, unsafe=False):
    """Run Ruff check on the specified files"""
    cmd = [sys.executable, "-m", "ruff", "check"]

    if fix:
        cmd.append("--fix")

    if unsafe:
        cmd.append("--unsafe-fixes")

    cmd.extend(files)

    return run_command(cmd)


def check_file_has_errors(file):
    """Check if a specific file has Ruff errors"""
    result = run_command([sys.executable, "-m", "ruff", "check", file], silent=True)
    return result.returncode != 0


def main():
    parser = argparse.ArgumentParser(description="Fix Ruff errors in MAGUS PRIME X")
    parser.add_argument(
        "--unsafe", action="store_true", help="Apply unsafe fixes (use with caution)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Check all Python files in the project"
    )
    parser.add_argument("files", nargs="*", help="Specific files to check and fix")
    args = parser.parse_args()

    print_colored("\n=== MAGUS PRIME X Error Fixer ===", "cyan", True)
    print_colored("This utility will help you fix Ruff errors in your code.\n", "cyan")

    # Determine which files to check
    if args.all:
        files_to_check = get_file_list()
        print_colored(
            f"Checking all {len(files_to_check)} Python files in the project...", "blue"
        )
    elif args.files:
        files_to_check = args.files
        print_colored(f"Checking specified files: {', '.join(files_to_check)}", "blue")
    else:
        files_to_check = ["bot.py"]  # Default to bot.py
        print_colored("Checking bot.py (default)...", "blue")

    # Check initial error count
    print_colored("\nChecking initial errors...", "yellow")
    run_ruff_check(files_to_check)

    # Apply fixes
    print_colored("\nApplying automatic fixes...", "yellow")
    run_ruff_check(files_to_check, fix=True, unsafe=args.unsafe)

    # Check remaining errors
    print_colored("\nChecking remaining errors...", "yellow")
    remaining_check = run_ruff_check(files_to_check)

    # Show summary
    print_colored("\n=== Summary ===", "magenta", True)

    if remaining_check.returncode == 0:
        print_colored("✅ All issues have been fixed successfully!", "green", True)
    else:
        print_colored("⚠️ Some issues remain that require manual fixes.", "yellow", True)
        print_colored("\nTo see the remaining issues in a specific file:", "white")
        print_colored(f"    {sys.executable} -m ruff check <filename>", "white")

        # Check which files still have errors
        print_colored("\nFiles with remaining errors:", "red")
        for file in files_to_check:
            if check_file_has_errors(file):
                print_colored(f"  - {file}", "red")

    print_colored("\nNext steps:", "blue", True)
    if not args.unsafe:
        print_colored(
            "  - Re-run with --unsafe to attempt fixing additional issues:", "white"
        )
        print_colored(f"    {sys.executable} fix_errors.py --unsafe", "white")

    print_colored(
        "  - For format-only issues, you can use Black to format your code:", "white"
    )
    print_colored(f"    {sys.executable} -m pip install black", "white")
    print_colored(f"    {sys.executable} -m black bot.py", "white")

    print_colored("\nHappy coding! 😊\n", "green")


if __name__ == "__main__":
    main()
