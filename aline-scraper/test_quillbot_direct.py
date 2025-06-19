#!/usr/bin/env python3

import logging
import sys
from app.scraping.selenium_scraper import SeleniumScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_quillbot():
    """Test QuillBot scraping directly with enhanced Selenium."""
    url = "https://quillbot.com/blog"
    
    print(f"Testing QuillBot scraping: {url}")
    
    # Test with regular Selenium but enhanced anti-detection
    scraper = SeleniumScraper(headless=False, use_undetected=False)  # Non-headless for debugging
    
    try:
        links = scraper.extract_links_with_selenium(
            url, 
            ["a.blog-card", "a[href*='/blog/']", ".blog-post a", "article a", "a[href*='blog']"]
        )
        
        print(f"Found {len(links)} links:")
        for i, link in enumerate(links[:5]):  # Show first 5
            print(f"  {i+1}. {link}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quillbot() 