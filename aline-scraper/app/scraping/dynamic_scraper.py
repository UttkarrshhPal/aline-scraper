import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DynamicScraper:
    def __init__(self, headless=True):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def get_page_with_js(self, url):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        return self.driver.page_source

    def extract_article_links(self, base_url, page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        links = set()
        patterns = [
            'a[href*="/blog/"]', 'a[href*="/post/"]', 'a[href*="/article/"]',
            'a[href*="/tutorial/"]', 'a[href*="/guide/"]', 'a[href*="/learn/"]',
            'a[href*="/interview"]', 'a[href*="/experience"]', 'a[href*="/dsa"]'
        ]
        for pattern in patterns:
            elements = soup.select(pattern)
            for el in elements:
                href = el.get('href')
                if href:
                    links.add(urljoin(base_url, href))
        content_areas = soup.select('main, .content, .posts, .articles, article')
        for area in content_areas:
            area_links = area.find_all('a', href=True)
            for link in area_links:
                href = link.get('href')
                if href and self.is_article_link(href):
                    links.add(urljoin(base_url, href))
        return list(links)

    def is_article_link(self, href):
        skip_patterns = ['#', 'mailto:', 'tel:', 'javascript:', '/tag/', '/category/', '/author/']
        if any(pattern in href for pattern in skip_patterns):
            return False
        include_patterns = ['/blog/', '/post/', '/article/', '/tutorial/', '/guide/', '/learn/', '/interview', '/experience']
        return any(pattern in href for pattern in include_patterns)

    def handle_infinite_scroll(self, max_scrolls=5):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            try:
                load_more = self.driver.find_element(By.CSS_SELECTOR, ".load-more, .show-more, .more-posts, .next-page")
                if load_more.is_displayed():
                    load_more.click()
                    time.sleep(3)
            except:
                pass
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1

    def handle_hash_navigation(self, url):
        self.driver.get(url)
        time.sleep(3)
        if '#' in url:
            hash_part = url.split('#')[1]
            try:
                nav_element = self.driver.find_element(By.CSS_SELECTOR, f'[href="#{hash_part}"], [data-target="#{hash_part}"], .{hash_part}')
                nav_element.click()
                time.sleep(3)
            except:
                pass
            self.driver.execute_script(f'''
                var element = document.getElementById('{hash_part}') || 
                             document.querySelector('.{hash_part}') ||
                             document.querySelector('[data-section="{hash_part}"]');
                if (element) {{
                    element.scrollIntoView();
                    element.style.display = 'block';
                }}
            ''')
            time.sleep(2)
        return self.driver.page_source

    def extract_content(self, url, page_source):
        try:
            import trafilatura
            content = trafilatura.extract(page_source, include_links=True, include_images=False)
            if content and len(content) > 200:
                return self.clean_content(content)
        except:
            pass
        try:
            from newspaper import Article
            article = Article(url)
            article.set_html(page_source)
            article.parse()
            if article.text and len(article.text) > 200:
                return self.clean_content(article.text)
        except:
            pass
        soup = BeautifulSoup(page_source, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', '.sidebar', '.navigation']):
            element.decompose()
        content_selectors = [
            'article .content, article .post-content, article .entry-content',
            '.post-body, .post-content, .entry-content',
            '.article-content, .tutorial-content, .guide-content',
            'main article, main .content',
            '[role="main"] article'
        ]
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(strip=True)
                if len(text) > 200:
                    return self.clean_content(text)
        return self.get_largest_text_block(soup)

    def clean_content(self, text):
        text = re.sub(r'\s+', ' ', text)
        unwanted_patterns = [
            r'Share this:.*$',
            r'Like this:.*$'
        ]
        for pat in unwanted_patterns:
            text = re.sub(pat, '', text, flags=re.MULTILINE)
        return text.strip()

    def get_largest_text_block(self, soup):
        paragraphs = soup.find_all('p')
        if not paragraphs:
            return ''
        largest = max(paragraphs, key=lambda p: len(p.text))
        return self.clean_content(largest.get_text())

    def close(self):
        self.driver.quit() 