import requests

url = "https://magus-prime-x.onrender.com/send-signal"
headers = {"Content-Type": "application/json", "X-API-Key": "magus_prime_secret_key"}

data = {
    "pair": "GOLD",
    "entry": 3110,
    "stop_loss": 3100,
    "tp1": 3120,
    "tp2": 3135,
    "tp3": 3150,
    "timeframe": "30m",
    "mode": "SAFE_RECOVERY",
    "type": "Breakout",
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
