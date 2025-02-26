"""
Configuration file for ticker mappings and exchange information.
Maps original tickers to their variants across different exchanges.
"""

from typing import Dict, List

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
    Get the appropriate ticker format for yfinance API.
    yfinance uses different suffixes for different exchanges.
    """
    return ticker  # yfinance already uses the standard suffixes

# Load and validate tickers from master file
def load_master_tickers() -> Dict[str, Dict]:
    """
    Load tickers from master file and create mapping with variants.
    Returns:
        Dict mapping original ticker to dict with variants and metadata
    """
    import pandas as pd
    
    try:
        df = pd.read_csv('master name ticker.csv', sep=';')
        mappings = {}
        
        for _, row in df.iterrows():
            ticker = row['Ticker']
            if ticker in ['Weighted Average  ', 'Median  ']:
                continue
                
            mappings[ticker] = {
                'name': row['Name'],
                'variants': get_ticker_variants(ticker),
                'finnhub': get_finnhub_ticker(ticker),
                'yfinance': get_yfinance_ticker(ticker)
            }
        
        return mappings
    except Exception as e:
        print(f"Error loading master tickers: {e}")
        return {} 