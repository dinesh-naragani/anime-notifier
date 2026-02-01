import requests

ANIMETOSHO_JSON = "https://feed.animetosho.org/json"

def fetch_feed(timeout: int = 30):
    """
    Fetch AnimeTosho JSON feed.
    Returns the raw JSON list exactly as provided by the API.
    """
    response = requests.get(ANIMETOSHO_JSON, timeout=timeout)
    response.raise_for_status()
    return response.json()
