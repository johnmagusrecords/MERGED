import os
import re
import sys


def cleanup_file(filename):
    print(f"Creating backup of {filename}...")
    backup_file = f"{filename}.bak"
    
    # Create backup
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup created: {backup_file}")
    else:
        print(f"Error: File {filename} not found!")
        return
    
    print(f"Fixing common syntax issues in {filename}...")
    
    # Fix common issues
    content = original_content
    
    # Fix duplicate imports
    imports = {}
    import_pattern = re.compile(r'^import\s+([^\s,;]+).*?$|^from\s+([^\s,;]+)\s+import', re.MULTILINE)
    for match in import_pattern.finditer(content):
        imp = match.group(1) or match.group(2)
        if imp:
            imports[imp] = imports.get(imp, 0) + 1
    
    # Report duplicate imports
    for imp, count in imports.items():
        if count > 1:
            print(f"Found {count} imports of '{imp}'")
    
    # Fix indentation issues
    lines = content.split('\n')
    fixed_lines = []
    in_class = False
    in_function = False
    class_indent = 0
    function_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip completely empty lines
        if not stripped:
            fixed_lines.append(line)
            continue
        
        # Fix class definitions
        if stripped.startswith('class ') and stripped.endswith(':'):
            in_class = True
            class_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
        
        # Fix function definitions
        elif stripped.startswith('def ') and stripped.endswith(':'):
            in_function = True
            function_indent = len(line) - len(line.lstrip())
            if in_class:
                # Ensure functions in classes have proper indentation
                if function_indent <= class_indent:
                    line = ' ' * (class_indent + 4) + stripped
            fixed_lines.append(line)
        
        # Fix missing blocks after colons
        elif line.strip().endswith(':') and i + 1 < len(lines) and not lines[i + 1].strip():
            fixed_lines.append(line)
            fixed_lines.append(' ' * (len(line) - len(line.lstrip()) + 4) + 'pass  # Added during cleanup')
        
        # Handle other lines
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix incomplete try blocks
    try_pattern = re.compile(r'try\s*:\s*(?!\s*\S)', re.MULTILINE)
    for match in try_pattern.finditer(content):
        pos = match.end()
        content = content[:pos] + '\n    pass  # Added during cleanup' + content[pos:]
    
    # Write fixed content
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Basic cleanup completed for {filename}")
    print("Now run: flake8 bot.py to see remaining issues")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "bot.py"
    
    cleanup_file(filename)
