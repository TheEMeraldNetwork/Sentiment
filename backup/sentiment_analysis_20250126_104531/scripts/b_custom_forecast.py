"""
Custom forecast module using Bayesian network analysis.
Combines historical data, sentiment, and market data for return predictions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import os
from scipy import stats

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers, get_yfinance_ticker

class BayesianForecaster:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        self.market_dir = Path('market')
        
    def load_sentiment_data(self) -> pd.DataFrame:
        """Load sentiment analysis results"""
        try:
            sentiment_path = self.results_dir / "a2_sentiment_summary.csv"
            if not sentiment_path.exists():
                print("Warning: Sentiment data not found. Run sentiment analysis first.")
                return pd.DataFrame()
            return pd.read_csv(sentiment_path)
        except Exception as e:
            print(f"Error loading sentiment data: {e}")
            return pd.DataFrame()
            
    def get_historical_data(self, ticker: str, period: str = '2y') -> Optional[pd.DataFrame]:
        """Get historical price data with proper error handling"""
        try:
            # Get proper yfinance ticker format
            yf_ticker = get_yfinance_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                print(f"No historical data found for {ticker}")
                return None
                
            return hist
        except Exception as e:
            print(f"Error getting historical data for {ticker}: {e}")
            return None
            
    def load_market_data(self, ticker: str) -> Dict:
        """Load relevant market and sector data"""
        try:
            # Find sector data files
            sector_files = list(self.market_dir.glob('US_*_tickers.parquet'))
            sector_data = {}
            
            for file in sector_files:
                sector = file.stem.split('_tickers')[0]
                tickers_df = pd.read_parquet(file)
                
                if ticker in tickers_df['ticker'].values:
                    # Load sector fundamentals and ETF data
                    fundamentals = pd.read_parquet(self.market_dir / f"{sector}_fundamentals.parquet")
                    etf_data = pd.read_parquet(self.market_dir / f"{sector}_etf.parquet")
                    
                    sector_data = {
                        'sector': sector,
                        'fundamentals': fundamentals,
                        'etf_data': etf_data
                    }
                    break
            
            # Load economic indicators
            econ_dir = self.market_dir / 'economic_data'
            if econ_dir.exists():
                economic = pd.read_csv(econ_dir / 'combined_indicators.csv')
                sector_data['economic'] = economic
                
            return sector_data
            
        except Exception as e:
            print(f"Error loading market data: {e}")
            return {}
            
    def calculate_bayesian_forecast(
        self, 
        hist_data: pd.DataFrame, 
        sentiment_score: float,
        market_data: Dict
    ) -> Tuple[float, float, float]:
        """
        Calculate Bayesian forecast combining multiple signals
        Returns: (expected_return, conf_low, conf_high)
        """
        if hist_data is None or len(hist_data) < 60:
            return 0.0, 0.0, 0.0
            
        # Calculate historical metrics
        returns = hist_data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        drift = returns.mean() * 252
        
        # Prior distribution parameters (based on historical data)
        prior_mean = drift
        prior_std = volatility / np.sqrt(252)  # Annual to daily
        
        # Likelihood parameters from different signals
        signals = []
        weights = []
        
        # 1. Sentiment signal
        sentiment_signal = (sentiment_score - 0.2) * 0.20  # Scale to ±20% effect
        signals.append(sentiment_signal)
        weights.append(0.3)  # 30% weight to sentiment
        
        # 2. Market/Sector signal
        if market_data and 'etf_data' in market_data:
            try:
                sector_returns = market_data['etf_data']['return'].mean()
                sector_signal = np.clip(sector_returns * 0.5, -0.25, 0.25)
                signals.append(sector_signal)
                weights.append(0.3)  # 30% weight to sector
            except:
                pass
                
        # 3. Economic signal
        if market_data and 'economic' in market_data:
            try:
                gdp = market_data['economic']['gdp_growth'].iloc[-1]
                inflation = market_data['economic']['inflation'].iloc[-1]
                
                # Simple economic score
                econ_score = (gdp - inflation) / 100  # Scale to decimal
                econ_signal = np.clip(econ_score * 0.15, -0.15, 0.15)
                signals.append(econ_signal)
                weights.append(0.2)  # 20% weight to economic
            except:
                pass
                
        # Combine signals with weights
        if signals:
            signal_adj = np.average(signals, weights=weights)
        else:
            signal_adj = 0
            
        # Posterior distribution (combining prior with signals)
        posterior_mean = prior_mean + signal_adj
        posterior_std = prior_std * 0.8  # Reduce uncertainty with signals
        
        # Calculate 12-month forecast with confidence intervals
        time = 1.0  # 1 year
        expected = np.exp(posterior_mean * time)
        conf_low = np.exp((posterior_mean - 1.96 * posterior_std) * time)
        conf_high = np.exp((posterior_mean + 1.96 * posterior_std) * time)
        
        # Convert to percentage returns
        current_price = hist_data['Close'].iloc[-1]
        expected_return = (expected / current_price - 1) * 100
        conf_low_return = (conf_low / current_price - 1) * 100
        conf_high_return = (conf_high / current_price - 1) * 100
        
        return expected_return, conf_low_return, conf_high_return
        
    def generate_forecasts(self) -> None:
        """Generate forecasts for all companies"""
        # Load sentiment data
        sentiment_df = self.load_sentiment_data()
        if sentiment_df.empty:
            print("No sentiment data available. Exiting.")
            return
            
        results = []
        failed_tickers = []
        
        for ticker, info in self.mappings.items():
            print(f"\nProcessing {ticker} ({info['name']})...")
            
            try:
                # Get historical data
                hist_data = self.get_historical_data(ticker)
                if hist_data is None:
                    failed_tickers.append(ticker)
                    continue
                    
                # Get sentiment score
                sentiment_score = sentiment_df[
                    sentiment_df['ticker'] == ticker
                ]['average_sentiment'].iloc[0] if ticker in sentiment_df['ticker'].values else 0.2
                
                # Get market data
                market_data = self.load_market_data(ticker)
                
                # Calculate forecast
                expected, conf_low, conf_high = self.calculate_bayesian_forecast(
                    hist_data, sentiment_score, market_data
                )
                
                results.append({
                    'ticker': ticker,
                    'company': info['name'],
                    'expected_return': expected,
                    'conf_low': conf_low,
                    'conf_high': conf_high,
                    'current_price': hist_data['Close'].iloc[-1],
                    'forecast_date': datetime.now(),
                    'sentiment_score': sentiment_score,
                    'sector': market_data.get('sector', 'Unknown')
                })
                
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                failed_tickers.append(ticker)
                
        if results:
            # Create DataFrame
            results_df = pd.DataFrame(results)
            
            # Save forecasts
            forecast_path = self.results_dir / "b_custom_forecast.csv"
            results_df.to_csv(forecast_path, index=False)
            
            # Print summary statistics
            print("\nForecast Summary:")
            print(f"Companies processed: {len(self.mappings)}")
            print(f"Failed tickers: {len(failed_tickers)}")
            if failed_tickers:
                print(f"Failed tickers: {', '.join(failed_tickers)}")
            print(f"\nReturn Statistics:")
            print(f"Average expected return: {results_df['expected_return'].mean():.2f}%")
            print(f"Return range: {results_df['expected_return'].min():.2f}% to {results_df['expected_return'].max():.2f}%")
            print(f"\nResults saved to: {forecast_path}")
        else:
            print("No results to save")

def main():
    """Main function to generate custom forecasts"""
    print("\nStarting custom forecast generation...")
    forecaster = BayesianForecaster()
    forecaster.generate_forecasts()
    print("\nForecast generation complete!")

if __name__ == "__main__":
    main() 