"""
External forecast module that fetches and processes analyst consensus data from Yahoo Finance.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
import sys
import os
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers, get_yfinance_ticker

class AnalystConsensus:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def get_analyst_data(self, ticker: str) -> Optional[Dict]:
        """Get analyst consensus data from Yahoo Finance"""
        try:
            # Get proper yfinance ticker format
            yf_ticker = get_yfinance_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            
            # Get analyst recommendations and price targets
            info = stock.info
            
            consensus_data = {
                'ticker': ticker,
                'company': self.mappings[ticker],
                'current_price': info.get('currentPrice'),
                'target_median': info.get('targetMedianPrice'),
                'target_mean': info.get('targetMeanPrice'),
                'target_low': info.get('targetLowPrice'),
                'target_high': info.get('targetHighPrice'),
                'num_analysts': info.get('numberOfAnalystOpinions', 0),
                'recommendation': info.get('recommendationKey', 'N/A'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Calculate potential return
            if consensus_data['current_price'] and consensus_data['target_median']:
                consensus_data['potential_return'] = (
                    (consensus_data['target_median'] - consensus_data['current_price']) 
                    / consensus_data['current_price'] * 100
                )
            else:
                consensus_data['potential_return'] = None
                
            return consensus_data
            
        except Exception as e:
            self.logger.error(f"Error getting analyst data for {ticker}: {e}")
            return None
    
    def generate_consensus_report(self) -> None:
        """Generate analyst consensus report for all stocks"""
        results = []
        failed_tickers = []
        
        # Process stocks in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(self.get_analyst_data, ticker): ticker
                for ticker in self.mappings.keys()
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        failed_tickers.append(ticker)
                except Exception as e:
                    self.logger.error(f"Error processing {ticker}: {e}")
                    failed_tickers.append(ticker)
        
        if results:
            # Create DataFrame
            results_df = pd.DataFrame(results)
            
            # Sort by potential return
            results_df.sort_values('potential_return', ascending=False, inplace=True)
            
            # Save results
            output_path = self.results_dir / "c_analyst_consensus.csv"
            results_df.to_csv(output_path, index=False)
            
            # Print summary
            self.logger.info("\nAnalyst Consensus Summary:")
            self.logger.info(f"Companies processed: {len(results_df)}")
            self.logger.info(f"Failed tickers: {len(failed_tickers)}")
            if failed_tickers:
                self.logger.info(f"Failed tickers: {', '.join(failed_tickers)}")
            
            self.logger.info("\nConsensus Statistics:")
            self.logger.info(f"Average target return: {results_df['potential_return'].mean():.2f}%")
            self.logger.info(f"Return range: {results_df['potential_return'].min():.2f}% to {results_df['potential_return'].max():.2f}%")
            self.logger.info(f"Average analyst count: {results_df['num_analysts'].mean():.1f}")
            self.logger.info(f"\nResults saved to: {output_path}")
        else:
            self.logger.error("No results to save")

def main():
    """Main function to generate analyst consensus report"""
    print("\nStarting analyst consensus analysis...")
    consensus = AnalystConsensus()
    consensus.generate_consensus_report()
    print("\nAnalyst consensus analysis complete!")

if __name__ == "__main__":
    main() 