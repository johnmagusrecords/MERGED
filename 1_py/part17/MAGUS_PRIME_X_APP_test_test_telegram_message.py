import os
from dotenv import load_dotenv
import httpx

load_dotenv()

# Always use the environment variable for the token
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

if not token:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN is not set in the environment variables.")

if not chat_id:
    raise ValueError(
        "TELEGRAM_CHAT_ID is not set in the environment variables.")

print("Using token:", token)
print("Using chat_id:", chat_id)  # Debug output

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = {
    "chat_id": chat_id,
    "text": "✅ Test message from MAGUS PRIME X Bot"
}

try:
    response = httpx.post(url, json=data)
    print(response.status_code, response.text)
except Exception as e:
    print("Error sending message:", e)
