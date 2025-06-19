#!/usr/bin/env python3
"""
Test script for improved BlogScraper with various blogs via API
"""

import requests
import json

def test_blog_scraping_api():
    """Test blog scraping through the API with improved selectors/fallbacks."""
    
    test_requests = [
        {
            "team_id": "test_team",
            "user_id": "test_user",
            "sources": [
                {
                    "type": "blog",
                    "url": "https://quillbot.com/blog",
                    "file_path": "",
                    "metadata": {
                        "author": "QuillBot",
                        "max_pages": 1,
                        "chunk_size": 1000
                    }
                }
            ]
        },
        {
            "team_id": "test_team",
            "user_id": "test_user",
            "sources": [
                {
                    "type": "blog",
                    "url": "https://realpython.com/",
                    "file_path": "",
                    "metadata": {
                        "author": "Real Python",
                        "max_pages": 1,
                        "chunk_size": 1000
                    }
                }
            ]
        },
        {
            "team_id": "test_team",
            "user_id": "test_user",
            "sources": [
                {
                    "type": "blog",
                    "url": "https://overreacted.io/",
                    "file_path": "",
                    "metadata": {
                        "author": "Dan Abramov",
                        "max_pages": 1,
                        "chunk_size": 1000
                    }
                }
            ]
        }
    ]
    
    base_url = "http://localhost:8000"
    
    for i, request_data in enumerate(test_requests):
        print(f"\n{'='*60}")
        print(f"Test {i+1}: {request_data['sources'][0]['url']}")
        print(f"{'='*60}")
        
        try:
            # Start scraping job
            response = requests.post(f"{base_url}/scrape", json=request_data)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data['job_id']
                print(f"Job ID: {job_id}")
                print(f"Status: {job_data['status']}")
                
                # Wait a moment for processing
                import time
                time.sleep(2)
                
                # Get results
                results_response = requests.get(f"{base_url}/scrape/{job_id}/results")
                print(f"Results status: {results_response.status_code}")
                
                if results_response.status_code == 200:
                    results = results_response.json()
                    items = results.get('items', [])
                    print(f"Found {len(items)} items")
                    
                    if items:
                        print("\nFirst few items:")
                        for j, item in enumerate(items[:2]):  # Show first 2
                            print(f"\n{j+1}. {item['title']}")
                            print(f"   Type: {item['content_type']}")
                            print(f"   URL: {item['source_url']}")
                            print(f"   Content length: {len(item['content'])} chars")
                            print(f"   Preview: {item['content'][:150]}...")
                    else:
                        print("No items found")
                else:
                    print(f"Error getting results: {results_response.text}")
            else:
                print(f"Error starting job: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_blog_scraping_api() 