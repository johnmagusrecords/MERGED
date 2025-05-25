import os
import ast

project_dir = '.'  # Current folder (you can change it if needed)
report_file = 'import_issues_report.txt'


def scan_python_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    return py_files


def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        code = file.read()
    tree = ast.parse(code)

    imported_names = set()
    used_names = set()

    # Collect imports
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name.split('.')[0])

        elif isinstance(node, ast.Name):
            used_names.add(node.id)

    # Unused imports: present in imported, not used
    unused = imported_names - used_names

    # Missing imports: used but not imported and not built-in
    # (We can filter out known built-ins manually)
    builtins = dir(__builtins__)
    missing = used_names - imported_names - set(builtins)

    return unused, missing


def main():
    results = {}
    files = scan_python_files(project_dir)

    for file_path in files:
        unused, missing = analyze_file(file_path)
        if unused or missing:
            results[file_path] = {
                'unused_imports': sorted(list(unused)),
                'missing_imports': sorted(list(missing))
            }

    # Write report
    with open(report_file, 'w', encoding='utf-8') as report:
        for file_path, issues in results.items():
            report.write(f"\n📄 File: {file_path}\n")
            if issues['unused_imports']:
                report.write("  🚫 Unused Imports:\n")
                for name in issues['unused_imports']:
                    report.write(f"    - {name}\n")
            if issues['missing_imports']:
                report.write("  ❗ Missing Imports (used but not imported):\n")
                for name in issues['missing_imports']:
                    report.write(f"    - {name}\n")
        report.write("\n✅ Scan complete.\n")

    print(f"\n📊 Report saved to: {report_file}")


if __name__ == "__main__":
    main()
