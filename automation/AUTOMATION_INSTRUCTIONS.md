# 🤖 Tigro Daily Automation Setup

## ✅ **AUTOMATION ACTIVE**

Your Tigro sentiment analysis system is now configured to run automatically every day at **7:30 PM** and send you an email with the 5 declining stocks.

## 📋 **What Happens Daily:**

1. **🔍 Data Collection**: Gathers news sentiment for all 96 stocks
2. **🧠 AI Analysis**: Processes with FinBERT model for sentiment scoring  
3. **📊 Dashboard Update**: Updates live dashboard at https://theemeraldnetwork.github.io/tigro/
4. **📧 Email Report**: Sends you declining stocks alert + full report
5. **🗄️ Data Archive**: Saves historical data for trend analysis

## ⏰ **Current Schedule:**
- **Daily Run Time**: 7:30 PM (19:30)
- **Estimated Duration**: 5-8 minutes
- **Email Delivery**: Within 2-3 minutes after completion

## 📧 **Email Content:**
- **Subject**: "Daily Tigro Sentiment Report - [Date]"
- **Top 5 Declining Stocks**: With sentiment changes and article counts
- **Summary Statistics**: Market overview and trend analysis
- **Dashboard Link**: Direct access to live charts

## 🔧 **Control Commands:**

### **Check Status:**
```bash
launchctl list | grep tigro
```

### **Stop Automation:**
```bash
launchctl unload ~/Library/LaunchAgents/com.tigro.daily.plist
```

### **Start Automation:**
```bash
launchctl load ~/Library/LaunchAgents/com.tigro.daily.plist
```

### **Run Manual Test:**
```bash
bash config/run_tigro_automation.sh
```

## ⏰ **Change Timing:**

To change the daily run time, edit `config/com.tigro.daily.plist`:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>19</integer>     <!-- Change this (0-23) -->
    <key>Minute</key>
    <integer>30</integer>     <!-- Change this (0-59) -->
</dict>
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.tigro.daily.plist
cp config/com.tigro.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.tigro.daily.plist
```

## 📊 **Popular Times:**
- **9:00 AM** (09:00): Morning market prep
- **6:00 PM** (18:00): After market close  
- **7:30 PM** (19:30): Current setting ✅
- **8:00 PM** (20:00): Evening review

## 📝 **Logs & Monitoring:**
- **Main Log**: `logs/tigro_daily.log`
- **Error Log**: `logs/tigro_daily_error.log`
- **Dashboard**: https://theemeraldnetwork.github.io/tigro/
- **Email Status**: Check your inbox daily at 7:35 PM

## 🚨 **Troubleshooting:**

### **No Email Received:**
1. Check logs: `tail -20 logs/tigro_daily.log`
2. Test email: `python -m utils.email.report_sender`
3. Verify LaunchAgent: `launchctl list | grep tigro`

### **Automation Not Running:**
1. Check if loaded: `launchctl list | grep tigro`
2. Reload LaunchAgent (commands above)
3. Check system permissions

### **Test Manual Run:**
```bash
cd "/Users/davideconsiglio/Library/Mobile Documents/com~apple~CloudDocs/portfolio_tracker/sentiment_analysis"
source venv/bin/activate
PYTHONPATH=. python master_runner_short.py
```

## 📧 **Email Format Preview:**

```
Subject: Daily Tigro Sentiment Report - July 19, 2025

🚨 TOP 5 DECLINING STOCKS:
1. TICKER - Company Name (-15.2% sentiment change)
2. TICKER - Company Name (-12.8% sentiment change)
...

📊 MARKET OVERVIEW:
- Total Stocks: 96
- Stocks with Data: 89
- Trending UP: 23
- Trending DOWN: 15

🔗 Full Dashboard: https://theemeraldnetwork.github.io/tigro/
```

---

**✅ Automation is ACTIVE and will run daily at 7:30 PM!** 