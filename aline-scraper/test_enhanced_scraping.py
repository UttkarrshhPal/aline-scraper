#!/usr/bin/env python3

import logging
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from selenium.common.exceptions import WebDriverException
from app.scraping.dynamic_scraper import DynamicScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraping.log')
    ]
)
logger = logging.getLogger(__name__)

# Create debug directory if it doesn't exist
debug_dir = Path("debug_output")
debug_dir.mkdir(exist_ok=True)

def initialize_scraper() -> Optional[DynamicScraper]:
    """Try to initialize the scraper with different configurations"""
    for headless in [False, True]:
        try:
            scraper = DynamicScraper(headless=headless)
            logger.info(f"Successfully initialized scraper with headless={headless}")
            return scraper
        except Exception as e:
            logger.error(f"Failed to initialize scraper with headless={headless}: {e}")
    return None

def test_enhanced_scraping() -> None:
    """Test scraping with enhanced features for all target websites"""
    scraper: Optional[DynamicScraper] = None
    results: Dict[str, Any] = {}
    
    try:
        urls_to_test = [
            "https://realpython.com/",
            "https://interviewing.io/learn#interview-guides",
            "https://interviewing.io/topics#companies",
            "https://www.geeksforgeeks.org/tag/interview-experiences/",
            "https://nilmamano.com/blog/category/dsa",
            "https://overreacted.io/"
        ]
        
        # Initialize the scraper
        scraper = initialize_scraper()
        if not scraper:
            raise RuntimeError("Failed to initialize scraper with any configuration")
        
        for url in urls_to_test:
            logger.info(f"\nTesting URL: {url}")
            page_source = None
            
            # Get page with retries
            success = False
            for attempt in range(3):
                try:
                    page_source = scraper.get_page_with_js(url)
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                    if attempt < 2:
                        time.sleep(5 * (attempt + 1))
                        # Try to clear browser state
                        try:
                            if scraper and scraper.driver:
                                scraper.driver.delete_all_cookies()
                        except:
                            pass
                        continue
            
            if not success:
                logger.error(f"Failed to process {url} after all retries")
                continue
            
            if not page_source:
                logger.error(f"Failed to get page source for {url}")
                continue
            
            # Save page source for debugging
            site_name = url.split('/')[2].replace('.', '_')
            debug_file = debug_dir / f"{site_name}_debug.html"
            debug_file.write_text(page_source, encoding='utf-8')
            logger.info(f"Saved page source to {debug_file}")
            
            # Extract and save links
            try:
                links = scraper.extract_article_links(url, page_source)
                logger.info(f"Found {len(links)} links on {url}:")
                for link in links:
                    logger.info(f"- {link}")
                
                results[url] = {
                    "total_links": len(links),
                    "links": links,
                    "samples": []
                }
                
                # Test content extraction from first 2 articles if available
                for i, link in enumerate(links[:2]):
                    try:
                        logger.info(f"\nTesting content extraction from: {link}")
                        article_source = scraper.get_page_with_js(link)
                        
                        # Save raw article source
                        article_debug = debug_dir / f"{site_name}_article_{i+1}_debug.html"
                        article_debug.write_text(article_source, encoding='utf-8')
                        
                        # Extract content
                        content = None
                        if article_source:
                            from app.scraping.content_cleaner import ContentCleaner
                            content = ContentCleaner.clean_html(article_source, link)
                        
                        if content:
                            logger.info("\nExtracted content preview:")
                            logger.info(f"{content[:500]}...")
                            
                            # Save cleaned content
                            content_file = debug_dir / f"{site_name}_article_{i+1}_content.txt"
                            content_file.write_text(content, encoding='utf-8')
                            
                            results[url]["samples"].append({
                                "url": link,
                                "content_length": len(content),
                                "content_preview": content[:500]
                            })
                        else:
                            logger.warning(f"No content extracted from article: {link}")
                            
                    except Exception as e:
                        logger.error(f"Error extracting article content: {str(e)}")
                
                # Save results for this site
                results_file = debug_dir / f"{site_name}_results.json"
                results_file.write_text(
                    json.dumps(results[url], indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
            except Exception as e:
                logger.error(f"Error processing links for {url}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise
        
    finally:
        # Save overall results
        try:
            if results:
                with open(debug_dir / "overall_results.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving overall results: {str(e)}")
            
        # Close the browser
        if scraper:
            try:
                scraper.close()
            except:
                pass

if __name__ == "__main__":
    test_enhanced_scraping()