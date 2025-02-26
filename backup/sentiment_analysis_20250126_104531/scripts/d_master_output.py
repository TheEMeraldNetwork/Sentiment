"""
Consolidated output module that focuses on sentiment analysis trends.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os
from typing import Dict, Optional
import logging

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config.ticker_config import load_master_tickers

def calculate_trend(current: float, previous: float) -> str:
    """Calculate trend between two periods"""
    if pd.isna(current) or pd.isna(previous):
        return 'NEW'
    diff = current - previous
    if abs(diff) < 0.05:
        return 'STABLE'
    return 'HIGHER' if diff > 0 else 'LOWER'

class ConsolidatedOutputGenerator:
    def __init__(self):
        self.mappings = load_master_tickers()
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def calculate_trend(self, current: float, previous: float) -> str:
        """Calculate trend between current and previous values"""
        if pd.isna(current):
            return 'NEW'  # No current data
        if pd.isna(previous):
            return 'NEW'  # No previous data
            
        diff = current - previous
        if abs(diff) < 0.05:
            return 'STABLE'
        return 'HIGHER' if diff > 0 else 'LOWER'

    def load_latest_sentiment(self) -> Optional[pd.DataFrame]:
        """Load most recent archived sentiment file"""
        try:
            files = sorted(self.results_dir.glob("a2_sentiment_summary_*.csv"))
            if not files:
                self.logger.info("No previous sentiment files found")
                return None
            latest = files[-1]
            self.logger.info(f"Loading previous sentiment from: {latest}")
            return pd.read_csv(latest)
        except Exception as e:
            self.logger.error(f"Error loading previous sentiment: {e}")
            return None

    def generate_output(self) -> None:
        """Generate consolidated output with trends"""
        try:
            # Load current sentiment
            current_df = pd.read_csv(self.results_dir / "a2_sentiment_summary.csv")
            
            # Load previous sentiment for trend comparison
            previous_df = self.load_latest_sentiment()
            
            # Calculate 15-day sentiment from detailed data
            detailed_df = pd.read_csv(self.results_dir / "a1_sentiment_detailed.csv")
            detailed_df['date'] = pd.to_datetime(detailed_df['date'])
            now = pd.Timestamp.now()
            mask_15d = detailed_df['date'] >= (now - pd.Timedelta(days=15))
            sent_15d = detailed_df[mask_15d].groupby('ticker')['sentiment_score'].mean()
            
            # Prepare master dataframe
            master_df = current_df.copy()
            
            # Add 15-day sentiment
            master_df = master_df.merge(
                sent_15d.reset_index().rename(columns={'sentiment_score': 'sent_15d'}),
                on='ticker', how='left'
            )
            
            # Rename columns for consistency
            master_df = master_df.rename(columns={
                'last_week_sentiment': 'sent_7d',
                'last_month_sentiment': 'sent_30d',
                'total_articles': 'articles_30d'
            })
            
            # Calculate trends if previous data exists
            if previous_df is not None:
                previous_df = previous_df.rename(columns={
                    'last_week_sentiment': 'sent_7d',
                    'last_month_sentiment': 'sent_30d'
                })
                
                for ticker in master_df['ticker']:
                    prev_row = previous_df[previous_df['ticker'] == ticker].iloc[0] if len(previous_df[previous_df['ticker'] == ticker]) > 0 else None
                    
                    # Calculate trends for each period
                    if prev_row is not None:
                        master_df.loc[master_df['ticker'] == ticker, 'trend_30d'] = self.calculate_trend(
                            master_df.loc[master_df['ticker'] == ticker, 'sent_30d'].iloc[0],
                            prev_row['sent_30d']
                        )
                        master_df.loc[master_df['ticker'] == ticker, 'trend_7d'] = self.calculate_trend(
                            master_df.loc[master_df['ticker'] == ticker, 'sent_7d'].iloc[0],
                            prev_row['sent_7d']
                        )
                    else:
                        master_df.loc[master_df['ticker'] == ticker, ['trend_30d', 'trend_7d']] = 'NEW'
                    
                    # 15-day trend always NEW for now (will build history over time)
                    master_df.loc[master_df['ticker'] == ticker, 'trend_15d'] = 'NEW'
            
            # Save current results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Archive current sentiment
            archive_path = self.results_dir / f"a2_sentiment_summary_{timestamp}.csv"
            current_df.to_csv(archive_path, index=False)
            
            # Save master output
            output_path = self.results_dir / "d_master_output.csv"
            master_df.to_csv(output_path, index=False)
            
            self.logger.info(f"Results saved to: {output_path}")
            self.logger.info(f"Sentiment archived to: {archive_path}")

        except Exception as e:
            self.logger.error(f"Error generating output: {e}")
            raise

def main():
    """Main function to generate consolidated output"""
    print("\nStarting consolidated output generation...")
    generator = ConsolidatedOutputGenerator()
    generator.generate_output()
    print("\nConsolidated output generation complete!")

if __name__ == "__main__":
    main() 