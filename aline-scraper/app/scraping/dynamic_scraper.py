import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DynamicScraper:
    def __init__(self, headless=True):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        # No version_main! Let uc auto-detect driver version.
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.headless = headless

    def get_page_with_js(self, url):
        """Load page and wait for JavaScript content"""
        if not self.driver:
            raise RuntimeError("Selenium driver is not initialized.")
        print(f"[DynamicScraper] Navigating to: {url}")
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        print(f"[DynamicScraper] Loaded page: {url}")
        return self.driver.page_source

    def extract_article_links(self, base_url, page_source):
        """Extract article links using multiple strategies, including site-specific selectors for realpython.com and overreacted.io"""
        print(f"[DynamicScraper] Extracting article links from: {base_url}")
        soup = BeautifulSoup(page_source, "html.parser")
        links = set()

        domain = base_url.split("//")[-1].split("/")[0].replace("www.", "")
        # Site-specific selectors for realpython.com and overreacted.io
        if domain == "realpython.com":
            patterns = [
                'a[href*="/tutorials/"]',
                'a[href*="/lessons/"]',
                'a[href*="/articles/"]',
                'a[href*="/blog/"]',
                'a.card[href^="/tutorials/"]',
                'a.card[href^="/lessons/"]',
                'a.card[href^="/articles/"]',
                'a.card[href^="/blog/"]',
            ]
        elif domain == "overreacted.io":
            # All internal links that look like blog posts (e.g. /my-post/)
            patterns = [
                'a[href^="/"]',
            ]
        else:
            patterns = [
                'a[href*="/blog/"]',
                'a[href*="/post/"]',
                'a[href*="/article/"]',
                'a[href*="/tutorial/"]',
                'a[href*="/guide/"]',
                'a[href*="/learn/"]',
                'a[href*="/interview"]',
                'a[href*="/experience"]',
                'a[href*="/dsa"]',
            ]
        for pattern in patterns:
            elements = soup.select(pattern)
            for el in elements:
                href = el.get("href")
                if isinstance(href, list):
                    href = href[0] if href else None
                if isinstance(href, str) and href:
                    # Only add internal links for overreacted.io
                    if domain == "overreacted.io":
                        if href.startswith("/") and href != "/":
                            # Exclude home and non-post links (e.g. /rss.xml, /favicon.ico)
                            if not any(href.endswith(ext) for ext in [".xml", ".ico", ".png", ".jpg", ".svg"]):
                                links.add(urljoin(base_url, href))
                    else:
                        if href.startswith("/") or domain in href:
                            links.add(urljoin(base_url, href))

        # Strategy 2: Find links in main content areas
        content_areas = soup.select("main, .content, .posts, .articles, article")
        for area in content_areas:
            area_links = area.find_all("a", href=True)
            for link in area_links:
                href = link.get("href")
                if href and self.is_article_link(href):
                    if href.startswith("/") or domain in href:
                        links.add(urljoin(base_url, href))

        print(f"[DynamicScraper] Found {len(links)} article links.")
        return list(links)

    def is_article_link(self, href):
        """Determine if a link points to an article"""
        skip_patterns = [
            "#", "mailto:", "tel:", "javascript:", "/tag/", "/category/", "/author/",
            ".xml", ".ico", ".png", ".jpg", ".svg"
        ]
        if any(pattern in href for pattern in skip_patterns):
            return False
        include_patterns = [
            "/blog/", "/post/", "/article/", "/tutorial/", "/guide/", "/learn/",
            "/interview", "/experience", "/dsa"
        ]
        # For overreacted.io, treat any /slug/ as a post
        if href.startswith("/") and href.count("/") == 2 and not any(pattern in href for pattern in skip_patterns):
            return True
        return any(pattern in href for pattern in include_patterns)

    def handle_infinite_scroll(self, max_scrolls=5):
        """Handle infinite scroll to load more content"""
        if not self.driver:
            raise RuntimeError("Selenium driver is not initialized.")
        print(f"[DynamicScraper] Starting infinite scroll (max_scrolls={max_scrolls})")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            try:
                load_more = self.driver.find_element(
                    By.CSS_SELECTOR, ".load-more, .show-more, .more-posts, .next-page"
                )
                if load_more.is_displayed():
                    load_more.click()
                    print("[DynamicScraper] Clicked 'load more' button.")
                    time.sleep(3)
            except Exception:
                pass
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("[DynamicScraper] No more content to scroll.")
                break
            last_height = new_height
            scrolls += 1
        print(f"[DynamicScraper] Finished infinite scroll after {scrolls} scrolls.")

    def handle_hash_navigation(self, url):
        """Handle URLs with hash fragments like interviewing.io/learn#interview-guides"""
        if not self.driver:
            raise RuntimeError("Selenium driver is not initialized.")
        print(f"[DynamicScraper] Navigating to (with hash): {url}")
        self.driver.get(url)
        time.sleep(3)
        if "#" in url:
            hash_part = url.split("#")[1]
            try:
                nav_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    f'[href="#{{hash_part}}"], [data-target="#{{hash_part}}"], .{{hash_part}}',
                )
                nav_element.click()
                print(f"[DynamicScraper] Clicked navigation for hash: {hash_part}")
                time.sleep(3)
            except Exception:
                print(f"[DynamicScraper] No clickable navigation found for hash: {hash_part}")
                pass
            self.driver.execute_script(
                f"""
                var element = document.getElementById('{hash_part}') || 
                            document.querySelector('.{hash_part}') ||
                            document.querySelector('[data-section="{hash_part}"]');
                if (element) {{
                    element.scrollIntoView();
                    element.style.display = 'block';
                }}
                """
            )
            print(f"[DynamicScraper] Executed JS scroll for hash: {hash_part}")
            time.sleep(2)
        print(f"[DynamicScraper] Loaded page (with hash): {url}")
        return self.driver.page_source

    def extract_content(self, url, page_source):
        """Extract article content using multiple strategies"""
        print(f"[DynamicScraper] Extracting content from: {url}")
        # Strategy 1: Use trafilatura
        try:
            import trafilatura
            content = trafilatura.extract(
                page_source, url=url, include_links=True, include_images=False
            )
            if content and len(content) > 200:
                return self.clean_content(content)
        except Exception:
            pass
        # Strategy 2: Use newspaper3k
        try:
            from newspaper import Article
            article = Article(url)
            article.set_html(page_source)
            article.parse()
            if article.text and len(article.text) > 200:
                return self.clean_content(article.text)
        except Exception:
            pass
        # Strategy 3: Manual extraction with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")
        for element in soup(
            ["script", "style", "nav", "header", "footer", "aside", ".sidebar", ".navigation"]
        ):
            element.decompose()
        content_selectors = [
            "article .content, article .post-content, article .entry-content",
            ".post-body, .post-content, .entry-content",
            ".article-content, .tutorial-content, .guide-content",
            "main article, main .content",
            '[role="main"] article',
        ]
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(strip=True)
                if len(text) > 200:
                    return self.clean_content(text)
        # Fallback: get largest text block
        print(f"[DynamicScraper] Finished extracting content from: {url}")
        return self.get_largest_text_block(soup)

    def clean_content(self, text):
        """Clean extracted content"""
        text = re.sub(r"\s+", " ", text)
        unwanted_patterns = [
            r"Share this:.*$",
            r"Like this:.*$",
            r"Related Posts.*$",
            r"Tags:.*$",
            r"Categories:.*$",
        ]
        for pattern in unwanted_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text.strip()

    def get_largest_text_block(self, soup):
        paragraphs = soup.find_all("p")
        if not paragraphs:
            return ""
        largest = max(paragraphs, key=lambda p: len(p.text))
        return self.clean_content(largest.get_text())

    def close(self):
        """Robustly close the Selenium driver."""
        print("[DynamicScraper] Closing Selenium driver.")
        try:
            if hasattr(self, "driver") and self.driver:
                self.driver.quit()
                self.driver = None
        except Exception:
            print("[DynamicScraper] Exception occurred while closing driver.")
            pass
