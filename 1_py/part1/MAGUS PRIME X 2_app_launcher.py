import subprocess
import os

def launch_app(app_path):
    try:
        subprocess.Popen(app_path, shell=True)
        print(f"Launched: {app_path}")
    except Exception as e:
        print(f"Error launching app: {str(e)}")

while True:
    os.system('cls')  # Clear screen (Windows)
    print("=================================")
    print("      MAGUS PRIME X Launcher")
    print("=================================")
    print("1. Open Notepad")
    print("2. Open Calculator")
    print("3. Open Chrome (example)")
    print("4. Exit")
    print("=================================")
    
    choice = input("Enter your choice [1-4]: ")
    
    if choice == "1":
        launch_app("notepad.exe")
    elif choice == "2":
        launch_app("calc.exe")
    elif choice == "3":
        # Replace with your actual Chrome path (or other app)
        launch_app(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    elif choice == "4":
        print("Exiting launcher...")
        break
    else:
        print("Invalid choice! Please enter 1-4.")
    input("Press Enter to continue...")