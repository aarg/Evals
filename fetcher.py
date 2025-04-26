import requests
from bs4 import BeautifulSoup
import os

def fetch_article_content(url: str) -> str:
    """Fetches and extracts the main text content from a blog post URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    # Try to extract the main content
    article = soup.find('article')
    if article:
        text = article.get_text(separator='\n', strip=True)
    else:
        # Fallback: join all <p> tags
        paragraphs = soup.find_all('p')
        text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
    return text

def save_article(text: str, url: str, directory: str = 'articles') -> str:
    """Saves the article text to a file named after the URL slug."""
    os.makedirs(directory, exist_ok=True)
    slug = url.split('//')[-1].replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_')
    filename = os.path.join(directory, f"{slug}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
    return filename
