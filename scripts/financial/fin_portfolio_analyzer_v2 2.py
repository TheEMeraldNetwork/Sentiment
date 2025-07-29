#!/usr/bin/env python3
"""
Tigro Portfolio Optimization System V2
Advanced portfolio analysis with sentiment integration and rate limiting
"""

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
import time
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

class PortfolioAnalyzerV2:
    """Advanced portfolio analysis with Modern Portfolio Theory and rate limiting"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% risk-free rate assumption
        self.current_portfolio = None
        self.universe_data = None
        self.price_data = None
        
    def parse_european_number(self, value_str):
        """Parse European number format (1.234,56 -> 1234.56)"""
        value_str = str(value_str).strip()
        if value_str == 'nan' or value_str == '':
            return 0.0
        # Replace thousands separator (.) with nothing, then decimal separator (,) with .
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
        return float(value_str)
        
    def load_portfolio(self, portfolio_file):
        """Load current portfolio from CSV"""
        print("📊 Loading current portfolio...")
        df = pd.read_csv(portfolio_file, sep=';', skiprows=2, nrows=14)
        
        # Clean and extract relevant columns
        portfolio_data = []
        for _, row in df.iterrows():
            if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                # Clean symbol (remove exchange suffix)
                symbol = row['Simbolo'].split('.')[0]
                if symbol.startswith('1'):  # European listing prefix
                    symbol = symbol[1:]
                
                portfolio_data.append({
                    'symbol': symbol,
                    'name': row['Titolo'],
                    'quantity': self.parse_european_number(row['Quantità']),
                    'avg_cost': self.parse_european_number(row['P.zo medio di carico']),
                    'current_value_eur': self.parse_european_number(row['Valore di mercato €']),
                    'return_pct': self.parse_european_number(row['Var%'])
                })
        
        self.current_portfolio = pd.DataFrame(portfolio_data)
        print(f"✅ Loaded {len(self.current_portfolio)} positions")
        return self.current_portfolio
    
    def load_universe(self, universe_file):
        """Load investment universe"""
        print("🌍 Loading investment universe...")
        self.universe_data = pd.read_csv(universe_file, sep=';')
        print(f"✅ Loaded {len(self.universe_data)} stocks in universe")
        return self.universe_data
    
    def fetch_market_data_batch(self, symbols, batch_size=5, delay=2):
        """Fetch market data in batches with rate limiting"""
        print(f"📈 Fetching market data for {len(symbols)} symbols in batches...")
        
        data = {}
        failed_symbols = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}: {batch}")
            
            for symbol in batch:
                try:
                    time.sleep(0.5)  # Small delay between individual requests
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='6mo')  # Reduced period to be faster
                    
                    if not hist.empty:
                        # Get basic info without detailed financials to avoid rate limits
                        current_price = hist['Close'].iloc[-1]
                        data[symbol] = {
                            'price_data': hist,
                            'current_price': current_price,
                            'symbol': symbol
                        }
                        print(f"    ✅ {symbol}: ${current_price:.2f}")
                    else:
                        failed_symbols.append(symbol)
                        print(f"    ❌ {symbol}: No data")
                        
                except Exception as e:
                    print(f"    ⚠️ {symbol}: {str(e)[:50]}...")
                    failed_symbols.append(symbol)
            
            # Delay between batches
            if i + batch_size < len(symbols):
                print(f"  Waiting {delay}s before next batch...")
                time.sleep(delay)
        
        print(f"✅ Successfully fetched {len(data)} symbols")
        if failed_symbols:
            print(f"❌ Failed symbols: {failed_symbols}")
            
        return data, failed_symbols
    
    def calculate_basic_portfolio_metrics(self, portfolio_data, price_data):
        """Calculate basic portfolio metrics from available data"""
        print("📊 Calculating portfolio metrics...")
        
        # Map portfolio symbols to market data
        portfolio_analysis = []
        total_value = 0
        
        for _, position in portfolio_data.iterrows():
            symbol = position['symbol']
            current_value = position['current_value_eur']
            total_value += current_value
            
            analysis_row = {
                'symbol': symbol,
                'name': position['name'],
                'current_value_eur': current_value,
                'return_pct': position['return_pct'],
                'weight': 0  # Will calculate after total_value
            }
            
            # Add market data if available
            if symbol in price_data:
                hist = price_data[symbol]['price_data']
                returns = hist['Close'].pct_change().dropna()
                
                if len(returns) > 20:  # Need sufficient data
                    analysis_row.update({
                        'daily_volatility': returns.std(),
                        'annual_volatility': returns.std() * np.sqrt(252),
                        'annual_return_estimate': returns.mean() * 252,
                        'current_price': price_data[symbol]['current_price']
                    })
            
            portfolio_analysis.append(analysis_row)
        
        # Calculate weights
        for row in portfolio_analysis:
            row['weight'] = row['current_value_eur'] / total_value
        
        analysis_df = pd.DataFrame(portfolio_analysis)
        
        # Portfolio-level metrics
        valid_returns = [row for row in portfolio_analysis if 'annual_return_estimate' in row]
        
        if valid_returns:
            weighted_return = sum(row['annual_return_estimate'] * row['weight'] for row in valid_returns)
            weighted_volatility = np.sqrt(sum((row['annual_volatility'] * row['weight'])**2 for row in valid_returns))
            sharpe_ratio = (weighted_return - self.risk_free_rate) / weighted_volatility if weighted_volatility > 0 else 0
            
            portfolio_metrics = {
                'total_value_eur': total_value,
                'portfolio_return': weighted_return,
                'portfolio_volatility': weighted_volatility,
                'sharpe_ratio': sharpe_ratio,
                'num_positions': len(analysis_df),
                'concentration_top5': analysis_df.nlargest(5, 'weight')['weight'].sum()
            }
        else:
            portfolio_metrics = {
                'total_value_eur': total_value,
                'portfolio_return': None,
                'portfolio_volatility': None,
                'sharpe_ratio': None,
                'num_positions': len(analysis_df),
                'concentration_top5': analysis_df.nlargest(5, 'weight')['weight'].sum()
            }
        
        return analysis_df, portfolio_metrics
    
    def calculate_forward_projections(self, portfolio_metrics, analysis_df):
        """Calculate forward-looking projections"""
        print("🔮 Calculating forward projections...")
        
        if portfolio_metrics['portfolio_return'] is None:
            return None
        
        current_return = portfolio_metrics['portfolio_return']
        current_vol = portfolio_metrics['portfolio_volatility']
        
        # Simple projections (can be enhanced with more sophisticated models)
        projections = {
            '3_month': {
                'expected_return': current_return * 0.25,
                'volatility': current_vol * np.sqrt(0.25),
                'confidence_95_lower': current_return * 0.25 - 1.96 * current_vol * np.sqrt(0.25),
                'confidence_95_upper': current_return * 0.25 + 1.96 * current_vol * np.sqrt(0.25)
            },
            '6_month': {
                'expected_return': current_return * 0.5,
                'volatility': current_vol * np.sqrt(0.5),
                'confidence_95_lower': current_return * 0.5 - 1.96 * current_vol * np.sqrt(0.5),
                'confidence_95_upper': current_return * 0.5 + 1.96 * current_vol * np.sqrt(0.5)
            },
            '9_month': {
                'expected_return': current_return * 0.75,
                'volatility': current_vol * np.sqrt(0.75),
                'confidence_95_lower': current_return * 0.75 - 1.96 * current_vol * np.sqrt(0.75),
                'confidence_95_upper': current_return * 0.75 + 1.96 * current_vol * np.sqrt(0.75)
            },
            '12_month': {
                'expected_return': current_return,
                'volatility': current_vol,
                'confidence_95_lower': current_return - 1.96 * current_vol,
                'confidence_95_upper': current_return + 1.96 * current_vol
            }
        }
        
        return projections

def main():
    """Main execution function"""
    print("🚀 Starting Tigro Portfolio Analysis V2...")
    
    analyzer = PortfolioAnalyzerV2()
    
    # Load data
    portfolio = analyzer.load_portfolio('actual-portfolio-master.csv')
    universe = analyzer.load_universe('master name ticker.csv')
    
    print(f"\n📋 Current Portfolio Overview:")
    print(portfolio[['symbol', 'name', 'current_value_eur', 'return_pct']].to_string(index=False))
    
    # Get portfolio symbols
    portfolio_symbols = portfolio['symbol'].tolist()
    
    # Fetch market data with rate limiting
    print("\n" + "="*50)
    print("PHASE 1: MARKET DATA COLLECTION")
    print("="*50)
    
    portfolio_market_data, failed_symbols = analyzer.fetch_market_data_batch(portfolio_symbols, batch_size=3, delay=3)
    
    if portfolio_market_data:
        # Calculate portfolio metrics
        print("\n" + "="*50)
        print("PHASE 2: PORTFOLIO ANALYSIS")
        print("="*50)
        
        analysis_df, portfolio_metrics = analyzer.calculate_basic_portfolio_metrics(portfolio, portfolio_market_data)
        
        print(f"\n📊 PORTFOLIO SUMMARY:")
        print(f"Total Value: €{portfolio_metrics['total_value_eur']:,.2f}")
        print(f"Number of Positions: {portfolio_metrics['num_positions']}")
        print(f"Top 5 Concentration: {portfolio_metrics['concentration_top5']:.1%}")
        
        if portfolio_metrics['portfolio_return'] is not None:
            print(f"Estimated Annual Return: {portfolio_metrics['portfolio_return']:.2%}")
            print(f"Estimated Annual Volatility: {portfolio_metrics['portfolio_volatility']:.2%}")
            print(f"Estimated Sharpe Ratio: {portfolio_metrics['sharpe_ratio']:.3f}")
            
            # Forward projections
            projections = analyzer.calculate_forward_projections(portfolio_metrics, analysis_df)
            
            print(f"\n🔮 FORWARD PROJECTIONS:")
            for period, proj in projections.items():
                print(f"{period.replace('_', ' ').title()}:")
                print(f"  Expected Return: {proj['expected_return']:.2%}")
                print(f"  95% Confidence Range: {proj['confidence_95_lower']:.2%} to {proj['confidence_95_upper']:.2%}")
        
        print(f"\n💼 POSITION ANALYSIS:")
        analysis_display = analysis_df[['symbol', 'name', 'weight', 'return_pct']].copy()
        analysis_display['weight'] = analysis_display['weight'] * 100
        print(analysis_display.round(2).to_string(index=False))
        
        # Save results
        analysis_df.to_csv('portfolio_analysis_output.csv', index=False)
        print(f"\n💾 Analysis saved to 'portfolio_analysis_output.csv'")
        
    else:
        print("❌ No market data available for analysis")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 