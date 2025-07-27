#!/usr/bin/env python3
"""
Position Sizing Engine - Component E1
Converts optimal weights to specific share quantities and trade recommendations
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

class PositionSizer:
    """Convert optimal portfolio weights to actionable trade recommendations"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize position sizer"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # User specifications
        self.standard_position_size = 2000  # $2,000 standard position
        self.new_cash_usd = 10000          # $10,000 new cash
        self.eur_usd_rate = 1.1           # Approximate EUR/USD rate
        self.stop_loss_pct = 0.08          # 8% stop loss
    
    def parse_european_number(self, value_str):
        """Parse European number format"""
        if pd.isna(value_str) or value_str == '' or str(value_str).strip() == '':
            return 0.0
        
        value_str = str(value_str).strip()
        
        if ',' in value_str and '.' in value_str:
            parts = value_str.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                value_str = integer_part + '.' + decimal_part
        elif ',' in value_str:
            value_str = value_str.replace(',', '.')
            
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def load_current_positions(self, portfolio_file="actual-portfolio-master.csv"):
        """
        Load current portfolio positions
        
        Returns:
            Dict with current positions
        """
        try:
            df = pd.read_csv(portfolio_file, sep=';', skiprows=2, nrows=20)
            
            positions = {}
            total_value_eur = 0
            
            for _, row in df.iterrows():
                if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                    # Clean symbol
                    symbol = row['Simbolo'].split('.')[0]
                    if symbol.startswith('1'):
                        symbol = symbol[1:]
                    
                    # Parse values
                    quantity = self.parse_european_number(row['Quantità'])
                    current_value_eur = self.parse_european_number(row['Valore di mercato €'])
                    cost_basis_eur = self.parse_european_number(row['Valore di carico'])
                    return_pct = self.parse_european_number(row['Var%'])
                    
                    positions[symbol] = {
                        'name': row['Titolo'],
                        'current_shares': quantity,
                        'current_value_eur': current_value_eur,
                        'cost_basis_eur': cost_basis_eur,
                        'return_pct': return_pct / 100,
                        'current_weight': 0  # Will calculate after total
                    }
                    
                    total_value_eur += current_value_eur
            
            # Calculate current weights
            for symbol in positions:
                positions[symbol]['current_weight'] = positions[symbol]['current_value_eur'] / total_value_eur
            
            self.logger.info(f"📊 Loaded {len(positions)} current positions")
            self.logger.info(f"💰 Total portfolio value: €{total_value_eur:,.2f}")
            
            return {
                'positions': positions,
                'total_value_eur': total_value_eur,
                'total_value_usd': total_value_eur * self.eur_usd_rate
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load current positions: {e}")
            return None
    
    def calculate_target_positions(self, optimal_weights: pd.Series, market_data: Dict,
                                 current_positions: Dict, sentiment_data: Dict = None) -> Dict:
        """
        Calculate target positions based on optimal weights
        
        Args:
            optimal_weights: Optimal portfolio weights from optimization
            market_data: Market data with current prices
            current_positions: Current portfolio positions
            
        Returns:
            Dict with target positions and trade recommendations
        """
        # Total portfolio value in USD (current + new cash)
        total_current_usd = current_positions['total_value_usd']
        total_target_usd = total_current_usd + self.new_cash_usd
        
        self.logger.info(f"💰 Total target portfolio: ${total_target_usd:,.2f}")
        
        trade_recommendations = {}
        
        for symbol in optimal_weights.index:
            if symbol not in market_data or not market_data[symbol]['success']:
                continue
            
            current_price_usd = market_data[symbol]['current_price']
            target_weight = optimal_weights[symbol]
            target_value_usd = target_weight * total_target_usd
            
            # Current position info
            current_shares = 0
            current_value_usd = 0
            current_weight = 0
            
            if symbol in current_positions['positions']:
                pos = current_positions['positions'][symbol]
                current_shares = pos['current_shares']
                current_value_usd = pos['current_value_eur'] * self.eur_usd_rate
                current_weight = current_value_usd / total_current_usd
            
            # Calculate target shares
            target_shares = target_value_usd / current_price_usd
            shares_change = target_shares - current_shares
            value_change_usd = shares_change * current_price_usd
            
            # Get additional context for smart decisions
            current_return = 0
            if symbol in current_positions['positions']:
                current_return = current_positions['positions'][symbol]['return_pct']
            
            volatility = market_data[symbol].get('volatility', 0.0)
            sentiment_info = sentiment_data.get(symbol, {'sentiment_score': 0.0, 'trend': 'neutral'}) if sentiment_data else {'sentiment_score': 0.0, 'trend': 'neutral'}
            
            # Determine action with intelligent logic
            action = 'HOLD'
            
            if abs(shares_change) < 0.1:  # Minimal change
                action = 'HOLD'
                rationale = self._generate_smart_rationale(symbol, 'HOLD', current_return, volatility, sentiment_info, current_weight, target_weight)
            elif shares_change > 0:
                if current_shares == 0:
                    action = 'BUY'
                    rationale = self._generate_smart_rationale(symbol, 'BUY', current_return, volatility, sentiment_info, current_weight, target_weight)
                else:
                    # Check positive return constraint - use as backup only
                    if current_return > 0:
                        action = 'TOP_UP_BACKUP'  # Mark for lower priority
                        rationale = f"BACKUP: Positive return stock ({current_return:+.1%}) - consider only if budget remains after new opportunities"
                    else:
                        action = 'ADD'
                        rationale = self._generate_smart_rationale(symbol, 'ADD', current_return, volatility, sentiment_info, current_weight, target_weight)
            else:
                # Smart logic for reducing positions - be conservative with winners
                is_strong_winner = current_return > 0.20  # 20%+ gain
                is_large_position = current_weight > 0.15  # Large position
                has_positive_sentiment = sentiment_info['sentiment_score'] > 0.1
                
                # Fix floating point precision: treat very small numbers as zero
                effective_target_shares = target_shares if abs(target_shares) > 1e-10 else 0.0
                
                # Primary check: if target is essentially zero or very small, it's a SELL
                if effective_target_shares < current_shares * 0.1:  # Selling most/all (90%+)
                    action = 'SELL'
                    rationale = self._generate_smart_rationale(symbol, 'SELL', current_return, volatility, sentiment_info, current_weight, target_weight)
                elif is_strong_winner and is_large_position and has_positive_sentiment:
                    # For strong performers with positive sentiment, prefer stops over selling
                    if effective_target_shares > current_shares * 0.8:  # Only small reduction
                        action = 'HOLD'
                        rationale = f"Strong performer ({current_return:.1%} gain) with positive sentiment - maintain position with stop loss protection rather than selling"
                    else:
                        action = 'TRIM'
                        rationale = self._generate_smart_rationale(symbol, 'TRIM', current_return, volatility, sentiment_info, current_weight, target_weight)
                else:
                    action = 'TRIM'
                    rationale = self._generate_smart_rationale(symbol, 'TRIM', current_return, volatility, sentiment_info, current_weight, target_weight)
            
            # Calculate stop loss
            stop_loss_price = current_price_usd * (1 - self.stop_loss_pct)
            
            # Compile recommendation
            trade_recommendations[symbol] = {
                'name': market_data[symbol].get('info', {}).get('longName', symbol),
                'current_price': current_price_usd,
                'current_shares': current_shares,
                'target_shares': target_shares,
                'shares_change': shares_change,
                'current_weight': current_weight,
                'target_weight': target_weight,
                'current_value_usd': current_value_usd,
                'target_value_usd': target_value_usd,
                'value_change_usd': value_change_usd,
                'action': action,
                'rationale': rationale,
                'stop_loss_price': stop_loss_price,
                'volatility': market_data[symbol].get('volatility', 0.0)
            }
        
        # Calculate cash usage with breakdown by action type
        total_purchases = sum(
            rec['value_change_usd'] for rec in trade_recommendations.values()
            if rec['value_change_usd'] > 0
        )
        
        total_sales = sum(
            abs(rec['value_change_usd']) for rec in trade_recommendations.values()
            if rec['value_change_usd'] < 0
        )
        
        # Break down sales by action type
        trim_proceeds = sum(
            abs(rec['value_change_usd']) for rec in trade_recommendations.values()
            if rec['value_change_usd'] < 0 and rec['action'] == 'TRIM'
        )
        
        sell_proceeds = sum(
            abs(rec['value_change_usd']) for rec in trade_recommendations.values()
            if rec['value_change_usd'] < 0 and rec['action'] == 'SELL'
        )
        
        # Net Cash Position = Total Purchases (negative) - Cash from Sales (positive)
        # When cash flows out for purchases, the net position should be negative
        net_cash_position = total_purchases - total_sales  # This is the net outflow
        
        self.logger.info(f"💰 Total purchases: ${total_purchases:,.2f}")
        self.logger.info(f"💰 Total sales: ${total_sales:,.2f}")
        self.logger.info(f"💰 Net cash position: ${net_cash_position:,.2f}")
        self.logger.info(f"💰 Available new cash: ${self.new_cash_usd:,.2f}")
        
        return {
            'recommendations': trade_recommendations,
            'portfolio_summary': {
                'total_current_usd': total_current_usd,
                'total_target_usd': total_target_usd,
                'new_cash_usd': self.new_cash_usd,
                'total_purchases': total_purchases,
                'total_sales': total_sales,
                'trim_proceeds': trim_proceeds,
                'sell_proceeds': sell_proceeds,
                'net_cash_used': net_cash_position,
                'remaining_cash': self.new_cash_usd - net_cash_position
            }
        }
    
    def generate_action_summary(self, trade_recommendations: Dict) -> Dict:
        """
        Generate summary of actions by type with backup processing
        
        Returns:
            Dict with action summary
        """
        actions = {'BUY': [], 'ADD': [], 'HOLD': [], 'TRIM': [], 'SELL': [], 'TOP_UP_BACKUP': []}
        
        # First pass: categorize all actions
        for symbol, rec in trade_recommendations.items():
            actions[rec['action']].append({
                'symbol': symbol,
                'name': rec['name'],
                'shares_change': rec['shares_change'],
                'value_change_usd': rec['value_change_usd'],
                'rationale': rec['rationale']
            })
        
        # Calculate primary cash usage (exclude backups)
        primary_purchases = sum(
            item['value_change_usd'] for action in ['BUY', 'ADD'] 
            for item in actions[action] if item['value_change_usd'] > 0
        )
        
        sales_proceeds = sum(
            abs(item['value_change_usd']) for action in ['TRIM', 'SELL'] 
            for item in actions[action] if item['value_change_usd'] < 0
        )
        
        net_primary_cost = primary_purchases - sales_proceeds
        remaining_budget = self.new_cash_usd - net_primary_cost
        
        # Process backups if budget remains
        processed_backups = 0
        if remaining_budget > 1000:  # Need at least $1000 for meaningful positions
            backup_items = sorted(actions['TOP_UP_BACKUP'], 
                                key=lambda x: x['value_change_usd'], reverse=True)
            
            for backup in backup_items:
                if remaining_budget >= backup['value_change_usd']:
                    # Convert to ADD action
                    actions['ADD'].append({
                        **backup,
                        'rationale': f"TOP UP: {backup['rationale']}"
                    })
                    remaining_budget -= backup['value_change_usd']
                    processed_backups += 1
                    
                    if remaining_budget < 1000:  # Stop if budget too low
                        break
        
        # Generate final summary
        summary = {}
        for action, items in actions.items():
            if action != 'TOP_UP_BACKUP':  # Don't include unprocessed backups in final summary
                summary[action] = {
                    'count': len(items),
                    'total_value': sum(item['value_change_usd'] for item in items),
                    'items': items
                }
        
        # Add backup processing info
        summary['BACKUP_INFO'] = {
            'backups_available': len(actions['TOP_UP_BACKUP']),
            'backups_processed': processed_backups,
            'remaining_budget': remaining_budget,
            'total_backup_value': sum(item['value_change_usd'] for item in actions['TOP_UP_BACKUP'])
        }
        
        return summary
    
    def calculate_dynamic_stop_losses(self, trade_recommendations: Dict, 
                                    volatility_factor: float = 2.0) -> Dict:
        """
        Calculate dynamic stop losses based on volatility
        
        Args:
            trade_recommendations: Trade recommendations
            volatility_factor: Multiplier for volatility-based stops
            
        Returns:
            Updated recommendations with dynamic stops
        """
        updated_recs = trade_recommendations.copy()
        
        for symbol, rec in updated_recs.items():
            volatility = rec['volatility']
            current_price = rec['current_price']
            
            # Dynamic stop based on volatility
            volatility_stop_pct = min(volatility * volatility_factor, 0.15)  # Max 15%
            dynamic_stop_price = current_price * (1 - volatility_stop_pct)
            
            # Use the more conservative of fixed 8% or dynamic stop
            conservative_stop = min(rec['stop_loss_price'], dynamic_stop_price)
            
            rec['dynamic_stop_price'] = dynamic_stop_price
            rec['final_stop_price'] = conservative_stop
            rec['stop_loss_pct'] = (current_price - conservative_stop) / current_price
        
        return updated_recs
    
    def _generate_smart_rationale(self, symbol: str, action: str, current_return: float, 
                                volatility: float, sentiment_info: Dict, 
                                current_weight: float, target_weight: float) -> str:
        """
        Generate intelligent AI-like rationale based on all available information
        
        Args:
            symbol: Stock symbol
            action: Recommended action
            current_return: Current position return
            volatility: Stock volatility
            sentiment_info: Sentiment data
            current_weight: Current portfolio weight
            target_weight: Target portfolio weight
            
        Returns:
            Intelligent rationale string
        """
        sentiment_score = sentiment_info['sentiment_score']
        sentiment_trend = sentiment_info['trend']
        
        # Performance categorization
        if current_return > 0.20:
            performance = "strong winner"
        elif current_return > 0.05:
            performance = "solid performer"
        elif current_return > -0.05:
            performance = "stable position"
        else:
            performance = "underperformer"
        
        # Volatility assessment
        if volatility > 0.30:
            vol_desc = "high volatility"
        elif volatility > 0.20:
            vol_desc = "moderate volatility"
        else:
            vol_desc = "low volatility"
        
        # Sentiment assessment
        if sentiment_score > 0.1:
            sentiment_desc = f"positive sentiment ({sentiment_score:.2f})"
        elif sentiment_score < -0.1:
            sentiment_desc = f"negative sentiment ({sentiment_score:.2f})"
        else:
            sentiment_desc = "neutral sentiment"
        
        # Generate action-specific rationale
        if action == 'BUY':
            return f"New opportunity: {vol_desc} stock with {sentiment_desc} and {sentiment_trend} trend. Optimal allocation at {target_weight:.1%}"
        
        elif action == 'ADD':
            return f"Increase {performance} from {current_weight:.1%} to {target_weight:.1%} - {sentiment_desc} supports expansion with {sentiment_trend} momentum"
        
        elif action == 'HOLD':
            if current_return > 0.15:
                return f"Maintain {performance} ({current_return:+.1%}) - {sentiment_desc} with {sentiment_trend} trend supports current {current_weight:.1%} allocation"
            else:
                return f"Hold steady - balanced risk/reward profile with {sentiment_desc} and {vol_desc} characteristics"
        
        elif action == 'TRIM':
            weight_change = target_weight - current_weight
            if current_return > 0.10:
                return f"Take profits on {performance} ({current_return:+.1%}) - reduce by {abs(weight_change):.1%} while maintaining core position due to {sentiment_desc}"
            else:
                return f"Rebalance overweight position - reduce {vol_desc} exposure from {current_weight:.1%} to {target_weight:.1%} given {sentiment_desc}"
        
        elif action == 'SELL':
            if current_return < -0.10:
                return f"Exit {performance} ({current_return:+.1%}) - {sentiment_desc} with {sentiment_trend} trend suggests limited recovery potential"
            else:
                return f"Portfolio rebalancing - reallocate capital from {vol_desc} position to higher-conviction opportunities"
        
        else:
            return f"Optimize allocation based on {sentiment_desc} and {vol_desc} profile"

def main():
    """Test position sizing engine"""
    print("💰 POSITION SIZING ENGINE TEST")
    print("=" * 50)
    
    # Initialize position sizer
    sizer = PositionSizer()
    
    # Load current positions
    current_positions = sizer.load_current_positions()
    
    if current_positions:
        print(f"✅ Loaded portfolio: €{current_positions['total_value_eur']:,.2f}")
        
        # Create mock optimal weights for testing
        symbols = list(current_positions['positions'].keys())[:5]  # First 5 for testing
        mock_weights = pd.Series([0.25, 0.20, 0.20, 0.20, 0.15], index=symbols)
        
        # Create mock market data
        mock_market_data = {}
        for symbol in symbols:
            mock_market_data[symbol] = {
                'success': True,
                'current_price': 100.0,  # Mock price
                'volatility': 0.25,      # Mock volatility
                'info': {'longName': f'{symbol} Corp'}
            }
        
        # Calculate target positions
        sizing_result = sizer.calculate_target_positions(
            mock_weights, mock_market_data, current_positions
        )
        
        print(f"\n📊 Portfolio Summary:")
        summary = sizing_result['portfolio_summary']
        print(f"  Current Value: ${summary['total_current_usd']:,.2f}")
        print(f"  Target Value: ${summary['total_target_usd']:,.2f}")
        print(f"  Net Cash Used: ${summary['net_cash_used']:,.2f}")
        
        # Show action summary
        action_summary = sizer.generate_action_summary(sizing_result['recommendations'])
        print(f"\n📋 Actions Summary:")
        for action, info in action_summary.items():
            if info['count'] > 0:
                print(f"  {action}: {info['count']} positions, ${info['total_value']:,.2f}")
        
        return sizing_result
    
    else:
        print("❌ Failed to load current positions")
        return None

if __name__ == "__main__":
    main() 