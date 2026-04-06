import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from decouple import config

TOR_PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

FLIBUSTA_URL = config('FLIBUSTA_URL')

def search_books(query):
    # try:
    #     response = requests.get(f'{FLIBUSTA_URL}/booksearch?ask={query}', proxies=TOR_PROXIES, timeout=15)
    #     response.raise_for_status()
    #     soup = BeautifulSoup(response.text, 'lxml')
    #     
    #     results = []
    #     # Parsing logic
    #     return results
    # except Exception:
    #     return []
    return []

def download_book(flibusta_id):
    # try:
    #     url = f'{FLIBUSTA_URL}/b/{flibusta_id}/fb2'
    #     response = requests.get(url, proxies=TOR_PROXIES, stream=True, timeout=30)
    #     response.raise_for_status()
    #     return ContentFile(response.content)
    # except Exception:
    #     return None
    return None
