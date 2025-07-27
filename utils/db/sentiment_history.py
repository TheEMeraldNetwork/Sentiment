"""
Historical sentiment database module.
Maintains a structured database of sentiment data over time.
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import shutil

class SentimentHistoryDB:
    def __init__(self):
        self.db_dir = Path('database')
        self.db_dir.mkdir(exist_ok=True)
        
        # Create database structure
        self.sentiment_dir = self.db_dir / 'sentiment'
        self.sentiment_dir.mkdir(exist_ok=True)
        
        # Separate directories for detailed and summary data
        self.detailed_dir = self.sentiment_dir / 'detailed'
        self.summary_dir = self.sentiment_dir / 'summary'
        self.detailed_dir.mkdir(exist_ok=True)
        self.summary_dir.mkdir(exist_ok=True)
        
        # Create backup directory
        self.backup_dir = self.db_dir / 'backup' / 'sentiment'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_historical_data(self, data_type: str = 'summary') -> pd.DataFrame:
        """Load all historical data of specified type"""
        target_dir = self.summary_dir if data_type == 'summary' else self.detailed_dir
        all_files = list(target_dir.glob('*.csv'))
        
        if not all_files:
            return pd.DataFrame()
            
        dfs = []
        for file in sorted(all_files):
            try:
                df = pd.read_csv(file)
                df['data_date'] = file.stem.split('_')[-1]  # Extract date from filename
                dfs.append(df)
            except Exception as e:
                self.logger.error(f"Error loading {file}: {e}")
                
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
    def save_current_data(self, detailed_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
        """Save current sentiment data to historical database"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        try:
            # Save detailed data
            detailed_path = self.detailed_dir / f"sentiment_detailed_{timestamp}.csv"
            detailed_df.to_csv(detailed_path, index=False)
            
            # Save summary data
            summary_path = self.summary_dir / f"sentiment_summary_{timestamp}.csv"
            summary_df.to_csv(summary_path, index=False)
            
            # Backup old files (keep last 30 days)
            self._cleanup_old_files(self.detailed_dir, 30)
            self._cleanup_old_files(self.summary_dir, 30)
            
            self.logger.info(f"Saved sentiment data for {timestamp}")
            self.logger.info(f"- Detailed data: {detailed_path}")
            self.logger.info(f"- Summary data: {summary_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving sentiment data: {e}")
            raise
            
    def get_sentiment_trends(self, lookback_days: int = 30) -> pd.DataFrame:
        """Calculate sentiment trends from historical data"""
        df = self.load_historical_data('summary')
        if df.empty:
            return pd.DataFrame()
            
        # Convert data_date to datetime
        df['data_date'] = pd.to_datetime(df['data_date'], format='%Y%m%d')
        
        # Sort by date and ticker
        df.sort_values(['ticker', 'data_date'], inplace=True)
        
        # Calculate trends
        trends = []
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].copy()
            if len(ticker_data) >= 2:
                latest = ticker_data.iloc[-1]
                previous = ticker_data.iloc[-2]
                
                trend = {
                    'ticker': ticker,
                    'company': latest['company'],
                    'current_sentiment': latest['average_sentiment'],
                    'previous_sentiment': previous['average_sentiment'],
                    'sentiment_change': latest['average_sentiment'] - previous['average_sentiment'],
                    'trend': 'UP' if latest['average_sentiment'] > previous['average_sentiment'] else 'DOWN',
                    'latest_date': latest['data_date'],
                    'days_of_history': len(ticker_data)
                }
                trends.append(trend)
                
        return pd.DataFrame(trends)
        
    def _cleanup_old_files(self, directory: Path, keep_days: int = 30) -> None:
        """Move files older than keep_days to backup"""
        files = list(directory.glob('*.csv'))
        files.sort()  # Sort by name (which includes date)
        
        # Keep the latest keep_days files
        files_to_backup = files[:-keep_days] if len(files) > keep_days else []
        
        for file in files_to_backup:
            backup_path = self.backup_dir / file.name
            shutil.move(str(file), str(backup_path))
            self.logger.info(f"Moved {file.name} to backup") 