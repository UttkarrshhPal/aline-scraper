# Blog scraping logic placeholder 

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Optional
from app.config import Config
from urllib.parse import urljoin, urlparse
import logging
from app.scraping.dynamic_scraper import DynamicScraper

logger = logging.getLogger(__name__)

class BlogScraper:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.dynamic_scraper = DynamicScraper(headless=True)
        self.logger = logging.getLogger(__name__)
        self.delay = self.config.request_delay
        self.max_retries = self.config.max_retries
        self.selectors = self.config.scraping_rules.get('default_selectors', {})
        self.site_specific = self.config.scraping_rules.get('site_specific', {})

    def scrape_index(self, url: str) -> List[str]:
        """Use DynamicScraper to extract all blog post links from an index page, handling JS and infinite scroll."""
        try:
            page_source = self.dynamic_scraper.get_page_with_js(url)
            # Optionally handle infinite scroll for certain domains
            if any(domain in url for domain in ["geeksforgeeks.org", "realpython.com"]):
                self.dynamic_scraper.handle_infinite_scroll(max_scrolls=5)
                page_source = self.dynamic_scraper.driver.page_source
            links = self.dynamic_scraper.extract_article_links(url, page_source)
            return links
        except Exception as e:
            self.logger.error(f"DynamicScraper failed to extract links: {e}")
            return []

    def extract_content(self, url: str) -> str:
        """Use DynamicScraper to extract main content from a blog post."""
        try:
            page_source = self.dynamic_scraper.get_page_with_js(url)
            content = self.dynamic_scraper.extract_content(url, page_source)
            return content
        except Exception as e:
            self.logger.error(f"DynamicScraper failed to extract content: {e}")
            return ""

    def __del__(self):
        self.dynamic_scraper.close()

    def _extract_links_with_category_navigation(self, selenium_scraper, base_url: str, site_conf: dict) -> set:
        """Extract blog post links by navigating through category pages."""
        links = set()
        
        # First, get category links from the main blog page
        category_selectors = site_conf.get('category_selectors', ['a[href*="/category/"]', 'a[href*="/tag/"]'])
        logger.info(f"Extracting category links with selectors: {category_selectors}")
        
        category_links = selenium_scraper.extract_links_with_selenium(base_url, category_selectors)
        logger.info(f"Found {len(category_links)} category links")
        
        # Filter category links to only include actual category pages
        filtered_categories = []
        for href in category_links:
            if self._is_category_link(href, base_url):
                filtered_categories.append(href)
        
        logger.info(f"Filtered to {len(filtered_categories)} valid category links")
        
        # Extract blog post links from each category page
        for category_url in filtered_categories[:5]:  # Limit to first 5 categories for performance
            try:
                logger.info(f"Extracting links from category: {category_url}")
                post_selectors = site_conf.get('post_selectors', ['a[href*="/blog/"]', 'article a', '.post-title a'])
                
                category_links = selenium_scraper.extract_links_with_selenium(category_url, post_selectors)
                
                for href in category_links:
                    if self._is_blog_post_link(href, base_url):
                        links.add(urljoin(base_url, href))
                
            except Exception as e:
                logger.error(f"Error extracting from category {category_url}: {e}")
                continue
        
        return links

    def _is_category_link(self, href: str, base_url: str) -> bool:
        """Check if a link is a category page link."""
        if not href:
            return False
        
        # Common category patterns
        category_patterns = [
            '/category/', '/tag/', '/topics/', '/sections/',
            '/blog/category/', '/blog/tag/', '/posts/category/'
        ]
        
        if any(pattern in href for pattern in category_patterns):
            # Exclude links that look like individual posts
            post_patterns = ['/20', '/202', '.html', '.php']
            if not any(pattern in href for pattern in post_patterns):
                return True
        
        return False

    def _is_blog_post_link(self, href: str, base_url: str) -> bool:
        # Heuristic: skip index, tag, category, or external links
        if not href or href.startswith('#') or 'tag' in href or 'category' in href:
            return False
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc not in urlparse(base_url).netloc:
            return False
        # Accept links that look like blog posts or articles
        patterns = [
            '/blog/', '/posts/', '/articles/', '/story/', '/news/', '/entry/', '/p/'
        ]
        if any(p in href for p in patterns):
            return True
        # Accept .html or .md files
        if href.endswith('.html') or href.endswith('.md'):
            return True
        # Accept links with year/month/day (common in blogs)
        import re
        if re.search(r'/20\d{2}/\d{2}/', href):
            return True
        return False

    def handle_pagination(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Detect and return the next page URL if pagination exists."""
        domain = urlparse(base_url).netloc
        site_conf = None
        for key in self.site_specific:
            if key in domain:
                site_conf = self.site_specific[key]
                break
        if site_conf and 'pagination' in site_conf:
            next_link = soup.select_one(site_conf['pagination'])
            if next_link and next_link.get('href'):
                return urljoin(base_url, next_link['href'])
        # Fallback: look for rel="next"
        next_link = soup.find('a', rel='next')
        if next_link and next_link.get('href'):
            return urljoin(base_url, next_link['href'])
        return None

    def rate_limit(self):
        """Respectful crawling delay between requests."""
        time.sleep(self.delay)

    def clean_content(self, html: str) -> str:
        """Remove ads, navigation, comments, and clean up the HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        # Remove unwanted elements
        for selector in ['nav', 'header', 'footer', '.ads', '.social', '.comments']:
            for tag in soup.select(selector):
                tag.decompose()
        # Remove scripts and styles
        for tag in soup(['script', 'style']):
            tag.decompose()
        # Normalize whitespace
        text = soup.get_text(separator='\n', strip=True)
        return text 