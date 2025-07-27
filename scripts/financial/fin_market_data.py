#!/usr/bin/env python3
"""
Market Data Collector - Components A3, C2, C5
Fetches 2 years of historical data + analyst targets from yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Tuple, Optional

class MarketDataCollector:
    """Comprehensive market data collection with rate limiting and error handling"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize market data collector"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Rate limiting parameters
        self.request_delay = 0.5  # Seconds between requests
        self.batch_delay = 2.0    # Seconds between batches
        self.batch_size = 5       # Symbols per batch
        
        # Data periods
        self.historical_period = "2y"  # 2 years as requested
        self.trading_days_year = 252   # For annualization
    
    def parse_european_number(self, value_str):
        """Parse European number format (1.234,56 -> 1234.56)"""
        if pd.isna(value_str) or value_str == '' or str(value_str).strip() == '':
            return 0.0
        
        value_str = str(value_str).strip()
        
        if ',' in value_str and '.' in value_str:
            # European format: 1.234,56
            parts = value_str.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                value_str = integer_part + '.' + decimal_part
        elif ',' in value_str:
            # Only comma, assume it's decimal separator
            value_str = value_str.replace(',', '.')
            
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def load_portfolio_symbols(self, portfolio_file="actual-portfolio-master.csv"):
        """Load symbols from portfolio file"""
        try:
            df = pd.read_csv(portfolio_file, sep=';', skiprows=2, nrows=20)
            symbols = []
            
            for _, row in df.iterrows():
                if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                    symbol = row['Simbolo'].split('.')[0]  # Remove exchange suffix
                    if symbol.startswith('1'):  # Remove '1' prefix from European symbols
                        symbol = symbol[1:]
                    symbols.append(symbol)
            
            self.logger.info(f"📊 Loaded {len(symbols)} portfolio symbols")
            return symbols
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load portfolio symbols: {e}")
            return []
    
    def load_universe_symbols(self, universe_file="master name ticker.csv"):
        """Load symbols from stock universe file"""
        try:
            df = pd.read_csv(universe_file, sep=';')
            symbols = df['Ticker'].tolist()
            
            self.logger.info(f"📊 Loaded {len(symbols)} universe symbols")
            return symbols
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load universe symbols: {e}")
            return []
    
    def fetch_single_stock_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive data for a single stock
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with historical prices, analyst data, and calculated metrics
        """
        data = {
            'symbol': symbol,
            'prices': None,
            'current_price': None,
            'returns': None,
            'volatility': None,
            'analyst_targets': {},
            'info': {},
            'success': False
        }
        
        try:
            self.logger.info(f"📈 Fetching data for {symbol}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data (2 years)
            hist = ticker.history(period=self.historical_period)
            
            if hist.empty:
                self.logger.warning(f"⚠️ No historical data for {symbol}")
                return data
            
            # Store price data
            data['prices'] = hist
            data['current_price'] = hist['Close'].iloc[-1]
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            data['returns'] = returns
            
            # Calculate annualized volatility
            data['volatility'] = returns.std() * np.sqrt(self.trading_days_year)
            
            # Fetch analyst targets and info
            try:
                info = ticker.info
                data['info'] = info
                
                # Extract analyst targets
                if 'targetLowPrice' in info and info['targetLowPrice']:
                    data['analyst_targets']['low'] = info['targetLowPrice']
                if 'targetMeanPrice' in info and info['targetMeanPrice']:
                    data['analyst_targets']['mean'] = info['targetMeanPrice']
                if 'targetHighPrice' in info and info['targetHighPrice']:
                    data['analyst_targets']['high'] = info['targetHighPrice']
                
                # Additional metrics
                if 'recommendationKey' in info:
                    data['analyst_targets']['recommendation'] = info['recommendationKey']
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get analyst data for {symbol}: {e}")
            
            data['success'] = True
            self.logger.info(f"✅ Successfully fetched {symbol}: ${data['current_price']:.2f}")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch {symbol}: {e}")
        
        return data
    
    def fetch_batch_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for a batch of symbols with rate limiting
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            Dict mapping symbols to their data
        """
        batch_data = {}
        
        # Process in batches
        for i in range(0, len(symbols), self.batch_size):
            batch = symbols[i:i + self.batch_size]
            
            self.logger.info(f"📦 Processing batch {i//self.batch_size + 1}: {batch}")
            
            for symbol in batch:
                batch_data[symbol] = self.fetch_single_stock_data(symbol)
            
            # Batch delay
            if i + self.batch_size < len(symbols):
                self.logger.info(f"⏳ Batch delay: {self.batch_delay}s")
                time.sleep(self.batch_delay)
        
        successful = sum(1 for data in batch_data.values() if data['success'])
        self.logger.info(f"✅ Successfully fetched {successful}/{len(symbols)} symbols")
        
        return batch_data
    
    def calculate_returns_matrix(self, market_data: Dict[str, Dict]) -> pd.DataFrame:
        """
        Calculate aligned returns matrix for portfolio optimization
        
        Args:
            market_data: Dict of market data by symbol
            
        Returns:
            DataFrame with aligned daily returns
        """
        returns_data = {}
        
        for symbol, data in market_data.items():
            if data['success'] and data['returns'] is not None:
                returns_data[symbol] = data['returns']
        
        if not returns_data:
            self.logger.error("❌ No valid returns data")
            return pd.DataFrame()
        
        # Align all return series
        returns_df = pd.DataFrame(returns_data)
        
        # Drop rows with any NaN values for clean covariance calculation
        returns_df = returns_df.dropna()
        
        self.logger.info(f"📊 Returns matrix: {returns_df.shape[0]} days, {returns_df.shape[1]} stocks")
        
        return returns_df
    
    def calculate_expected_returns(self, returns_df: pd.DataFrame) -> pd.Series:
        """
        Calculate annualized expected returns using geometric mean
        
        Mathematical Foundation:
        Geometric mean accounts for compounding: (1+r1)*(1+r2)*...*(1+rn) = (1+r_geometric)^n
        This is more accurate for investment returns than arithmetic mean.
        
        Args:
            returns_df: DataFrame of daily returns
            
        Returns:
            Series of annualized expected returns
        """
        if returns_df.empty:
            return pd.Series()
        
        # Method 1: Geometric mean (more accurate for compound returns)
        # Convert returns to price relatives, take geometric mean, annualize
        try:
            n_days = len(returns_df)
            
            # Calculate compound returns: (1+r1)*(1+r2)*...*(1+rn)^(252/n) - 1
            price_relatives = 1 + returns_df
            geometric_means = price_relatives.prod() ** (self.trading_days_year / n_days) - 1
            
            # For numerical stability, also calculate arithmetic mean as backup
            arithmetic_means = returns_df.mean() * self.trading_days_year
            
            # Log both methods for comparison
            self.logger.info(f"📈 Expected returns calculated for {len(geometric_means)} stocks")
            self.logger.info(f"📊 Method comparison for sample stocks:")
            
            for symbol in geometric_means.head(3).index:
                geo = geometric_means[symbol]
                arith = arithmetic_means[symbol]
                self.logger.info(f"   {symbol}: Geometric={geo:.4f} ({geo:.2%}), Arithmetic={arith:.4f} ({arith:.2%})")
            
            # Use geometric mean as primary method
            annual_returns = geometric_means
            
            # Handle any invalid values (replace with arithmetic mean)
            invalid_mask = ~np.isfinite(annual_returns) | (annual_returns < -0.95) | (annual_returns > 5.0)
            if invalid_mask.any():
                self.logger.warning(f"⚠️ Replacing {invalid_mask.sum()} invalid geometric returns with arithmetic mean")
                annual_returns[invalid_mask] = arithmetic_means[invalid_mask]
            
            return annual_returns
            
        except Exception as e:
            self.logger.error(f"❌ Geometric mean calculation failed: {e}")
            self.logger.warning("⚠️ Falling back to arithmetic mean")
            
            # Fallback to arithmetic mean
            daily_means = returns_df.mean()
            annual_returns = daily_means * self.trading_days_year
            
            self.logger.info(f"📈 Expected returns (arithmetic) calculated for {len(annual_returns)} stocks")
            return annual_returns
    
    def calculate_covariance_matrix(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate annualized covariance matrix with mathematical validation
        
        Mathematical Foundation:
        Cov(X,Y) = E[(X-μx)(Y-μy)] annualized by multiplying by trading days
        
        Args:
            returns_df: DataFrame of daily returns
            
        Returns:
            DataFrame covariance matrix (annualized)
        """
        if returns_df.empty:
            return pd.DataFrame()
        
        # Calculate daily covariance matrix
        daily_cov = returns_df.cov()
        
        # Annualize covariance matrix
        annual_cov = daily_cov * self.trading_days_year
        
        # Mathematical validation
        n_assets = annual_cov.shape[0]
        
        # Check matrix properties
        is_symmetric = np.allclose(annual_cov, annual_cov.T, atol=1e-10)
        eigenvals = np.linalg.eigvals(annual_cov.values)
        is_positive_semidefinite = np.all(eigenvals >= -1e-8)  # Allow small numerical errors
        min_eigenval = np.min(eigenvals)
        condition_number = np.max(eigenvals) / np.max([np.min(eigenvals[eigenvals > 1e-10]), 1e-10])
        
        self.logger.info(f"🔢 Covariance matrix calculated: {annual_cov.shape}")
        self.logger.info(f"📊 Matrix validation:")
        self.logger.info(f"   Symmetric: {is_symmetric}")
        self.logger.info(f"   Positive semi-definite: {is_positive_semidefinite}")
        self.logger.info(f"   Min eigenvalue: {min_eigenval:.6f}")
        self.logger.info(f"   Condition number: {condition_number:.2f}")
        
        # Handle numerical issues
        if not is_positive_semidefinite:
            self.logger.warning("⚠️ Covariance matrix not positive semi-definite, applying regularization")
            # Add small diagonal term to ensure positive definiteness
            regularization = max(-min_eigenval * 1.1, 1e-6)
            annual_cov += np.eye(n_assets) * regularization
            self.logger.info(f"✅ Added regularization: {regularization:.6f}")
        
        if condition_number > 1e12:
            self.logger.warning(f"⚠️ High condition number ({condition_number:.2e}), matrix may be ill-conditioned")
        
        # Verify final matrix properties
        final_eigenvals = np.linalg.eigvals(annual_cov.values)
        final_min_eigenval = np.min(final_eigenvals)
        
        if final_min_eigenval < 0:
            self.logger.error(f"❌ Final matrix still not positive semi-definite: min eigenval = {final_min_eigenval:.6f}")
        else:
            self.logger.info(f"✅ Final matrix is positive semi-definite: min eigenval = {final_min_eigenval:.6f}")
        
        return annual_cov
    
    def get_analyst_targets_summary(self, market_data: Dict[str, Dict]) -> pd.DataFrame:
        """
        Compile analyst targets for all stocks
        
        Args:
            market_data: Dict of market data by symbol
            
        Returns:
            DataFrame with analyst targets
        """
        targets_data = []
        
        for symbol, data in market_data.items():
            if data['success']:
                target_info = {
                    'symbol': symbol,
                    'current_price': data['current_price'],
                    'low_target': data['analyst_targets'].get('low'),
                    'mean_target': data['analyst_targets'].get('mean'),
                    'high_target': data['analyst_targets'].get('high'),
                    'recommendation': data['analyst_targets'].get('recommendation'),
                    'volatility': data['volatility']
                }
                
                # Calculate upside potential using low target (conservative approach)
                if target_info['low_target'] and target_info['current_price']:
                    target_info['upside_potential'] = (
                        target_info['low_target'] - target_info['current_price']
                    ) / target_info['current_price']
                else:
                    target_info['upside_potential'] = None
                
                targets_data.append(target_info)
        
        targets_df = pd.DataFrame(targets_data)
        
        # Filter stocks with analyst targets (as requested)
        targets_with_data = targets_df[targets_df['low_target'].notna()]
        
        self.logger.info(f"📊 Analyst targets: {len(targets_with_data)}/{len(targets_df)} stocks have low targets")
        
        return targets_with_data

def main():
    """Test market data collection"""
    collector = MarketDataCollector()
    
    print("📈 MARKET DATA COLLECTION TEST")
    print("=" * 50)
    
    # Test with a few portfolio symbols
    portfolio_symbols = collector.load_portfolio_symbols()[:5]  # First 5 for testing
    
    if portfolio_symbols:
        print(f"🧪 Testing with symbols: {portfolio_symbols}")
        
        # Fetch market data
        market_data = collector.fetch_batch_data(portfolio_symbols)
        
        # Calculate returns matrix
        returns_df = collector.calculate_returns_matrix(market_data)
        print(f"📊 Returns matrix shape: {returns_df.shape}")
        
        # Calculate expected returns
        expected_returns = collector.calculate_expected_returns(returns_df)
        print(f"📈 Expected returns calculated for {len(expected_returns)} stocks")
        
        # Calculate covariance matrix
        cov_matrix = collector.calculate_covariance_matrix(returns_df)
        print(f"🔢 Covariance matrix shape: {cov_matrix.shape}")
        
        # Get analyst targets
        targets_df = collector.get_analyst_targets_summary(market_data)
        print(f"🎯 Analyst targets available for {len(targets_df)} stocks")
        
        return {
            'market_data': market_data,
            'returns_df': returns_df,
            'expected_returns': expected_returns,
            'covariance_matrix': cov_matrix,
            'analyst_targets': targets_df
        }
    
    else:
        print("❌ No portfolio symbols found")
        return None

if __name__ == "__main__":
    main() 