#!/bin/bash

# Tigro Daily Automation Wrapper for LaunchD
# This script handles the spaces in the file path that LaunchD can't handle

# Set working directory (with proper escaping)
cd "/Users/davideconsiglio/Library/Mobile Documents/com~apple~CloudDocs/portfolio_tracker/sentiment_analysis"

# Set environment variables
export PATH="/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="/Users/davideconsiglio/Library/Mobile Documents/com~apple~CloudDocs/portfolio_tracker/sentiment_analysis:."

# Log the start
echo "$(date): Starting Tigro automation from LaunchD wrapper" >> logs/tigro_daily.log

# Activate virtual environment and run automation
source venv/bin/activate
PYTHONPATH=. python master_runner_short.py >> logs/tigro_daily.log 2>> logs/tigro_daily_error.log

# Log the completion
echo "$(date): Tigro automation completed with exit code $?" >> logs/tigro_daily.log 