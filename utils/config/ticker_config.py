"""
Configuration file for ticker mappings and exchange information.
Maps original tickers to their variants across different exchanges.
"""

from typing import Dict, List
import json
from pathlib import Path

# Exchange suffixes for different geographies
EXCHANGE_SUFFIXES = {
    'US': '',  # No suffix for US stocks
    'CA': '.TO',  # Toronto
    'UK': '.L',   # London
    'FR': '.PA',  # Paris
    'DE': '.DE',  # Germany
    'CH': '.SW',  # Switzerland
    'IT': '.MI',  # Milan
    'ES': '.MC',  # Madrid
    'NL': '.AS',  # Amsterdam
    'BE': '.BR',  # Brussels
    'SE': '.ST',  # Stockholm
    'NO': '.OL',  # Oslo
    'DK': '.CO',  # Copenhagen
    'FI': '.HE',  # Helsinki
    'JP': '.T',   # Tokyo
    'HK': '.HK',  # Hong Kong
    'AU': '.AX',  # Australia
    'BR': '.SA',  # Sao Paulo
}

def get_ticker_variants(ticker: str) -> List[str]:
    """
    Generate all possible variants of a ticker symbol.
    Args:
        ticker: Original ticker from master list
    Returns:
        List of possible ticker variants for different exchanges
    """
    variants = [
        ticker,  # Original
        ticker.split('.')[0],  # Base ticker without any suffix
        f"{ticker.split('.')[0]}.US",  # Explicit US suffix
    ]
    
    # Add exchange-specific variants
    base_ticker = ticker.split('.')[0]
    variants.extend([f"{base_ticker}{suffix}" for suffix in EXCHANGE_SUFFIXES.values()])
    
    return list(set(variants))  # Remove duplicates

def get_finnhub_ticker(ticker: str) -> str:
    """
    Get the appropriate ticker format for Finnhub API.
    Finnhub prefers SYMBOL-EXCHANGE format for non-US stocks.
    """
    if '.' not in ticker:
        return ticker  # US stock
    
    base, exchange = ticker.split('.')
    exchange_map = {
        'TO': 'TSX',
        'L': 'LSE',
        'PA': 'PARIS',
        'DE': 'XETRA',
        'SW': 'SWX',
        'MI': 'MIL',
        'MC': 'BME',
        'AS': 'AMS',
        'BR': 'BRU',
        'ST': 'STO',
        'OL': 'OSL',
        'CO': 'CPH',
        'HE': 'HEL',
        'T': 'TSE',
        'HK': 'HKEX',
        'AX': 'ASX',
        'SA': 'BOVESPA'
    }
    
    if exchange in exchange_map:
        return f"{base}-{exchange_map[exchange]}"
    return ticker

def get_yfinance_ticker(ticker: str) -> str:
    """
    Convert ticker to Yahoo Finance format if needed.
    Some tickers need special handling for Yahoo Finance.
    """
    # Special cases for Yahoo Finance
    yf_mappings = {
        'BRK.A': 'BRK-A',
        'BRK.B': 'BRK-B',
        'BF.A': 'BF-A',
        'BF.B': 'BF-B'
    }
    return yf_mappings.get(ticker, ticker)

def load_master_tickers() -> Dict[str, Dict[str, str]]:
    """
    Load master ticker list with company information.
    Returns a dictionary mapping ticker to company info.
    """
    # Try to load from config file
    config_path = Path(__file__).parent / 'tickers.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    # Default tickers if no config file exists
    return {
        'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
        'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology'},
        'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
        'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical'},
        'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
        'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
        'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical'},
        'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
        'V': {'name': 'Visa Inc.', 'sector': 'Financial Services'},
        'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare'}
    } 