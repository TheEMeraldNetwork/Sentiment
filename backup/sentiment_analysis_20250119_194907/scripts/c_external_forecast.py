"""
External forecast module that fetches and processes analyst forecasts from various providers.
Combines price targets, recommendations, and earnings forecasts.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
import sys
import os
from typing import Dict, List, Optional, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers, get_yfinance_ticker

class ExternalForecaster:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
    def get_yf_forecasts(self, ticker: str) -> Dict:
        """Get forecasts from Yahoo Finance"""
        try:
            # Get proper yfinance ticker format
            yf_ticker = get_yfinance_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            
            # Get current price
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            # Get analyst recommendations
            try:
                recommendations = stock.recommendations
                if recommendations is not None and not recommendations.empty:
                    recommendations = recommendations.tail(90)  # Last 90 days
            except:
                recommendations = None
            
            # Get analyst price targets using info
            info = stock.info
            targets = {
                'Low': info.get('targetLowPrice'),
                'High': info.get('targetHighPrice'),
                'Mean': info.get('targetMeanPrice'),
                'Median': info.get('targetMedianPrice')
            }
            
            # Get number of analysts
            num_analysts = info.get('numberOfAnalystOpinions', 0)
            
            return {
                'current_price': current_price,
                'recommendations': recommendations,
                'price_targets': targets,
                'num_analysts': num_analysts
            }
        except Exception as e:
            print(f"Error getting Yahoo Finance data for {ticker}: {e}")
            return {}
            
    def process_recommendations(self, recommendations: pd.DataFrame) -> Dict:
        """Process analyst recommendations"""
        if recommendations is None or recommendations.empty:
            return {
                'buy_ratio': None,
                'sell_ratio': None,
                'consensus': 'Unknown',
                'total_analysts': 0,
                'latest_date': None
            }
            
        latest = recommendations.iloc[-1]
        total = sum([
            latest.get('Strong Buy', 0),
            latest.get('Buy', 0),
            latest.get('Hold', 0),
            latest.get('Sell', 0),
            latest.get('Strong Sell', 0)
        ])
        
        if total == 0:
            return {
                'buy_ratio': None,
                'sell_ratio': None,
                'consensus': 'Unknown',
                'total_analysts': 0,
                'latest_date': latest.name
            }
            
        buy_ratio = (latest.get('Strong Buy', 0) + latest.get('Buy', 0)) / total
        sell_ratio = (latest.get('Strong Sell', 0) + latest.get('Sell', 0)) / total
        
        # Determine consensus
        if buy_ratio > 0.6:
            consensus = 'Strong Buy'
        elif buy_ratio > 0.4:
            consensus = 'Buy'
        elif sell_ratio > 0.6:
            consensus = 'Strong Sell'
        elif sell_ratio > 0.4:
            consensus = 'Sell'
        else:
            consensus = 'Hold'
            
        return {
            'buy_ratio': buy_ratio,
            'sell_ratio': sell_ratio,
            'consensus': consensus,
            'total_analysts': total,
            'latest_date': latest.name
        }
        
    def process_price_targets(self, targets: Dict) -> Dict:
        """Process analyst price targets"""
        return {
            'target_low': targets.get('Low', None),
            'target_high': targets.get('High', None),
            'target_mean': targets.get('Mean', None),
            'target_median': targets.get('Median', None)
        }
        
    def process_earnings(self, earnings: Dict) -> Dict:
        """Process earnings forecasts"""
        return {
            'eps_forecast': earnings.get('Avg. Estimate', {}).get('Current Qtr.', None),
            'eps_year': earnings.get('Avg. Estimate', {}).get('Current Year', None),
            'growth_current': earnings.get('Growth', {}).get('Current Qtr.', None),
            'growth_year': earnings.get('Growth', {}).get('Current Year', None)
        }
        
    def process_stock(self, ticker: str, info: Dict) -> Optional[Dict]:
        """Process forecasts for a single stock"""
        try:
            print(f"Processing {ticker}...")
            
            # Get current price for reference
            stock = yf.Ticker(get_yfinance_ticker(ticker))
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            
            # Get all forecasts
            forecasts = self.get_yf_forecasts(ticker)
            if not forecasts:
                return None
                
            # Process each component
            recommendations = self.process_recommendations(forecasts.get('recommendations'))
            targets = self.process_price_targets(forecasts.get('price_targets', {}))
            earnings = self.process_earnings(forecasts.get('earnings_forecasts', {}))
            
            # Calculate potential returns from targets
            if targets['target_mean'] is not None and current_price > 0:
                mean_return = (targets['target_mean'] / current_price - 1) * 100
                high_return = (targets['target_high'] / current_price - 1) * 100
                low_return = (targets['target_low'] / current_price - 1) * 100
            else:
                mean_return = high_return = low_return = None
                
            return {
                'ticker': ticker,
                'company': info['name'],
                'current_price': current_price,
                'forecast_date': datetime.now(),
                # Recommendation data
                'analyst_consensus': recommendations['consensus'],
                'buy_ratio': recommendations['buy_ratio'],
                'sell_ratio': recommendations['sell_ratio'],
                'total_analysts': recommendations['total_analysts'],
                'recommendation_date': recommendations['latest_date'],
                # Target prices and returns
                'target_price_mean': targets['target_mean'],
                'target_price_high': targets['target_high'],
                'target_price_low': targets['target_low'],
                'expected_return': mean_return,
                'high_return': high_return,
                'low_return': low_return,
                # Earnings forecasts
                'eps_forecast_quarter': earnings['eps_forecast'],
                'eps_forecast_year': earnings['eps_year'],
                'growth_quarter': earnings['growth_current'],
                'growth_year': earnings['growth_year']
            }
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            return None
            
    def generate_forecasts(self) -> None:
        """Generate external forecasts for all stocks"""
        results = []
        failed_tickers = []
        
        # Process stocks in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(self.process_stock, ticker, info): ticker
                for ticker, info in self.mappings.items()
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
                    print(f"Error processing {ticker}: {e}")
                    failed_tickers.append(ticker)
        
        if results:
            # Create DataFrame
            results_df = pd.DataFrame(results)
            
            # Sort by expected return
            results_df.sort_values('expected_return', ascending=False, inplace=True)
            
            # Save results
            output_path = self.results_dir / "c_external_forecast.csv"
            results_df.to_csv(output_path, index=False)
            
            # Print summary
            print("\nExternal Forecast Summary:")
            print(f"Companies processed: {len(results_df)}")
            print(f"Failed tickers: {len(failed_tickers)}")
            if failed_tickers:
                print(f"Failed tickers: {', '.join(failed_tickers)}")
            
            print("\nForecast Statistics:")
            print(f"Average expected return: {results_df['expected_return'].mean():.2f}%")
            print(f"Return range: {results_df['expected_return'].min():.2f}% to {results_df['expected_return'].max():.2f}%")
            print(f"Average analyst count: {results_df['total_analysts'].mean():.1f}")
            print(f"\nResults saved to: {output_path}")
        else:
            print("No results to save")

def main():
    """Main function to generate external forecasts"""
    print("\nStarting external forecast generation...")
    forecaster = ExternalForecaster()
    forecaster.generate_forecasts()
    print("\nExternal forecast generation complete!")

if __name__ == "__main__":
    main() 