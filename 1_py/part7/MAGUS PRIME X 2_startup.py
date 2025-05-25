import os
import subprocess
import sys
import time


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    try:
        # Import key modules
        import_cmd = (
            "import flask, requests, pandas, numpy, talib, json, telegram, dotenv"
        )
        result = subprocess.run(
            [sys.executable, "-c", import_cmd], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("Some dependencies are missing. Installing now...")
            subprocess.run([sys.executable, "fix_dependencies.py"])
            return False
        return True
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False


def print_menu():
    """Print the main menu"""
    clear_screen()
    print("=" * 50)
    print("          MAGUS PRIME X TRADING BOT")
    print("=" * 50)
    print()
    print("1. Start Trading Bot")
    print("2. Check API Authentication")
    print("3. Test Signal Sender")
    print("4. Run Signal API Server")
    print("5. Install Dependencies")
    print("6. Edit .env Configuration")
    print("7. View Documentation")
    print("0. Exit")
    print()
    return input("Select an option: ")


def main():
    """Main program loop"""
    while True:
        choice = print_menu()

        if choice == "1":
            print("Starting Trading Bot...")
            subprocess.run([sys.executable, "bot.py"])

        elif choice == "2":
            print("Checking API Authentication...")
            subprocess.run([sys.executable, "auth_check.py"])
            input("Press Enter to continue...")

        elif choice == "3":
            print("Testing Signal Sender...")
            subprocess.run([sys.executable, "test_goldx.py"])
            input("Press Enter to continue...")

        elif choice == "4":
            print("Running Signal API Server...")
            subprocess.run([sys.executable, "signal_sender_api.py"])

        elif choice == "5":
            print("Installing Dependencies...")
            subprocess.run([sys.executable, "fix_dependencies.py"])
            input("Press Enter to continue...")

        elif choice == "6":
            # Open .env in default text editor
            print("Opening .env file...")
            if os.name == "nt":  # Windows
                os.system("notepad .env")
            else:  # Linux/Mac
                os.system("nano .env")

        elif choice == "7":
            # Show documentation
            clear_screen()
            print("=" * 50)
            print("          MAGUS PRIME X DOCUMENTATION")
            print("=" * 50)
            print()
            print("QUICK START:")
            print("1. Edit the .env file with your API keys")
            print("2. Check API Authentication")
            print("3. Start the Trading Bot")
            print()
            print("TROUBLESHOOTING:")
            print("- If authentication fails, check your API credentials")
            print("- If signals aren't being sent, run the Signal API Server")
            print("- For errors, check the log files in the logs directory")
            print()
            input("Press Enter to return to the menu...")

        elif choice == "0":
            print("Exiting...")
            time.sleep(1)
            sys.exit(0)

        else:
            print("Invalid option. Please try again.")
            time.sleep(2)


if __name__ == "__main__":
    # Check dependencies on startup
    check_dependencies()

    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
