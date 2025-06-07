"""
Quick test script to verify Finnhub API functionality.
"""

import finnhub
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json

def test_finnhub_api():
    # Load API key from config
    config_path = Path('utils/config/api_keys.json')
    with open(config_path) as f:
        config = json.load(f)
        api_key = config['FINNHUB_KEY']
    
    print(f"\nTesting Finnhub API...")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    # Initialize client
    client = finnhub.Client(api_key=api_key)
    
    try:
        # Test 1: Basic quote data
        print("\nTest 1: Fetching GOOGL quote...")
        quote = client.quote('GOOGL')
        print(f"Quote data: {quote}")
        
        # Test 2: Company news
        print("\nTest 2: Fetching GOOGL news (last 7 days)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        news = client.company_news(
            'GOOGL',
            _from=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"Found {len(news)} news articles")
        
        # Print first 3 articles
        for i, article in enumerate(news[:3]):
            print(f"\nArticle {i+1}:")
            print(f"Title: {article.get('headline', 'N/A')}")
            print(f"Date: {datetime.fromtimestamp(article.get('datetime', 0))}")
            print(f"Source: {article.get('source', 'N/A')}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
        
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_finnhub_api() 