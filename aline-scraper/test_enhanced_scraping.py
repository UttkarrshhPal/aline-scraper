#!/usr/bin/env python3

import requests
import json
import time

def test_enhanced_scraping():
    """Test enhanced scraping techniques on multiple sites."""
    
    test_sites = [
        {
            "name": "QuillBot Blog",
            "url": "https://quillbot.com/blog",
            "expected_features": ["category_navigation", "cloudflare_protection"]
        },
        {
            "name": "RealPython",
            "url": "https://realpython.com/",
            "expected_features": ["adaptive_scraping", "js_rendering"]
        },
        {
            "name": "Overreacted",
            "url": "https://overreacted.io/",
            "expected_features": ["adaptive_scraping", "js_rendering"]
        }
    ]
    
    for site in test_sites:
        print(f"\n{'='*60}")
        print(f"Testing: {site['name']}")
        print(f"URL: {site['url']}")
        print(f"Expected features: {', '.join(site['expected_features'])}")
        print(f"{'='*60}")
        
        # Make API request
        response = requests.post(
            "http://localhost:8000/scrape",
            json={
                "team_id": "test123",
                "user_id": "test_user",
                "sources": [
                    {
                        "type": "blog",
                        "url": site['url']
                    }
                ]
            }
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print(f"Job ID: {job_id}")
            
            # Wait for processing (longer for category navigation)
            wait_time = 20 if "category_navigation" in site['expected_features'] else 10
            print(f"Waiting {wait_time} seconds for processing...")
            time.sleep(wait_time)
            
            # Get results
            results_response = requests.get(f"http://localhost:8000/scrape/{job_id}/results")
            print(f"Results status: {results_response.status_code}")
            
            if results_response.status_code == 200:
                results = results_response.json()
                items = results.get("items", [])
                print(f"Found {len(items)} items")
                
                if items:
                    print("Sample items:")
                    for i, item in enumerate(items[:3]):  # Show first 3
                        print(f"\n  Item {i+1}:")
                        print(f"    Title: {item.get('title', 'N/A')}")
                        print(f"    Content type: {item.get('content_type', 'N/A')}")
                        print(f"    Source URL: {item.get('source_url', 'N/A')}")
                        content = item.get('content', '')
                        print(f"    Content preview: {content[:150]}...")
                else:
                    print("No items found - this may indicate the site needs further tuning")
            else:
                print(f"Error getting results: {results_response.text}")
        else:
            print(f"Error: {response.text}")
        
        print(f"\n{'-'*60}")

if __name__ == "__main__":
    test_enhanced_scraping() 