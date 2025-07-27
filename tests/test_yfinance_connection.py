#!/usr/bin/env python3
"""Test script to verify yfinance functionality"""

import yfinance as yf
import time

def test_single_symbol(symbol):
    """Test fetching data for a single symbol"""
    try:
        print(f"Testing {symbol}...")
        ticker = yf.Ticker(symbol)
        
        # Try to get basic price data
        hist = ticker.history(period="1mo")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            print(f"  ✅ {symbol}: ${current_price:.2f}")
            return True
        else:
            print(f"  ❌ {symbol}: No price data")
            return False
            
    except Exception as e:
        print(f"  ⚠️ {symbol}: {str(e)}")
        return False

def main():
    """Test a few portfolio symbols"""
    # Test symbols from your portfolio
    test_symbols = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN']  # Known good symbols
    portfolio_symbols = ['CCJ', 'CLS', 'ASML', 'CVNA', 'LFST']  # Your actual symbols
    
    print("Testing known good symbols:")
    good_count = 0
    for symbol in test_symbols:
        if test_single_symbol(symbol):
            good_count += 1
        time.sleep(1)  # Small delay
    
    print(f"\nKnown symbols success rate: {good_count}/{len(test_symbols)}")
    
    print("\nTesting your portfolio symbols:")
    portfolio_count = 0
    for symbol in portfolio_symbols:
        if test_single_symbol(symbol):
            portfolio_count += 1
        time.sleep(1)  # Small delay
    
    print(f"Portfolio symbols success rate: {portfolio_count}/{len(portfolio_symbols)}")

if __name__ == "__main__":
    main() 