import os
import shutil
import fnmatch
import logging

# --- Configuration ---

# Top-level folders to create
FOLDER_MAP = {
    '1_py': ['*.py', '*.ipynb'],
    '2_configs': [
        '.env', 'requirements.txt', 'Pipfile', 'poetry.lock', 'Dockerfile', 'docker-compose.yml',
        '*.json', '*.yml'
    ],
    '3_frontend': ['*.html', '*.css', '*.js', '*.jsx', '*.tsx'],
    '4_docs': [
        '*.md', '*.rst', 'README*', 'CHANGELOG*', 'LICENSE'
    ]
}

# Patterns to skip/delete
SKIP_PATTERNS = [
    'venv', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', 'build', 'dist',
    '*.egg-info', '.vscode', '.idea', '.DS_Store', 'Thumbs.db', 'desktop.ini', '.ipynb_checkpoints'
]
SKIP_FILE_PATTERNS = ['*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db', 'desktop.ini']

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def should_skip_dir(dirname):
    for pattern in SKIP_PATTERNS:
        if fnmatch.fnmatch(dirname, pattern):
            return True
    return False

def should_skip_file(filename):
    for pattern in SKIP_FILE_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False

def get_target_folder(filename):
    for folder, patterns in FOLDER_MAP.items():
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return folder
    return None

def flatten_path(root, file_path):
    # Remove root prefix and flatten path to avoid subfolders
    rel_path = os.path.relpath(file_path, root)
    return rel_path.replace(os.sep, '_')

def update_gitignore(root):
    gitignore_path = os.path.join(root, '.gitignore')
    patterns = [
        'venv/', '.venv/', '__pycache__/', '*.pyc', '*.pyo', '.pytest_cache/', '.mypy_cache/',
        '.ipynb_checkpoints/', 'build/', 'dist/', '*.egg-info/', '.vscode/', '.idea/',
        '.DS_Store', 'Thumbs.db', 'desktop.ini'
    ]
    with open(gitignore_path, 'w') as f:
        for pat in patterns:
            f.write(pat + '\n')
    logging.info(f"Updated .gitignore at {gitignore_path}")

def main():
    root = os.path.dirname(os.path.abspath(__file__))

    # Step 1: Create top-level folders if missing
    for folder in FOLDER_MAP.keys():
        folder_path = os.path.join(root, folder)
        os.makedirs(folder_path, exist_ok=True)
        logging.info(f"Ensured folder: {folder_path}")

    # Step 2: Walk the directory tree
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Skip our own top-level folders
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir in FOLDER_MAP.keys():
            dirnames[:] = []
            continue

        # Remove unwanted dirs from traversal
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        # Step 3: Process files
        for fname in filenames:
            if should_skip_file(fname):
                # Delete unwanted files
                try:
                    os.remove(os.path.join(dirpath, fname))
                    logging.info(f"Deleted unwanted file: {os.path.join(dirpath, fname)}")
                except Exception as e:
                    logging.warning(f"Could not delete {fname}: {e}")
                continue

            src_path = os.path.join(dirpath, fname)
            tgt_folder = get_target_folder(fname)
            if tgt_folder:
                # Flatten path and move file
                flat_name = flatten_path(root, src_path)
                tgt_path = os.path.join(root, tgt_folder, flat_name)
                try:
                    shutil.move(src_path, tgt_path)
                    logging.info(f"Moved {src_path} -> {tgt_path}")
                except Exception as e:
                    logging.error(f"Failed to move {src_path}: {e}")

    # Step 4: Update .gitignore
    update_gitignore(root)

    logging.info("Reorganization complete.")

if __name__ == '__main__':
    main()
