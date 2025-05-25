"""
Directly repair critical pip files that are preventing reinstallation
"""
import os
import re
import sys


def fix_spinners_py():
    """Fix the unterminated string in spinners.py that's preventing pip from working"""
    spinners_path = os.path.join(
        sys.prefix, 
        "Lib", 
        "site-packages", 
        "pip", 
        "_internal", 
        "cli", 
        "spinners.py"
    )
    
    if not os.path.exists(spinners_path):
        print(f"❌ Could not find pip spinners.py at: {spinners_path}")
        return False
    
    print(f"Fixing: {spinners_path}")
    
    try:
        # Read the corrupted file
        with open(spinners_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix line 40 - unterminated string literal issue
        # Look for patterns like: "something... ')
        corrupted_pattern = r'(["\'](.*?)\.\.\.\s*[\'"])\s*\)'
        
        def fix_match(match):
            # Replace with properly terminated string
            return match.group(1) + ')'
        
        # Apply the fix
        fixed_content = re.sub(corrupted_pattern, fix_match, content)
        
        # If no change was made, try a more specific fix for the known issue
        if fixed_content == content:
            print("Applying targeted fix for spinners.py...")
            line40_fix = r'self._file.write\(" " \* get_indentation\(\) \+ self\._messag \.\.\. \'\)'
            replacement = r'self._file.write(" " * get_indentation() + self._message)'
            fixed_content = re.sub(line40_fix, replacement, content)
        
        # Save the fixed content
        with open(spinners_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed spinners.py")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing spinners.py: {e}")
        return False


def fix_console_py():
    """Fix the pip._vendor.rich.console.py file which also has corruption"""
    console_path = os.path.join(
        sys.prefix, 
        "Lib", 
        "site-packages", 
        "pip", 
        "_vendor", 
        "rich", 
        "console.py"
    )
    
    if not os.path.exists(console_path):
        print(f"❌ Could not find rich console.py at: {console_path}")
        return False
    
    print(f"Fixing: {console_path}")
    
    try:
        # Read the corrupted file
        with open(console_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the known issue in line ~2202
        corrupted_pattern = (
            r'\{error\.reason\}\\n\*\*\* You may need to add\s+\+\s+"PYTHONIOENCODING=utf-8 '
            r'to your environme\s+\+\s+"nt \*\*\*"'
        )
        replacement = r'{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 to your environment ***"'
        
        # Apply the fix
        fixed_content = re.sub(corrupted_pattern, replacement, content)
        
        # Save the fixed content
        with open(console_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed console.py")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing console.py: {e}")
        return False


def main():
    print("=== PIP Repair Tool ===")
    print("Fixing critical pip files to allow package reinstallation...")
    
    spinners_fixed = fix_spinners_py()
    console_fixed = fix_console_py()
    
    if spinners_fixed and console_fixed:
        print("\n✅ Critical pip files repaired successfully!")
        print("\nNow run the following command to reinstall pip in your environment:")
        print(f"    {sys.executable} -m ensurepip --upgrade")
        print("\nAfter that succeeds, reinstall the other packages:")
        print(f"    {sys.executable} -m pip install --upgrade pip")
        print(
            f"    {sys.executable} -m pip install --force-reinstall "
            f"black ruff pre-commit platformdirs"
        )
    else:
        print("\n⚠️ Some repairs failed. You might need to recreate your virtual environment.")
        print("\nTo create a new environment:")
        print("    python -m venv new_env")
        print("    new_env\\Scripts\\activate")
        print("    python -m pip install --upgrade pip")
        print("    python -m pip install black ruff pre-commit platformdirs")
    
    return 0 if spinners_fixed and console_fixed else 1


if __name__ == "__main__":
    sys.exit(main())
