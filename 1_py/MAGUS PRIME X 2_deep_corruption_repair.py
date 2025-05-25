"""
Enhanced Python package corruption repair tool

This tool fixes multiple types of corruption patterns found in your environment:
- String concatenation with '+'
- Unterminated string literals
- String concat inside f-strings 
- Missing closing quotes
- Other syntax issues

For severe cases, it recommends package reinstallation.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict

# Define corruption patterns to detect and fix
CORRUPTION_PATTERNS = [
    # Pattern 0: Basic string concatenation: "string" + "more string"
    (r'(["\'].*?)(\s*\+\s*["\'](.*?)["\'])', 
     lambda m: m.group(1)[:-1] + m.group(3) + m.group(1)[-1]),
    
    # Pattern 1: Unterminated string literals: "string... "
    (r'(["\'].*?)(\.\.\.\s*["\'])', 
     lambda m: m.group(1)),
    
    # Pattern 2: Missing closing quote with '+': "string + other
    (r'(["\'].*?)(\s*\+\s*[^"\'\n]*?)$', 
     lambda m: m.group(1)),
    
    # Pattern 3: String concatenation inside f-strings: f"...{var + "text"}..."
    (r'(f["\'].*?\{)(.*?\s*\+\s*.*?)(\}.*?["\'])', 
     lambda m: m.group(1) + m.group(2).replace('"', '\\"').replace("'", "\\'") + m.group(3)),
]

# High-priority packages that are critical for functionality
CRITICAL_PACKAGES = ["pip", "black", "ruff", "platformdirs", "setuptools"]

def backup_file(file_path):
    """Create a backup of the file before modifying it"""
    backup_path = file_path + ".bak"
    try:
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        print(f"Warning: Couldn't create backup of {file_path}: {e}")
        return False

def find_corrupted_files(site_packages_dir, pattern_ids=None, packages=None):
    """
    Find Python files containing corrupted strings based on specified patterns
    
    Args:
        site_packages_dir: Path to the site-packages directory
        pattern_ids: List of pattern IDs to check (None = all patterns)
        packages: List of package names to check (None = all packages)
    
    Returns:
        Dictionary mapping file paths to lists of detected pattern IDs
    """
    corrupted_files = defaultdict(list)
    corruption_stats = defaultdict(int)
    package_stats = defaultdict(int)
    
    # Determine which patterns to use
    patterns_to_check = range(len(CORRUPTION_PATTERNS))
    if pattern_ids is not None:
        patterns_to_check = [i for i in pattern_ids if 0 <= i < len(CORRUPTION_PATTERNS)]
    
    # Get all Python files in site-packages
    all_files = list(glob.glob(os.path.join(site_packages_dir, "**/*.py"), recursive=True))
    total_files = len(all_files)
    print(f"Scanning {total_files} Python files in {site_packages_dir}...")
    
    # Filter files by package if specified
    if packages:
        filtered_files = []
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, site_packages_dir)
            package_name = rel_path.split(os.sep)[0]
            if package_name in packages:
                filtered_files.append(file_path)
        all_files = filtered_files
        print(f"Filtered to {len(all_files)} files in specified packages")
    
    # Process files
    for i, py_file in enumerate(all_files):
        if i % 100 == 0:
            print(f"Checked {i}/{len(all_files)} files...")
        
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract package name
            rel_path = os.path.relpath(py_file, site_packages_dir)
            package_name = rel_path.split(os.sep)[0]
            
            # Check each corruption pattern
            file_corrupted = False
            for pattern_id in patterns_to_check:
                pattern, _ = CORRUPTION_PATTERNS[pattern_id]
                matches = re.findall(pattern, content)
                if matches:
                    corrupted_files[py_file].append(pattern_id)
                    corruption_stats[pattern_id] += len(matches)
                    file_corrupted = True
            
            # Update package statistics if file was corrupted
            if file_corrupted:
                package_stats[package_name] += 1
            
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return corrupted_files, corruption_stats, package_stats

def fix_file(file_path, pattern_ids=None):
    """
    Fix corruption in a single file
    
    Args:
        file_path: Path to the file to fix
        pattern_ids: List of pattern IDs to fix (None = all patterns)
    
    Returns:
        Dictionary with statistics about fixes
    """
    stats = {
        'fixes': 0,
        'errors': 0,
        'patterns': defaultdict(int)
    }
    
    # Backup file before fixing
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Determine which patterns to use
        patterns_to_fix = range(len(CORRUPTION_PATTERNS))
        if pattern_ids is not None:
            patterns_to_fix = [i for i in pattern_ids if 0 <= i < len(CORRUPTION_PATTERNS)]
        
        # Apply each fix pattern
        modified = False
        for pattern_id in patterns_to_fix:
            pattern, replacement_func = CORRUPTION_PATTERNS[pattern_id]
            
            # Count matches before fixing
            matches = re.findall(pattern, content)
            match_count = len(matches)
            
            if match_count > 0:
                # Apply the fix using the replacement function
                def replace(match):
                    stats['fixes'] += 1
                    stats['patterns'][pattern_id] += 1
                    return replacement_func(match)
                
                try:
                    new_content = re.sub(pattern, replace, content)
                    if new_content != content:
                        content = new_content
                        modified = True
                except Exception as e:
                    print(f"Error applying pattern {pattern_id} to {file_path}: {e}")
                    stats['errors'] += 1
        
        # Save the fixed content if changes were made
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return stats
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        stats['errors'] += 1
        return stats

def reinstall_package(package_name):
    """Reinstall a package using pip"""
    print(f"Reinstalling package: {package_name}")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--force-reinstall", package_name
        ])
        print(f"✅ Successfully reinstalled {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to reinstall {package_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Enhanced Python package corruption repair tool")
    parser.add_argument("--scan-only", action="store_true", help="Only scan for corruption, don't fix")
    parser.add_argument("--pattern", type=int, action="append", help="Fix specific pattern(s) (can be used multiple times)")
    parser.add_argument("--package", type=str, action="append", help="Fix specific package(s) (can be used multiple times)")
    parser.add_argument("--reinstall", action="store_true", help="Reinstall packages after fixing")
    parser.add_argument("--critical-only", action="store_true", help="Only fix critical packages")
    args = parser.parse_args()
    
    print("=== Enhanced Python Package Corruption Repair Tool ===")
    
    # Determine site-packages directory
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
    else:
        # Standard Python installation
        import site
        site_packages = site.getsitepackages()[0]
    
    # Determine which packages to check/fix
    target_packages = args.package
    if args.critical_only:
        target_packages = CRITICAL_PACKAGES
    
    # Scan for corrupted files
    print(f"\nScanning for corruption in {site_packages}...")
    corrupted_files, corruption_stats, package_stats = find_corrupted_files(
        site_packages, 
        pattern_ids=args.pattern,
        packages=target_packages
    )
    
    # Report scan results
    total_corrupted = len(corrupted_files)
    print(f"\nFound {total_corrupted} corrupted files across {len(package_stats)} packages.")
    
    if total_corrupted == 0:
        print("No corruption found! Your environment appears to be clean.")
        return
    
    print("\nCorruption patterns detected:")
    pattern_names = [
        "String concatenation with '+'",
        "Unterminated string literal",
        "Missing closing quote with '+'",
        "String concat inside f-string"
    ]
    
    for pattern_id, count in sorted(corruption_stats.items(), key=lambda x: x[1], reverse=True):
        pattern_name = pattern_names[pattern_id] if pattern_id < len(pattern_names) else f"Pattern {pattern_id}"
        print(f"- {pattern_name}: {count} occurrences")
    
    print("\nMost affected packages:")
    for package, count in sorted(package_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {package}: {count} files")
    
    # Exit if scan-only mode
    if args.scan_only:
        print("\nScan complete. Use --scan-only flag to fix the issues.")
        return
    
    # Fix corrupted files
    print("\nFixing corrupted files...")
    fix_stats = {
        'total_files': total_corrupted,
        'fixed_files': 0,
        'error_files': 0,
        'fixes': 0,
        'patterns': defaultdict(int)
    }
    
    for i, (file_path, patterns) in enumerate(corrupted_files.items()):
        if i % 20 == 0:
            print(f"Fixing file {i+1}/{total_corrupted}...")
        
        file_stats = fix_file(file_path, pattern_ids=args.pattern)
        
        if file_stats['fixes'] > 0:
            fix_stats['fixed_files'] += 1
            fix_stats['fixes'] += file_stats['fixes']
            
            for pattern_id, count in file_stats['patterns'].items():
                fix_stats['patterns'][pattern_id] += count
        
        if file_stats['errors'] > 0:
            fix_stats['error_files'] += 1
    
    # Print fix results
    print("\n=== Fix Results ===")
    print(f"Total corrupted files: {fix_stats['total_files']}")
    print(f"Files fixed: {fix_stats['fixed_files']}")
    print(f"Files with errors: {fix_stats['error_files']}")
    print(f"Total fixes applied: {fix_stats['fixes']}")
    
    print("\nFixes by pattern:")
    for pattern_id, count in sorted(fix_stats['patterns'].items(), key=lambda x: x[1], reverse=True):
        pattern_name = pattern_names[pattern_id] if pattern_id < len(pattern_names) else f"Pattern {pattern_id}"
        print(f"- {pattern_name}: {count} fixes")
    
    # Reinstall packages if requested
    if args.reinstall:
        print("\nReinstalling affected packages...")
        
        # Sort packages by corruption count (highest first)
        packages_to_reinstall = sorted(
            package_stats.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Add critical packages to the beginning
        for critical in CRITICAL_PACKAGES:
            if critical not in [p[0] for p in packages_to_reinstall]:
                packages_to_reinstall.insert(0, (critical, 0))
        
        # Reinstall packages
        for package, _ in packages_to_reinstall:
            reinstall_package(package)
    
    # Final recommendations
    print("\n=== Recommendations ===")
    print("1. Run the following command to verify if corruption has been fixed:")
    print(f"   {sys.executable} find_more_corruption.py")
    
    if not args.reinstall:
        print("\n2. Consider reinstalling critical packages:")
        for package in CRITICAL_PACKAGES:
            print(f"   {sys.executable} -m pip install --force-reinstall {package}")
    
    if fix_stats['error_files'] > 0:
        print("\n3. Some files could not be fixed automatically. You might need to:")
        print("   - Reinstall specific packages with corrupted files")
        print("   - Or create a new virtual environment as a last resort")
        print(f"   {sys.executable} recreate_env.py")

if __name__ == "__main__":
    main()
