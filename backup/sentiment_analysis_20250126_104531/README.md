# Financial Sentiment Analysis Pipeline

A comprehensive market analysis pipeline that combines news sentiment analysis with analyst consensus data to generate investment insights.

## Project Structure

```
sentiment_analysis/
├── scripts/                # Core processing scripts
│   ├── a_sentiment_analysis.py  # News sentiment analysis
│   ├── b_custom_forecast.py     # Custom forecasting models
│   ├── c_external_forecast.py   # Analyst consensus data
│   ├── d_master_output.py       # Data consolidation
│   ├── e_open_html.py          # Interactive report
│   ├── backup_project.py       # Project backup utility
│   └── cleanup_project.py      # Maintenance utility
├── utils/                 # Configuration and utilities
│   └── config/
│       ├── api_providers_config.py
│       └── ticker_config.py
├── results/              # Output and archived results
│   ├── a1_sentiment_detailed.csv
│   ├── a2_sentiment_summary.csv
│   ├── c_analyst_consensus.csv
│   ├── d_master_output.csv
│   └── sentiment_report.html
├── backup/              # Periodic backups
├── requirements.txt     # Project dependencies
└── master_runner.py     # Main execution script
```

## Core Components

### Analysis Scripts
1. `a_sentiment_analysis.py`
   - Processes financial news using FinBERT model
   - Weights headline (40%) and content (60%) sentiment
   - Calculates confidence scores for predictions
   - Generates detailed and summary outputs

2. `c_external_forecast.py`
   - Fetches analyst consensus data from Yahoo Finance
   - Processes price targets and recommendations
   - Calculates potential returns based on median targets
   - Tracks number of analysts covering each stock

3. `d_master_output.py`
   - Consolidates sentiment and analyst data
   - Calculates sentiment trends (7D/15D/30D)
   - Archives historical data
   - Maintains data consistency

4. `e_open_html.py`
   - Generates interactive HTML report
   - Provides sortable and searchable interface
   - Shows trend indicators (U/D/S/N)
   - Displays analyst consensus metrics

### Analysis Methodology

1. Sentiment Analysis:
   - Real-time news fetching from Finnhub
   - FinBERT model for financial text
   - Headline weight: 40%
   - Content weight: 60%
   - Confidence scoring

2. Analyst Consensus:
   - Price targets (median, mean, high, low)
   - Number of covering analysts
   - Consensus recommendations
   - Potential return calculations

3. Time Windows:
   - 30-day sentiment window
   - 15-day trend analysis
   - 7-day short-term signals

### Trend Analysis

1. Sentiment Indicators:
   - U: Upward trend (HIGHER)
   - D: Downward trend (LOWER)
   - S: Stable trend (< 5% change)
   - N: New or insufficient data

2. Consensus Integration:
   - Analyst price targets
   - Expected return potential
   - Coverage breadth
   - Recommendation strength

## Setup and Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```python
# utils/config/api_providers_config.py
FINNHUB_KEY = 'your_api_key_here'
```

4. Update ticker list:
- Edit `utils/config/ticker_config.py`
- Add company names and symbols

## Usage

1. Run analysis:
```bash
python master_runner.py
# Choose analysis type:
# 1. Analyst Consensus only (faster)
# 2. Full analysis (Sentiment + Analyst Consensus)
```

2. View results:
```bash
python scripts/e_open_html.py
```

3. Create backup:
```bash
python scripts/backup_project.py
```

4. Clean project:
```bash
python scripts/cleanup_project.py
```

## Maintenance

1. Backup Management:
   - Automatic timestamped backups
   - Complete project state preservation
   - Retention of last 10 sentiment archives

2. Data Consistency:
   - Validation of sentiment calculations
   - Verification of analyst data
   - Archive integrity checks

3. Error Handling:
   - Graceful handling of missing data
   - Comprehensive logging
   - Automatic error recovery

## Dependencies

- Python 3.8+
- FinBERT for sentiment analysis
- yfinance for analyst data
- Pandas for data processing
- Finnhub API for news data
- Additional requirements in requirements.txt

## License

[MIT License]
