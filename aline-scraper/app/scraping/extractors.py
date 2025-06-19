# Content extraction strategies placeholder 

from typing import List, Optional
from bs4 import BeautifulSoup
from ..config import Config
import requests
import undetected_chromedriver as uc
from urllib.parse import urljoin

class DsaBlogScraper:
    def __init__(self, config=None, headless: bool = True):
        self.config = config or Config()
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.driver = uc.Chrome(options=options)

    def filter_category(self, index_url: str) -> List[str]:
        """Return only DSA category post links from the index page."""
        links = set()
        self.driver.get(index_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # Find all post links in the main content area
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Only keep links to DSA blog posts (contain /blog/ and ?category=dsa)
            if (
                '/blog/' in href and
                '?category=dsa' in href and
                not href.startswith('#')
            ):
                # Remove URL fragments and deduplicate
                clean_href = href.split('#')[0]
                links.add(urljoin(index_url, clean_href))
        print("[DSA DEBUG] Found links:", links)
        self.driver.quit()
        return list(links)

    def extract_content_with_code_and_math(self, url: str) -> str:
        """Extract content, preserving code blocks and mathematical notation."""
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Preserve code blocks
        for pre in soup.find_all('pre'):
            pre.insert_before('\n```\n')
            pre.insert_after('\n```\n')
        # Preserve inline code
        for code in soup.find_all('code'):
            code.insert_before('`')
            code.insert_after('`')
        # Preserve math (heuristic: look for <span class="math"> or $...$)
        for span in soup.find_all('span', class_='math'):
            span.insert_before('$$')
            span.insert_after('$$')
        # Extract main content
        main = soup.find('main') or soup.find('article') or soup
        text = main.get_text(separator='\n', strip=True)
        return text

    def detect_and_format_algorithms(self, content: str) -> str:
        """Detect and properly format algorithm descriptions in the content."""
        # Heuristic: wrap lines starting with 'Algorithm:' in a markdown blockquote
        lines = content.split('\n')
        formatted = []
        for line in lines:
            if line.strip().lower().startswith('algorithm:'):
                formatted.append('> ' + line)
            else:
                formatted.append(line)
        return '\n'.join(formatted)