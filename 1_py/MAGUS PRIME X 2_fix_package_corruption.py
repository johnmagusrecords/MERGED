"""
Fix corrupted Python packages in the virtual environment by repairing syntax errors
caused by improperly inserted '+' characters in string literals.
"""
import glob
import os
import re
import sys


def find_corrupted_files(site_packages_dir):
    """Find Python files containing corrupted strings with inappropriate '+' characters."""
    corrupted_files = []
    
    # Pattern to match corrupted strings like: "some text" + " more text"
    pattern = r'(["\'].*?)(\s*\+\s*["\'](.*?)["\'])'
    
    for py_file in glob.glob(os.path.join(site_packages_dir, "**/*.py"), recursive=True):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if the file contains the problematic pattern
                if re.search(pattern, content):
                    corrupted_files.append(py_file)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return corrupted_files

def fix_corrupted_file(file_path):
    """Fix a corrupted Python file by removing improper '+' string concatenations."""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix pattern where strings are improperly split with '+'
    # For example: "CurrentVersio" + "n\Explorer"
    pattern = r'(["\'].*?)(\s*\+\s*["\'](.*?)["\'])'
    
    def replace_match(match):
        part1 = match.group(1)  # First string with opening quote
        part3 = match.group(3)  # Content of second string
        
        # Remove the closing quote from part1 to join the strings
        if part1.endswith('"'):
            part1 = part1[:-1] + part3 + '"'
        else:  # Single quote
            part1 = part1[:-1] + part3 + "'"
        
        return part1
    
    # Apply the fix
    fixed_content = re.sub(pattern, replace_match, content)
    
    # Save the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    return True

def main():
    # Get the site-packages directory
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
    else:
        # Standard Python installation
        import site
        site_packages = site.getsitepackages()[0]
    
    print(f"Scanning for corrupted files in: {site_packages}")
    
    # Find corrupted files
    corrupted_files = find_corrupted_files(site_packages)
    
    if not corrupted_files:
        print("No corrupted files found.")
        return
    
    print(f"Found {len(corrupted_files)} corrupted files.")
    
    # Fix each corrupted file
    fixed_count = 0
    for file_path in corrupted_files:
        if fix_corrupted_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} corrupted files.")
    print("\nAfter fixing the corrupted files, you should reinstall the following packages to ensure they're in a stable state:")
    print("    pip install --force-reinstall platformdirs black pre-commit")

if __name__ == "__main__":
    main()
