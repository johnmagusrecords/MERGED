import requests

# ✅ New Capital API Key
CAPITAL_API_KEY = "MFjNMipztEELvdrV"

# ✅ Use the correct API URL (Demo or Live)
url = "https://demo-api-capital.backend-capital.com/api/v1/accounts"

# ✅ Ensure the request headers are correct
headers = {
    "X-CAP-API-KEY": CAPITAL_API_KEY,
    "Content-Type": "application/json"
}

# ⏳ Send the request
response = requests.get(url, headers=headers)

# 🔍 Print the result
if response.status_code == 200:
    print("✅ API is working successfully!")
    print(response.json())  # Print account details
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)  # Print full error message