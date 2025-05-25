import os
import re

# Path to the bot.py file
bot_file_path = "c:/Users/djjoh/OneDrive/Desktop/MAGUS PRIME X/bot.py"

# Try different encodings to read the file
encodings = ['utf-8', 'latin-1', 'utf-16', 'cp1252']
content = None

for encoding in encodings:
    try:
        print(f"Trying to read file with {encoding} encoding...")
        with open(bot_file_path, 'r', encoding=encoding) as file:
            content = file.read()
        print(f"Successfully read file with {encoding} encoding")
        break
    except UnicodeDecodeError:
        print(f"Failed to read with {encoding} encoding")
    except Exception as e:
        print(f"Other error: {e}")

if content is None:
    print("Could not read the file with any encoding. Skipping modification.")
else:
    # Check for TELEGRAM_TOKEN reference and replace with TELEGRAM_BOT_TOKEN
    if 'TELEGRAM_TOKEN' in content:
        print("Found TELEGRAM_TOKEN reference in bot.py")
        modified_content = content.replace(
            'TELEGRAM_TOKEN', 'TELEGRAM_BOT_TOKEN')

        # Write the changes back to the file using the same successful encoding
        try:
            with open(bot_file_path, 'w', encoding=encoding) as file:
                file.write(modified_content)
            print(
                f"Successfully updated bot.py to use TELEGRAM_BOT_TOKEN with {encoding} encoding")
        except Exception as e:
            print(f"Error writing file: {e}")
    else:
        print("No TELEGRAM_TOKEN reference found in bot.py")
