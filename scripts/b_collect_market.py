"""
Market data collection module that fetches and processes analyst consensus data from Yahoo Finance.
Generates timestamped outputs for market data and analyst forecasts.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
from pathlib import Path
import sys
import os
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import shutil
import time
import random

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers, get_yfinance_ticker

class MarketDataCollector:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Create archive directory
        self.archive_dir = self.results_dir / 'archive' / 'market'
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def get_market_data(self, ticker: str, max_retries: int = 3) -> Dict:
        """Get market data and analyst consensus from Yahoo Finance with retries"""
        for attempt in range(max_retries):
            try:
                # Add random delay between 2-5 seconds
                time.sleep(2 + random.random() * 3)
                
                # Get proper yfinance ticker format
                yf_ticker = get_yfinance_ticker(ticker)
                stock = yf.Ticker(yf_ticker)
                
                # Get analyst recommendations and price targets
                info = stock.info
                if not info:
                    raise ValueError(f"No data returned from Yahoo Finance for {ticker}")
                
                # Get current price with fallback to regular market price
                current_price = info.get('currentPrice')
                if current_price is None:
                    current_price = info.get('regularMarketPrice')
                    if current_price is None:
                        self.logger.warning(f"No price data available for {ticker}")
                
                target_median = info.get('targetMedianPrice')
                if target_median is None:
                    self.logger.warning(f"No target price available for {ticker}")
                
                # Get historical data for 1-week return calculation
                try:
                    hist = stock.history(period="5d")  # Using 5d for a week of trading days
                    week_return = None
                    if len(hist) >= 2:  # Need at least 2 days for return calculation
                        week_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                    else:
                        self.logger.warning(f"Insufficient historical data for {ticker}")
                except Exception as e:
                    self.logger.warning(f"Could not fetch historical data for {ticker}: {e}")
                    week_return = None
                
                # Return market data
                market_data = {
                    'ticker': ticker,
                    'company': self.mappings[ticker]['name'],
                    'current_price': current_price,
                    'target_median': target_median,
                    'target_mean': info.get('targetMeanPrice'),
                    'target_low': info.get('targetLowPrice'),
                    'target_high': info.get('targetHighPrice'),
                    'num_analysts': info.get('numberOfAnalystOpinions', 0),
                    'recommendation': info.get('recommendationKey', ''),
                    'week_return': week_return,
                    'volume': info.get('volume', 0),
                    'avg_volume': info.get('averageVolume', 0),
                    'market_cap': info.get('marketCap', 0),
                    'beta': info.get('beta'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Calculate potential return only if both values exist
                if market_data['current_price'] and market_data['target_median']:
                    market_data['potential_return'] = (
                        (market_data['target_median'] - market_data['current_price']) 
                        / market_data['current_price'] * 100
                    )
                else:
                    market_data['potential_return'] = None
                    
                return market_data
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                if attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 5  # Exponential backoff
                    self.logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"All attempts failed for {ticker}")
        
        # Return empty data if all attempts fail
        return {
            'ticker': ticker,
            'company': self.mappings[ticker]['name'],
            'current_price': None,
            'target_median': None,
            'target_mean': None,
            'target_low': None,
            'target_high': None,
            'num_analysts': 0,
            'recommendation': '',
            'potential_return': None,
            'week_return': None,
            'volume': 0,
            'avg_volume': 0,
            'market_cap': 0,
            'beta': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def collect_market_data(self) -> None:
        """Collect market data for all stocks"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = []
        
        # Process stocks in parallel with fewer workers to avoid rate limits
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_ticker = {
                executor.submit(self.get_market_data, ticker): ticker
                for ticker in self.mappings.keys()
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {ticker}: {e}")
                    # Add empty result to maintain ticker list
                    results.append({
                        'ticker': ticker,
                        'company': self.mappings[ticker]['name'],
                        'current_price': None,
                        'target_median': None,
                        'target_mean': None,
                        'target_low': None,
                        'target_high': None,
                        'num_analysts': 0,
                        'recommendation': '',
                        'potential_return': None,
                        'week_return': None,
                        'volume': 0,
                        'avg_volume': 0,
                        'market_cap': 0,
                        'beta': None,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Create DataFrame with all tickers
        results_df = pd.DataFrame(results)
        
        # Sort by ticker to maintain consistent order
        results_df.sort_values('ticker', inplace=True)
        
        # Save results with timestamp
        output_path = self.results_dir / f"market_data_{timestamp}.csv"
        results_df.to_csv(output_path, index=False)
        
        # Create symlink for latest file
        latest_path = self.results_dir / "market_data_latest.csv"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(output_path.name)
        
        # Archive previous files
        for file in self.results_dir.glob("market_data_2*.csv"):
            if timestamp not in str(file):
                archive_path = self.archive_dir / file.name
                shutil.move(str(file), str(archive_path))
        
        # Print summary of valid data
        valid_data = results_df[results_df['target_median'].notna()]
        self.logger.info("\nMarket Data Summary:")
        self.logger.info(f"Total companies: {len(results_df)}")
        self.logger.info(f"Companies with analyst data: {len(valid_data)}")
        self.logger.info(f"Companies without data: {len(results_df) - len(valid_data)}")
        
        if len(valid_data) > 0:
            self.logger.info("\nMarket Statistics (for companies with data):")
            self.logger.info(f"Average target return: {valid_data['potential_return'].mean():.2f}%")
            self.logger.info(f"Return range: {valid_data['potential_return'].min():.2f}% to {valid_data['potential_return'].max():.2f}%")
            self.logger.info(f"Average analyst count: {valid_data['num_analysts'].mean():.1f}")
            self.logger.info(f"Average 1-week return: {valid_data['week_return'].mean():.2f}%")
        
        self.logger.info(f"\nResults saved to: {output_path}")
        self.logger.info(f"Archive directory: {self.archive_dir}")

def main():
    """Main function to collect market data"""
    print("\nStarting market data collection...")
    collector = MarketDataCollector()
    collector.collect_market_data()
    print("\nMarket data collection complete!")

if __name__ == "__main__":
    main() 