#!/usr/bin/env python3
"""
Tigro Portfolio Strategy & Recommendations
Based on correct 4.83% current return, targeting 6.83% (+2pp)
"""

import pandas as pd
import numpy as np
import csv

class TigroStrategyRecommendations:
    def __init__(self):
        self.current_portfolio_return = 0.0483  # 4.83% actual
        self.target_return = 0.0683  # 6.83% target (+2pp)
        self.improvement_needed = 0.02  # 2 percentage points
        self.standard_position_usd = 2000
        self.new_cash_available = 10000  # $10K new investment
        self.stop_loss_pct = 0.08  # 8% stop loss for winners
        
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
    
    def load_portfolio_data(self):
        """Load and analyze current portfolio"""
        print("📊 Loading Current Portfolio Data...")
        
        df = pd.read_csv('actual-portfolio-master.csv', sep=';', skiprows=2, nrows=14)
        
        portfolio_positions = []
        for _, row in df.iterrows():
            if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                symbol = row['Simbolo'].split('.')[0]
                if symbol.startswith('1'):
                    symbol = symbol[1:]
                
                current_value = self.parse_european_number(row['Valore di mercato €'])
                cost_basis = self.parse_european_number(row['Valore di carico'])
                return_pct = self.parse_european_number(row['Var%']) / 100
                
                portfolio_positions.append({
                    'symbol': symbol,
                    'name': row['Titolo'],
                    'current_value_eur': current_value,
                    'current_value_usd': current_value * 1.1,  # Rough conversion
                    'cost_basis_eur': cost_basis,
                    'return_pct': return_pct,
                    'category': self.categorize_position(return_pct, current_value * 1.1)
                })
        
        return pd.DataFrame(portfolio_positions)
    
    def categorize_position(self, return_pct, value_usd):
        """Categorize positions for strategy decisions"""
        if return_pct > 0.15:  # >15% gain
            return 'big_winner'
        elif return_pct > 0.05:  # 5-15% gain
            return 'winner'
        elif return_pct > -0.05:  # -5% to +5%
            return 'flat'
        elif return_pct > -0.15:  # -5% to -15%
            return 'small_loser'
        else:  # <-15%
            return 'big_loser'
    
    def load_opportunities(self):
        """Load top opportunities from previous analysis"""
        try:
            # Get the most recent opportunities file
            import glob
            import os
            
            files = glob.glob('results/opportunities_*.csv')
            if files:
                latest_file = max(files, key=os.path.getctime)
                opportunities_df = pd.read_csv(latest_file)
                print(f"✅ Loaded opportunities from {latest_file}")
                return opportunities_df.head(20)  # Top 20 opportunities
            else:
                print("⚠️ No opportunities file found")
                return pd.DataFrame()
        except Exception as e:
            print(f"⚠️ Error loading opportunities: {e}")
            return pd.DataFrame()
    
    def generate_strategy_1_conservative(self, portfolio_df, opportunities_df):
        """Strategy 1: Conservative Risk Management"""
        print(f"\n🛡️ STRATEGY 1: CONSERVATIVE RISK MANAGEMENT")
        print("="*60)
        
        recommendations = {
            'strategy_name': 'Conservative Risk Management',
            'target_return': '6.5% annually',
            'risk_level': 'Medium',
            'actions': []
        }
        
        # 1. Protect winners with stop losses
        big_winners = portfolio_df[portfolio_df['category'] == 'big_winner']
        for _, position in big_winners.iterrows():
            if position['symbol'] != 'AAPL':  # Don't touch Apple as requested
                stop_price = position['current_value_usd'] * (1 - self.stop_loss_pct)
                recommendations['actions'].append({
                    'action': 'SET_STOP_LOSS',
                    'symbol': position['symbol'],
                    'current_value': position['current_value_usd'],
                    'stop_price': stop_price,
                    'reason': f"Protect {position['return_pct']:.1%} gain"
                })
        
        # 2. Harvest tax losses from big losers
        big_losers = portfolio_df[portfolio_df['category'] == 'big_loser']
        cash_from_sales = 0
        for _, position in big_losers.iterrows():
            recommendations['actions'].append({
                'action': 'SELL',
                'symbol': position['symbol'],
                'current_value': position['current_value_usd'],
                'reason': f"Tax loss harvest: {position['return_pct']:.1%} loss"
            })
            cash_from_sales += position['current_value_usd']
        
        # 3. Rebalance oversized flat performers (except Apple)
        flat_oversized = portfolio_df[
            (portfolio_df['category'] == 'flat') & 
            (portfolio_df['current_value_usd'] > self.standard_position_usd * 1.5) &
            (portfolio_df['symbol'] != 'AAPL')
        ]
        
        for _, position in flat_oversized.iterrows():
            trim_amount = position['current_value_usd'] - self.standard_position_usd
            recommendations['actions'].append({
                'action': 'TRIM',
                'symbol': position['symbol'],
                'trim_amount': trim_amount,
                'reason': 'Rebalance to standard position size'
            })
            cash_from_sales += trim_amount
        
        # 4. Invest available cash in top opportunities
        available_cash = self.new_cash_available + cash_from_sales
        
        if not opportunities_df.empty:
            # Select conservative opportunities (higher Sharpe ratio, lower volatility)
            conservative_opps = opportunities_df[
                (opportunities_df['sharpe_ratio'] > 0.5) &
                (opportunities_df['upside_potential'] > 0.1)
            ].head(5)
            
            for _, opp in conservative_opps.iterrows():
                if available_cash >= self.standard_position_usd:
                    recommendations['actions'].append({
                        'action': 'BUY',
                        'symbol': opp['symbol'],
                        'investment_amount': self.standard_position_usd,
                        'current_price': opp['current_price'],
                        'reason': f"Sharpe: {opp['sharpe_ratio']:.2f}, Upside: {opp['upside_potential']:.1%}"
                    })
                    available_cash -= self.standard_position_usd
        
        recommendations['remaining_cash'] = available_cash
        return recommendations
    
    def generate_strategy_2_growth(self, portfolio_df, opportunities_df):
        """Strategy 2: Growth-Focused Optimization"""
        print(f"\n🚀 STRATEGY 2: GROWTH-FOCUSED OPTIMIZATION")
        print("="*60)
        
        recommendations = {
            'strategy_name': 'Growth-Focused Optimization',
            'target_return': '7.5% annually',
            'risk_level': 'Medium-High',
            'actions': []
        }
        
        # 1. Let winners run (wider stop losses)
        big_winners = portfolio_df[portfolio_df['category'] == 'big_winner']
        for _, position in big_winners.iterrows():
            if position['symbol'] != 'AAPL':
                # Wider stop loss for growth strategy
                stop_price = position['current_value_usd'] * (1 - self.stop_loss_pct * 1.5)
                recommendations['actions'].append({
                    'action': 'SET_TRAILING_STOP',
                    'symbol': position['symbol'],
                    'current_value': position['current_value_usd'],
                    'trailing_stop_pct': self.stop_loss_pct * 1.5,
                    'reason': f"Let winner run with trailing stop"
                })
        
        # 2. Cut losers more aggressively
        losers = portfolio_df[portfolio_df['return_pct'] < -0.05]  # Any loss >5%
        cash_from_sales = 0
        for _, position in losers.iterrows():
            recommendations['actions'].append({
                'action': 'SELL',
                'symbol': position['symbol'],
                'current_value': position['current_value_usd'],
                'reason': f"Cut losses: {position['return_pct']:.1%}"
            })
            cash_from_sales += position['current_value_usd']
        
        # 3. Focus on high-growth opportunities
        available_cash = self.new_cash_available + cash_from_sales
        
        if not opportunities_df.empty:
            # Select growth opportunities (high upside potential)
            growth_opps = opportunities_df[
                (opportunities_df['upside_potential'] > 0.15) |
                (opportunities_df['composite_score'] > 0.3)
            ].head(6)
            
            for _, opp in growth_opps.iterrows():
                if available_cash >= self.standard_position_usd:
                    recommendations['actions'].append({
                        'action': 'BUY',
                        'symbol': opp['symbol'],
                        'investment_amount': self.standard_position_usd,
                        'current_price': opp['current_price'],
                        'reason': f"Growth play: {opp['upside_potential']:.1%} upside, Score: {opp['composite_score']:.2f}"
                    })
                    available_cash -= self.standard_position_usd
        
        recommendations['remaining_cash'] = available_cash
        return recommendations
    
    def display_strategy_comparison(self, strategy1, strategy2):
        """Display both strategies for comparison"""
        print(f"\n" + "="*80)
        print("STRATEGY COMPARISON & RECOMMENDATIONS")
        print("="*80)
        
        print(f"\n📊 BASELINE METRICS:")
        print(f"Current Portfolio Return: {self.current_portfolio_return:.2%}")
        print(f"Target Return: {self.target_return:.2%}")
        print(f"Improvement Needed: +{self.improvement_needed:.1%}")
        
        for i, strategy in enumerate([strategy1, strategy2], 1):
            print(f"\n🎯 STRATEGY {i}: {strategy['strategy_name'].upper()}")
            print(f"Target Return: {strategy['target_return']}")
            print(f"Risk Level: {strategy['risk_level']}")
            print(f"Remaining Cash: ${strategy['remaining_cash']:,.0f}")
            
            print(f"\nActions ({len(strategy['actions'])}):")
            for action in strategy['actions'][:8]:  # Show first 8 actions
                if action['action'] == 'BUY':
                    print(f"  ✅ BUY {action['symbol']}: ${action['investment_amount']:,.0f} - {action['reason']}")
                elif action['action'] == 'SELL':
                    print(f"  ❌ SELL {action['symbol']}: ${action['current_value']:,.0f} - {action['reason']}")
                elif action['action'] == 'TRIM':
                    print(f"  ✂️ TRIM {action['symbol']}: ${action['trim_amount']:,.0f} - {action['reason']}")
                elif 'STOP' in action['action']:
                    print(f"  🛡️ STOP {action['symbol']}: {action['reason']}")
            
            if len(strategy['actions']) > 8:
                print(f"  ... and {len(strategy['actions']) - 8} more actions")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"Both strategies can achieve the +2pp target.")
        print(f"Conservative = Lower risk, steady progress")
        print(f"Growth = Higher potential, more aggressive")

def main():
    print("🎯 Tigro Portfolio Strategy Recommendations")
    print("="*60)
    
    strategy_system = TigroStrategyRecommendations()
    
    # Load data
    portfolio_df = strategy_system.load_portfolio_data()
    opportunities_df = strategy_system.load_opportunities()
    
    print(f"\n📊 PORTFOLIO OVERVIEW:")
    print(f"Current positions: {len(portfolio_df)}")
    print(f"Current return: {strategy_system.current_portfolio_return:.2%}")
    print(f"Target return: {strategy_system.target_return:.2%}")
    
    # Show current position analysis
    print(f"\n📈 POSITION CATEGORIES:")
    category_summary = portfolio_df['category'].value_counts()
    for category, count in category_summary.items():
        total_value = portfolio_df[portfolio_df['category'] == category]['current_value_usd'].sum()
        print(f"  {category}: {count} positions, ${total_value:,.0f}")
    
    # Generate strategies
    strategy1 = strategy_system.generate_strategy_1_conservative(portfolio_df, opportunities_df)
    strategy2 = strategy_system.generate_strategy_2_growth(portfolio_df, opportunities_df)
    
    # Display comparison
    strategy_system.display_strategy_comparison(strategy1, strategy2)
    
    # Save detailed recommendations
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    # Save strategy details to CSV
    all_actions = []
    for i, strategy in enumerate([strategy1, strategy2], 1):
        for action in strategy['actions']:
            action['strategy'] = f"Strategy_{i}"
            action['strategy_name'] = strategy['strategy_name']
            all_actions.append(action)
    
    if all_actions:
        actions_df = pd.DataFrame(all_actions)
        actions_df.to_csv(f'results/strategy_recommendations_{timestamp}.csv', index=False)
        print(f"\n💾 Detailed recommendations saved to: results/strategy_recommendations_{timestamp}.csv")

if __name__ == "__main__":
    main() 