#!/usr/bin/env python3
"""
Tigro Portfolio Optimization System - Complete Implementation
Advanced portfolio analysis with sentiment integration and optimization
"""

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
import time
import os
import glob
from datetime import datetime, timedelta
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

class TigroPortfolioOptimizer:
    """Complete portfolio optimization system with sentiment integration"""
    
    def __init__(self):
        # System parameters based on user requirements
        self.risk_free_rate = 0.05  # 5% risk-free rate
        self.standard_position_size_usd = 2000  # Standard position size
        self.max_sector_weight = 0.40  # 40% max per sector
        self.stop_loss_pct = 0.08  # 8% stop loss for winners
        self.target_return_increase = 0.02  # +2pp target
        self.new_cash_available = 10000  # $10K new investment
        self.reserved_cash = 10000  # $10K to keep in reserve
        
        # Portfolio data
        self.current_portfolio = None
        self.universe_data = None
        self.market_data = {}
        self.sentiment_data = {}
        
    def parse_european_number(self, value_str):
        """Parse European number format (1.234,56 -> 1234.56)"""
        value_str = str(value_str).strip()
        if value_str == 'nan' or value_str == '':
            return 0.0
        if ',' in value_str and '.' in value_str:
            parts = value_str.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                value_str = integer_part + '.' + decimal_part
        elif ',' in value_str:
            value_str = value_str.replace(',', '.')
        return float(value_str)
    
    def load_portfolio(self, portfolio_file):
        """Load current portfolio from CSV"""
        print("📊 Loading current portfolio...")
        df = pd.read_csv(portfolio_file, sep=';', skiprows=2, nrows=14)
        
        portfolio_data = []
        for _, row in df.iterrows():
            if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                symbol = row['Simbolo'].split('.')[0]
                if symbol.startswith('1'):
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
    
    def fetch_market_data_robust(self, symbols, batch_size=10, delay=1):
        """Fetch market data with robust error handling"""
        print(f"📈 Fetching market data for {len(symbols)} symbols...")
        
        data = {}
        failed_symbols = []
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}")
            
            for symbol in batch:
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # Get historical data (6 months for analysis)
                    hist = ticker.history(period='6mo')
                    
                    # Get current info (with error handling for missing data)
                    info = {}
                    try:
                        info = ticker.info
                    except:
                        info = {}  # Continue with empty info if fails
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        
                        # Calculate basic metrics
                        returns = hist['Close'].pct_change().dropna()
                        
                        data[symbol] = {
                            'price_data': hist,
                            'current_price': current_price,
                            'returns': returns,
                            'annual_return': returns.mean() * 252 if len(returns) > 20 else 0,
                            'annual_volatility': returns.std() * np.sqrt(252) if len(returns) > 20 else 0,
                            'target_price': info.get('targetMeanPrice', None),
                            'recommendation': info.get('recommendationMean', None),
                            'market_cap': info.get('marketCap', None),
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown'),
                            'pe_ratio': info.get('trailingPE', None),
                            'forward_pe': info.get('forwardPE', None),
                            'symbol': symbol
                        }
                        
                        # Calculate upside potential
                        if data[symbol]['target_price']:
                            data[symbol]['upside_potential'] = (data[symbol]['target_price'] - current_price) / current_price
                        else:
                            data[symbol]['upside_potential'] = 0
                        
                        # Calculate Sharpe ratio
                        if data[symbol]['annual_volatility'] > 0:
                            data[symbol]['sharpe_ratio'] = (data[symbol]['annual_return'] - self.risk_free_rate) / data[symbol]['annual_volatility']
                        else:
                            data[symbol]['sharpe_ratio'] = 0
                        
                        print(f"    ✅ {symbol}: ${current_price:.2f}")
                    else:
                        failed_symbols.append(symbol)
                        print(f"    ❌ {symbol}: No data")
                        
                except Exception as e:
                    failed_symbols.append(symbol)
                    print(f"    ⚠️ {symbol}: {str(e)[:50]}...")
                
                time.sleep(0.3)  # Small delay between requests
            
            if i + batch_size < len(symbols):
                print(f"  Waiting {delay}s before next batch...")
                time.sleep(delay)
        
        print(f"✅ Successfully fetched {len(data)} symbols")
        if failed_symbols:
            print(f"❌ Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}...")
        
        self.market_data = data
        return data, failed_symbols
    
    def load_sentiment_data(self):
        """Load latest sentiment data from database"""
        print("🧠 Loading sentiment analysis data...")
        
        sentiment_files = glob.glob('database/sentiment/detailed/sentiment_detailed_*.csv')
        if not sentiment_files:
            print("⚠️ No sentiment files found")
            return {}
        
        # Get the most recent sentiment file
        latest_file = max(sentiment_files, key=os.path.getctime)
        print(f"  Using: {latest_file}")
        
        try:
            sentiment_df = pd.read_csv(latest_file)
            
            # Create sentiment dictionary
            sentiment_dict = {}
            for _, row in sentiment_df.iterrows():
                symbol = row.get('symbol', '').strip().upper()
                if symbol:
                    sentiment_dict[symbol] = {
                        'sentiment_score': row.get('sentiment_score', 0),
                        'sentiment_label': row.get('sentiment_label', 'neutral'),
                        'confidence': row.get('confidence', 0),
                        'article_count': row.get('article_count', 0)
                    }
            
            print(f"✅ Loaded sentiment data for {len(sentiment_dict)} symbols")
            self.sentiment_data = sentiment_dict
            return sentiment_dict
            
        except Exception as e:
            print(f"⚠️ Error loading sentiment data: {e}")
            return {}
    
    def analyze_current_portfolio(self):
        """Comprehensive analysis of current portfolio"""
        print("\n" + "="*60)
        print("CURRENT PORTFOLIO ANALYSIS")
        print("="*60)
        
        # Basic portfolio metrics
        total_value = self.current_portfolio['current_value_eur'].sum()
        
        # Add market data to portfolio analysis
        portfolio_analysis = []
        for _, position in self.current_portfolio.iterrows():
            symbol = position['symbol']
            
            analysis_row = {
                'symbol': symbol,
                'name': position['name'],
                'current_value_eur': position['current_value_eur'],
                'current_value_usd': position['current_value_eur'] * 1.1,  # Rough EUR/USD conversion
                'return_pct': position['return_pct'],
                'weight': position['current_value_eur'] / total_value
            }
            
            # Add market data if available
            if symbol in self.market_data:
                market_info = self.market_data[symbol]
                analysis_row.update({
                    'current_price': market_info['current_price'],
                    'annual_return': market_info['annual_return'],
                    'annual_volatility': market_info['annual_volatility'],
                    'sharpe_ratio': market_info['sharpe_ratio'],
                    'sector': market_info['sector'],
                    'upside_potential': market_info['upside_potential'],
                    'target_price': market_info['target_price']
                })
            
            # Add sentiment data if available
            if symbol in self.sentiment_data:
                sentiment_info = self.sentiment_data[symbol]
                analysis_row.update({
                    'sentiment_score': sentiment_info['sentiment_score'],
                    'sentiment_label': sentiment_info['sentiment_label']
                })
            
            portfolio_analysis.append(analysis_row)
        
        analysis_df = pd.DataFrame(portfolio_analysis)
        
        # Portfolio-level calculations
        valid_positions = analysis_df[analysis_df['annual_return'].notna()]
        
        if len(valid_positions) > 0:
            portfolio_return = (valid_positions['annual_return'] * valid_positions['weight']).sum()
            portfolio_volatility = np.sqrt((valid_positions['annual_volatility'] * valid_positions['weight'])**2).sum()
            portfolio_sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        else:
            portfolio_return = portfolio_volatility = portfolio_sharpe = None
        
        # Sector concentration analysis
        sector_weights = analysis_df.groupby('sector')['weight'].sum().sort_values(ascending=False)
        
        portfolio_metrics = {
            'total_value_eur': total_value,
            'total_value_usd': total_value * 1.1,  # Rough conversion
            'num_positions': len(analysis_df),
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'portfolio_sharpe': portfolio_sharpe,
            'top_5_concentration': analysis_df.nlargest(5, 'weight')['weight'].sum(),
            'sector_weights': sector_weights,
            'analysis_df': analysis_df
        }
        
        # Display results
        print(f"\n📊 PORTFOLIO SUMMARY:")
        print(f"Total Value: €{portfolio_metrics['total_value_eur']:,.2f} (≈${portfolio_metrics['total_value_usd']:,.2f})")
        print(f"Number of Positions: {portfolio_metrics['num_positions']}")
        print(f"Top 5 Concentration: {portfolio_metrics['top_5_concentration']:.1%}")
        
        if portfolio_return is not None:
            print(f"Portfolio Annual Return: {portfolio_return:.2%}")
            print(f"Portfolio Volatility: {portfolio_volatility:.2%}")
            print(f"Portfolio Sharpe Ratio: {portfolio_sharpe:.3f}")
            print(f"Target Return (+2pp): {portfolio_return + self.target_return_increase:.2%}")
        
        print(f"\n🏭 SECTOR ALLOCATION:")
        for sector, weight in sector_weights.head(5).items():
            print(f"  {sector}: {weight:.1%}")
        
        return portfolio_metrics
    
    def screen_universe_opportunities(self):
        """Screen the universe for investment opportunities"""
        print("\n" + "="*60)
        print("UNIVERSE SCREENING")
        print("="*60)
        
        opportunities = []
        
        for symbol in self.universe_data['Ticker']:
            if symbol in self.market_data:
                market_info = self.market_data[symbol]
                
                # Base opportunity data
                opp = {
                    'symbol': symbol,
                    'current_price': market_info['current_price'],
                    'annual_return': market_info['annual_return'],
                    'annual_volatility': market_info['annual_volatility'],
                    'sharpe_ratio': market_info['sharpe_ratio'],
                    'upside_potential': market_info['upside_potential'],
                    'target_price': market_info['target_price'],
                    'sector': market_info['sector'],
                    'market_cap': market_info['market_cap'],
                    'pe_ratio': market_info['pe_ratio']
                }
                
                # Add sentiment score if available
                if symbol in self.sentiment_data:
                    sentiment_info = self.sentiment_data[symbol]
                    opp.update({
                        'sentiment_score': sentiment_info['sentiment_score'],
                        'sentiment_label': sentiment_info['sentiment_label'],
                        'sentiment_confidence': sentiment_info['confidence']
                    })
                else:
                    opp.update({
                        'sentiment_score': 0,
                        'sentiment_label': 'neutral',
                        'sentiment_confidence': 0
                    })
                
                # Calculate composite score (combine financial metrics + sentiment)
                financial_score = 0
                if opp['sharpe_ratio'] and not np.isnan(opp['sharpe_ratio']):
                    financial_score += min(opp['sharpe_ratio'], 2) * 0.4  # Cap at 2, weight 40%
                if opp['upside_potential'] and not np.isnan(opp['upside_potential']):
                    financial_score += min(max(opp['upside_potential'], -0.5), 1) * 0.4  # Cap between -50% and 100%, weight 40%
                
                sentiment_score = opp['sentiment_score'] * 0.2  # Weight 20%
                
                opp['composite_score'] = financial_score + sentiment_score
                opportunities.append(opp)
        
        opportunities_df = pd.DataFrame(opportunities)
        
        # Filter and rank opportunities
        # Remove current portfolio holdings for new investments
        current_symbols = set(self.current_portfolio['symbol'])
        new_opportunities = opportunities_df[~opportunities_df['symbol'].isin(current_symbols)]
        
        # Quality filters
        quality_filter = (
            (new_opportunities['annual_volatility'] < 0.8) &  # Not too volatile
            (new_opportunities['current_price'] > 5) &  # No penny stocks
            (new_opportunities['market_cap'].fillna(0) > 1e9)  # Min $1B market cap
        )
        
        filtered_opportunities = new_opportunities[quality_filter]
        top_opportunities = filtered_opportunities.nlargest(20, 'composite_score')
        
        print(f"✅ Screened {len(opportunities_df)} total opportunities")
        print(f"✅ Found {len(filtered_opportunities)} quality opportunities (excluding current holdings)")
        
        print(f"\n🎯 TOP 10 NEW INVESTMENT OPPORTUNITIES:")
        display_cols = ['symbol', 'sector', 'composite_score', 'sharpe_ratio', 'upside_potential', 'sentiment_label']
        print(top_opportunities[display_cols].head(10).round(3).to_string(index=False))
        
        return opportunities_df, top_opportunities

def main():
    """Main execution function"""
    print("🚀 Starting Tigro Portfolio Optimization System")
    print("=" * 80)
    
    optimizer = TigroPortfolioOptimizer()
    
    # Load data
    portfolio = optimizer.load_portfolio('actual-portfolio-master.csv')
    universe = optimizer.load_universe('master name ticker.csv')
    sentiment_data = optimizer.load_sentiment_data()
    
    # Get all symbols we need data for
    portfolio_symbols = portfolio['symbol'].tolist()
    universe_symbols = universe['Ticker'].tolist()[:50]  # Start with first 50 for testing
    all_symbols = list(set(portfolio_symbols + universe_symbols))
    
    print(f"\n📊 DATA OVERVIEW:")
    print(f"Portfolio positions: {len(portfolio_symbols)}")
    print(f"Universe stocks (sample): {len(universe_symbols)}")
    print(f"Sentiment data available: {len(sentiment_data)}")
    print(f"Total symbols to analyze: {len(all_symbols)}")
    
    # Fetch market data
    print(f"\n{'='*60}")
    print("MARKET DATA COLLECTION")
    print(f"{'='*60}")
    
    market_data, failed_symbols = optimizer.fetch_market_data_robust(all_symbols, batch_size=8, delay=2)
    
    if len(market_data) > 0:
        # Analyze current portfolio
        portfolio_metrics = optimizer.analyze_current_portfolio()
        
        # Screen universe for opportunities
        opportunities_df, top_opportunities = optimizer.screen_universe_opportunities()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        portfolio_metrics['analysis_df'].to_csv(f'results/portfolio_analysis_{timestamp}.csv', index=False)
        top_opportunities.to_csv(f'results/opportunities_{timestamp}.csv', index=False)
        
        print(f"\n💾 Results saved:")
        print(f"  Portfolio analysis: results/portfolio_analysis_{timestamp}.csv")
        print(f"  Opportunities: results/opportunities_{timestamp}.csv")
        
        print(f"\n✅ Phase 1 Complete - Portfolio Analysis & Universe Screening")
        print(f"Next: Generate optimization strategies and specific recommendations")
        
    else:
        print("❌ Insufficient market data for analysis")

if __name__ == "__main__":
    main() 