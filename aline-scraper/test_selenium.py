#!/usr/bin/env python3
"""
Test script for Selenium support with interviewing.io guide URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraping.guide_scraper import GuideCollectionScraper
import json

def test_guide_scraping():
    """Test guide scraping with Selenium support."""
    
    # Test URLs from the assignment
    test_urls = [
        "https://interviewing.io/topics#companies",
        "https://interviewing.io/learn#interview-guides"
    ]
    
    scraper = GuideCollectionScraper()
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print(f"{'='*60}")
        
        try:
            results = scraper.extract_guides(url)
            print(f"Found {len(results)} guides")
            
            if results:
                print("\nFirst few results:")
                for i, result in enumerate(results[:3]):  # Show first 3
                    print(f"\n{i+1}. {result['title']}")
                    print(f"   URL: {result['source_url']}")
                    print(f"   Content length: {len(result['content'])} chars")
                    print(f"   Content preview: {result['content'][:200]}...")
            else:
                print("No guides found")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_guide_scraping() 