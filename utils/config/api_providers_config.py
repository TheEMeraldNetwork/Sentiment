"""
API provider configuration file.
Contains API keys and settings for external data providers.
"""

import os
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_api_keys() -> dict:
    """Load API keys from config file or environment variables"""
    keys = {
        'FINNHUB_KEY': '',
        'NEWSAPI_KEY': ''
    }
    
    # Try to load from config file first
    config_path = Path(__file__).parent / 'api_keys.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                file_keys = json.load(f)
                keys.update(file_keys)
                logger.info("Loaded API keys from configuration file")
        except Exception as e:
            logger.error(f"Error loading api_keys.json: {e}")
    
    # Override with environment variables if they exist
    env_finnhub = os.getenv('FINNHUB_KEY')
    env_newsapi = os.getenv('NEWSAPI_KEY')
    
    if env_finnhub:
        keys['FINNHUB_KEY'] = env_finnhub
        logger.info("Using Finnhub API key from environment")
    
    if env_newsapi:
        keys['NEWSAPI_KEY'] = env_newsapi
        logger.info("Using NewsAPI key from environment")
    
    return keys

# Load API keys
api_keys = load_api_keys()

# Export API keys
FINNHUB_KEY = api_keys.get('FINNHUB_KEY', '')
NEWSAPI_KEY = api_keys.get('NEWSAPI_KEY', '')

# Validate required keys
if not FINNHUB_KEY:
    raise ValueError(
        "FINNHUB_KEY not found. Please either:\n"
        "1. Create utils/config/api_keys.json with {'FINNHUB_KEY': 'your-key'}\n"
        "2. Set FINNHUB_KEY environment variable"
    )

if not NEWSAPI_KEY:
    raise ValueError(
        "NEWSAPI_KEY not found. Please either:\n"
        "1. Create utils/config/api_keys.json with {'NEWSAPI_KEY': 'your-key'}\n"
        "2. Set NEWSAPI_KEY environment variable"
    )

# API Rate Limits (requests per minute)
RATE_LIMITS = {
    "news_api": 100,
    "finnhub": 60
} 