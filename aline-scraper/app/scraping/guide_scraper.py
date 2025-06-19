import requests
from bs4 import BeautifulSoup
from typing import List, Dict

import requests.compat
from app.scraping.blog_scraper import BlogScraper
from app.scraping.selenium_scraper import SeleniumScraper
import logging

logger = logging.getLogger(__name__)

class GuideCollectionScraper:
    def __init__(self):
        self.blog_scraper = BlogScraper()
        self.selenium_scraper = SeleniumScraper()

    def extract_guides(self, url: str) -> List[Dict]:
        """Extract all guide links from a collection page and scrape their content."""
        logger.info(f"Extracting guides from: {url}")
        
        # Use Selenium for JS-heavy sites
        if 'interviewing.io' in url:
            return self._extract_guides_with_selenium(url)
        else:
            return self._extract_guides_with_requests(url)
    
    def _extract_guides_with_selenium(self, url: str) -> List[Dict]:
        """Extract guides using Selenium for JS-heavy sites."""
        # Define selectors for different types of guide pages
        link_selectors = [
            'a[href*="/topics/"]',
            'a[href*="/learn/"]', 
            '.guide-link',
            '.topic-link',
            'a[href*="guide"]',
            'a[href*="topic"]'
        ]
        
        # Wait for content to load
        wait_for = '.guide-list, .topic-list, [class*="guide"], [class*="topic"]'
        
        links = self.selenium_scraper.extract_links_with_selenium(
            url, link_selectors, wait_for
        )
        
        logger.info(f"Found {len(links)} guide links with Selenium")
        return self._process_guide_links(links)
    
    def _extract_guides_with_requests(self, url: str) -> List[Dict]:
        """Extract guides using requests for simpler sites."""
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if ('/topics/' in href or '/learn/' in href or 
                    'guide' in href.lower() or 'topic' in href.lower()) and not href.startswith('#'):
                    full_url = requests.compat.urljoin(url, href)
                    links.add(full_url)
            
            logger.info(f"Found {len(links)} guide links with requests")
            return self._process_guide_links(list(links))
            
        except Exception as e:
            logger.error(f"Error extracting guides with requests: {e}")
            return []
    
    def _process_guide_links(self, links: List[str]) -> List[Dict]:
        """Process guide links and extract content."""
        results = []
        
        for link in links:
            try:
                # Use Selenium for content extraction if it's a JS-heavy site
                if 'interviewing.io' in link:
                    content = self._extract_content_with_selenium(link)
                else:
                    content = self.blog_scraper.extract_content(link)
                
                if content.strip():
                    results.append({
                        "title": self._extract_title_from_url(link),
                        "content": content,
                        "content_type": "other",
                        "source_url": link,
                        "author": "",
                        "user_id": ""
                    })
                    
            except Exception as e:
                logger.error(f"Error processing guide link {link}: {e}")
        
        logger.info(f"Successfully processed {len(results)} guides")
        return results
    
    def _extract_content_with_selenium(self, url: str) -> str:
        """Extract content using Selenium for JS-heavy pages."""
        content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.guide-content',
            '.topic-content',
            'main',
            '[class*="content"]'
        ]
        
        return self.selenium_scraper.extract_content_with_selenium(
            url, content_selectors
        )
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a readable title from the URL."""
        # Remove domain and common paths
        title = url.split('/')[-1]
        title = title.replace('-', ' ').replace('_', ' ')
        title = title.title()
        return title or "Guide" 