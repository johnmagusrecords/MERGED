import os
import ast
import sys
from collections import defaultdict

project_root = os.path.abspath("MAGUS_PRIME_X_APP")

results = defaultdict(list)


def analyze_python_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        defined_funcs = set()
        called_funcs = set()
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports.append((node.lineno, ast.unparse(node)))
            if isinstance(node, ast.FunctionDef):
                defined_funcs.add(node.name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called_funcs.add(node.func.id)

        unused_funcs = defined_funcs - called_funcs

        for line, imp in imports:
            if imp.split()[1] not in source.split(imp)[-1]:
                results['unused_imports'].append(f"{filepath}:{line} -> {imp}")

        for fn in unused_funcs:
            results['unused_functions'].append(
                f"{filepath} -> {fn}() is defined but never used")

    except SyntaxError as e:
        results['syntax_errors'].append(f"{filepath}:{e.lineno} -> {e.msg}")
    except Exception as e:
        results['other_errors'].append(f"{filepath} -> {str(e)}")


def scan_directory(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                analyze_python_file(os.path.join(root, file))
            elif file.endswith(('.html', '.js', '.css')):
                results['unverified_files'].append(os.path.join(root, file))


def output_results():
    print("\n✅ Analysis Report:")
    for category, items in results.items():
        print(f"\n-- {category.upper()} --")
        for item in items:
            print(f"  {item}")


if __name__ == "__main__":
    print(f"🔍 Scanning project at: {project_root}...")
    scan_directory(project_root)
    output_results()
