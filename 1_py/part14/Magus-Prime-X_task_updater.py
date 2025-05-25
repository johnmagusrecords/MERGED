import sys
import re
import datetime  # Keep this import

TRACKER_MD = "project_tracker.md"
TRACKER_TXT = "project_tracker.txt"
LOG_FILE = "tracker_log.json"


def update_file(path, task_name):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        found = False
        for i, line in enumerate(lines):
            if task_name.lower() in line.lower() and "[ ]" in line:
                lines[i] = re.sub(r"\[ \]", "[✅]", line)
                found = True
                break

        if found:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"✅ Updated in {path}: {task_name}")
        else:
            print(f"❌ Task not found in {path}: {task_name}")

    except Exception as e:
        print(f"Error updating {path}: {e}")


def log_completion(task_name):
    import json
    try:
        log_data = {}
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except:
            pass
        # Updated to use datetime from the datetime module
        timestamp = datetime.datetime.utcnow().isoformat()
        log_data[task_name] = timestamp
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4)
        print(f"🕒 Logged completion in {LOG_FILE}")
    except Exception as e:
        print(f"Log error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ Usage: python task_updater.py \"Task Name\"")
        sys.exit(1)

    task = sys.argv[1]
    update_file(TRACKER_MD, task)
    update_file(TRACKER_TXT, task)
    log_completion(task)
    print(f"✅ Task '{task}' marked as completed in both files.")
