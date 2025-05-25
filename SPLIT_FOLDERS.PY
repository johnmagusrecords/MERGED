# split_folders.py
import os
import shutil
import argparse

def chunk_directory(dir_path: str, chunk_size: int):
    # list only files (not directories)
    files = [f for f in os.listdir(dir_path)
             if os.path.isfile(os.path.join(dir_path, f))]
    if not files:
        print(f"  ↳ no files in {dir_path}, skipping")
        return

    for idx in range(0, len(files), chunk_size):
        chunk = files[idx : idx + chunk_size]
        part_num = idx // chunk_size + 1
        part_dir = os.path.join(dir_path, f"part{part_num}")
        os.makedirs(part_dir, exist_ok=True)
        print(f"  ↳ moving {len(chunk)} files → {part_dir}/")
        for fname in chunk:
            shutil.move(
                os.path.join(dir_path, fname),
                os.path.join(part_dir, fname)
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split large folders into sub-folders of N files each"
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Root of your project (default: current directory)"
    )
    parser.add_argument(
        "--folders",
        nargs="+",
        default=["1_PY", "2_CONFIGS", "3_FRONTEND", "4_DOCS"],
        help="List of top-level folders to split"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=900,
        help="Maximum number of files per subfolder"
    )
    args = parser.parse_args()

    for fld in args.folders:
        path = os.path.join(args.base_dir, fld)
        if os.path.isdir(path):
            print(f"Processing {path} (contains {len(os.listdir(path))} entries)…")
            chunk_directory(path, args.chunk_size)
        else:
            print(f"Warning: {path} does not exist, skipping.")
