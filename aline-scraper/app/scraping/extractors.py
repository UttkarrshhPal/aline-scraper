# Content extraction strategies placeholder 

from typing import List, Optional
from bs4 import BeautifulSoup
from ..config import Config
import requests

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class DsaBlogScraper:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        if SELENIUM_AVAILABLE:
            options = Options()
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = None

    def filter_category(self, index_url: str) -> List[str]:
        """Return only DSA category post links from the index page."""
        links = set()
        if self.driver:
            self.driver.get(index_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        else:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(index_url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
        # Find all post links in the main content area
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Heuristic: skip category/tag links, only keep links to individual posts
            if (
                '/blog/' in href and
                'category' not in href and
                'tag' not in href and
                not href.startswith('#')
            ):
                links.add(requests.compat.urljoin(index_url, href))
        print("[DSA DEBUG] Found links:", links)
        if self.driver:
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