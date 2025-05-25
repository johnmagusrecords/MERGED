import os

from dotenv import load_dotenv


def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)


def update_env_file(updates):
    """Update values in the .env file"""
    env_path = os.path.join(os.getcwd(), ".env")

    if not os.path.exists(env_path):
        print(f"❌ ERROR: .env file not found at {env_path}")
        return False

    try:
        # Read the current .env file
        with open(env_path, "r") as f:
            lines = f.readlines()

        # Track which values were updated
        updated_keys = set()

        # Update the values
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                new_lines.append(line)
                continue

            try:
                key, value = line.split("=", 1)
                key = key.strip()

                if key in updates:
                    new_lines.append(f"{key}={updates[key]}")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)

        # Add any new values that weren't in the file
        for key, value in updates.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}")

        # Write the updated file
        with open(env_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")

        print("✅ Successfully updated .env file")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to update .env file: {e}")
        return False


def main():
    print_header("Capital.com API Rate Limit Configurator")
    print("This tool helps configure API rate limits to avoid throttling issues.")

    # Load current values
    load_dotenv()
    current_interval = os.getenv("API_CALL_INTERVAL", "0.5")
    current_retries = os.getenv("API_MAX_RETRIES", "5")
    current_backoff = os.getenv("API_BACKOFF_FACTOR", "2")

    print("\nCurrent settings:")
    print(f"API call interval: {current_interval} seconds")
    print(f"Max retries: {current_retries}")
    print(f"Backoff factor: {current_backoff}")

    print("\nRecommended settings for Capital.com API:")
    print("API call interval: 1.0 seconds")
    print("Max retries: 10")
    print("Backoff factor: 1.5")

    print("\nWhat would you like to do?")
    print("1. Use recommended settings")
    print("2. Enter custom settings")
    print("3. Exit without changes")

    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        updates = {
            "API_CALL_INTERVAL": "1.0",
            "API_MAX_RETRIES": "10",
            "API_BACKOFF_FACTOR": "1.5",
        }
        if update_env_file(updates):
            print("\n✅ Successfully updated to recommended settings")
    elif choice == "2":
        interval = (
            input(f"Enter API call interval in seconds [{current_interval}]: ")
            or current_interval
        )
        retries = input(f"Enter max retries [{current_retries}]: ") or current_retries
        backoff = (
            input(f"Enter backoff factor [{current_backoff}]: ") or current_backoff
        )

        updates = {
            "API_CALL_INTERVAL": interval,
            "API_MAX_RETRIES": retries,
            "API_BACKOFF_FACTOR": backoff,
        }
        if update_env_file(updates):
            print("\n✅ Successfully updated to custom settings")
    else:
        print("\n❌ No changes made")

    print("\nTo use these settings, restart your bot.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        print("\nPress Enter to exit...")
        input()
