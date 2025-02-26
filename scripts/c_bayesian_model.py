"""
Bayesian prediction module that combines sentiment analysis and market data.
Generates probability estimates for exceeding analyst consensus in 1-week horizon.
Stores full posterior distributions for future analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import os
from typing import Dict, Optional, Tuple
import logging
from scipy import stats
import pickle
import pymc as pm
import aesara.tensor as at
import shutil

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers

class BayesianPredictor:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Create archive directories
        self.archive_dir = self.results_dir / 'archive' / 'predictions'
        self.posterior_dir = self.results_dir / 'archive' / 'posterior'
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.posterior_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Load sentiment and market data"""
        try:
            # Load latest sentiment data
            sentiment_path = self.results_dir / "sentiment_summary_latest.csv"
            sentiment_df = pd.read_csv(sentiment_path) if sentiment_path.exists() else None
            
            # Load latest market data
            market_path = self.results_dir / "market_data_latest.csv"
            market_df = pd.read_csv(market_path) if market_path.exists() else None
            
            return sentiment_df, market_df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None, None
            
    def build_model(self, sentiment_data: pd.DataFrame, market_data: pd.DataFrame) -> pm.Model:
        """
        Build PyMC model for 1-week return predictions
        Incorporates:
        - Sentiment scores and trends
        - Market data (volume, beta, etc.)
        - Analyst consensus
        """
        with pm.Model() as model:
            # Global parameters
            μ_market = pm.Normal('μ_market', mu=0, sigma=5)
            σ_market = pm.HalfNormal('σ_market', sigma=3)
            
            # Sentiment impact
            β_sentiment = pm.Normal('β_sentiment', mu=0.5, sigma=0.5)
            β_volume = pm.Normal('β_volume', mu=0.1, sigma=0.2)
            β_momentum = pm.Normal('β_momentum', mu=0.3, sigma=0.3)
            
            # Calculate expected returns
            sentiment_effect = β_sentiment * sentiment_data['average_sentiment'].values
            volume_effect = β_volume * np.log1p(market_data['volume'] / market_data['avg_volume'])
            momentum_effect = β_momentum * market_data['week_return'].fillna(0).values
            
            # Expected 1-week return
            μ_return = μ_market + sentiment_effect + volume_effect + momentum_effect
            
            # Likelihood of exceeding consensus
            exceed_prob = pm.Deterministic(
                'exceed_prob',
                pm.math.sigmoid(μ_return)
            )
            
            # Observed data (if available)
            if 'exceeded_prev' in market_data.columns:
                pm.Bernoulli(
                    'exceeded',
                    p=exceed_prob,
                    observed=market_data['exceeded_prev'].values
                )
            
        return model
            
    def generate_predictions(self) -> None:
        """Generate Bayesian predictions combining all data sources"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Load data
            sentiment_df, market_df = self.load_data()
            
            if sentiment_df is None or market_df is None:
                self.logger.error("Missing required data")
                return
                
            # Merge data
            data = pd.merge(
                sentiment_df,
                market_df,
                on=['ticker', 'company'],
                how='inner'
            )
            
            # Build and run model
            model = self.build_model(data, market_df)
            
            with model:
                # MCMC sampling
                trace = pm.sample(
                    draws=2000,
                    tune=1000,
                    chains=2,
                    target_accept=0.9
                )
                
                # Generate predictions
                predictions = pm.sample_posterior_predictive(
                    trace,
                    var_names=['exceed_prob']
                )
            
            # Process results
            results = []
            for idx, row in data.iterrows():
                ticker = row['ticker']
                
                # Calculate probability and confidence intervals
                prob_samples = predictions['exceed_prob'][:, idx]
                prob_mean = prob_samples.mean()
                ci_low, ci_high = np.percentile(prob_samples, [2.5, 97.5])
                
                results.append({
                    'ticker': ticker,
                    'company': row['company'],
                    'prob_exceed_consensus': prob_mean,
                    'ci_2.5': ci_low,
                    'ci_97.5': ci_high,
                    'sentiment_score': row['average_sentiment'],
                    'market_momentum': row['week_return'],
                    'target_return': row['potential_return'],
                    'volume_ratio': row['volume'] / row['avg_volume'] if row['avg_volume'] > 0 else None
                })
            
            # Save predictions
            results_df = pd.DataFrame(results)
            pred_path = self.results_dir / f"bayesian_pred_{timestamp}.csv"
            results_df.to_csv(pred_path, index=False)
            
            # Create symlink for latest predictions
            latest_pred = self.results_dir / "bayesian_pred_latest.csv"
            if latest_pred.exists():
                latest_pred.unlink()
            latest_pred.symlink_to(pred_path.name)
            
            # Save full posterior distribution
            posterior_path = self.posterior_dir / f"posterior_{timestamp}.pkl"
            with open(posterior_path, 'wb') as f:
                pickle.dump({
                    'trace': trace,
                    'predictions': predictions
                }, f)
            
            # Archive previous files
            for file in self.results_dir.glob("bayesian_pred_2*.csv"):
                if timestamp not in str(file):
                    archive_path = self.archive_dir / file.name
                    shutil.move(str(file), str(archive_path))
            
            # Print summary
            self.logger.info("\nBayesian Prediction Summary:")
            self.logger.info(f"Companies analyzed: {len(results_df)}")
            self.logger.info(f"Average probability: {results_df['prob_exceed_consensus'].mean():.2%}")
            self.logger.info(f"High confidence predictions: {len(results_df[results_df['prob_exceed_consensus'] > 0.7])}")
            self.logger.info(f"\nResults saved to:")
            self.logger.info(f"- Predictions: {pred_path}")
            self.logger.info(f"- Posterior distribution: {posterior_path}")
            self.logger.info(f"- Archive directory: {self.archive_dir}")
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
            raise

def main():
    """Main function to generate Bayesian predictions"""
    print("\nStarting Bayesian prediction generation...")
    predictor = BayesianPredictor()
    predictor.generate_predictions()
    print("\nBayesian prediction generation complete!")

if __name__ == "__main__":
    main() 