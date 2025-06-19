from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any
import logging
import random

logger = logging.getLogger(__name__)

class SeleniumScraper:
    def __init__(self, headless: bool = True, use_undetected: bool = False):
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        
    def _setup_driver(self):
        """Setup Chrome driver with appropriate options and anti-detection measures."""
        try:
            if self.use_undetected:
                # Use undetected-chromedriver for Cloudflare protection
                try:
                    import undetected_chromedriver as uc
                    chrome_options = uc.ChromeOptions()
                    if self.headless:
                        chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--window-size=1920,1080")
                    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    chrome_options.add_experimental_option('useAutomationExtension', False)
                    
                    # Randomize User-Agent
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
                    ]
                    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
                    
                    self.driver = uc.Chrome(options=chrome_options)
                    logger.info("Using undetected-chromedriver for anti-detection")
                    return True
                except ImportError:
                    logger.warning("undetected-chromedriver not available, falling back to regular selenium")
                    self.use_undetected = False
            
            # Regular Selenium setup
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            # Anti-detection options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # Randomize User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            # Remove automation flags
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            logger.info("Using regular selenium webdriver")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def _wait_for_element(self, selector: str, timeout: int = 10, by: By = By.CSS_SELECTOR):
        """Wait for an element to be present on the page."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return False
    
    def scrape_page(self, url: str, wait_for: str = None, timeout: int = 10) -> str:
        """Scrape a page and return the HTML content."""
        if not self._setup_driver():
            return ""
        
        try:
            logger.info(f"Scraping URL: {url}")
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for:
                self._wait_for_element(wait_for, timeout)
            else:
                # Default wait for page to load
                time.sleep(3)
            
            # Get the page source after JavaScript has rendered
            page_source = self.driver.page_source
            logger.info(f"Successfully scraped {len(page_source)} characters from {url}")
            return page_source
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def extract_links_with_selenium(self, url: str, link_selectors: List[str], 
                                  wait_for: str = None) -> List[str]:
        """Extract links from a page using Selenium, with scrolling and longer waits."""
        if not self._setup_driver():
            return []
        
        try:
            logger.info(f"Extracting links from: {url}")
            self.driver.get(url)
            
            # Check for Cloudflare protection
            if "Just a moment" in self.driver.title or "Checking your browser" in self.driver.page_source:
                logger.info("Detected Cloudflare protection, waiting for challenge to complete...")
                # Wait longer for Cloudflare challenge
                time.sleep(random.uniform(15, 25))
                
                # Check if still on challenge page
                if "Just a moment" in self.driver.title:
                    logger.warning("Still on Cloudflare challenge page after wait")
                    # Save the challenge page for debugging
                    html_path = f"cloudflare_challenge_{url.split('//')[-1].replace('/', '_')}.html"
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    logger.warning(f"Saved Cloudflare challenge page to {html_path}")
                    return []
            
            # Wait for content to load
            time.sleep(random.uniform(5, 10))
            
            # Enhanced scrolling with infinite scroll detection
            self._handle_infinite_scroll()
            
            # Wait for main selector if provided
            if wait_for:
                self._wait_for_element(wait_for, timeout=20)  # Increased timeout
            
            # Try adaptive selectors if initial selectors fail
            links = []
            for selector in link_selectors:
                try:
                    logger.info(f"Trying link selector: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Selector '{selector}' found {len(elements)} elements.")
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in links:
                            links.append(href)
                    
                    if elements:
                        logger.info(f"First 3 hrefs for selector '{selector}': {[e.get_attribute('href') for e in elements[:3]]}")
                except Exception as e:
                    logger.warning(f"Error with selector {selector}: {e}")
            
            # If no links found, try adaptive selectors
            if not links:
                links = self._try_adaptive_selectors()
            
            # Always save HTML for debugging
            html_path = f"selenium_links_debug_{url.split('//')[-1].replace('/', '_')}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"Saved HTML to {html_path} (found {len(links)} links)")
            
            if not links:
                logger.warning(f"No links extracted from {url}. See {html_path} for page source.")
            else:
                logger.info(f"Found {len(links)} links from {url}")
            
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _handle_infinite_scroll(self):
        """Handle infinite scrolling with smart detection."""
        scroll_pause = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 8  # Increased for dynamic sites
        no_change_count = 0
        
        for _ in range(max_scrolls):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Scroll up a bit to trigger more loading (mimics human behavior)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
            time.sleep(1)
            
            # Check if page height changed
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= 3:  # Try scrolling 3 times before giving up
                    logger.info("No more content to load, stopping infinite scroll")
                    break
            else:
                no_change_count = 0
                last_height = new_height
                logger.info(f"Page height increased to {new_height}, continuing scroll")
            
            # Additional wait for dynamic content
            time.sleep(random.uniform(2, 4))

    def _try_adaptive_selectors(self) -> List[str]:
        """Try adaptive selectors when standard selectors fail."""
        links = []
        
        # Common blog post patterns
        adaptive_selectors = [
            # WordPress patterns
            "article a", ".entry-title a", ".post-title a", ".blog-post a",
            # Generic patterns
            "a[href*='/blog/']", "a[href*='/post/']", "a[href*='/article/']",
            # Date-based patterns
            "a[href*='/20']", "a[href*='/202']",
            # Content patterns
            ".content a", ".main a", "main a",
            # Fallback: all links
            "a"
        ]
        
        for selector in adaptive_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Adaptive selector '{selector}' found {len(elements)} elements")
                
                for element in elements:
                    href = element.get_attribute('href')
                    if href and href not in links and self._looks_like_blog_post(href):
                        links.append(href)
                
                if links:
                    logger.info(f"Adaptive selector '{selector}' found {len(links)} blog post links")
                    break
                    
            except Exception as e:
                logger.warning(f"Error with adaptive selector {selector}: {e}")
                continue
        
        return links

    def _looks_like_blog_post(self, href: str) -> bool:
        """Check if a URL looks like a blog post."""
        if not href:
            return False
        
        # Blog post indicators
        blog_indicators = [
            '/blog/', '/post/', '/article/', '/story/', '/news/',
            '/20', '/202', '.html', '.php'
        ]
        
        # Exclude common non-blog patterns
        exclude_patterns = [
            '/category/', '/tag/', '/author/', '/page/',
            '/feed/', '/rss/', '/sitemap', '/search',
            'mailto:', 'tel:', '#', 'javascript:'
        ]
        
        # Check for blog indicators
        has_blog_indicator = any(indicator in href for indicator in blog_indicators)
        
        # Check for excluded patterns
        has_excluded_pattern = any(pattern in href for pattern in exclude_patterns)
        
        return has_blog_indicator and not has_excluded_pattern
    
    def extract_content_with_selenium(self, url: str, content_selectors: List[str],
                                    wait_for: str = None) -> str:
        """Extract content from a page using Selenium."""
        if not self._setup_driver():
            return ""
        
        try:
            logger.info(f"Extracting content from: {url}")
            self.driver.get(url)
            # Add random delay to mimic human behavior
            time.sleep(random.uniform(5, 10))
            # Wait for content to load (explicit wait for main selector)
            found = False
            if wait_for:
                found = self._wait_for_element(wait_for, timeout=15)
            else:
                # Try to wait for any of the content selectors
                for sel in content_selectors:
                    if self._wait_for_element(sel, timeout=10):
                        found = True
                        break
            if not found:
                logger.warning("Main content selector not found after wait.")
            content = ""
            for selector in content_selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        content += element.text + "\n"
                    if content.strip():
                        break  # Use first successful selector
                except Exception as e:
                    logger.warning(f"Error with content selector {selector}: {e}")
            
            if not content.strip():
                # Save HTML for debugging
                html_path = f"selenium_debug_{url.split('//')[-1].replace('/', '_')}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.warning(f"No content extracted. Saved HTML to {html_path}")
            else:
                logger.info(f"Extracted {len(content)} characters from {url}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None 