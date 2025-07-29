#!/usr/bin/env python3
"""
Markowitz Portfolio Optimization Engine - Component D1
Implements rigorous mean-variance optimization using quadratic programming
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy import linalg
import logging
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class MarkowitzOptimizer:
    """Rigorous Markowitz mean-variance portfolio optimization"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize Markowitz optimizer"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Optimization parameters
        self.max_iterations = 1000
        self.tolerance = 1e-8
    
    def validate_inputs(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame) -> bool:
        """
        Validate input data for optimization
        
        Args:
            expected_returns: Series of expected returns
            cov_matrix: Covariance matrix
            
        Returns:
            bool: True if inputs are valid
        """
        # Check dimensions match
        if len(expected_returns) != cov_matrix.shape[0] or len(expected_returns) != cov_matrix.shape[1]:
            self.logger.error("❌ Dimension mismatch between returns and covariance matrix")
            return False
        
        # Check covariance matrix is symmetric
        if not np.allclose(cov_matrix, cov_matrix.T):
            self.logger.error("❌ Covariance matrix is not symmetric")
            return False
        
        # Check covariance matrix is positive semi-definite
        eigenvals = np.linalg.eigvals(cov_matrix)
        if np.any(eigenvals < -1e-8):  # Allow small numerical errors
            self.logger.error("❌ Covariance matrix is not positive semi-definite")
            return False
        
        # Check for NaN/infinite values
        if expected_returns.isna().any() or np.isinf(expected_returns).any():
            self.logger.error("❌ Expected returns contain NaN or infinite values")
            return False
        
        if cov_matrix.isna().any().any() or np.isinf(cov_matrix).any().any():
            self.logger.error("❌ Covariance matrix contains NaN or infinite values")
            return False
        
        self.logger.info("✅ Input validation passed")
        return True
    
    def minimize_variance_target_return(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame, 
                                      target_return: float, constraints: Dict = None) -> Dict:
        """
        Minimize portfolio variance for a target return (classical Markowitz)
        
        Args:
            expected_returns: Expected returns for each asset
            cov_matrix: Covariance matrix
            target_return: Target portfolio return
            constraints: Additional constraints dict
            
        Returns:
            Dict with optimization results
        """
        if not self.validate_inputs(expected_returns, cov_matrix):
            return {'success': False, 'message': 'Input validation failed'}
        
        n_assets = len(expected_returns)
        
        # Objective function: minimize 0.5 * w^T * Cov * w
        def objective(weights):
            return 0.5 * np.dot(weights, np.dot(cov_matrix.values, weights))
        
        # Gradient of objective function
        def gradient(weights):
            return np.dot(cov_matrix.values, weights)
        
        # Constraints
        constraints_list = [
            # Return constraint: w^T * r = target_return
            {'type': 'eq', 'fun': lambda w: np.dot(w, expected_returns.values) - target_return},
            # Sum to 1 constraint: sum(w) = 1
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        
        # Add custom constraints if provided
        if constraints:
            if 'max_weight' in constraints:
                # Individual position limits
                for i in range(n_assets):
                    constraints_list.append({
                        'type': 'ineq', 
                        'fun': lambda w, i=i: constraints['max_weight'] - w[i]
                    })
            
            if 'sector_limits' in constraints:
                # Sector concentration limits
                for sector, (indices, limit) in constraints['sector_limits'].items():
                    constraints_list.append({
                        'type': 'ineq',
                        'fun': lambda w, indices=indices, limit=limit: limit - np.sum(w[indices])
                    })
        
        # Bounds: allow long positions only (can be modified for long/short)
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess: equal weights
        x0 = np.ones(n_assets) / n_assets
        
        # Optimize
        try:
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                jac=gradient,
                bounds=bounds,
                constraints=constraints_list,
                options={
                    'ftol': self.tolerance,
                    'disp': False,
                    'maxiter': self.max_iterations
                }
            )
            
            if result.success:
                weights = pd.Series(result.x, index=expected_returns.index)
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                
                self.logger.info(f"✅ Optimization successful: Return={portfolio_return:.4f}, Vol={portfolio_volatility:.4f}")
                
                return {
                    'success': True,
                    'weights': weights,
                    'portfolio_return': portfolio_return,
                    'portfolio_volatility': portfolio_volatility,
                    'portfolio_variance': portfolio_variance,
                    'solver_result': result
                }
            else:
                self.logger.error(f"❌ Optimization failed: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            self.logger.error(f"❌ Optimization error: {e}")
            return {'success': False, 'message': str(e)}
    
    def maximize_sharpe_ratio(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame, 
                             risk_free_rate: float, constraints: Dict = None) -> Dict:
        """
        Maximize Sharpe ratio (tangency portfolio)
        
        Args:
            expected_returns: Expected returns for each asset
            cov_matrix: Covariance matrix
            risk_free_rate: Risk-free rate
            constraints: Additional constraints dict
            
        Returns:
            Dict with optimization results
        """
        if not self.validate_inputs(expected_returns, cov_matrix):
            return {'success': False, 'message': 'Input validation failed'}
        
        # Excess returns
        excess_returns = expected_returns - risk_free_rate
        
        n_assets = len(expected_returns)
        
        # Objective function: minimize -(excess_return / volatility)
        def objective(weights):
            portfolio_return = np.dot(weights, excess_returns.values)
            portfolio_variance = np.dot(weights, np.dot(cov_matrix.values, weights))
            
            if portfolio_variance <= 0:
                return 1e10  # Large penalty for invalid portfolios
            
            sharpe = portfolio_return / np.sqrt(portfolio_variance)
            return -sharpe  # Minimize negative Sharpe (maximize Sharpe)
        
        # Constraints
        constraints_list = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Sum to 1
        ]
        
        # Add custom constraints
        if constraints:
            if 'max_weight' in constraints:
                for i in range(n_assets):
                    constraints_list.append({
                        'type': 'ineq', 
                        'fun': lambda w, i=i: constraints['max_weight'] - w[i]
                    })
            
            if 'sector_limits' in constraints:
                for sector, (indices, limit) in constraints['sector_limits'].items():
                    constraints_list.append({
                        'type': 'ineq',
                        'fun': lambda w, indices=indices, limit=limit: limit - np.sum(w[indices])
                    })
        
        bounds = [(0, 1) for _ in range(n_assets)]
        x0 = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={
                    'ftol': self.tolerance,
                    'disp': False,
                    'maxiter': self.max_iterations
                }
            )
            
            if result.success:
                weights = pd.Series(result.x, index=expected_returns.index)
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
                
                self.logger.info(f"✅ Max Sharpe optimization: Sharpe={sharpe_ratio:.4f}, Return={portfolio_return:.4f}")
                
                return {
                    'success': True,
                    'weights': weights,
                    'portfolio_return': portfolio_return,
                    'portfolio_volatility': portfolio_volatility,
                    'portfolio_variance': portfolio_variance,
                    'sharpe_ratio': sharpe_ratio,
                    'solver_result': result
                }
            else:
                self.logger.error(f"❌ Max Sharpe optimization failed: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            self.logger.error(f"❌ Max Sharpe optimization error: {e}")
            return {'success': False, 'message': str(e)}
    
    def efficient_frontier(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame, 
                          n_points: int = 50, constraints: Dict = None) -> pd.DataFrame:
        """
        Calculate the efficient frontier
        
        Args:
            expected_returns: Expected returns for each asset
            cov_matrix: Covariance matrix
            n_points: Number of points on the frontier
            constraints: Additional constraints dict
            
        Returns:
            DataFrame with efficient frontier points
        """
        if not self.validate_inputs(expected_returns, cov_matrix):
            return pd.DataFrame()
        
        # Calculate range of returns
        min_return = expected_returns.min()
        max_return = expected_returns.max()
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier_results = []
        
        for target_return in target_returns:
            result = self.minimize_variance_target_return(
                expected_returns, cov_matrix, target_return, constraints
            )
            
            if result['success']:
                frontier_results.append({
                    'target_return': target_return,
                    'portfolio_return': result['portfolio_return'],
                    'portfolio_volatility': result['portfolio_volatility'],
                    'weights': result['weights']
                })
        
        if frontier_results:
            self.logger.info(f"✅ Efficient frontier calculated: {len(frontier_results)} points")
            return pd.DataFrame(frontier_results)
        else:
            self.logger.error("❌ Failed to calculate efficient frontier")
            return pd.DataFrame()
    
    def target_volatility_optimization(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame,
                                     target_volatility: float, constraints: Dict = None) -> Dict:
        """
        Maximize return for a target volatility level
        
        Args:
            expected_returns: Expected returns for each asset
            cov_matrix: Covariance matrix
            target_volatility: Target portfolio volatility
            constraints: Additional constraints dict
            
        Returns:
            Dict with optimization results
        """
        if not self.validate_inputs(expected_returns, cov_matrix):
            return {'success': False, 'message': 'Input validation failed'}
        
        n_assets = len(expected_returns)
        
        # Objective function: maximize return
        def objective(weights):
            return -np.dot(weights, expected_returns.values)  # Minimize negative return
        
        # Constraints
        constraints_list = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
            # Volatility constraint: sqrt(w^T * Cov * w) = target_volatility
            {'type': 'eq', 'fun': lambda w: np.sqrt(np.dot(w, np.dot(cov_matrix.values, w))) - target_volatility}
        ]
        
        # Add custom constraints
        if constraints:
            if 'max_weight' in constraints:
                for i in range(n_assets):
                    constraints_list.append({
                        'type': 'ineq', 
                        'fun': lambda w, i=i: constraints['max_weight'] - w[i]
                    })
        
        bounds = [(0, 1) for _ in range(n_assets)]
        x0 = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={
                    'ftol': self.tolerance,
                    'disp': False,
                    'maxiter': self.max_iterations
                }
            )
            
            if result.success:
                weights = pd.Series(result.x, index=expected_returns.index)
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                
                self.logger.info(f"✅ Target volatility optimization: Vol={portfolio_volatility:.4f}, Return={portfolio_return:.4f}")
                
                return {
                    'success': True,
                    'weights': weights,
                    'portfolio_return': portfolio_return,
                    'portfolio_volatility': portfolio_volatility,
                    'portfolio_variance': portfolio_variance,
                    'solver_result': result
                }
            else:
                self.logger.error(f"❌ Target volatility optimization failed: {result.message}")
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            self.logger.error(f"❌ Target volatility optimization error: {e}")
            return {'success': False, 'message': str(e)}

def main():
    """Test Markowitz optimization engine"""
    print("⚖️ MARKOWITZ OPTIMIZATION ENGINE TEST")
    print("=" * 50)
    
    # Create synthetic test data
    n_assets = 5
    np.random.seed(42)
    
    # Generate expected returns
    expected_returns = pd.Series(
        np.random.normal(0.08, 0.02, n_assets),
        index=[f'STOCK_{i}' for i in range(n_assets)]
    )
    
    # Generate covariance matrix
    random_matrix = np.random.randn(n_assets, n_assets)
    cov_matrix = pd.DataFrame(
        np.dot(random_matrix, random_matrix.T) / 100,  # Scale down
        index=expected_returns.index,
        columns=expected_returns.index
    )
    
    # Initialize optimizer
    optimizer = MarkowitzOptimizer()
    
    print(f"📊 Test data: {n_assets} assets")
    print(f"📈 Expected returns range: {expected_returns.min():.3f} to {expected_returns.max():.3f}")
    
    # Test 1: Target return optimization
    print("\n🎯 Test 1: Target Return Optimization")
    target_return = 0.10
    result1 = optimizer.minimize_variance_target_return(expected_returns, cov_matrix, target_return)
    
    if result1['success']:
        print(f"✅ Target: {target_return:.3f}, Achieved: {result1['portfolio_return']:.3f}")
        print(f"📊 Volatility: {result1['portfolio_volatility']:.3f}")
    
    # Test 2: Maximum Sharpe ratio
    print("\n📈 Test 2: Maximum Sharpe Ratio")
    risk_free_rate = 0.02
    result2 = optimizer.maximize_sharpe_ratio(expected_returns, cov_matrix, risk_free_rate)
    
    if result2['success']:
        print(f"✅ Sharpe Ratio: {result2['sharpe_ratio']:.3f}")
        print(f"📊 Return: {result2['portfolio_return']:.3f}, Vol: {result2['portfolio_volatility']:.3f}")
    
    # Test 3: Target volatility
    print("\n🎯 Test 3: Target Volatility Optimization")
    target_volatility = 0.15
    result3 = optimizer.target_volatility_optimization(expected_returns, cov_matrix, target_volatility)
    
    if result3['success']:
        print(f"✅ Target Vol: {target_volatility:.3f}, Achieved: {result3['portfolio_volatility']:.3f}")
        print(f"📊 Return: {result3['portfolio_return']:.3f}")
    
    return {
        'optimizer': optimizer,
        'test_data': {
            'expected_returns': expected_returns,
            'cov_matrix': cov_matrix
        },
        'results': {
            'target_return': result1,
            'max_sharpe': result2,
            'target_volatility': result3
        }
    }

if __name__ == "__main__":
    main() 