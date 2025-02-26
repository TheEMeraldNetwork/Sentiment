"""
API provider configuration file.
Contains API keys and settings for external data providers.
"""

import os
from pathlib import Path
import json

def load_api_keys() -> dict:
    """Load API keys from config file or environment variables"""
    # Try to load from config file first
    config_path = Path(__file__).parent / 'api_keys.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    # Fallback to environment variables
    return {
        'FINNHUB_KEY': os.getenv('FINNHUB_KEY', 'cu0qch9r01qjiermd96gcu0qch9r01qjiermd970')
    }

# Load API keys
api_keys = load_api_keys()

# Export API keys
FINNHUB_KEY = api_keys.get('FINNHUB_KEY', '')

# Validate required keys
if not FINNHUB_KEY:
    raise ValueError(
        "FINNHUB_KEY not found. Please either:\n"
        "1. Create utils/config/api_keys.json with {'FINNHUB_KEY': 'your-key'}\n"
        "2. Set FINNHUB_KEY environment variable"
    )

# Financial Data API Providers Configuration

# News and Market Data Providers
NEWSAPI_KEY = "c6a86bf7051d46059a2d316e88ac2d4b"

# Dictionary of API providers and their keys
API_KEYS = {
    "news_api": NEWSAPI_KEY,
    "finnhub": FINNHUB_KEY
}

# API Rate Limits (requests per minute)
RATE_LIMITS = {
    "news_api": 100,
    "finnhub": 60
} 