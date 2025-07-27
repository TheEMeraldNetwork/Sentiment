#!/usr/bin/env python3
"""
Two-Phase Portfolio Optimization Engine
Implements pure Markowitz optimization followed by strategic adjustment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

# Import existing components
from optimization.opt_rigorous_portfolio_master import RigorousPortfolioOptimizer
from optimization.opt_position_sizer import PositionSizer

class TwoPhaseOptimizer:
    """
    Advanced two-phase portfolio optimization system
    Phase 1: Pure Markowitz optimization
    Phase 2: Strategic adjustment respecting order and constraints
    """
    
    def __init__(self, log_level=logging.INFO):
        """Initialize two-phase optimizer"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Initialize base components
        self.base_optimizer = RigorousPortfolioOptimizer(log_level)
        self.position_sizer = PositionSizer(log_level)
        
        # Phase tracking
        self.phase1_results = None
        self.phase2_results = None
        self.strategic_conflicts = []
        
        # Constraints from requirements
        self.max_cash_investment = 10000  # $10K limit
        self.sector_limit = 0.40  # 40% max per sector
        
    def run_complete_optimization(self) -> Dict:
        """
        Execute complete two-phase optimization process
        
        Returns:
            Dict with comprehensive results from both phases
        """
        self.logger.info("🚀 STARTING TWO-PHASE OPTIMIZATION")
        self.logger.info("=" * 60)
        
        # Phase 1: Pure Markowitz
        phase1_success = self._execute_phase1()
        if not phase1_success:
            return {'success': False, 'message': 'Phase 1 optimization failed'}
        
        # Phase 2: Strategic Adjustment  
        phase2_success = self._execute_phase2()
        if not phase2_success:
            return {'success': False, 'message': 'Phase 2 strategic adjustment failed'}
        
        # Compare and analyze phases
        comparison = self._compare_phases()
        
        # Generate final recommendations
        final_recommendations = self._generate_final_recommendations()
        
        return {
            'success': True,
            'phase1_results': self.phase1_results,
            'phase2_results': self.phase2_results,
            'strategic_conflicts': self.strategic_conflicts,
            'phase_comparison': comparison,
            'final_recommendations': final_recommendations,
            'timestamp': datetime.now()
        }
    
    def _execute_phase1(self) -> bool:
        """
        Phase 1: Pure Markowitz optimization without strategic constraints
        """
        self.logger.info("📊 PHASE 1: Pure Markowitz Optimization")
        self.logger.info("-" * 40)
        
        try:
            # Run optimization with full universe
            results = self.base_optimizer.optimize_portfolio(include_universe=True)
            
            if not results['success']:
                self.logger.error("❌ Phase 1 optimization failed")
                return False
            
            self.phase1_results = results
            
            # Log Phase 1 summary
            weights = results['optimization_result']['weights']
            self.logger.info(f"✅ Phase 1 complete: {len(weights)} positions optimized")
            self.logger.info(f"📈 Expected return: {results['optimization_result']['expected_return']:.4f}")
            self.logger.info(f"📊 Volatility: {results['optimization_result']['volatility']:.4f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Phase 1 failed: {e}")
            return False
    
    def _execute_phase2(self) -> bool:
        """
        Phase 2: Strategic adjustment respecting SELL→TRIM→BUY NEW→TOP UP order
        """
        self.logger.info("🎯 PHASE 2: Strategic Adjustment")
        self.logger.info("-" * 40)
        
        try:
            # Load current positions for comparison
            current_positions = self.position_sizer.load_current_positions()
            if not current_positions:
                return False
            
            # Get Phase 1 optimal weights
            phase1_weights = self.phase1_results['optimization_result']['weights']
            market_data = self.phase1_results['market_data']
            sentiment_data = self.phase1_results['sentiment_data']
            
            # Calculate strategic adjustments
            strategic_recommendations = self._calculate_strategic_positions(
                phase1_weights, current_positions, market_data, sentiment_data
            )
            
            # Apply two-phase position sizing with strategic constraints
            phase2_sizing = self.position_sizer.calculate_target_positions(
                strategic_recommendations['adjusted_weights'],
                market_data,
                current_positions, 
                sentiment_data
            )
            
            self.phase2_results = {
                'strategic_weights': strategic_recommendations['adjusted_weights'],
                'action_classification': strategic_recommendations['action_classification'],
                'sizing_results': phase2_sizing,
                'cash_usage': phase2_sizing['portfolio_summary']['net_cash_used'],
                'budget_compliance': abs(phase2_sizing['portfolio_summary']['net_cash_used']) <= self.max_cash_investment
            }
            
            self.logger.info(f"✅ Phase 2 complete: Strategic adjustment applied")
            self.logger.info(f"💰 Net cash usage: ${self.phase2_results['cash_usage']:,.2f}")
            self.logger.info(f"✅ Budget compliance: {self.phase2_results['budget_compliance']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Phase 2 failed: {e}")
            return False
    
    def _calculate_strategic_positions(self, phase1_weights: pd.Series, 
                                     current_positions: Dict, market_data: Dict, 
                                     sentiment_data: Dict) -> Dict:
        """
        Calculate strategic adjustments to Phase 1 weights
        Respects SELL→TRIM→BUY NEW→TOP UP order
        """
        self.logger.info("🎲 Calculating strategic position adjustments...")
        
        # Initialize tracking
        action_classification = {
            'SELL': [],
            'TRIM': [], 
            'BUY_NEW': [],
            'TOP_UP_BACKUP': [],
            'HOLD': []
        }
        
        adjusted_weights = phase1_weights.copy()
        total_current_value = current_positions['total_value_usd']
        
        # Analyze each position vs Phase 1 optimal
        for symbol in phase1_weights.index:
            if symbol not in market_data or not market_data[symbol]['success']:
                continue
                
            phase1_weight = phase1_weights[symbol]
            current_weight = 0
            current_return = 0
            
            # Get current position info
            if symbol in current_positions['positions']:
                pos = current_positions['positions'][symbol]
                current_weight = pos['current_weight']
                current_return = pos['return_pct']
            
            # Determine strategic action
            action = self._classify_strategic_action(
                symbol, phase1_weight, current_weight, current_return,
                sentiment_data.get(symbol, {}), market_data[symbol]
            )
            
            action_classification[action].append({
                'symbol': symbol,
                'phase1_weight': phase1_weight,
                'current_weight': current_weight,
                'current_return': current_return,
                'weight_change': phase1_weight - current_weight
            })
            
            # Apply strategic constraints to weights
            adjusted_weights[symbol] = self._apply_strategic_constraint(
                symbol, phase1_weight, current_weight, action
            )
        
        # Normalize adjusted weights
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return {
            'adjusted_weights': adjusted_weights,
            'action_classification': action_classification
        }
    
    def _classify_strategic_action(self, symbol: str, phase1_weight: float, 
                                 current_weight: float, current_return: float,
                                 sentiment_info: Dict, market_data: Dict) -> str:
        """
        Classify each position into strategic action categories
        """
        weight_change = phase1_weight - current_weight
        sentiment_score = sentiment_info.get('sentiment_score', 0.0)
        
        # SELL criteria: Large reduction + negative factors
        if (phase1_weight < current_weight * 0.1 or  # >90% reduction
            (sentiment_score < -0.2 and current_return < -0.1)):  # Negative sentiment + loss
            return 'SELL'
        
        # TRIM criteria: Moderate reduction for risk management
        elif weight_change < -0.05:  # Reducing by >5%
            return 'TRIM'
        
        # BUY NEW criteria: New positions or adding to non-profitable
        elif current_weight == 0:  # New position
            return 'BUY_NEW'
        elif weight_change > 0 and current_return <= 0:  # Adding to breakeven/loss positions
            return 'BUY_NEW'
        
        # TOP UP BACKUP criteria: Adding to profitable positions (lower priority)
        elif weight_change > 0 and current_return > 0:
            return 'TOP_UP_BACKUP'
        
        # Default: HOLD
        else:
            return 'HOLD'
    
    def _apply_strategic_constraint(self, symbol: str, phase1_weight: float, 
                                  current_weight: float, action: str) -> float:
        """
        Apply strategic constraints to Phase 1 optimal weights
        """
        if action == 'TOP_UP_BACKUP':
            # Reduce weight for backup positions (will be processed later if budget allows)
            return min(phase1_weight * 0.5, current_weight * 1.1)  # Conservative increase
        
        elif action == 'SELL':
            # Ensure complete or near-complete exits
            return max(0, phase1_weight * 0.1)  # Keep minimal position if any
        
        elif action == 'TRIM':
            # Moderate reduction while maintaining position
            return max(phase1_weight, current_weight * 0.7)  # At least 30% reduction
        
        else:
            # BUY_NEW and HOLD: Use Phase 1 optimal
            return phase1_weight
    
    def _compare_phases(self) -> Dict:
        """
        Compare Phase 1 vs Phase 2 results
        Identify strategic conflicts and trade-offs
        """
        self.logger.info("🔍 Comparing Phase 1 vs Phase 2 results...")
        
        phase1_weights = self.phase1_results['optimization_result']['weights']
        phase2_weights = self.phase2_results['strategic_weights']
        
        # Calculate differences
        weight_differences = {}
        for symbol in phase1_weights.index:
            p1_weight = phase1_weights[symbol]
            p2_weight = phase2_weights.get(symbol, 0)
            weight_differences[symbol] = {
                'phase1_weight': p1_weight,
                'phase2_weight': p2_weight,
                'difference': p2_weight - p1_weight,
                'pct_change': ((p2_weight - p1_weight) / p1_weight * 100) if p1_weight > 0 else 0
            }
        
        # Identify significant conflicts
        significant_conflicts = {
            symbol: diff for symbol, diff in weight_differences.items()
            if abs(diff['difference']) > 0.05  # >5% weight difference
        }
        
        self.strategic_conflicts = list(significant_conflicts.keys())
        
        return {
            'weight_differences': weight_differences,
            'significant_conflicts': significant_conflicts,
            'total_conflicts': len(significant_conflicts),
            'phase1_expected_return': self.phase1_results['optimization_result']['expected_return'],
            'phase2_cash_compliance': self.phase2_results['budget_compliance']
        }
    
    def _generate_final_recommendations(self) -> Dict:
        """
        Generate final actionable recommendations from Phase 2
        """
        self.logger.info("📋 Generating final recommendations...")
        
        # Get Phase 2 sizing results
        sizing_results = self.phase2_results['sizing_results']
        
        # Apply final position sizing and dynamic stops
        final_recommendations = self.position_sizer.calculate_dynamic_stop_losses(
            sizing_results['recommendations']
        )
        
        # Generate action summary with backup processing
        action_summary = self.position_sizer.generate_action_summary(final_recommendations)
        
        return {
            'recommendations': final_recommendations,
            'action_summary': action_summary,
            'portfolio_summary': sizing_results['portfolio_summary'],
            'execution_ready': True
        }

def main():
    """Test the two-phase optimization"""
    print("🚀 TWO-PHASE PORTFOLIO OPTIMIZATION TEST")
    print("=" * 60)
    
    optimizer = TwoPhaseOptimizer()
    results = optimizer.run_complete_optimization()
    
    if results['success']:
        print("✅ Two-phase optimization completed successfully")
        print(f"💰 Final cash usage: ${results['final_recommendations']['portfolio_summary']['net_cash_used']:,.2f}")
        print(f"🎯 Strategic conflicts identified: {len(results['strategic_conflicts'])}")
    else:
        print(f"❌ Optimization failed: {results['message']}")

if __name__ == "__main__":
    main() 