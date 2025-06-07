"""
Data consolidation module that combines sentiment analysis, market data, and Bayesian predictions.
Generates timestamped master output with trend analysis.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os
from typing import Dict, Optional
import logging
import shutil

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers

class DataConsolidator:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Create archive directory
        self.archive_dir = self.results_dir / 'archive' / 'master'
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_latest_data(self) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Load latest data from all sources"""
        try:
            # Load latest sentiment data
            sentiment_path = self.results_dir / "sentiment_summary_latest.csv"
            sentiment_df = pd.read_csv(sentiment_path) if sentiment_path.exists() else None
            
            # Load latest market data
            market_path = self.results_dir / "market_data_latest.csv"
            market_df = pd.read_csv(market_path) if market_path.exists() else None
            
            # Load latest Bayesian predictions
            pred_path = self.results_dir / "bayesian_pred_latest.csv"
            pred_df = pd.read_csv(pred_path) if pred_path.exists() else None
            
            return sentiment_df, market_df, pred_df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None, None, None
            
    def calculate_trend(self, current: float, previous: float) -> str:
        """Calculate trend between two periods"""
        if pd.isna(current) or pd.isna(previous):
            return 'NEW'
        diff = current - previous
        if abs(diff) < 0.05:  # 5% threshold for stability
            return 'STABLE'
        return 'HIGHER' if diff > 0 else 'LOWER'
        
    def consolidate_data(self) -> None:
        """Combine all data sources and generate master output"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Load all data sources
            sentiment_df, market_df, pred_df = self.load_latest_data()
            
            if any(df is None for df in [sentiment_df, market_df]):
                self.logger.error("Missing required data sources")
                return
                
            # Merge sentiment and market data
            master_df = pd.merge(
                sentiment_df,
                market_df,
                on=['ticker', 'company'],
                how='outer'
            )
            
            # Optionally merge Bayesian predictions if available
            if pred_df is not None:
                master_df = pd.merge(
                    master_df,
                    pred_df,
                    on=['ticker', 'company'],
                    how='left'
                )
            
            # Calculate trends
            for period in ['7d', '15d', '30d']:
                col = f'last_{period}_sentiment'
                if col in master_df.columns:
                    # Load previous master data if exists
                    prev_path = list(self.archive_dir.glob("master_output_*.csv"))
                    if prev_path:
                        prev_df = pd.read_csv(sorted(prev_path)[-1])
                        master_df[f'trend_{period}'] = master_df.apply(
                            lambda row: self.calculate_trend(
                                row[col],
                                prev_df[prev_df['ticker'] == row['ticker']][col].iloc[0]
                                if len(prev_df[prev_df['ticker'] == row['ticker']]) > 0
                                else None
                            ),
                            axis=1
                        )
                    else:
                        master_df[f'trend_{period}'] = 'NEW'
            
            # Add metadata
            master_df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            master_df['data_version'] = timestamp
            
            # Save master output with timestamp
            output_path = self.results_dir / f"master_output_{timestamp}.csv"
            master_df.to_csv(output_path, index=False)
            
            # Create symlink for latest file
            latest_path = self.results_dir / "master_output_latest.csv"
            if latest_path.exists():
                latest_path.unlink()
            latest_path.symlink_to(output_path.name)
            
            # Archive previous files
            for file in self.results_dir.glob("master_output_2*.csv"):
                if timestamp not in str(file):
                    archive_path = self.archive_dir / file.name
                    shutil.move(str(file), str(archive_path))
            
            # Print summary
            self.logger.info("\nData Consolidation Summary:")
            self.logger.info(f"Total companies: {len(master_df)}")
            self.logger.info(f"Companies with complete data: {len(master_df.dropna(subset=['average_sentiment', 'potential_return']))}")
            
            # Print trend statistics
            if 'trend_7d' in master_df.columns:
                trend_stats = master_df['trend_7d'].value_counts()
                self.logger.info("\nWeekly Trend Statistics:")
                for trend, count in trend_stats.items():
                    self.logger.info(f"- {trend}: {count}")
            
            self.logger.info(f"\nResults saved to: {output_path}")
            self.logger.info(f"Archive directory: {self.archive_dir}")
            
        except Exception as e:
            self.logger.error(f"Error consolidating data: {e}")
            raise

def main():
    """Main function to consolidate all data"""
    print("\nStarting data consolidation...")
    consolidator = DataConsolidator()
    consolidator.consolidate_data()
    print("\nData consolidation complete!")

if __name__ == "__main__":
    main() 