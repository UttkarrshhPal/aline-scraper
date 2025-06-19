# CURSOR INSTRUCTIONS: Fix Dynamic Scraping for Challenging URLs

## Problem Statement
Current scraper fails on these URLs. You MUST make it work for ALL of them:
- https://realpython.com/
- https://interviewing.io/learn#interview-guides 
- https://interviewing.io/topics#companies
- https://www.geeksforgeeks.org/tag/interview-experiences/
- https://nilmamano.com/blog/category/dsa
- https://overreacted.io/

## ROOT CAUSE ANALYSIS
The current code likely fails because:
1. **No JavaScript Support**: Using requests/BeautifulSoup only
2. **Wrong Selectors**: Hardcoded selectors that don't match these sites
3. **No Dynamic Loading**: Not waiting for content to load
4. **Missing Anti-Detection**: Sites block basic scrapers

## MANDATORY FIXES

### 1. IMPLEMENT SELENIUM-FIRST ARCHITECTURE

**Replace the current scraper base class with this approach:**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time

class DynamicScraper:
    def __init__(self):
        # Use undetected Chrome to bypass bot detection
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
    
    def get_page_with_js(self, url):
        """Load page and wait for JavaScript content"""
        self.driver.get(url)
        
        # Wait for body to load
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        return self.driver.page_source
```

### 2. IMPLEMENT SITE-SPECIFIC LINK EXTRACTION

**Create this exact function to find article links dynamically:**

```python
def extract_article_links(self, base_url, page_source):
    """Extract article links using multiple strategies"""
    soup = BeautifulSoup(page_source, 'html.parser')
    links = set()
    
    # Strategy 1: Common article link patterns
    patterns = [
        'a[href*="/blog/"]',
        'a[href*="/post/"]', 
        'a[href*="/article/"]',
        'a[href*="/tutorial/"]',
        'a[href*="/guide/"]',
        'a[href*="/learn/"]',
        'a[href*="/interview"]',
        'a[href*="/experience"]',
        'a[href*="/dsa"]'
    ]
    
    for pattern in patterns:
        elements = soup.select(pattern)
        for el in elements:
            href = el.get('href')
            if href:
                links.add(urljoin(base_url, href))
    
    # Strategy 2: Find links in main content areas
    content_areas = soup.select('main, .content, .posts, .articles, article')
    for area in content_areas:
        area_links = area.find_all('a', href=True)
        for link in area_links:
            href = link.get('href')
            if href and self.is_article_link(href):
                links.add(urljoin(base_url, href))
    
    return list(links)

def is_article_link(self, href):
    """Determine if a link points to an article"""
    # Skip navigation, external links, etc.
    skip_patterns = ['#', 'mailto:', 'tel:', 'javascript:', '/tag/', '/category/', '/author/']
    if any(pattern in href for pattern in skip_patterns):
        return False
    
    # Include patterns that likely point to articles
    include_patterns = ['/blog/', '/post/', '/article/', '/tutorial/', '/guide/', '/learn/', '/interview', '/experience']
    return any(pattern in href for pattern in include_patterns)
```

### 3. HANDLE INFINITE SCROLL AND DYNAMIC LOADING

**Add this function to handle sites like GeeksforGeeks:**

```python
def handle_infinite_scroll(self, max_scrolls=5):
    """Handle infinite scroll to load more content"""
    last_height = self.driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    
    while scrolls < max_scrolls:
        # Scroll to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(3)
        
        # Check for "Load More" buttons
        try:
            load_more = self.driver.find_element(By.CSS_SELECTOR, 
                ".load-more, .show-more, .more-posts, .next-page")
            if load_more.is_displayed():
                load_more.click()
                time.sleep(3)
        except:
            pass
        
        # Check if new content loaded
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
            
        last_height = new_height
        scrolls += 1
```

### 4. IMPLEMENT HASH NAVIGATION FOR INTERVIEWING.IO

**Add this specific handler for URLs with hash fragments:**

```python
def handle_hash_navigation(self, url):
    """Handle URLs with hash fragments like interviewing.io/learn#interview-guides"""
    self.driver.get(url)
    
    # Wait for initial page load
    time.sleep(3)
    
    # If URL has hash, try to trigger that section
    if '#' in url:
        hash_part = url.split('#')[1]
        
        # Try to click on navigation that matches the hash
        try:
            nav_element = self.driver.find_element(By.CSS_SELECTOR, 
                f'[href="#{hash_part}"], [data-target="#{hash_part}"], .{hash_part}')
            nav_element.click()
            time.sleep(3)
        except:
            pass
        
        # Execute JavaScript to show the target section
        self.driver.execute_script(f"""
            var element = document.getElementById('{hash_part}') || 
                         document.querySelector('.{hash_part}') ||
                         document.querySelector('[data-section="{hash_part}"]');
            if (element) {{
                element.scrollIntoView();
                element.style.display = 'block';
            }}
        """)
        time.sleep(2)
    
    return self.driver.page_source
```

### 5. ROBUST CONTENT EXTRACTION

**Replace your content extraction with this multi-strategy approach:**

```python
def extract_content(self, url, page_source):
    """Extract article content using multiple strategies"""
    
    # Strategy 1: Use trafilatura (best for article extraction)
    try:
        import trafilatura
        content = trafilatura.extract(page_source, include_links=True, include_images=False)
        if content and len(content) > 200:
            return self.clean_content(content)
    except:
        pass
    
    # Strategy 2: Use newspaper3k
    try:
        from newspaper import Article
        article = Article(url)
        article.set_html(page_source)
        article.parse()
        if article.text and len(article.text) > 200:
            return self.clean_content(article.text)
    except:
        pass
    
    # Strategy 3: Manual extraction with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', '.sidebar', '.navigation']):
        element.decompose()
    
    # Try common content selectors
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
    
    # Fallback: get largest text block
    return self.get_largest_text_block(soup)

def clean_content(self, text):
    """Clean extracted content"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        r'Share this:.*$',
        r'Like this:.*$',
        r'Related Posts.*$',
        r'Tags:.*$',
        r'Categories:.*$'
    ]
    
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()
```

### 6. SITE-SPECIFIC CONFIGURATIONS

**Create this configuration system:**   

```python
SITE_CONFIGS = {
    'realpython.com': {
        'requires_js': True,
        'link_selectors': ['a[href*="/blog/"]', 'a[href*="/tutorials/"]'],
        'content_selectors': ['.tutorial-content', '.article-body'],
        'infinite_scroll': False,
        'wait_time': 5
    },
    
    'interviewing.io': {
        'requires_js': True,
        'hash_navigation': True,
        'link_selectors': ['a[href*="/guides/"]', 'a[href*="/companies/"]'],
        'content_selectors': ['.guide-content', '.interview-content'],
        'wait_time': 5
    },
    
    'geeksforgeeks.org': {
        'requires_js': True,
        'infinite_scroll': True,
        'max_scrolls': 10,
        'link_selectors': ['a[href*="/interview-experiences/"]'],
        'content_selectors': ['.text', '.article-content'],
        'wait_time': 3
    },
    
    'nilmamano.com': {
        'requires_js': False,
        'link_selectors': ['a[href*="/blog/"]'],
        'content_selectors': ['.post-content', '.entry-content'],
        'category_filter': 'dsa'
    },
    
    'overreacted.io': {
        'requires_js': True,
        'spa_navigation': True,
        'link_selectors': ['a[href^="/"]'],  # All internal links
        'content_selectors': ['.post', 'article'],
        'wait_time': 5
    }
}
```

### 7. MAIN SCRAPING WORKFLOW

**Implement this exact scraping workflow:**

```python
def scrape_site(self, base_url):
    """Main scraping workflow that adapts to each site"""
    domain = urlparse(base_url).netloc.replace('www.', '')
    config = SITE_CONFIGS.get(domain, {})
    
    results = []
    
    try:
        # Step 1: Load main page
        if config.get('hash_navigation'):
            page_source = self.handle_hash_navigation(base_url)
        else:
            page_source = self.get_page_with_js(base_url)
        
        # Step 2: Handle infinite scroll if needed
        if config.get('infinite_scroll'):
            self.handle_infinite_scroll(config.get('max_scrolls', 5))
            page_source = self.driver.page_source
        
        # Step 3: Extract article links
        article_links = self.extract_article_links(base_url, page_source)
        
        print(f"Found {len(article_links)} article links for {domain}")
        
        # Step 4: Scrape each article
        for link in article_links[:20]:  # Limit for testing
            try:
                article_source = self.get_page_with_js(link)
                content = self.extract_content(link, article_source)
                
                if content and len(content) > 100:
                    results.append({
                        'title': self.extract_title(article_source),
                        'content': content,
                        'source_url': link,
                        'content_type': 'blog'
                    })
                    
            except Exception as e:
                print(f"Failed to scrape {link}: {e}")
                continue
                
    except Exception as e:
        print(f"Failed to scrape {base_url}: {e}")
    
    finally:
        self.driver.quit()
    
    return results
```

## TESTING REQUIREMENTS

**Test each URL individually with this code:**

```python
def test_individual_sites():
    urls = [
        'https://realpython.com/',
        'https://interviewing.io/learn#interview-guides',
        'https://interviewing.io/topics#companies', 
        'https://www.geeksforgeeks.org/tag/interview-experiences/',
        'https://nilmamano.com/blog/category/dsa',
        'https://overreacted.io/'
    ]
    
    for url in urls:
        print(f"\n=== Testing {url} ===")
        scraper = DynamicScraper()
        results = scraper.scrape_site(url)
        print(f"Extracted {len(results)} articles")
        
        if results:
            print("Sample content:")
            print(results[0]['content'][:200] + "...")
        else:
            print("❌ FAILED - No content extracted")
```

## ERROR HANDLING REQUIREMENTS

**Add comprehensive error handling:**

```python
def robust_scrape_with_fallbacks(self, url):
    """Try multiple approaches if first one fails"""
    
    # Attempt 1: Full JavaScript with undetected Chrome
    try:
        return self.scrape_with_selenium(url)
    except Exception as e1:
        print(f"Selenium failed: {e1}")
    
    # Attempt 2: Playwright (better for SPAs)
    try:
        return self.scrape_with_playwright(url)
    except Exception as e2:
        print(f"Playwright failed: {e2}")
    
    # Attempt 3: Basic requests (fallback)
    try:
        return self.scrape_with_requests(url)
    except Exception as e3:
        print(f"Requests failed: {e3}")
    
    return []
```

## SUCCESS CRITERIA

You MUST achieve:
- ✅ Each URL returns at least 5 articles with content > 100 words
- ✅ Content is properly cleaned markdown
- ✅ No 403/blocked errors
- ✅ Handles dynamic loading correctly
- ✅ Works consistently on repeated runs

## DEBUGGING STEPS

If still failing:
1. **Print page source length** to verify content loads
2. **Take screenshots** to see what the browser sees
3. **Print found links** to verify link extraction
4. **Test individual selectors** in browser dev tools
5. **Check for rate limiting** with delays between requests

Make these changes and test each URL individually before combining them.