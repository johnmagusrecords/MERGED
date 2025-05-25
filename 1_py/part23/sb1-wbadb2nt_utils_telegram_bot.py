import os
from dotenv import load_dotenv
import httpx

load_dotenv()

# Always use the environment variable for the token
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_GROUP_ID")

if not token:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN is not set in the environment variables.")

print("Using token:", token)

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = {
    "chat_id": chat_id,
    "text": "✅ Test message from MAGUS PRIME X Bot"
}

response = httpx.post(url, json=data)
print(response.status_code, response.text)