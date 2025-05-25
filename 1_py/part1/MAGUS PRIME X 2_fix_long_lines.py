"""
Fix long lines in Python files
"""
import argparse
import glob
import os
import re


def fix_long_lines_in_file(file_path, max_line_length=100):
    """Fix long lines in a file using line continuation and string splitting"""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            lines = file.readlines()
        except UnicodeDecodeError:
            print(f"Skipping {file_path} due to encoding issues")
            return 0
    
    fixed_count = 0
    new_lines = []
    
    for line in lines:
        if len(line.rstrip()) <= max_line_length:
            new_lines.append(line)
            continue
        
        # Skip comments as they're handled by Black
        if line.strip().startswith('#'):
            new_lines.append(line)
            continue
        
        # Handle string literals with + operator
        if '"' in line or "'" in line:
            # Find string literals
            matches = re.findall(r'(["\'])(.*?)\1', line)
            if matches:
                for quote, string in matches:
                    if len(string) > 40:  # Only split long strings
                        parts = []
                        for i in range(0, len(string), 40):
                            parts.append(string[i:i+40])
                        replacement = f"{quote} {quote}\n" + f" + {quote}".join(parts) + f"{quote}"
                        line = line.replace(f"{quote}{string}{quote}", replacement)
                        fixed_count += 1
        
        # Add line continuation for long lines
        if len(line.rstrip()) > max_line_length:
            # Check if it's a function call or list/dict with multiple items
            if ('(' in line and ')' in line) or ('[' in line and ']' in line) or ('{' in line and '}' in line):
                for char, pair in [('(', ')'), ('[', ']'), ('{', '}')]:
                    if char in line and pair in line:
                        open_pos = line.find(char)
                        # Split after the opening bracket and indent the content
                        if open_pos > 0 and open_pos < max_line_length:
                            indent = ' ' * (open_pos + 4)
                            content = line[open_pos+1:].strip()
                            # Split by commas
                            if ',' in content:
                                items = content.split(',')
                                new_content = f"{line[:open_pos+1]}\n"
                                for item in items[:-1]:
                                    new_content += f"{indent}{item.strip()},\n"
                                new_content += f"{indent}{items[-1].strip()}"
                                line = new_content
                                fixed_count += 1
        
        new_lines.append(line)
    
    if fixed_count > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
    
    return fixed_count

def main():
    parser = argparse.ArgumentParser(description="Fix long lines in Python files")
    parser.add_argument("--dir", default=".", help="Directory to search for Python files")
    parser.add_argument("--max-length", type=int, default=100, help="Maximum line length")
    args = parser.parse_args()
    
    py_files = glob.glob(os.path.join(args.dir, "**/*.py"), recursive=True)
    total_fixed = 0
    
    for file_path in py_files:
        fixed = fix_long_lines_in_file(file_path, args.max_length)
        if fixed > 0:
            print(f"Fixed {fixed} long lines in {file_path}")
            total_fixed += fixed
    
    print(f"\nTotal fixed lines: {total_fixed}")
    print("Now run Black to properly format the files:")
    print("    .\\black .")

if __name__ == "__main__":
    main()
