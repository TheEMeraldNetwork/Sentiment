# 🐅 TIGRO - AI-Powered Market Sentiment Analysis System

<div align="center">

**🌐 Live Dashboard**: https://theemeraldnetwork.github.io/sentiment/  
**📊 GitHub Actions**: https://github.com/TheEMeraldNetwork/Sentiment/actions  
**📧 Email Alerts**: Daily automated reports with declining stock notifications  

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![AI](https://img.shields.io/badge/AI-FinBERT-orange)
![Automation](https://img.shields.io/badge/Automation-GitHub%20Actions-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

</div>

---

## 📋 **TABLE OF CONTENTS**

1. [🎯 System Overview](#-system-overview)
2. [🚀 Quick Start](#-quick-start)
3. [🗂️ Project Structure](#-project-structure)
4. [⚙️ Installation & Setup](#-installation--setup)
5. [🤖 GitHub Actions Automation](#-github-actions-automation)
6. [📊 Portfolio Optimization](#-portfolio-optimization)
7. [🔧 Manual Operations](#-manual-operations)
8. [📁 File Documentation](#-file-documentation)
9. [🔍 Troubleshooting](#-troubleshooting)
10. [📈 Development History](#-development-history)

---

## 🎯 **SYSTEM OVERVIEW**

### **What is TIGRO?**
TIGRO is a dual-purpose financial system combining:
- **🧠 AI-Powered Sentiment Analysis**: FinBERT analysis of 149 stocks with daily automation
- **📊 Portfolio Optimization**: Markowitz Mean-Variance optimization with analyst-driven returns

### **Current Status**
- ✅ **Sentiment Analysis**: Production ready, fully automated
- ⚠️ **Portfolio Optimization**: Operational but under redesign
- 🔄 **Daily Automation**: Running at 2:50 PM CET via GitHub Actions
- 📧 **Email Alerts**: Active with Gmail integration

### **Live System**
- **Dashboard**: https://theemeraldnetwork.github.io/sentiment/
- **Stocks Analyzed**: 149 companies daily
- **Data Source**: Finnhub API + FinBERT AI
- **Update Frequency**: Daily automated + manual triggers
- **Email Reports**: Daily declining stock alerts

---

## 🚀 **QUICK START**

### **For End Users:**
1. **View Dashboard**: https://theemeraldnetwork.github.io/sentiment/
2. **Trigger Analysis**: Click "🔄 Update Analysis" button
3. **Send Email**: Click "📧 Send Email Report" button
4. **Monitor**: Check GitHub Actions for workflow status

### **For Developers:**
```bash
# Clone and setup
git clone https://github.com/TheEMeraldNetwork/Sentiment.git
cd sentiment_analysis
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run sentiment analysis
python scripts/sentiment/sent_collect_data.py

# Generate dashboard
python scripts/visualization/viz_dashboard_generator.py

# Run portfolio optimization
python run_portfolio_optimization.py
```

---

## 🗂️ **PROJECT STRUCTURE**

```
sentiment_analysis/
├── 📊 CORE SYSTEM
│   ├── master_runner_short.py          # Main automation script
│   ├── run_portfolio_optimization.py   # Portfolio analysis runner
│   ├── index.html                       # Dashboard redirect
│   └── requirements.txt                 # Python dependencies
│
├── 📁 SCRIPTS (Core Logic)
│   ├── sentiment/
│   │   └── sent_collect_data.py         # FinBERT sentiment analysis
│   ├── visualization/
│   │   └── viz_dashboard_generator.py   # Dashboard creation
│   ├── optimization/
│   │   ├── opt_markowitz_engine.py      # Portfolio optimization
│   │   └── opt_portfolio_optimizer.py   # Main optimizer
│   └── financial/
│       └── fin_market_data.py           # Market data collection
│
├── 🔧 UTILITIES & CONFIG
│   ├── utils/
│   │   ├── config/                      # API keys & configuration
│   │   ├── db/                          # Database operations
│   │   └── email/                       # Email reporting
│   └── config/
│       └── com.tigro.daily.plist        # macOS automation
│
├── 📊 DATA & RESULTS
│   ├── data/
│   │   ├── database/sentiment/          # Historical sentiment data
│   │   ├── market/                      # Market data cache
│   │   └── results/                     # Generated reports
│   ├── results/                         # Latest analysis outputs
│   └── docs/                           # GitHub Pages content
│
├── 🤖 AUTOMATION
│   ├── .github/workflows/
│   │   ├── sentiment_analysis.yml       # Main automation workflow
│   │   └── send_email.yml              # Email workflow
│   └── tests/                          # System tests
│
└── 📝 DATA FILES
    ├── master name ticker.csv          # Stock universe (149 stocks)
    ├── actual-portfolio-master.csv     # Current portfolio
    └── database/sentiment/             # Historical data
```

---

## ⚙️ **INSTALLATION & SETUP**

### **System Requirements**
- Python 3.8+
- Git
- Virtual environment support
- Internet connection for APIs

### **Dependencies**
```bash
# Core libraries
pandas>=1.3.0
numpy>=1.21.0
torch>=1.9.0
transformers>=4.21.0

# APIs & Data
yfinance>=0.1.74
finnhub-python>=2.4.10
requests>=2.28.0

# Visualization
plotly>=5.10.0
beautifulsoup4>=4.11.0

# Email & Utilities
python-dateutil>=2.8.0
tqdm>=4.64.0
```

### **API Configuration**
Required API keys (already configured):
- **Finnhub API**: `cu0qch9r01qjiermd96gcu0qch9r01qjiermd970`
- **NewsAPI**: `c6a86bf7051d46059a2d316e88ac2d4b`
- **Gmail Email**: `davideconsiglio1978@gmail.com`
- **Gmail App Password**: `yapl pqyf rzpp olbr`

### **Local Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify API configuration
python -c "from utils.config.api_providers_config import FINNHUB_KEY; print('API Key loaded:', FINNHUB_KEY[:10] + '...')"

# Test sentiment analysis
python scripts/sentiment/sent_collect_data.py

# Generate dashboard
python scripts/visualization/viz_dashboard_generator.py
```

---

## 🤖 **GITHUB ACTIONS AUTOMATION**

### **Overview**
The system uses GitHub Actions for cloud-based automation, eliminating the need for local computer uptime.

### **Workflows Created**
- ✅ **sentiment_analysis.yml**: Main automation (daily 2:50 PM CET)
- ✅ **send_email.yml**: Email report sending

### **Setup GitHub Secrets**

**Repository**: https://github.com/TheEmeraldNetwork/Sentiment

**Steps**:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add these 4 secrets:

```
Secret #1:
Name: FINNHUB_API_KEY
Value: cu0qch9r01qjiermd96gcu0qch9r01qjiermd970

Secret #2: 
Name: ALPHA_VANTAGE_API_KEY
Value: c6a86bf7051d46059a2d316e88ac2d4b

Secret #3:
Name: GMAIL_EMAIL  
Value: davideconsiglio1978@gmail.com

Secret #4:
Name: GMAIL_APP_PASSWORD
Value: yapl pqyf rzpp olbr
```

### **How to Use Dashboard Buttons**

#### **🔄 Update Analysis Button**
1. Click "🔄 Update Analysis" on dashboard
2. Redirects to GitHub Actions
3. Click "Run workflow" → "Run workflow" 
4. Process takes ~5-10 minutes
5. Dashboard updates automatically

#### **📧 Send Email Button**
1. Click "📧 Send Email Report"
2. Redirects to email workflow
3. Click "Run workflow" → "Run workflow"
4. Email sent in ~2 minutes

### **Monitoring Workflows**
- **Status**: https://github.com/TheEmeraldNetwork/Sentiment/actions
- **Logs**: Click on workflow runs for detailed output
- **Dashboard**: Updates automatically after completion

### **Automatic Triggers**
- **Daily**: 2:50 PM CET (13:50 UTC)
- **Manual**: Via dashboard buttons
- **Code changes**: When scripts are updated

---

## 📊 **PORTFOLIO OPTIMIZATION**

### **System Overview**
- **Framework**: Markowitz Mean-Variance Optimization (1952)
- **Data Source**: Analyst targets (conservative) + yfinance
- **Approach**: Risk-constrained return maximization
- **Status**: Operational (under redesign)

### **Key Features**
- **Conservative Returns**: Uses analyst target lows with 10% momentum discount
- **Fundamental Screening**: P/E < 10, Expected return > 10%, 5+ strong buys
- **Risk Management**: VaR constraint (max 15% annual loss)
- **Sentiment Integration**: Display-only for tactical timing

### **Usage**
```bash
# Run optimization
python run_portfolio_optimization.py

# Output file
portfolio_optimization_report_YYYYMMDD_HHMMSS.txt
```

### **Mathematical Foundation**
- **Objective**: `Sharpe Ratio = (E[R] - Rf) / σ(R)`
- **Portfolio Return**: `E[Rp] = Σ(wi × E[Ri])`
- **Portfolio Risk**: `σp² = Σ Σ (wi × wj × σij)`
- **VaR Calculation**: `VaR₉₇% = μp - 2.33 × σp`

### **Safety Features**
- ✅ Conservative analyst estimates (target low)
- ✅ Momentum risk discounting
- ✅ Profitability requirements (P/E > 0)
- ✅ Stop-loss recommendations (-8%)
- ✅ Mathematical validation

---

## 🔧 **MANUAL OPERATIONS**

### **Daily Automation (Local)**
```bash
# Complete workflow
python master_runner_short.py

# Individual steps
python scripts/sentiment/sent_collect_data.py
python scripts/visualization/viz_dashboard_generator.py
```

### **Email Operations**
```bash
# Send email report
python -c "
from utils.email.report_sender import SentimentEmailSender
import pandas as pd
df = pd.read_csv('results/sentiment_summary_latest.csv')
sender = SentimentEmailSender()
sender.send_email(df)
"
```

### **Data Management**
```bash
# View latest results
ls -la results/sentiment_*latest*

# Check database
ls -la database/sentiment/summary/

# Archive old data
python scripts/utilities/util_audit_reviewer.py
```

---

## 📁 **FILE DOCUMENTATION**

### **🔥 Core System Files**

#### **`master_runner_short.py`** (12KB, 328 lines)
**Purpose**: Main automation orchestrator
**Functions**:
- Sentiment data collection
- Dashboard generation  
- GitHub push operations
- Email report sending
- Comprehensive logging
**Usage**: `python master_runner_short.py`
**Critical**: ✅ Production ready, do not modify

#### **`run_portfolio_optimization.py`** (7.8KB, 190 lines)
**Purpose**: Portfolio optimization execution
**Functions**:
- Markowitz optimization
- Risk-return analysis
- Performance reporting
- Fundamental screening
**Usage**: `python run_portfolio_optimization.py`
**Status**: ⚠️ Operational but under redesign

#### **`index.html`** (10KB, 334 lines)
**Purpose**: Dashboard entry point with interactive buttons
**Functions**:
- Redirect to latest dashboard
- GitHub Actions integration
- Real-time statistics
- Loading states and alerts
**Location**: Root directory
**Critical**: ✅ Production ready

### **🧠 Sentiment Analysis Engine**

#### **`scripts/sentiment/sent_collect_data.py`** (255 lines)
**Purpose**: Core FinBERT sentiment analysis
**Functions**:
- Finnhub API integration
- News article processing
- FinBERT model execution
- Sentiment scoring and aggregation
**Input**: Stock tickers from master list
**Output**: Detailed and summary sentiment CSV files
**Critical**: ✅ Production ready, do not modify

#### **`scripts/visualization/viz_dashboard_generator.py`**
**Purpose**: HTML dashboard creation
**Functions**:
- Interactive data visualization
- Plotly chart generation
- Responsive design
- GitHub Pages compatibility
**Input**: Sentiment analysis results
**Output**: HTML dashboard files
**Critical**: ✅ Production ready

### **🔧 Utilities & Configuration**

#### **`utils/config/api_providers_config.py`** (76 lines)
**Purpose**: API key management and validation
**Functions**:
- API key loading from JSON/environment
- Connection testing
- Error handling
**Required Keys**: Finnhub, NewsAPI, Gmail
**Critical**: ✅ Essential for all operations

#### **`utils/email/report_sender.py`**
**Purpose**: Automated email reporting
**Functions**:
- Gmail SMTP integration
- HTML email generation
- Declining stock alerts
- Error handling
**Config**: Gmail credentials in email_config.json
**Critical**: ✅ Production ready

#### **`utils/db/sentiment_history.py`**
**Purpose**: Historical data management
**Functions**:
- SQLite database operations
- Data archiving
- Trend analysis
**Storage**: database/sentiment/ directory
**Status**: ✅ Operational

### **📊 Data Files**

#### **`master name ticker.csv`** (4KB, 153 lines)
**Purpose**: Stock universe definition
**Content**: 149 stocks with tickers and company names
**Format**: CSV with Ticker, Name columns
**Usage**: Source for all sentiment analysis
**Critical**: ✅ Do not modify without testing

#### **`actual-portfolio-master.csv`** (2.1KB, 20 lines)  
**Purpose**: Current portfolio holdings
**Content**: European-formatted portfolio data
**Format**: Symbol, Quantity, Price, Value columns
**Usage**: Portfolio optimization input
**Status**: ⚠️ Manual updates required

### **🤖 Automation Files**

#### **`.github/workflows/sentiment_analysis.yml`**
**Purpose**: Main GitHub Actions workflow
**Triggers**: Daily 2:50 PM CET, manual, code changes
**Functions**:
- Complete sentiment analysis pipeline
- Dashboard generation and deployment
- Email sending (optional)
- Error handling and reporting
**Status**: ✅ Production ready

#### **`.github/workflows/send_email.yml`**
**Purpose**: Dedicated email workflow
**Triggers**: Manual via dashboard button
**Functions**:
- Email report generation
- Gmail integration
- Error handling
**Status**: ✅ Production ready

#### **`config/com.tigro.daily.plist`**
**Purpose**: macOS LaunchAgent configuration
**Function**: Local daily automation backup
**Schedule**: 2:50 PM CET daily
**Status**: ✅ Backup system (GitHub Actions preferred)

### **📝 Dependencies & Setup**

#### **`requirements.txt`** (551B, 33 lines)
**Purpose**: Python package dependencies
**Content**: All required libraries with versions
**Usage**: `pip install -r requirements.txt`
**Status**: ✅ Verified and tested

#### **`.gitignore`** (569B, 49 lines)
**Purpose**: Git exclusion patterns
**Excludes**: API keys, temporary files, virtual environments
**Status**: ✅ Security configured

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **API Errors**
```bash
# Test API connectivity
python -c "from utils.config.api_providers_config import FINNHUB_KEY; print('API Key:', FINNHUB_KEY[:10] + '...')"

# Verify API limits
# Finnhub: 60 calls/minute, 500/day (free tier)
```

#### **GitHub Actions Failures**
1. **Check Secrets**: Ensure all 4 repository secrets are set
2. **Check Logs**: Click on failed workflow for details  
3. **API Limits**: Wait and retry if rate limited
4. **Manual Backup**: Run locally if GitHub fails

#### **Dashboard Not Updating**
1. **Check Workflow Status**: GitHub Actions completed successfully
2. **Wait 2-3 minutes**: GitHub Pages deployment delay
3. **Hard Refresh**: Ctrl+F5 or Cmd+Shift+R
4. **Check Files**: Verify sentiment_report_latest.html exists

#### **Email Not Sending**
```bash
# Test email configuration
python -c "
from utils.email.report_sender import SentimentEmailSender
sender = SentimentEmailSender()
print('Email config loaded successfully')
"
```

#### **Missing Data**
```bash
# Check data files
ls -la results/sentiment_*latest*
ls -la database/sentiment/summary/

# Regenerate if missing
python scripts/sentiment/sent_collect_data.py
```

### **Manual Recovery**
```bash
# Complete system reset
python master_runner_short.py

# Individual components
python scripts/sentiment/sent_collect_data.py
python scripts/visualization/viz_dashboard_generator.py

# Force GitHub push
git add -A && git commit -m "Manual update" && git push
```

---

## 📈 **DEVELOPMENT HISTORY**

### **July 28, 2025 - Production Checkpoint**
- ✅ Sentiment analysis system declared production ready
- ✅ 149 stocks analyzed daily with FinBERT
- ✅ LaunchAgent automation working
- ✅ Email integration operational
- ✅ GitHub Pages deployment active
- ⚠️ Portfolio optimization flagged for redesign

### **Recent Enhancements**
- ✅ GitHub Actions implementation (cloud automation)
- ✅ Interactive dashboard buttons
- ✅ Real-time workflow status
- ✅ Comprehensive error handling
- ✅ Email alert system
- ✅ Historical data management

### **Current Focus**
- 🔄 GitHub Actions optimization
- 🔄 Dashboard user experience
- 🔄 Portfolio optimization redesign
- 🔄 Error recovery automation

---

## 🎯 **SYSTEM STATUS**

| Component | Status | Last Update | Notes |
|-----------|--------|-------------|-------|
| **Sentiment Analysis** | ✅ Production | Daily | 149 stocks, FinBERT AI |
| **GitHub Actions** | ✅ Active | Daily 2:50 PM | Cloud automation |
| **Dashboard** | ✅ Live | Real-time | Interactive buttons |
| **Email Alerts** | ✅ Working | Daily | Gmail integration |
| **Portfolio Optimization** | ⚠️ Redesign | On-demand | Markowitz model |
| **API Integration** | ✅ Stable | Continuous | Finnhub + NewsAPI |

---

## 📞 **SUPPORT & CONTACT**

- **Live Dashboard**: https://theemeraldnetwork.github.io/sentiment/
- **GitHub Repository**: https://github.com/TheEmeraldNetwork/Sentiment
- **Workflow Status**: https://github.com/TheEmeraldNetwork/Sentiment/actions
- **Issues**: Use GitHub Issues for bug reports and feature requests

---

**🐅 TIGRO System - AI-Powered Market Intelligence**  
*Built with Python, FinBERT AI, and GitHub Actions automation* 