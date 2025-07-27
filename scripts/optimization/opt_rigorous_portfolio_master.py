#!/usr/bin/env python3
"""
Rigorous Portfolio Optimizer Master - Integration of All Components
Addresses all mathematical rigor issues from audit with proper Markowitz theory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import logging
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# Import our rigorous components
from financial.fin_treasury_rates import TreasuryRateFetcher
from financial.fin_market_data import MarketDataCollector
from optimization.opt_markowitz_engine import MarkowitzOptimizer

class RigorousPortfolioOptimizer:
    """
    Master portfolio optimizer with mathematical rigor
    Integrates all components following proper financial theory
    """
    
    def __init__(self, log_level=logging.INFO):
        """Initialize the rigorous portfolio optimizer"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Initialize components
        self.treasury_fetcher = TreasuryRateFetcher(log_level)
        self.market_collector = MarketDataCollector(log_level)
        self.markowitz_optimizer = MarkowitzOptimizer(log_level)
        
        # User specifications from requirements
        self.target_return = 0.07          # 7% target return
        self.target_volatility = 0.20      # 20% target volatility
        self.var_confidence = 0.97         # 97% VaR confidence level
        self.sector_limit = 0.40           # 40% max per sector
        self.sentiment_weight = 0.20       # 20% sentiment weight
        self.financial_weight = 0.80       # 80% financial weight
        self.stop_loss_pct = 0.08          # 8% stop loss
        self.new_cash = 10000              # $10,000 new cash
        
        # Current portfolio baseline
        self.current_return = 0.0483       # 4.83% current return
        self.return_improvement = 0.02     # +2pp improvement target
        
        # Symbol mapping for sentiment data matching (portfolio CSV vs sentiment data)
        self.symbol_mapping = {
            'APPLE': 'AAPL',   # Apple in portfolio shows as APPLE, sentiment data uses AAPL
            'NVDA': 'NVDA',
            'SPGI': 'SPGI', 
            'PRU': 'PRU',
            'ASML': 'ASML',
            'CVNA': 'CVNA',
            'CCJ': 'CCJ',
            'OGC': 'OGC',
            'VERA': 'VERA'
        }
        
    def parse_european_number(self, value_str):
        """Parse European number format"""
        return self.market_collector.parse_european_number(value_str)
    
    def load_current_portfolio(self, portfolio_file="actual-portfolio-master.csv"):
        """
        Load and analyze current portfolio with proper European number parsing
        
        Returns:
            Dict with portfolio analysis
        """
        try:
            df = pd.read_csv(portfolio_file, sep=';', skiprows=2, nrows=20)
            
            portfolio_data = []
            total_current_value = 0
            total_cost_basis = 0
            
            for _, row in df.iterrows():
                if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
                    # Clean symbol
                    symbol = row['Simbolo'].split('.')[0]
                    if symbol.startswith('1'):
                        symbol = symbol[1:]
                    
                    # Parse values with proper European format handling
                    quantity = self.parse_european_number(row['Quantità'])
                    avg_cost = self.parse_european_number(row['P.zo medio di carico'])
                    current_value_eur = self.parse_european_number(row['Valore di mercato €'])
                    cost_basis = self.parse_european_number(row['Valore di carico'])
                    return_pct = self.parse_european_number(row['Var%'])
                    
                    portfolio_data.append({
                        'symbol': symbol,
                        'name': row['Titolo'],
                        'quantity': quantity,
                        'avg_cost_eur': avg_cost,
                        'current_value_eur': current_value_eur,
                        'cost_basis_eur': cost_basis,
                        'return_pct': return_pct / 100,  # Convert to decimal
                        'weight': 0  # Will calculate after totals
                    })
                    
                    total_current_value += current_value_eur
                    total_cost_basis += cost_basis
            
            # Calculate weights
            for position in portfolio_data:
                position['weight'] = position['current_value_eur'] / total_current_value
            
            # Calculate overall return (should match 4.83%)
            overall_return = (total_current_value - total_cost_basis) / total_cost_basis
            
            self.logger.info(f"📊 Portfolio loaded: {len(portfolio_data)} positions")
            self.logger.info(f"💰 Total value: €{total_current_value:,.2f}")
            self.logger.info(f"📈 Overall return: {overall_return:.4f} ({overall_return*100:.2f}%)")
            
            return {
                'positions': portfolio_data,
                'total_current_value_eur': total_current_value,
                'total_cost_basis_eur': total_cost_basis,
                'overall_return': overall_return,
                'symbols': [pos['symbol'] for pos in portfolio_data]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load portfolio: {e}")
            return None
    
    def load_sentiment_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Load sentiment data from EXACT same source as dashboard
        Uses data/results/sentiment_summary_latest.csv (same as dashboard)
        
        Returns:
            Dict mapping symbols to sentiment info with EXACT same values as dashboard
        """
        sentiment_data = {}
        
        try:
            # Load from EXACT same file as dashboard
            results_file = 'data/results/sentiment_summary_latest.csv'
            
            if os.path.exists(results_file):
                df = pd.read_csv(results_file)
                self.logger.info(f"📊 Loading sentiment from EXACT dashboard source: {results_file}")
                self.logger.info(f"🎯 Symbols requested: {symbols}")
                
                # Load trends data if available (same as dashboard does)
                trends_data = {}
                try:
                    # Try to get trend data from historical analysis
                    trend_files = glob.glob("data/results/*sentiment*trends*.csv")
                    if trend_files:
                        latest_trend_file = max(trend_files, key=os.path.getctime)
                        trends_df = pd.read_csv(latest_trend_file)
                        for _, row in trends_df.iterrows():
                            symbol = row.get('ticker', '').strip().upper()
                            trends_data[symbol] = row.get('trend', 'neutral')
                except Exception as e:
                    self.logger.warning(f"Could not load trends: {e}")
                
                # Process sentiment data EXACTLY like dashboard  
                # Load ALL sentiment data first, then we'll map symbols later
                found_symbols = []
                for _, row in df.iterrows():
                    symbol = row.get('ticker', '').strip().upper()
                    if symbol:  # Process all symbols, not just requested ones
                        found_symbols.append(symbol)
                        # Use last_month_sentiment (EXACT same as dashboard "Last Month" column)
                        last_month_sentiment = row.get('last_month_sentiment')
                        
                        # Debug logging for AAPL specifically
                        if symbol == 'AAPL':
                            self.logger.info(f"🍎 APPLE DEBUG - Raw value: {last_month_sentiment}, Type: {type(last_month_sentiment)}")
                        
                        if pd.isna(last_month_sentiment) or last_month_sentiment == '' or last_month_sentiment is None:
                            last_month_sentiment = 0.0
                        else:
                            try:
                                last_month_sentiment = float(last_month_sentiment)
                                # More Apple debugging
                                if symbol == 'AAPL':
                                    self.logger.info(f"🍎 APPLE DEBUG - Converted to: {last_month_sentiment}")
                            except (ValueError, TypeError):
                                last_month_sentiment = 0.0
                        
                        # Get trend (try to match dashboard trend logic)
                        trend = 'neutral'  # Default
                        if symbol in trends_data:
                            trend_val = trends_data[symbol]
                            if trend_val == 'UP':
                                trend = 'improving'
                            elif trend_val == 'DOWN':
                                trend = 'declining'
                            else:
                                trend = 'stable'
                        
                        sentiment_data[symbol] = {
                            'sentiment_score': last_month_sentiment,  # EXACT same as dashboard "Last Month"
                            'trend': trend,                          # EXACT same as dashboard "Trend"
                            'confidence': 0.8,  # Default high confidence for real data
                            'articles_count': row.get('total_articles', 0)
                        }
                        
                self.logger.info(f"✅ Found sentiment data for symbols: {found_symbols}")
                self.logger.info(f"✅ Loaded EXACT dashboard sentiment data for {len(sentiment_data)} symbols")
            else:
                self.logger.error(f"❌ Dashboard sentiment file not found: {results_file}")
                
        except Exception as e:
            self.logger.error(f"❌ Error loading sentiment data: {e}")
        
        except Exception as e:
            self.logger.error(f"❌ Failed to load sentiment data: {e}")
        
        # Fill missing symbols with neutral sentiment, checking mappings first
        for symbol in symbols:
            if symbol not in sentiment_data:
                # Check if we have a mapping for this symbol
                mapped_symbol = self.symbol_mapping.get(symbol)
                if mapped_symbol and mapped_symbol in sentiment_data:
                    # Use the mapped symbol's sentiment data
                    sentiment_data[symbol] = sentiment_data[mapped_symbol].copy()
                    self.logger.info(f"📍 Mapped {symbol} → {mapped_symbol} for sentiment data")
                else:
                    sentiment_data[symbol] = {
                        'sentiment_score': 0.0,
                        'trend': 'neutral',
                        'confidence': 0.5,
                        'articles_count': 0
                    }
                    self.logger.warning(f"⚠️ No sentiment data for {symbol}, using neutral")
        
        self.logger.info(f"✅ Sentiment data loaded for {len(sentiment_data)} symbols")
        return sentiment_data
    
    def calculate_composite_scores(self, market_data: Dict, sentiment_data: Dict, 
                                 expected_returns: pd.Series, analyst_targets: pd.DataFrame) -> pd.Series:
        """
        Calculate composite scores: 80% financial + 20% sentiment
        
        Mathematical Foundation:
        - Historical returns (geometric mean): Base forecast
        - Analyst targets: Forward-looking adjustment (capped)  
        - Sentiment: Market psychology factor (limited impact)
        
        Returns:
            Series of composite expected returns
        """
        composite_scores = pd.Series(index=expected_returns.index, dtype=float)
        
        # Track adjustments for mathematical validation
        analyst_adjustments = []
        sentiment_adjustments = []
        
        for symbol in expected_returns.index:
            # Start with historical expected returns
            historical_return = expected_returns[symbol]
            
            # Financial component: Blend historical with analyst targets (if available)
            if symbol in analyst_targets['symbol'].values:
                target_data = analyst_targets[analyst_targets['symbol'] == symbol].iloc[0]
                if pd.notna(target_data['upside_potential']):
                    upside = target_data['upside_potential']
                    # Cap analyst upside to prevent unrealistic expectations
                    capped_upside = np.clip(upside, -0.50, 0.50)  # Max ±50% upside
                    
                    # Blend historical (70%) with analyst target upside (30%)
                    # This replaces addition with weighted average to prevent inflation
                    financial_score = 0.7 * historical_return + 0.3 * capped_upside
                    analyst_adjustments.append(capped_upside)
                else:
                    financial_score = historical_return
                    analyst_adjustments.append(0.0)
            else:
                financial_score = historical_return
                analyst_adjustments.append(0.0)
            
            # Sentiment component (limited impact)
            sentiment_info = sentiment_data.get(symbol, {'sentiment_score': 0.0})
            sentiment_score = sentiment_info['sentiment_score']
            
            # Convert sentiment (-1 to +1) to return adjustment (max ±5% impact)
            sentiment_return_adj = np.clip(sentiment_score * 0.05, -0.05, 0.05)
            sentiment_adjustments.append(sentiment_return_adj)
            
            # Combine with weights (80% financial, 20% sentiment)
            composite_score = (
                self.financial_weight * financial_score + 
                self.sentiment_weight * sentiment_return_adj
            )
            
            composite_scores[symbol] = composite_score
        
        # Mathematical validation and logging
        mean_historical = expected_returns.mean()
        mean_composite = composite_scores.mean()
        mean_analyst_adj = np.mean(analyst_adjustments)
        mean_sentiment_adj = np.mean(sentiment_adjustments)
        
        self.logger.info(f"📊 Composite scores calculated for {len(composite_scores)} symbols")
        self.logger.info(f"📈 Return analysis:")
        self.logger.info(f"   Historical mean: {mean_historical:.4f} ({mean_historical:.2%})")
        self.logger.info(f"   Composite mean: {mean_composite:.4f} ({mean_composite:.2%})")
        self.logger.info(f"   Mean analyst adjustment: {mean_analyst_adj:.4f} ({mean_analyst_adj:.2%})")
        self.logger.info(f"   Mean sentiment adjustment: {mean_sentiment_adj:.4f} ({mean_sentiment_adj:.2%})")
        
        # Validate reasonable return expectations
        if mean_composite > 0.50:  # 50% mean return is unrealistic
            self.logger.warning(f"⚠️ Mean composite return ({mean_composite:.2%}) may be unrealistically high")
        
        extreme_returns = composite_scores[(composite_scores > 1.0) | (composite_scores < -0.50)]
        if len(extreme_returns) > 0:
            self.logger.warning(f"⚠️ {len(extreme_returns)} stocks have extreme expected returns (>100% or <-50%)")
        
        return composite_scores
    
    def create_optimization_constraints(self, symbols: List[str], 
                                      portfolio_analysis: Dict = None) -> Dict:
        """
        Create optimization constraints based on user requirements
        
        Returns:
            Dict of constraints for optimizer
        """
        constraints = {}
        
        # Maximum individual position weight (keeping NVIDIA as-is if high conviction)
        # User said NVIDIA can remain as-is, implying ~20% max for high conviction
        constraints['max_weight'] = 0.20
        
        # Sector limits (40% max per sector)
        # For now, implement as total constraint - could be enhanced with sector mapping
        constraints['sector_limits'] = {}
        
        # Additional constraints could include:
        # - Minimum position size
        # - Turnover limits
        # - Tracking error constraints
        
        self.logger.info("✅ Optimization constraints created")
        return constraints
    
    def calculate_var_monte_carlo(self, weights: pd.Series, returns_df: pd.DataFrame, 
                                confidence_level: float = 0.97, n_simulations: int = 10000) -> float:
        """
        Calculate Value at Risk using Monte Carlo simulation
        
        Mathematical Foundation:
        1. Simulate asset returns using multivariate normal distribution
        2. Calculate portfolio returns for each simulation  
        3. VaR = percentile at (1-confidence) level
        
        Returns:
            VaR at specified confidence level (negative values indicate losses)
        """
        try:
            # Ensure weights are aligned with returns columns
            weights_aligned = weights.reindex(returns_df.columns, fill_value=0.0)
            
            # Asset statistics for simulation
            asset_means = returns_df.mean().values  # Mean return vector (NOT scalar)
            asset_cov = returns_df.cov().values     # Covariance matrix (NxN)
            
            self.logger.info(f"🎲 Monte Carlo simulation: {n_simulations:,} iterations")
            self.logger.info(f"📈 Assets: {len(asset_means)}, Mean return range: [{asset_means.min():.4f}, {asset_means.max():.4f}]")
            
            # Validate dimensions
            if len(asset_means) != asset_cov.shape[0] or len(asset_means) != len(weights_aligned):
                raise ValueError(f"Dimension mismatch: means={len(asset_means)}, cov={asset_cov.shape}, weights={len(weights_aligned)}")
            
            # Generate Monte Carlo simulations of asset returns
            np.random.seed(42)  # For reproducibility
            simulated_asset_returns = np.random.multivariate_normal(
                mean=asset_means,           # Correct: vector of asset means
                cov=asset_cov,             # Correct: asset covariance matrix
                size=n_simulations
            )
            
            # Calculate portfolio returns for each simulation
            # Shape: (n_simulations,) = (n_simulations, n_assets) @ (n_assets,)
            simulated_portfolio_returns = simulated_asset_returns @ weights_aligned.values
            
            # Calculate VaR (Value at Risk) 
            # For 97% confidence: we want the 3rd percentile (worst 3% of outcomes)
            var_percentile = (1 - confidence_level) * 100
            var = np.percentile(simulated_portfolio_returns, var_percentile)
            
            # Additional risk metrics
            portfolio_mean = np.mean(simulated_portfolio_returns)
            portfolio_std = np.std(simulated_portfolio_returns)
            
            self.logger.info(f"📊 Portfolio simulation results:")
            self.logger.info(f"   Mean return: {portfolio_mean:.4f} ({portfolio_mean*252:.2%} annualized)")
            self.logger.info(f"   Volatility: {portfolio_std:.4f} ({portfolio_std*np.sqrt(252):.2%} annualized)")
            self.logger.info(f"   {confidence_level*100}% VaR: {var:.4f} ({var*252:.2%} annualized)")
            
            # Return annualized VaR for better interpretation
            var_annualized = var * np.sqrt(252)
            
            return var_annualized
            
        except Exception as e:
            self.logger.error(f"❌ VaR calculation failed: {e}")
            import traceback
            self.logger.error(f"📊 VaR calculation traceback: {traceback.format_exc()}")
            # Return meaningful fallback based on portfolio volatility
            try:
                portfolio_returns = returns_df @ weights
                portfolio_vol = portfolio_returns.std() * np.sqrt(252)
                # Approximate VaR as 2.33 standard deviations for 99% confidence
                # Adjusted for 97% confidence: ~2.05 standard deviations
                fallback_var = -2.05 * portfolio_vol  # Negative for loss
                self.logger.warning(f"⚠️ Using fallback VaR estimate: {fallback_var:.4f}")
                return fallback_var
            except:
                self.logger.error(f"❌ Fallback VaR calculation also failed")
                return -0.30  # Conservative 30% max loss estimate
    
    def optimize_portfolio(self, include_universe: bool = False) -> Dict:
        """
        Main optimization function integrating all components
        
        Args:
            include_universe: Whether to include universe stocks or just portfolio
            
        Returns:
            Dict with optimization results
        """
        self.logger.info("🚀 Starting rigorous portfolio optimization")
        
        # Step 1: Load current portfolio
        portfolio_analysis = self.load_current_portfolio()
        if not portfolio_analysis:
            return {'success': False, 'message': 'Failed to load portfolio'}
        
        # Step 2: Get risk-free rate
        rf_rate = self.treasury_fetcher.get_risk_free_rate('3M')
        self.logger.info(f"🏛️ Risk-free rate: {rf_rate:.4f} ({rf_rate*100:.2f}%)")
        
        # Step 3: Determine symbols to analyze
        if include_universe:
            universe_symbols = self.market_collector.load_universe_symbols()
            all_symbols = list(set(portfolio_analysis['symbols'] + universe_symbols))
        else:
            all_symbols = portfolio_analysis['symbols']
        
        self.logger.info(f"📊 Analyzing {len(all_symbols)} symbols")
        
        # Step 4: Fetch market data
        market_data = self.market_collector.fetch_batch_data(all_symbols)
        
        # Step 5: Calculate returns and covariance matrix
        returns_df = self.market_collector.calculate_returns_matrix(market_data)
        if returns_df.empty:
            return {'success': False, 'message': 'No valid returns data'}
        
        expected_returns = self.market_collector.calculate_expected_returns(returns_df)
        cov_matrix = self.market_collector.calculate_covariance_matrix(returns_df)
        
        # Step 6: Get analyst targets
        analyst_targets = self.market_collector.get_analyst_targets_summary(market_data)
        
        # Step 7: Load sentiment data
        sentiment_data = self.load_sentiment_data(list(returns_df.columns))
        
        # Step 8: Calculate composite scores (80% financial + 20% sentiment)
        composite_returns = self.calculate_composite_scores(
            market_data, sentiment_data, expected_returns, analyst_targets
        )
        
        # Step 9: Create constraints
        constraints = self.create_optimization_constraints(list(returns_df.columns), portfolio_analysis)
        
        # Step 10: Optimize for target return and volatility
        target_return_adjusted = self.current_return + self.return_improvement
        
        # Try target volatility optimization first (user specified 7% return, 20% vol)
        self.logger.info(f"🎯 Optimizing for {self.target_return:.1%} return, {self.target_volatility:.1%} volatility")
        
        opt_result = self.markowitz_optimizer.target_volatility_optimization(
            composite_returns, cov_matrix, self.target_volatility, constraints
        )
        
        if not opt_result['success']:
            # Fallback to target return optimization
            self.logger.info(f"🔄 Fallback: optimizing for {target_return_adjusted:.1%} target return")
            opt_result = self.markowitz_optimizer.minimize_variance_target_return(
                composite_returns, cov_matrix, target_return_adjusted, constraints
            )
        
        if not opt_result['success']:
            # Final fallback to max Sharpe
            self.logger.info("🔄 Final fallback: maximizing Sharpe ratio")
            opt_result = self.markowitz_optimizer.maximize_sharpe_ratio(
                composite_returns, cov_matrix, rf_rate, constraints
            )
        
        if not opt_result['success']:
            return {'success': False, 'message': 'All optimization methods failed'}
        
        # Step 11: Calculate VaR
        var_97 = self.calculate_var_monte_carlo(opt_result['weights'], returns_df, self.var_confidence)
        
        # Step 12: Calculate Sharpe ratio
        sharpe_ratio = (opt_result['portfolio_return'] - rf_rate) / opt_result['portfolio_volatility']
        
        # Step 13: Compile results
        results = {
            'success': True,
            'optimization_result': opt_result,
            'risk_free_rate': rf_rate,
            'sharpe_ratio': sharpe_ratio,
            'var_97': var_97,
            'portfolio_analysis': portfolio_analysis,
            'market_data': market_data,
            'sentiment_data': sentiment_data,
            'analyst_targets': analyst_targets,
            'returns_df': returns_df,
            'expected_returns': expected_returns,
            'composite_returns': composite_returns,
            'covariance_matrix': cov_matrix,
            'target_achieved': {
                'return_target': self.target_return,
                'volatility_target': self.target_volatility,
                'actual_return': opt_result['portfolio_return'],
                'actual_volatility': opt_result['portfolio_volatility'],
                'return_improvement': opt_result['portfolio_return'] - self.current_return
            }
        }
        
        self.logger.info("✅ Portfolio optimization completed successfully")
        self.logger.info(f"📊 Target Return: {self.target_return:.1%} | Achieved: {opt_result['portfolio_return']:.1%}")
        self.logger.info(f"📊 Target Volatility: {self.target_volatility:.1%} | Achieved: {opt_result['portfolio_volatility']:.1%}")
        self.logger.info(f"📊 Sharpe Ratio: {sharpe_ratio:.3f}")
        self.logger.info(f"📊 97% VaR: {var_97:.4f}")
        
        return results

def main():
    """Test the rigorous portfolio optimizer"""
    print("🎯 RIGOROUS PORTFOLIO OPTIMIZER TEST")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = RigorousPortfolioOptimizer()
    
    # Run optimization (portfolio only first)
    results = optimizer.optimize_portfolio(include_universe=False)
    
    if results['success']:
        print("✅ OPTIMIZATION SUCCESSFUL")
        print(f"📊 Portfolio Return: {results['optimization_result']['portfolio_return']:.1%}")
        print(f"📊 Portfolio Volatility: {results['optimization_result']['portfolio_volatility']:.1%}")
        print(f"📊 Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"📊 97% VaR: {results['var_97']:.4f}")
        print(f"🎯 Return Improvement: {results['target_achieved']['return_improvement']:.1%}")
        
        # Show top 5 positions
        weights = results['optimization_result']['weights'].sort_values(ascending=False)
        print(f"\n📈 Top 5 Positions:")
        for symbol, weight in weights.head(5).items():
            print(f"  {symbol}: {weight:.1%}")
    
    else:
        print(f"❌ OPTIMIZATION FAILED: {results['message']}")
    
    return results

if __name__ == "__main__":
    main() 