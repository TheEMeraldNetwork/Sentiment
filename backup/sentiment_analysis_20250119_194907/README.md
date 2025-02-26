# Financial Sentiment Analysis Pipeline

A sophisticated financial analysis pipeline that combines news sentiment analysis, custom forecasting, and external analyst data to generate comprehensive investment insights.

## Project Structure

```
├── scripts/              # Core processing scripts
├── results/              # Output and archived results
├── utils/               # Configuration and utilities
├── backup/              # Periodic backups
└── master_runner.py     # Main execution script
```

## Core Components

### Analysis Scripts
1. `scripts/a_sentiment_analysis.py`
   - Processes financial news using FinBERT model
   - Generates detailed and summary sentiment outputs
   - Uses Finnhub API for real-time news data
   - Weights headline (40%) and content (60%) sentiment
   - Calculates confidence scores for predictions

2. `scripts/b_custom_forecast.py`
   - Implements Bayesian network analysis
   - Combines historical data with sentiment
   - Generates custom return predictions
   - Integrates market metrics and sentiment scores

3. `scripts/c_external_forecast.py`
   - Fetches analyst forecasts and recommendations
   - Processes price targets and consensus data
   - Uses Yahoo Finance as data source
   - Provides external validation metrics

4. `scripts/d_master_output.py`
   - Consolidates all analysis results
   - Calculates sentiment trends (7D/15D/30D)
   - Archives historical sentiment data
   - Compares with previous runs for trend analysis
   - Maintains historical data with timestamps

5. `scripts/e_open_html.py`
   - Generates interactive HTML report
   - Provides sortable and searchable interface
   - Shows trend indicators (U/D/S/N)
   - Color-codes top and bottom performers
   - Implements responsive design and keyboard shortcuts

### Output Files

1. Sentiment Analysis:
   - `results/a1_sentiment_detailed.csv`: Article-level sentiment with full details
   - `results/a2_sentiment_summary.csv`: Aggregated company-level sentiment
   - `results/a2_sentiment_summary_*.csv`: Historical archives with timestamps
   - `results/d_master_output.csv`: Final consolidated output with trends
   - `results/sentiment_report.html`: Interactive web report

### Sentiment Analysis Methodology

1. Data Collection:
   - Real-time news fetching from Finnhub
   - Multiple news sources integration
   - Automatic deduplication of articles

2. Sentiment Processing:
   - FinBERT model trained on financial text
   - Headline weight: 40%
   - Content weight: 60%
   - Confidence scoring for each prediction

3. Time Windows:
   - 30-day window: Base sentiment calculation
   - 15-day window: Medium-term trend analysis
   - 7-day window: Short-term trend detection

### Trend Analysis

1. Indicators:
   - U: Upward trend (HIGHER) - Positive sentiment change
   - D: Downward trend (LOWER) - Negative sentiment change
   - S: Stable trend (< 5% change) - Minimal variation
   - N: New or insufficient data

2. Calculation:
   - Compares current sentiment with previous archived run
   - Uses 5% threshold for trend determination
   - Handles missing data and new stocks appropriately
   - Archives results for historical tracking

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys:
```python
# utils/config/api_providers_config.py
FINNHUB_KEY = 'your_api_key_here'
```

3. Update ticker list:
- Edit `utils/config/ticker_config.py`
- Add company names and symbols
- Configure any custom groupings

## Usage

Run complete analysis:
```bash
python master_runner.py
```

Open HTML report directly:
```bash
python scripts/e_open_html.py
```

## Data Flow

1. Sentiment Analysis:
   - Fetches news articles
   - Processes with FinBERT
   - Generates detailed and summary outputs
   - Archives results with timestamps

2. Trend Analysis:
   - Compares current with previous sentiment
   - Calculates trends for different timeframes
   - Archives results for historical tracking
   - Maintains data consistency

3. Output Generation:
   - Consolidates all metrics
   - Generates interactive HTML report
   - Archives historical data
   - Provides trend visualization

## Interactive Report Features

1. Display:
   - Sortable columns
   - Search functionality
   - Color-coded top/bottom performers
   - Trend indicators next to sentiment values

2. Navigation:
   - Keyboard shortcuts (e.g., Ctrl+F for search)
   - Sticky header during scroll
   - Responsive layout
   - Auto-refresh capability

## Maintenance

- Historical data is archived with timestamps
- Regular backups in backup/ directory
- Cleanup of old archives (keep last 5-10 versions)
- Periodic validation of data consistency

## Error Handling

- Graceful handling of missing data
- Logging of processing errors
- Validation of input data
- Backup of critical outputs

## License

[MIT License]
