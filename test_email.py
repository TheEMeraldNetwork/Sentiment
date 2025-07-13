#!/usr/bin/env python3

"""
Test script to verify email configuration works
"""

import sys
import os
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent / 'utils'))

try:
    from utils.email.report_sender import SentimentEmailSender
    import pandas as pd
    from pathlib import Path
    
    print("✅ Email module imported successfully")
    
    # Create test data
    test_data = {
        'ticker': ['TSLA', 'META', 'AAPL', 'GOOGL', 'MSFT'],
        'company': ['Tesla Inc.', 'Meta Platforms', 'Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.'],
        'average_sentiment': [-0.15, -0.08, 0.05, 0.12, 0.03],
        'total_articles': [45, 32, 67, 23, 41]
    }
    
    test_df = pd.DataFrame(test_data)
    
    print("🧪 Sending REAL test email...")
    sender = SentimentEmailSender()
    success = sender.send_email(test_df, test_mode=False)  # Real email delivery
    
    if success:
        print("🎉 Email test successful! Check your inbox.")
    else:
        print("❌ Email test failed. Check your credentials.")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the email module exists")
except Exception as e:
    print(f"❌ Test failed: {e}") 