import requests
from selectorlib import Extractor


def scrape_amazon(url, extractor):
    headers = {
        "User-Agent": "Your User Agent",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return extractor.extract(response.text)
    return None
