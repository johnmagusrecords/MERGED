import requests

url = "https://magus-prime-x.onrender.com/send-signal"
headers = {"Content-Type": "application/json", "X-API-Key": "magus_prime_secret_key"}

data = {
    "pair": "GOLD",
    "entry": 3110,
    "stop_loss": 3100,
    "take_profit_1": 3120,
    "take_profit_2": 3135,
    "take_profit_3": 3150,
    "timeframe": "30m",
    "mode": "SAFE_RECOVERY",
    "trade_type": "Breakout",
}

print("Data being sent:", data)  # Debugging line to print the data
response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
