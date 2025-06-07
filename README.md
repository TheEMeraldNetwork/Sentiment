# Financial Sentiment Analysis Pipeline

A comprehensive market analysis pipeline that combines news sentiment analysis with analyst consensus data to generate investment insights.

## Quick Start

1. Clone the repository
2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Set up your API keys (see [API Keys Setup](#api-keys-setup))
4. Run the analysis:
```bash
./master_runner_short.py
```

## API Keys Setup

This project requires API keys from:
1. **Finnhub.io** - For financial news and market data
2. **NewsAPI** - For additional news sources

### Option 1: Configuration File (Recommended)
1. Copy the template:
```bash
cp utils/config/api_keys.template.json utils/config/api_keys.json
```

2. Edit `utils/config/api_keys.json`:
```json
{
    "FINNHUB_KEY": "your-finnhub-api-key",
    "NEWSAPI_KEY": "your-newsapi-key"
}
```

### Option 2: Environment Variables
```bash
export FINNHUB_KEY=your-finnhub-api-key
export NEWSAPI_KEY=your-newsapi-key
```

## Project Structure

```
sentiment_analysis/
├── scripts/                      # Core processing scripts
│   ├── a_collect_sentiment.py    # News sentiment analysis
│   └── e_generate_dashboard.py   # Interactive dashboard
├── utils/                        # Configuration and utilities
│   └── config/
│       ├── api_providers_config.py
│       ├── api_keys.template.json
│       └── ticker_config.py
├── results/                      # Output and archived results
├── logs/                        # Application logs
├── master_runner_short.py       # Main execution script
└── requirements.txt            # Python dependencies
```

## Features

### Sentiment Analysis
- Real-time news fetching from Finnhub
- FinBERT model for financial text analysis
- Weighted sentiment scoring:
  - Headline weight: 40%
  - Content weight: 60%
- 30-day rolling window for articles

### Interactive Dashboard
- Modern, responsive design
- Real-time sentiment tracking
- Trend indicators and historical data
- Article display with sentiment scores
- Automatic data archiving

### Automated Updates
- Automatic GitHub synchronization
- Timestamped backups
- Version tracking
- Data integrity checks

## Running the Pipeline

### Option 1: Full Pipeline (Recommended)
```bash
./master_runner_short.py
```
This will:
1. Collect latest sentiment data
2. Generate the dashboard
3. Push changes to GitHub

### Option 2: Individual Components
```bash
# Collect sentiment data only
python scripts/a_collect_sentiment.py

# Generate dashboard only
python scripts/e_generate_dashboard.py
```

## Viewing Results

The dashboard will automatically open in your default browser after generation. You can also:
1. Open `results/sentiment_report_latest.html`
2. View individual stock pages at `results/articles_TICKER_latest.html`

## Maintenance

### Data Management
- Results are stored in `results/`
- Automatic archiving of old reports
- Symlinks maintained for latest versions

### Error Handling
- Comprehensive logging
- Automatic error recovery
- Rate limiting for API calls

## Dependencies

- Python 3.8+
- FinBERT for sentiment analysis
- Finnhub API for news data
- Additional requirements in `requirements.txt`

## Testing

To verify your API setup:
```bash
python test_finnhub.py
```

## License

[MIT License]

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
