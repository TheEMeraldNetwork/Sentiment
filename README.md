# 🐅 TIGRO - Financial Sentiment Analysis & Portfolio Management System

[![GitHub Pages](https://img.shields.io/badge/Live%20Dashboard-GitHub%20Pages-blue)](https://theemeraldnetwork.github.io/tigro/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Status](https://img.shields.io/badge/Sentiment%20Analysis-PRODUCTION-brightgreen)](https://theemeraldnetwork.github.io/tigro/)
[![Status](https://img.shields.io/badge/Portfolio%20Optimization-REDESIGN%20NEEDED-red)](#portfolio-optimization-status)

## 📍 CURRENT CHECKPOINT STATUS (July 28, 2025)

### ✅ **PRODUCTION READY - DO NOT MODIFY**
**SENTIMENT ANALYSIS SYSTEM**: Fully operational, deployed, and generating daily reports.

**🚨 CRITICAL WARNING**: The sentiment analysis flow is a **PROTECTED PRODUCTION SYSTEM**. Any future dashboard or portfolio optimization work **MUST NOT** modify or interfere with the sentiment analysis components.

### ❌ **NEEDS COMPLETE REDESIGN**
**PORTFOLIO OPTIMIZATION**: Requires full rebuild with proper mathematical foundations and clean architecture.

---

## 🎯 **SYSTEM OVERVIEW**

TIGRO (The Investment Growth & Risk Optimization) system combines:
1. **✅ AI-Powered Sentiment Analysis** (FinBERT) - PRODUCTION READY
2. **❌ Portfolio Optimization** (Markowitz + Strategic Constraints) - NEEDS REDESIGN
3. **🔄 Automated Daily Reports** - WORKING
4. **📊 Interactive Dashboard** - WORKING (Sentiment Only)

---

## 🔒 **PROTECTED PRODUCTION COMPONENTS**

### **⚡ Sentiment Analysis Pipeline** 
**STATUS**: 🟢 FULLY OPERATIONAL - **DO NOT TOUCH**

**Components Protected:**
- `scripts/a_collect_sentiment.py` - Core sentiment collection
- `master_runner_short.py` - Daily automation runner  
- `master name ticker.csv` - Stock universe (132+ stocks)
- All FinBERT AI processing logic
- Email automation system
- Dashboard generation for sentiment data
- `docs/sentiment_report_latest.html` - Live dashboard
- `index.html` - Redirect to sentiment dashboard

**Live Dashboard**: https://theemeraldnetwork.github.io/tigro/

**Features Working:**
- ✅ 132+ stocks analyzed daily
- ✅ FinBERT AI sentiment scoring
- ✅ Trend analysis (Last Week vs Last Month)
- ✅ Article count and confidence metrics
- ✅ Automated email reports
- ✅ GitHub Pages deployment
- ✅ LaunchAgent automation (5:15 PM CET)
- ✅ Comprehensive logging system

**Data Flow:**
```
Article Collection → FinBERT Processing → Sentiment Scoring → 
Trend Analysis → Dashboard Generation → Email Reports → GitHub Deploy
```

---

## ❌ **PORTFOLIO OPTIMIZATION - REDESIGN REQUIRED**

### **Current Issues Identified:**
1. **Mathematical Errors**: VaR calculation bugs, incorrect covariance matrices
2. **Logic Conflicts**: Pure Markowitz vs Strategic constraints incompatible
3. **Data Integration**: Sentiment-Portfolio symbol mapping issues
4. **Floating Point Precision**: Action classification errors (NVIDIA case)
5. **Architecture**: Monolithic, hard to test and validate
6. **User Experience**: Complex output format, mixed data sources

### **What Needs Complete Rebuild:**
- All optimization scripts in `scripts/optimization/`
- Portfolio dashboard integration
- Mathematical foundations
- Data validation systems
- User interface for portfolio recommendations

### **Requirements for Redesign:**
1. **Clean Separation**: Sentiment analysis must remain untouched
2. **Mathematical Rigor**: Proper covariance, VaR, Sharpe calculations
3. **Strategic Order**: SELL → TRIM → BUY NEW → TOP UP
4. **Budget Constraints**: Maximum $10,000 new cash deployment
5. **Return Targets**: 10-12% annual returns with acceptable Sharpe ratio
6. **Real Money Ready**: No hardcoded values, full validation

---

## 📁 **PROJECT STRUCTURE**

### **🔒 PROTECTED (Production Sentiment Analysis)**
```
sentiment_analysis/
├── scripts/
│   ├── a_collect_sentiment.py          # 🔒 PROTECTED - Core sentiment engine
│   └── e_generate_dashboard.py         # 🔒 PROTECTED - Dashboard generator
├── master_runner_short.py              # 🔒 PROTECTED - Daily automation
├── master name ticker.csv              # 🔒 PROTECTED - Stock universe
├── index.html                          # 🔒 PROTECTED - Dashboard redirect
├── docs/sentiment_report_latest.html   # 🔒 PROTECTED - Live dashboard
├── database/sentiment/                 # 🔒 PROTECTED - Historical data
├── results/                            # 🔒 PROTECTED - Generated reports
└── utils/                              # 🔒 PROTECTED - Support modules
```

### **❌ TO BE REDESIGNED (Portfolio Optimization)**
```
├── scripts/optimization/               # ❌ REBUILD REQUIRED
├── scripts/financial/                  # ❌ REBUILD REQUIRED  
├── scripts/visualization/              # ❌ REBUILD REQUIRED
├── actual-portfolio-master.csv         # ✅ Data source (keep)
└── Any portfolio dashboard files       # ❌ REBUILD REQUIRED
```

### **✅ SUPPORTING INFRASTRUCTURE**
```
├── config/                             # ✅ Configuration files
├── automation/                         # ✅ LaunchAgent & monitoring
├── documentation/                      # ✅ Setup guides
├── requirements.txt                    # ✅ Dependencies
└── .gitignore                          # ✅ Git configuration
```

---

## 🚀 **DEPLOYMENT & AUTOMATION**

### **Daily Automation (WORKING)**
- **Schedule**: 5:15 PM CET daily
- **LaunchAgent**: `com.tigro.daily.plist`
- **Process**: Sentiment collection → Dashboard update → Email report → GitHub deploy
- **Monitoring**: `logs/tigro_master_detailed.log`
- **Runtime**: ~18 minutes for 132+ stocks

### **Email Integration (WORKING)**
- **Gmail**: davideconsiglio1978@gmail.com
- **App Password**: yapl pqyf rzpp olbr
- **Reports**: Detailed HTML + Summary
- **Frequency**: Daily after analysis completion

---

## 🔧 **INSTALLATION & SETUP**

### **Requirements**
```bash
Python 3.8+
Virtual Environment (venv/)
Required packages in requirements.txt
```

### **Quick Start (Sentiment Analysis Only)**
```bash
# Clone repository
git clone <repository-url>
cd sentiment_analysis

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run sentiment analysis
python master_runner_short.py
```

### **Configuration Files**
- `utils/config/api_keys.json` - API credentials
- `config/com.tigro.daily.plist` - LaunchAgent automation
- `master name ticker.csv` - Stock universe

---

## 📊 **DATA SOURCES & INTEGRATIONS**

### **Sentiment Analysis Sources**
- **News Articles**: Financial news aggregation
- **AI Processing**: FinBERT transformer model
- **Storage**: Local CSV database + GitHub Pages
- **Delivery**: Email + Web dashboard

### **Portfolio Data Sources** 
- **Portfolio**: `actual-portfolio-master.csv`
- **Market Data**: yfinance API (when optimization rebuilt)
- **Fundamental Data**: To be integrated in redesign

---

## 🛡️ **SYSTEM PROTECTION RULES**

### **🚨 CRITICAL - SENTIMENT ANALYSIS PROTECTION**

**ANY FUTURE DEVELOPMENT MUST:**
1. ✅ **NEVER modify** sentiment analysis scripts
2. ✅ **NEVER change** `master_runner_short.py` automation
3. ✅ **NEVER alter** dashboard generation for sentiment
4. ✅ **NEVER touch** the daily LaunchAgent workflow
5. ✅ **ALWAYS preserve** `index.html` redirect to sentiment dashboard

**IF PORTFOLIO OPTIMIZATION IS ADDED:**
1. ✅ Create **separate scripts** with clear naming
2. ✅ Use **separate dashboard files** (not index.html)
3. ✅ Implement **independent data flows**
4. ✅ Never interfere with existing automation
5. ✅ Maintain sentiment analysis as the primary system

---

## 📝 **CHANGELOG - CLEANUP (July 28, 2025)**

### **✅ COMPLETED CLEANUP**
- Removed 27+ temporary files (`temp_*`)
- Deleted failed HTML dashboard attempts
- Cleaned debug scripts and utilities
- Removed incomplete optimization logic
- Cleared Python cache directories
- Protected sentiment analysis as production system

### **✅ PRESERVED WORKING COMPONENTS**
- Complete sentiment analysis pipeline
- Daily automation system
- Email integration
- GitHub Pages deployment
- Historical sentiment data
- Documentation and configuration

### **❌ REMOVED FOR REDESIGN**
- Portfolio optimization scripts
- Two-phase optimizer
- Supervisor execution system
- Mathematical validation scripts
- Failed dashboard integration attempts

---

## 🎯 **NEXT STEPS (When Ready)**

### **For Portfolio Optimization Redesign:**
1. **Study working sentiment system** - understand data flows
2. **Design clean architecture** - separate from sentiment analysis  
3. **Implement mathematical foundations** - proper Markowitz optimization
4. **Build validation systems** - real money deployment standards
5. **Create independent dashboard** - do not modify sentiment dashboard
6. **Test extensively** - with small amounts before full deployment

### **Success Criteria:**
- ✅ Sentiment analysis remains untouched and operational
- ✅ Portfolio optimization works independently
- ✅ Mathematical accuracy verified
- ✅ User interface meets requirements
- ✅ Real money deployment ready

---

## 📞 **SUPPORT & MONITORING**

### **Live Dashboard**: https://theemeraldnetwork.github.io/tigro/
### **Monitoring Tools**:
- `automation/realtime_monitor.py`
- `automation/countdown_monitor.py`
- `logs/tigro_master_detailed.log`

### **Status Check**:
```bash
# Check sentiment system status
python -c "import pandas as pd; print('✅ Sentiment System:', 'OPERATIONAL' if pd.read_csv('database/sentiment/summary/sentiment_summary_latest.csv') is not None else '❌ ERROR')"
```

---

**🔒 REMEMBER: The sentiment analysis is a working production system generating real value. Protect it while building the portfolio optimization separately.** 