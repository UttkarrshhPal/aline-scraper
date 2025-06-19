import logging
import json
import time
from pathlib import Path
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

def test_interviewing_io():
    """Test scraping interviewing.io website"""
    scraper = DynamicScraper(headless=True)
    urls_to_test = [
        "https://interviewing.io/blog",
        "https://interviewing.io/learn#interview-guides",
        "https://interviewing.io/topics#companies"
    ]
    
    try:
        for url in urls_to_test:
            logger.info(f"\nTesting URL: {url}")
            page_source = None
            
            # Get page with retries
            for attempt in range(3):
                try:
                    page_source = scraper.get_page_with_js(url)
                    break
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                    if attempt < 2:  # Less than max retries
                        time.sleep(5 * (attempt + 1))  # Exponential backoff
                        continue
                    raise
            
            if not page_source:
                logger.error(f"Failed to get page source for {url}")
                continue
                
            # Save page source for debugging
            debug_file = debug_dir / f"interviewing_io_{url.split('/')[-1].split('#')[0]}_debug.html"
            debug_file.write_text(page_source, encoding='utf-8')
            logger.info(f"Saved page source to {debug_file}")
            
            # Extract and save links
            links = scraper.extract_article_links(url, page_source)
            logger.info(f"Found {len(links)} links on {url}:")
            for link in links:
                logger.info(f"- {link}")
            
            # Save links to JSON for reference
            links_file = debug_dir / f"interviewing_io_{url.split('/')[-1].split('#')[0]}_links.json"
            links_file.write_text(json.dumps(links, indent=2), encoding='utf-8')
            
            # Test content extraction from first article if available
            if links:
                test_url = links[0]
                logger.info(f"\nTesting content extraction from: {test_url}")
                try:
                    article_source = scraper.get_page_with_js(test_url)
                    content = scraper.extract_content(test_url, article_source)
                    
                    # Save article source and content
                    article_debug = debug_dir / f"interviewing_io_article_debug_{test_url.split('/')[-1]}.html"
                    article_debug.write_text(article_source, encoding='utf-8')
                    
                    if content:
                        logger.info("\nExtracted content preview:")
                        logger.info(f"{content[:500]}...")
                        
                        content_file = debug_dir / f"interviewing_io_article_content_{test_url.split('/')[-1]}.txt"
                        content_file.write_text(content, encoding='utf-8')
                    else:
                        logger.warning("No content extracted from article")
                        
                except Exception as e:
                    logger.error(f"Error extracting article content: {str(e)}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
        raise
    finally:
        scraper.close()

if __name__ == "__main__":
    test_interviewing_io()
