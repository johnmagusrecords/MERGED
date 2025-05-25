import requests

url = "https://demo-api-capital.backend-capital.com/api/v1"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
