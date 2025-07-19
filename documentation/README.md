# 🐅 Tigro Financial Sentiment Analysis Pipeline

A comprehensive market analysis pipeline that combines news sentiment analysis with FinBERT AI to generate investment insights. **Currently tracking 91 stocks** with real-time sentiment monitoring and instant email reporting.

## 🚀 Current Status (Last Updated: July 12, 2025)

- ✅ **Sentiment Analysis**: Active and processing 30-day rolling news data  
- ✅ **API Integration**: Finnhub and NewsAPI working correctly
- ✅ **Historical Database**: Maintaining data since February 2025
- ✅ **Interactive Dashboard**: Live at https://theemeraldnetwork.github.io/tigro/
- ✅ **Instant Email Reports**: Integrated button in dashboard for immediate reports
- ✅ **GitHub Pages**: Automatic deployment and publishing
- ✅ **Email System**: Gmail integration with app-specific password
- ❌ **Automated Scheduling**: Cron/launchd issues on macOS (manual execution working)

## 🌟 Key Features

### 🧠 Advanced Sentiment Analysis
- **FinBERT Model**: Purpose-built for financial text analysis
- **Multi-source Data**: Real-time news from Finnhub API and NewsAPI
- **Weighted Scoring**: 
  - Headline weight: 40%
  - Content weight: 60%
- **30-day Rolling Window**: Captures recent market sentiment trends
- **91 Stocks Tracked**: Comprehensive coverage across sectors

### 📊 Interactive Dashboard
- **Live Dashboard**: https://theemeraldnetwork.github.io/tigro/
- **Modern UI**: Responsive design with professional styling
- **Real-time Tracking**: Live sentiment scores and trends
- **Historical Analysis**: Trend indicators and comparative data
- **Individual Stock Pages**: Detailed article breakdown per ticker
- **Instant Email Reports**: Send reports immediately via dashboard button

### 📧 Email Reporting System
- **Instant Reports**: Click button in dashboard for immediate email
- **Gmail Integration**: Secure SMTP with app-specific password
- **Rich HTML Format**: Professional email layout with alerts
- **Trend Analysis**: Automatic detection of declining stocks
- **Weekly Summaries**: Comprehensive market overview

### 🗄️ Historical Database Management
- **Structured Storage**: Daily snapshots in CSV format
- **Trend Analysis**: Automatic calculation of sentiment changes
- **Backup System**: 30-day retention with automatic cleanup
- **Data Integrity**: Comprehensive logging and error handling

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sentiment_analysis.git
cd sentiment_analysis
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **Configure API keys** (see [Security Setup](#security-setup))

4. **Run the analysis**
```bash
python master_runner_short.py
```

5. **View results**: Dashboard opens automatically or visit https://theemeraldnetwork.github.io/tigro/

## Security Setup

### API Keys Configuration
Create your API keys file (never commit to git):
```bash
cp utils/config/api_keys.template.json utils/config/api_keys.json
```

Edit `utils/config/api_keys.json`:
```json
{
    "FINNHUB_KEY": "your-finnhub-api-key",
    "NEWSAPI_KEY": "your-newsapi-key"
}
```

### Email Configuration
For instant email reports, you'll need Gmail app-specific password:
1. Enable 2-factor authentication on Gmail
2. Generate app-specific password
3. Configure in your email system (not stored in git)

### Webhook Security
The instant email system uses authentication token `tigro_2025_secure` for webhook security.

### Protected Files
The following files are automatically excluded from git:
- `utils/config/api_keys.json` - API keys
- `.env` - Environment variables
- `*.pem`, `*.key` - Certificates and private keys
- `credentials.json` - OAuth credentials

## Project Structure

```
sentiment_analysis/
├── scripts/                      # Core processing scripts
│   ├── a_collect_sentiment.py    # News sentiment analysis (FinBERT)
│   ├── e_generate_dashboard.py   # Interactive dashboard generation
│   └── whatsapp_trigger.py       # Webhook service for instant emails
├── utils/                        # Configuration and utilities
│   ├── config/
│   │   ├── api_providers_config.py    # API configuration
│   │   ├── api_keys.json             # API keys (create from template)
│   │   └── ticker_config.py          # Stock symbol mappings
│   ├── db/
│   │   └── sentiment_history.py      # Historical data management
│   └── email/
│       └── report_sender.py          # Email system
├── database/                     # Historical sentiment data storage
│   └── sentiment/
│       ├── detailed/            # Article-level sentiment data
│       └── summary/             # Stock-level aggregated data
├── docs/                         # GitHub Pages deployment
│   ├── assets/                  # CSS and styling
│   └── *.html                   # Published reports
├── results/                      # Output and archived results
│   ├── sentiment_*_latest.csv   # Latest sentiment analysis
│   ├── articles_*_latest.html   # Individual stock reports
│   └── sentiment_report_latest.html  # Main dashboard
├── master name ticker.csv       # 91 stocks (sorted A-Z, no duplicates)
├── master_runner_short.py       # Main execution script
└── requirements.txt            # Python dependencies
```

## Usage

### Option 1: Full Pipeline (Recommended)
```bash
python master_runner_short.py
```
This will:
1. Collect latest sentiment data from APIs
2. Generate interactive dashboard and individual stock pages
3. Update historical database
4. Push changes to GitHub Pages
5. Open dashboard in browser

### Option 2: Individual Components
```bash
# Collect sentiment data only
python scripts/a_collect_sentiment.py

# Generate dashboard only
python scripts/e_generate_dashboard.py

# Start webhook service for instant emails
python scripts/whatsapp_trigger.py
```

### Option 3: Instant Email Reports
1. Visit https://theemeraldnetwork.github.io/tigro/
2. Click "📧 Send Instant Report" button
3. Report will be sent immediately to configured email

## Viewing Results

1. **Live Dashboard**: https://theemeraldnetwork.github.io/tigro/
2. **Local Dashboard**: Open `results/sentiment_report_latest.html`
3. **Individual Stocks**: View `results/articles_TICKER_latest.html` 
4. **Raw Data**: Check `results/sentiment_summary_latest.csv`

## System Architecture

### Data Flow
1. **News Collection**: Finnhub API + NewsAPI → Raw articles
2. **Sentiment Analysis**: FinBERT model → Sentiment scores
3. **Historical Integration**: Database updates → Trend analysis
4. **Dashboard Generation**: HTML reports → GitHub Pages
5. **Email Reporting**: Webhook service → Gmail SMTP

### Technology Stack
- **AI Model**: FinBERT (Financial BERT)
- **APIs**: Finnhub, NewsAPI
- **Frontend**: HTML/CSS/JavaScript
- **Backend**: Python Flask (webhook service)
- **Database**: CSV-based historical storage
- **Deployment**: GitHub Pages
- **Email**: Gmail SMTP with app passwords

## Troubleshooting

### Common Issues
```bash
# Test API connectivity
python test_finnhub.py

# Check logs
tail -f logs/sentiment_analysis.log

# Validate data integrity
python utils/db/sentiment_history.py

# Test email system
python -c "from utils.email.report_sender import SentimentEmailSender; sender = SentimentEmailSender(); print('Email system ready')"
```

### Debug Webhook Service
```bash
# Start webhook service in debug mode
python scripts/whatsapp_trigger.py

# Test endpoints
curl -X GET http://localhost:5001/status
curl -X POST http://localhost:5001/email-only -H "Content-Type: application/json" -d '{"token": "tigro_2025_secure"}'
```

## Dependencies

Core packages:
- `transformers>=4.30.0` (FinBERT model)
- `pandas>=2.0.0` (data processing)
- `finnhub-python>=2.4.18` (API client)
- `flask>=2.0.0` (webhook service)
- `flask-cors>=4.0.0` (CORS handling)
- `requests>=2.25.0` (HTTP requests)

See `requirements.txt` for complete list.

## Future Automation Exploration

### Zapier Integration (Explored)
We investigated Zapier for WhatsApp triggers but found limitations:
- **Issue**: Zapier doesn't support WhatsApp Business API triggers
- **Alternative**: Could use Zapier webhooks with SMS or email triggers
- **Setup**: Would require Zapier Pro account for webhook functionality

### Telegram Bot Integration (Explored)
We created a Telegram bot for instant triggers:
- **Bot Token**: `7703923976:AAEL5VoAsSEPwQ__i5K1okbiaLjMNevt-c`
- **Status**: Authentication issues encountered
- **Potential**: Good alternative for instant messaging triggers
- **Future**: Consider re-implementing with proper bot activation

### Alternative Automation Options
1. **GitHub Actions**: Schedule runs via GitHub workflows
2. **Cloud Functions**: AWS Lambda, Google Cloud Functions
3. **Email Triggers**: IFTTT email-to-webhook automation
4. **SMS Integration**: Twilio webhook integration
5. **Calendar Integration**: Google Calendar webhook triggers

### Current Webhook Service
The Flask webhook service (`scripts/whatsapp_trigger.py`) provides:
- **Instant Email Endpoint**: `/email-only` for dashboard integration
- **Full Pipeline Endpoint**: `/trigger` for complete runs
- **Health Check**: `/status` for monitoring
- **Security**: Token-based authentication
- **CORS**: Configured for GitHub Pages integration

## Recent Updates

### July 12, 2025
- ✅ Implemented instant email reporting via dashboard button
- ✅ Created webhook service for real-time triggers
- ✅ Fixed CORS issues for GitHub Pages integration
- ✅ Added authentication tokens for webhook security
- ✅ Tested complete email pipeline (2-3 second response time)
- ✅ Updated dashboard with Tigro branding and modern styling

### January 8, 2025
- ✅ Verified all systems operational
- ✅ Sorted master ticker list alphabetically  
- ✅ Removed duplicate ticker (CTRA)
- ✅ Confirmed API connectivity and data flow
- ✅ Validated historical database integrity

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions:
1. Check the logs in `/logs` directory
2. Run `python test_finnhub.py` to verify API setup
3. Review recent results in `/results` directory
4. Check database integrity in `/database/sentiment`
5. Visit live dashboard: https://theemeraldnetwork.github.io/tigro/

---

**Last Verified**: July 12, 2025 - All systems operational ✅  
**Dashboard**: https://theemeraldnetwork.github.io/tigro/  
**Instant Email**: ✅ Working (2-3 second response)
