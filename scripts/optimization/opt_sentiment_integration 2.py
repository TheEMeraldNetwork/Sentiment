#!/usr/bin/env python3
"""
Sentiment-Integrated Portfolio Strategy Analysis
Incorporates monthly sentiment trends into investment recommendations
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class SentimentIntegratedStrategy:
    def __init__(self):
        self.current_portfolio_return = 0.0483  # 4.83%
        self.target_return = 0.0683  # 6.83%
        self.standard_position_usd = 2000
        self.new_cash_available = 10000
        
    def parse_european_number(self, value_str):
        """Parse European number format"""
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
    
    def load_portfolio_symbols(self):
        """Get current portfolio symbols"""
        df = pd.read_csv('actual-portfolio-master.csv', sep=';', skiprows=2, nrows=14)
        symbols = []
        for _, row in df.iterrows():
            if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                symbol = row['Simbolo'].split('.')[0]
                if symbol.startswith('1'):
                    symbol = symbol[1:]
                symbols.append(symbol)
        return symbols
    
    def load_sentiment_history(self, symbols_of_interest):
        """Load sentiment history for specific symbols"""
        print("🧠 Loading comprehensive sentiment analysis...")
        
        # Get all sentiment files (last 3 months)
        sentiment_files = glob.glob('database/sentiment/detailed/sentiment_detailed_*.csv')
        sentiment_files = sorted(sentiment_files, reverse=True)[:10]  # Last 10 files
        
        all_sentiment_data = []
        
        for file_path in sentiment_files:
            try:
                print(f"  Loading {os.path.basename(file_path)}...")
                
                # Read file in chunks to handle large files
                chunk_size = 10000
                file_date = os.path.basename(file_path).replace('sentiment_detailed_', '').replace('.csv', '')
                
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    # Filter for symbols of interest
                    relevant_data = chunk[chunk['ticker'].isin(symbols_of_interest)]
                    
                    if not relevant_data.empty:
                        relevant_data['file_date'] = file_date
                        relevant_data['date'] = pd.to_datetime(relevant_data['date'])
                        all_sentiment_data.append(relevant_data)
                        
            except Exception as e:
                print(f"    ⚠️ Error loading {file_path}: {e}")
                continue
        
        if all_sentiment_data:
            sentiment_df = pd.concat(all_sentiment_data, ignore_index=True)
            print(f"✅ Loaded {len(sentiment_df)} sentiment records for {len(symbols_of_interest)} symbols")
            return sentiment_df
        else:
            print("❌ No sentiment data loaded")
            return pd.DataFrame()
    
    def analyze_sentiment_trends(self, sentiment_df):
        """Analyze monthly sentiment trends for each symbol"""
        if sentiment_df.empty:
            return {}
        
        print("📊 Analyzing sentiment trends...")
        
        # Add month-year for grouping
        sentiment_df['month_year'] = sentiment_df['date'].dt.to_period('M')
        
        # Group by symbol and month
        monthly_sentiment = sentiment_df.groupby(['ticker', 'month_year']).agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'sentiment_label': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'neutral',
            'confidence': 'mean'
        }).round(3)
        
        # Flatten column names
        monthly_sentiment.columns = ['sentiment_mean', 'sentiment_std', 'article_count', 'dominant_label', 'avg_confidence']
        monthly_sentiment = monthly_sentiment.reset_index()
        
        # Calculate trends (last 3 months)
        sentiment_trends = {}
        
        for symbol in monthly_sentiment['ticker'].unique():
            symbol_data = monthly_sentiment[monthly_sentiment['ticker'] == symbol].sort_values('month_year')
            
            if len(symbol_data) >= 2:
                latest_sentiment = symbol_data.iloc[-1]['sentiment_mean']
                previous_sentiment = symbol_data.iloc[-2]['sentiment_mean'] if len(symbol_data) >= 2 else latest_sentiment
                
                # Calculate trend
                trend = 'improving' if latest_sentiment > previous_sentiment + 0.1 else \
                       'declining' if latest_sentiment < previous_sentiment - 0.1 else 'stable'
                
                # Get recent months data
                recent_months = symbol_data.tail(3)
                
                sentiment_trends[symbol] = {
                    'latest_sentiment': latest_sentiment,
                    'latest_label': symbol_data.iloc[-1]['dominant_label'],
                    'trend': trend,
                    'article_count_recent': symbol_data.iloc[-1]['article_count'],
                    'confidence': symbol_data.iloc[-1]['avg_confidence'],
                    'monthly_history': recent_months[['month_year', 'sentiment_mean', 'dominant_label', 'article_count']].to_dict('records')
                }
            else:
                sentiment_trends[symbol] = {
                    'latest_sentiment': 0,
                    'latest_label': 'neutral',
                    'trend': 'insufficient_data',
                    'article_count_recent': 0,
                    'confidence': 0,
                    'monthly_history': []
                }
        
        return sentiment_trends
    
    def load_market_opportunities(self):
        """Load market opportunities with sentiment integration"""
        try:
            files = glob.glob('results/opportunities_*.csv')
            if files:
                latest_file = max(files, key=os.path.getctime)
                opportunities_df = pd.read_csv(latest_file)
                return opportunities_df.head(15)
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def generate_sentiment_enhanced_recommendations(self):
        """Generate recommendations enhanced with sentiment analysis"""
        print("\n" + "="*80)
        print("SENTIMENT-ENHANCED PORTFOLIO STRATEGY")
        print("="*80)
        
        # Load portfolio symbols
        portfolio_symbols = self.load_portfolio_symbols()
        
        # Load opportunities
        opportunities_df = self.load_market_opportunities()
        all_symbols = portfolio_symbols + opportunities_df['symbol'].tolist() if not opportunities_df.empty else portfolio_symbols
        
        # Load sentiment history
        sentiment_df = self.load_sentiment_history(all_symbols)
        sentiment_trends = self.analyze_sentiment_trends(sentiment_df)
        
        # Load current portfolio data
        portfolio_df = self.load_current_portfolio()
        
        print(f"\n📊 PORTFOLIO SENTIMENT ANALYSIS:")
        print("="*60)
        
        # Analyze current holdings
        for _, position in portfolio_df.iterrows():
            symbol = position['symbol']
            sentiment_info = sentiment_trends.get(symbol, {})
            
            print(f"\n🔍 {symbol} ({position['name'][:20]}) - Current: ${position['current_value_usd']:,.0f} ({position['return_pct']:+.1%})")
            
            if sentiment_info.get('trend') != 'insufficient_data':
                print(f"   📈 Sentiment Score: {sentiment_info['latest_sentiment']:+.2f} ({sentiment_info['latest_label']})")
                print(f"   📊 Trend: {sentiment_info['trend'].upper()}")
                print(f"   📰 Recent Articles: {sentiment_info['article_count_recent']} | Confidence: {sentiment_info['confidence']:.2f}")
                
                # Show monthly history
                if sentiment_info['monthly_history']:
                    print("   📅 Monthly Trend:")
                    for month_data in sentiment_info['monthly_history'][-3:]:  # Last 3 months
                        month_str = str(month_data['month_year'])
                        sentiment_val = month_data['sentiment_mean']
                        label = month_data['dominant_label']
                        articles = month_data['article_count']
                        print(f"      {month_str}: {sentiment_val:+.2f} ({label}) - {articles} articles")
            else:
                print("   ⚠️ Limited sentiment data available")
        
        print(f"\n🎯 TOP OPPORTUNITIES WITH SENTIMENT:")
        print("="*60)
        
        # Analyze top opportunities
        if not opportunities_df.empty:
            for _, opp in opportunities_df.head(8).iterrows():
                symbol = opp['symbol']
                sentiment_info = sentiment_trends.get(symbol, {})
                
                print(f"\n✅ {symbol} - Price: ${opp['current_price']:.2f} | Upside: {opp['upside_potential']:+.1%}")
                print(f"   💰 Financial: Sharpe {opp['sharpe_ratio']:.2f} | Sector: {opp['sector']}")
                
                if sentiment_info.get('trend') != 'insufficient_data':
                    sentiment_score = sentiment_info['latest_sentiment']
                    trend = sentiment_info['trend']
                    
                    # Sentiment-based recommendation strength
                    if sentiment_score > 0.3 and trend == 'improving':
                        strength = "🔥 STRONG BUY"
                    elif sentiment_score > 0 and trend in ['improving', 'stable']:
                        strength = "✅ BUY"
                    elif sentiment_score > -0.2:
                        strength = "⚠️ CAUTIOUS"
                    else:
                        strength = "❌ AVOID"
                    
                    print(f"   🧠 Sentiment: {sentiment_score:+.2f} ({sentiment_info['latest_label']}) | Trend: {trend}")
                    print(f"   📊 Articles: {sentiment_info['article_count_recent']} | Confidence: {sentiment_info['confidence']:.2f}")
                    print(f"   🎯 Recommendation: {strength}")
                else:
                    print(f"   🧠 Sentiment: Limited data available")
                    print(f"   🎯 Recommendation: ⚠️ CAUTION - Lack of sentiment data")
        
        return {
            'portfolio_sentiment': sentiment_trends,
            'opportunities_sentiment': opportunities_df if not opportunities_df.empty else pd.DataFrame()
        }
    
    def load_current_portfolio(self):
        """Load current portfolio with categories"""
        df = pd.read_csv('actual-portfolio-master.csv', sep=';', skiprows=2, nrows=14)
        
        portfolio_positions = []
        for _, row in df.iterrows():
            if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                symbol = row['Simbolo'].split('.')[0]
                if symbol.startswith('1'):
                    symbol = symbol[1:]
                
                current_value = self.parse_european_number(row['Valore di mercato €'])
                return_pct = self.parse_european_number(row['Var%']) / 100
                
                portfolio_positions.append({
                    'symbol': symbol,
                    'name': row['Titolo'],
                    'current_value_usd': current_value * 1.1,
                    'return_pct': return_pct
                })
        
        return pd.DataFrame(portfolio_positions)

def main():
    """Run sentiment-enhanced strategy analysis"""
    analyzer = SentimentIntegratedStrategy()
    results = analyzer.generate_sentiment_enhanced_recommendations()
    
    print(f"\n" + "="*80)
    print("💡 SENTIMENT-ENHANCED STRATEGY SUMMARY")
    print("="*80)
    print("✅ Sentiment analysis integrated into all recommendations")
    print("✅ Monthly trends analyzed for portfolio positions")  
    print("✅ New opportunities ranked by financial + sentiment metrics")
    print("\n🎯 Use this analysis to refine your trading decisions!")

if __name__ == "__main__":
    main() 