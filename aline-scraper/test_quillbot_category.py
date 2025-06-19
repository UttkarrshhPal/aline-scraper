#!/usr/bin/env python3

import requests
import json
import time

def test_quillbot_category_navigation():
    """Test QuillBot category navigation and blog post extraction."""
    
    test_url = "https://quillbot.com/blog"
    
    print(f"Testing QuillBot category navigation: {test_url}")
    
    # Make API request with correct format
    response = requests.post(
        "http://localhost:8000/scrape",
        json={
            "team_id": "test123",
            "user_id": "test_user",
            "sources": [
                {
                    "type": "blog",
                    "url": test_url
                }
            ]
        }
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"Job ID: {job_id}")
        
        # Wait longer for category navigation processing
        time.sleep(15)
        
        # Get results
        results_response = requests.get(f"http://localhost:8000/scrape/{job_id}/results")
        print(f"Results status: {results_response.status_code}")
        
        if results_response.status_code == 200:
            results = results_response.json()
            items = results.get("items", [])
            print(f"Found {len(items)} items")
            
            for i, item in enumerate(items[:5]):  # Show first 5
                print(f"\nItem {i+1}:")
                print(f"  Title: {item.get('title', 'N/A')}")
                print(f"  Content type: {item.get('content_type', 'N/A')}")
                print(f"  Source URL: {item.get('source_url', 'N/A')}")
                content = item.get('content', '')
                print(f"  Content preview: {content[:200]}...")
        else:
            print(f"Error getting results: {results_response.text}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_quillbot_category_navigation() 