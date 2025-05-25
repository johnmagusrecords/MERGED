"""
Find additional corrupted files in your Python environment
This tool scans for the '+' string concatenation corruption pattern
"""
import glob
import os
import re
import sys
from collections import defaultdict


def find_corrupted_files(site_packages_dir):
    """Find Python files containing corrupted strings with inappropriate '+' characters."""
    corrupted_files = []
    corruption_patterns = defaultdict(int)
    
    # Multiple patterns to detect different types of corruption
    patterns = [
        # Basic pattern: "string" + "more string"
        r'(["\'].*?)(\s*\+\s*["\'](.*?)["\'])',
        
        # Unterminated string literal
        r'(["\'].*?)(\.\.\..*?["\'])',
        
        # Missing closing quote with +
        r'(["\'].*?)(\s*\+\s*[^"\'\n]*?$)',
        
        # String concat inside f-string
        r'f(["\'].*?\{.*?\s*\+\s*.*?\}.*?["\'])'
    ]
    
    # Count total files and progress
    all_files = list(glob.glob(os.path.join(site_packages_dir, "**/*.py"), recursive=True))
    total_files = len(all_files)
    checked_files = 0
    
    print(f"Scanning {total_files} Python files in {site_packages_dir}...")
    
    for py_file in all_files:
        checked_files += 1
        if checked_files % 100 == 0:
            print(f"Checked {checked_files}/{total_files} files...")
        
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for all corruption patterns
                found_corruption = False
                for i, pattern in enumerate(patterns):
                    matches = re.findall(pattern, content)
                    if matches:
                        corrupted_files.append((py_file, i))
                        corruption_patterns[i] += len(matches)
                        found_corruption = True
                        
                # Also check for SyntaxError-causing lines
                if not found_corruption:
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if '+' in line and ('"' in line or "'" in line):
                            # Additional manual check for suspicious concatenations
                            if re.search(r'["\']\s*\+\s*["\']', line):
                                corrupted_files.append((py_file, 4))
                                corruption_patterns[4] += 1
                                break
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return corrupted_files, corruption_patterns

def analyze_file(file_path):
    """Analyze a single file to show its corruption patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Show the most suspicious lines
        print(f"\nAnalyzing {file_path}...\n")
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '+' in line and ('"' in line or "'" in line):
                print(f"Line {i}: {line[:80]}" + ("..." if len(line) > 80 else ""))
        
        print("\nSuggested manual fix approach:")
        print("1. Open the file in a text editor")
        print("2. Look for strings improperly concatenated with '+' operator")
        print("3. Join the strings by removing the '+' and the quotes between segments")
        print("   Example: Change \"hello\" + \"world\" to \"helloworld\"")
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

def main():
    # Get the site-packages directory
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
    else:
        # Standard Python installation
        import site
        site_packages = site.getsitepackages()[0]
    
    print("=== Python Corruption Scanner ===")
    print(f"Scanning environment: {sys.prefix}")
    
    # Find corrupted files
    corrupted_files, pattern_counts = find_corrupted_files(site_packages)
    
    if not corrupted_files:
        print("\n✓ No corrupted files found!")
        return
    
    # Group files by package
    packages = defaultdict(list)
    for file_path, pattern_type in corrupted_files:
        # Extract package name from path
        rel_path = os.path.relpath(file_path, site_packages)
        package = rel_path.split(os.sep)[0]
        packages[package].append((file_path, pattern_type))
    
    # Report findings
    print(f"\n! Found {len(corrupted_files)} potentially corrupted files in {len(packages)} packages.")
    
    print("\nCorruption patterns detected:")
    pattern_names = [
        "String concatenation with '+'", 
        "Unterminated string literal",
        "Missing closing quote with '+'",
        "String concat inside f-string",
        "Suspicious concatenation"
    ]
    for pattern_id, count in pattern_counts.items():
        print(f"- {pattern_names[pattern_id if pattern_id < len(pattern_names) else -1]}: {count} occurrences")
    
    print("\nMost affected packages:")
    for package, files in sorted(packages.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"- {package}: {len(files)} files")
    
    # If there's a specific package the user wants to fix
    while True:
        print("\nOptions:")
        print("1. List all affected packages")
        print("2. Examine a specific package")
        print("3. Analyze a specific file")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            print("\nAll affected packages:")
            for i, (package, files) in enumerate(sorted(packages.items()), 1):
                print(f"{i}. {package}: {len(files)} files")
        
        elif choice == '2':
            package_name = input("Enter package name to examine: ")
            if package_name in packages:
                print(f"\nFiles in {package_name}:")
                for i, (file_path, pattern_type) in enumerate(packages[package_name], 1):
                    rel_path = os.path.relpath(file_path, site_packages)
                    print(f"{i}. {rel_path} (Pattern type: {pattern_names[pattern_type if pattern_type < len(pattern_names) else -1]})")
            else:
                print(f"Package {package_name} not found in the list of corrupted packages.")
        
        elif choice == '3':
            file_index = input("Enter file path or number from a previous listing: ")
            if file_index.isdigit():
                # User entered a number, assume it's from the last listing
                try:
                    file_index = int(file_index) - 1
                    if 'last_files' in locals() and 0 <= file_index < len(last_files):
                        file_path = last_files[file_index][0]
                        analyze_file(file_path)
                    else:
                        print("Invalid file number.")
                except ValueError:
                    print("Invalid number format.")
            else:
                # User entered a file path
                analyze_file(file_index)
        
        elif choice == '4':
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
    
    print("\nRecommendations:")
    print("1. Run fix_package_corruption.py to automatically fix most issues")
    print("2. For remaining problems, reinstall affected packages:")
    for package in list(packages.keys())[:5]:
        print(f"   pip install --force-reinstall {package}")
    print("3. If problems persist, consider creating a new virtual environment")

if __name__ == "__main__":
    main()
