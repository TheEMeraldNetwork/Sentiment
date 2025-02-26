# Financial Data API Providers Configuration

# News and Market Data Providers
NEWSAPI_KEY = "c6a86bf7051d46059a2d316e88ac2d4b"
FINNHUB_KEY = "cu0qch9r01qjiermd96gcu0qch9r01qjiermd970"

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