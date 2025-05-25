import os


def check_and_correct_token_in_file(file_path, correct_token):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        if correct_token in content:
            print(f"Token is correct in: {file_path}")
        elif "TELEGRAM_BOT_TOKEN=" in content or "TELEGRAM_TOKEN=" in content:
            # Replace incorrect token
            updated_content = content.replace(
                content.split("TELEGRAM_BOT_TOKEN=")[1].split("\n")[0],
                correct_token
            ).replace(
                content.split("TELEGRAM_TOKEN=")[1].split("\n")[0],
                correct_token
            )
            with open(file_path, 'w') as file:
                file.write(updated_content)
            print(f"Token corrected in: {file_path}")
        else:
            print(f"No token found in: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def check_and_correct_token_in_project(project_path, correct_token):
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.env') or file.endswith('.py') or file.endswith('.txt'):
                file_path = os.path.join(root, file)
                check_and_correct_token_in_file(file_path, correct_token)


# Define the path to your project and the correct token
project_path = "c:\\Users\\djjoh\\OneDrive\\Desktop\\MAGUS_PRIME_X_APP"
correct_bot_token = "8132805121:AAH0vmH8sBbCynckfqxAWIEP7E6Tj99i4_c"

# Run the check and correction
check_and_correct_token_in_project(project_path, correct_bot_token)
