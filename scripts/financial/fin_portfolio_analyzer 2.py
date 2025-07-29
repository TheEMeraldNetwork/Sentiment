#!/usr/bin/env python3
"""
Tigro Portfolio Optimization System
Advanced portfolio analysis with sentiment integration
"""

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

class PortfolioAnalyzer:
    """Advanced portfolio analysis with Modern Portfolio Theory"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% risk-free rate assumption
        self.current_portfolio = None
        self.universe_data = None
        self.price_data = None
        
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
                
                # Helper function to parse European number format
                def parse_european_number(value_str):
                    """Parse European number format (1.234,56 -> 1234.56)"""
                    value_str = str(value_str).strip()
                    if value_str == 'nan' or value_str == '':
                        return 0.0
                    # Replace thousands separator (.) with nothing, then decimal separator (,) with .
                    # But first check if it's already in US format
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
                
                portfolio_data.append({
                    'symbol': symbol,
                    'name': row['Titolo'],
                    'quantity': parse_european_number(row['Quantità']),
                    'avg_cost': parse_european_number(row['P.zo medio di carico']),
                    'current_value_eur': parse_european_number(row['Valore di mercato €']),
                    'return_pct': parse_european_number(row['Var%'])
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
    
    def fetch_market_data(self, symbols, period='1y'):
        """Fetch market data for given symbols"""
        print(f"📈 Fetching market data for {len(symbols)} symbols...")
        
        data = {}
        failed_symbols = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                info = ticker.info
                
                if not hist.empty:
                    data[symbol] = {
                        'price_data': hist,
                        'current_price': hist['Close'].iloc[-1],
                        'info': info
                    }
                else:
                    failed_symbols.append(symbol)
                    
            except Exception as e:
                print(f"⚠️ Failed to fetch {symbol}: {str(e)}")
                failed_symbols.append(symbol)
        
        print(f"✅ Successfully fetched {len(data)} symbols")
        if failed_symbols:
            print(f"❌ Failed symbols: {failed_symbols}")
            
        return data, failed_symbols
    
    def calculate_portfolio_metrics(self, portfolio_symbols, price_data):
        """Calculate comprehensive portfolio metrics"""
        print("📊 Calculating portfolio metrics...")
        
        # Extract returns for portfolio stocks
        returns_data = {}
        for symbol in portfolio_symbols:
            if symbol in price_data:
                prices = price_data[symbol]['price_data']['Close']
                returns = prices.pct_change().dropna()
                returns_data[symbol] = returns
        
        if not returns_data:
            print("❌ No valid return data found")
            return None
        
        # Create returns matrix
        returns_df = pd.DataFrame(returns_data).dropna()
        
        # Calculate metrics
        mean_returns = returns_df.mean() * 252  # Annualized
        volatility = returns_df.std() * np.sqrt(252)  # Annualized
        correlation_matrix = returns_df.corr()
        
        # Portfolio-level calculations (equal weighted for now)
        portfolio_weights = np.array([1/len(returns_df.columns)] * len(returns_df.columns))
        
        portfolio_return = np.sum(mean_returns * portfolio_weights)
        portfolio_variance = np.dot(portfolio_weights.T, np.dot(returns_df.cov() * 252, portfolio_weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        metrics = {
            'individual_returns': mean_returns,
            'individual_volatility': volatility,
            'correlation_matrix': correlation_matrix,
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'returns_df': returns_df
        }
        
        print(f"✅ Portfolio Return: {portfolio_return:.2%}")
        print(f"✅ Portfolio Volatility: {portfolio_volatility:.2%}")
        print(f"✅ Sharpe Ratio: {sharpe_ratio:.3f}")
        
        return metrics
    
    def analyze_universe_opportunities(self, universe_symbols, price_data):
        """Analyze investment universe for opportunities"""
        print("🔍 Analyzing universe opportunities...")
        
        opportunities = []
        
        for symbol in universe_symbols:
            if symbol in price_data:
                info = price_data[symbol]['info']
                price_data_symbol = price_data[symbol]['price_data']
                
                # Calculate basic metrics
                returns = price_data_symbol['Close'].pct_change().dropna()
                
                if len(returns) > 50:  # Need sufficient data
                    annual_return = returns.mean() * 252
                    annual_vol = returns.std() * np.sqrt(252)
                    sharpe = (annual_return - self.risk_free_rate) / annual_vol if annual_vol > 0 else 0
                    
                    # Extract analyst data
                    target_price = info.get('targetMeanPrice', None)
                    recommendation = info.get('recommendationMean', None)
                    current_price = price_data[symbol]['current_price']
                    
                    upside_potential = 0
                    if target_price and current_price:
                        upside_potential = (target_price - current_price) / current_price
                    
                    opportunities.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'target_price': target_price,
                        'upside_potential': upside_potential,
                        'recommendation_mean': recommendation,
                        'annual_return': annual_return,
                        'annual_volatility': annual_vol,
                        'sharpe_ratio': sharpe,
                        'market_cap': info.get('marketCap', None),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown')
                    })
        
        opportunities_df = pd.DataFrame(opportunities)
        print(f"✅ Analyzed {len(opportunities_df)} opportunities")
        
        return opportunities_df
    
    def generate_portfolio_report(self, portfolio_metrics, current_portfolio, opportunities_df):
        """Generate comprehensive portfolio analysis report"""
        print("📋 Generating portfolio report...")
        
        report = {
            'timestamp': datetime.now(),
            'current_portfolio_summary': {
                'total_positions': len(current_portfolio),
                'total_value_eur': current_portfolio['current_value_eur'].sum(),
                'portfolio_return': portfolio_metrics['portfolio_return'],
                'portfolio_volatility': portfolio_metrics['portfolio_volatility'],
                'sharpe_ratio': portfolio_metrics['sharpe_ratio']
            },
            'top_opportunities': opportunities_df.nlargest(10, 'sharpe_ratio')[['symbol', 'upside_potential', 'sharpe_ratio', 'sector']],
            'portfolio_concentration': current_portfolio.set_index('symbol')['current_value_eur'] / current_portfolio['current_value_eur'].sum(),
            'recommendations': {
                'high_conviction_buys': [],
                'position_increases': [],
                'position_decreases': [],
                'holds': []
            }
        }
        
        return report

def main():
    """Main execution function"""
    print("🚀 Starting Tigro Portfolio Analysis...")
    
    analyzer = PortfolioAnalyzer()
    
    # Load data
    portfolio = analyzer.load_portfolio('actual-portfolio-master.csv')
    universe = analyzer.load_universe('master name ticker.csv')
    
    # Get symbols
    portfolio_symbols = portfolio['symbol'].tolist()
    universe_symbols = universe['Ticker'].tolist()
    
    # Fetch market data
    print("\n" + "="*50)
    print("PHASE 1: PORTFOLIO ANALYSIS")
    print("="*50)
    
    portfolio_data, failed_portfolio = analyzer.fetch_market_data(portfolio_symbols)
    
    if portfolio_data:
        portfolio_metrics = analyzer.calculate_portfolio_metrics(portfolio_symbols, portfolio_data)
        
        print("\n" + "="*50)
        print("PHASE 2: UNIVERSE ANALYSIS")
        print("="*50)
        
        # Sample universe for efficiency (can process full universe later)
        sample_universe = universe_symbols[:50]  # Start with 50 stocks
        universe_data, failed_universe = analyzer.fetch_market_data(sample_universe)
        
        if universe_data:
            opportunities = analyzer.analyze_universe_opportunities(sample_universe, universe_data)
            
            print("\n" + "="*50)
            print("PHASE 3: REPORT GENERATION")
            print("="*50)
            
            report = analyzer.generate_portfolio_report(portfolio_metrics, portfolio, opportunities)
            
            print("\n📊 PORTFOLIO SUMMARY:")
            print(f"Total Value: €{report['current_portfolio_summary']['total_value_eur']:,.2f}")
            print(f"Expected Annual Return: {report['current_portfolio_summary']['portfolio_return']:.2%}")
            print(f"Annual Volatility: {report['current_portfolio_summary']['portfolio_volatility']:.2%}")
            print(f"Sharpe Ratio: {report['current_portfolio_summary']['sharpe_ratio']:.3f}")
            
            print("\n🎯 TOP OPPORTUNITIES:")
            print(report['top_opportunities'].to_string(index=False))
            
            print("\n💼 PORTFOLIO CONCENTRATION:")
            concentration = report['portfolio_concentration'].sort_values(ascending=False)
            for symbol, weight in concentration.head(5).items():
                print(f"{symbol}: {weight:.1%}")
            
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 