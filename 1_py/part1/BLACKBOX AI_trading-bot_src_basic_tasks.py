import requests

def web_search(query):
    """
    Perform a web search using a simple API (e.g., DuckDuckGo).
    """
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Search failed"}
