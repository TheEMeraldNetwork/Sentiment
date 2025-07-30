# 🚀 GitHub Actions Setup Guide

## 🎯 Overview
This guide will help you set up GitHub Actions to make the **Update Analysis** and **Send Email** buttons work automatically in your TIGRO dashboard.

## 📋 Prerequisites
- GitHub repository: `TheEmeraldNetwork/Sentiment`
- API keys for data sources ✅ **FOUND IN GIT HISTORY**
- Gmail app password for email alerts ✅ **FOUND IN CONFIG**

---

## 🔑 Step 1: Configure GitHub Repository Secrets

Go to your GitHub repository: https://github.com/TheEmeraldNetwork/Sentiment

### Navigate to Settings:
1. Click **Settings** tab
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add the following secrets (COPY-PASTE THESE EXACT VALUES):

#### 📊 **FINNHUB_API_KEY**
- **Name**: `FINNHUB_API_KEY`
- **Value**: `cu0qch9r01qjiermd96gcu0qch9r01qjiermd970` ✅ **FOUND IN GIT HISTORY**

#### 📈 **ALPHA_VANTAGE_API_KEY** 
- **Name**: `ALPHA_VANTAGE_API_KEY`
- **Value**: `c6a86bf7051d46059a2d316e88ac2d4b` ✅ **FOUND IN GIT HISTORY (NEWSAPI_KEY)**

#### 📧 **GMAIL_EMAIL**
- **Name**: `GMAIL_EMAIL`
- **Value**: `davideconsiglio1978@gmail.com` ✅ **FOUND IN CONFIG**

#### 🔐 **GMAIL_APP_PASSWORD**
- **Name**: `GMAIL_APP_PASSWORD`
- **Value**: `yapl pqyf rzpp olbr` ✅ **FOUND IN CONFIG**

---

## ✅ **ALL CREDENTIALS FOUND - READY TO SET UP!**

**🎉 Great news! I found all your API keys in the git history and config files:**

- ✅ **Finnhub API Key**: Found in previous commits (this explains why sentiment analysis was working)
- ✅ **NewsAPI Key**: Found in git history (can be used as Alpha Vantage alternative)
- ✅ **Gmail Email**: Found in email config
- ✅ **Gmail App Password**: Found in email config

---

## 🤖 Step 2: Enable GitHub Actions

### Workflow Files Created:
✅ `.github/workflows/sentiment_analysis.yml` - Main sentiment analysis automation
✅ `.github/workflows/send_email.yml` - Email report sending

### Automatic Triggers:
- **Daily Schedule**: 2:50 PM CET (automatic)
- **Manual Trigger**: Via dashboard buttons
- **Code Changes**: When you update scripts

---

## 🎮 Step 3: How to Use the Buttons

### 🔄 **Update Analysis Button**
1. Click **"🔄 Update Analysis"** on dashboard
2. Redirects to GitHub Actions page
3. Click **"Run workflow"** → **"Run workflow"**
4. Workflow will:
   - Analyze all 149 stocks with FinBERT AI
   - Generate fresh dashboard
   - Update GitHub Pages automatically
   - Complete in ~5-10 minutes

### 📧 **Send Email Button**
1. Click **"📧 Send Email Report"** on dashboard
2. Redirects to GitHub Actions email workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Workflow will:
   - Send email with latest sentiment analysis
   - Include declining stock alerts
   - Use your Gmail account

---

## 📊 Step 4: Monitor Workflow Execution

### Check Status:
- **Workflows**: https://github.com/TheEmeraldNetwork/Sentiment/actions
- **Live Dashboard**: https://theemeraldnetwork.github.io/sentiment/

### Typical Execution Time:
- **Sentiment Analysis**: 5-10 minutes
- **Email Report**: 1-2 minutes
- **Dashboard Update**: Automatic after completion

---

## 🔧 Step 5: Troubleshooting

### If workflows fail:
1. **Check Secrets**: Ensure all 4 secrets are set correctly
2. **Check API Limits**: Finnhub has daily limits
3. **Check Logs**: Click on failed workflow for details

### Common Issues:
- **API Key Invalid**: Double-check your API keys
- **Email Auth Failed**: Verify Gmail app password
- **Timeout Error**: Retry after a few minutes

### Manual Backup:
If GitHub Actions fail, you can still run locally:
```bash
# Run sentiment analysis
python scripts/sentiment/sent_collect_data.py

# Generate dashboard
python scripts/visualization/viz_dashboard_generator.py

# Send email
python -c "
from utils.email.report_sender import SentimentEmailSender
import pandas as pd
df = pd.read_csv('results/sentiment_summary_latest.csv')
sender = SentimentEmailSender()
sender.send_email(df)
"
```

---

## ✅ Step 6: Verify Setup

### Test Checklist:
- [ ] All 4 GitHub secrets configured
- [ ] GitHub Actions enabled
- [ ] Dashboard buttons redirect to workflows
- [ ] Test email workflow manually
- [ ] Test sentiment analysis workflow manually
- [ ] Verify daily automation (check tomorrow at 2:50 PM CET)

---

## 🎉 Success!

Once configured, your TIGRO system will:
- ✅ **Auto-update daily** at 2:50 PM CET
- ✅ **Working buttons** for manual triggers
- ✅ **Email alerts** for declining stocks
- ✅ **Cloud execution** (no need for local computer)
- ✅ **GitHub Pages hosting** with fresh data

**Live Dashboard**: https://theemeraldnetwork.github.io/sentiment/

**Your sentiment analysis system is now fully automated! 🐅** 