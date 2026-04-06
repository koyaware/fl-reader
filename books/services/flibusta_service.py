import logging
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from decouple import config

logger = logging.getLogger(__name__)

FLIBUSTA_URL = config('FLIBUSTA_URL')
TOR_PROXIES = {
    'http': f'socks5h://{config("TOR_PROXY_HOST", default="127.0.0.1")}:{config("TOR_PROXY_PORT", default=9050)}',
    'https': f'socks5h://{config("TOR_PROXY_HOST", default="127.0.0.1")}:{config("TOR_PROXY_PORT", default=9050)}',
}


def search_books(query):
    try:
        response = requests.get(
            f'{FLIBUSTA_URL}/booksearch',
            params={'ask': query},
            proxies=TOR_PROXIES,
            timeout=25,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        main = soup.find(id='main')
        if not main:
            return results

        for li in main.find_all('li'):
            links = li.find_all('a')
            if not links:
                continue

            book_link = None
            for a in links:
                href = a.get('href', '')
                if href.startswith('/b/') and len(href.split('/')) >= 3:
                    book_link = a
                    break

            if not book_link:
                continue

            try:
                book_id = book_link['href'].split('/')[2]
            except (IndexError, KeyError):
                continue

            title = book_link.get_text(separator=' ', strip=True)
            author = ''
            author_link = li.find('a', href=lambda h: h and h.startswith('/a/'))
            if author_link:
                author = author_link.get_text(separator=' ', strip=True)

            if title and book_id:
                import re
                title = re.sub(r'\s+', ' ', title)
                author = re.sub(r'\s+', ' ', author) if author else 'Неизвестный автор'
                results.append({'id': book_id, 'title': title, 'author': author})

        return results
    except Exception as e:
        logger.error('Flibusta search error: %s', e)
        return None


import zipfile
import io

def download_book(flibusta_id):
    try:
        url = f'{FLIBUSTA_URL}/b/{flibusta_id}/fb2'
        response = requests.get(url, proxies=TOR_PROXIES, stream=True, timeout=60)
        response.raise_for_status()
        
        content = response.content
        if content.startswith(b'PK\x03\x04'):
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                fb2_name = next((name for name in z.namelist() if name.lower().endswith('.fb2')), None)
                if fb2_name:
                    content = z.read(fb2_name)

        return ContentFile(content)
    except Exception as e:
        logger.error('Flibusta download error: %s', e)
        return None
