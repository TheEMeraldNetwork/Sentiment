#!/usr/bin/env python3

"""
Test script to verify email automation with 2 stocks: AAPL and TSLA.
This allows testing the full pipeline before running on all 97 stocks.
"""

import os
import sys
import pandas as pd
from pathlib import Path
import logging
import shutil
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def backup_master_tickers():
    """Backup the original master ticker file"""
    original_file = Path('master name ticker.csv')
    backup_file = Path('master name ticker_backup.csv')
    
    if original_file.exists():
        shutil.copy2(original_file, backup_file)
        return True
    return False

def create_test_ticker_file():
    """Create a temporary master ticker file with just AAPL and TSLA"""
    test_data = """Ticker;Name
AAPL;Apple Inc.
TSLA;Tesla Inc."""
    
    with open('master name ticker.csv', 'w') as f:
        f.write(test_data)
    
    print("✅ Created test ticker file with AAPL and TSLA")

def restore_master_tickers():
    """Restore the original master ticker file"""
    original_file = Path('master name ticker.csv')
    backup_file = Path('master name ticker_backup.csv')
    
    if backup_file.exists():
        shutil.move(backup_file, original_file)
        print("✅ Restored original master ticker file")
    else:
        print("⚠️ Backup file not found, original file not restored")

def run_sentiment_analysis():
    """Run sentiment analysis on the test stocks"""
    try:
        print("\n🔄 Running sentiment analysis...")
        from scripts.a_collect_sentiment import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        analyzer.process_all_stocks()
        
        print("✅ Sentiment analysis completed")
        return True
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return False

def run_dashboard_generation():
    """Run dashboard generation"""
    try:
        print("\n🔄 Generating dashboard...")
        from scripts.e_generate_dashboard import DashboardGenerator
        
        generator = DashboardGenerator()
        generator.generate_dashboard()
        
        print("✅ Dashboard generation completed")
        return True
    except Exception as e:
        print(f"❌ Error in dashboard generation: {e}")
        return False

def test_email_sending():
    """Test email functionality with the 2-stock data"""
    try:
        print("\n📧 Testing email functionality...")
        from utils.email.report_sender import SentimentEmailSender
        
        # Load the test sentiment data
        results_dir = Path('results')
        sentiment_file = results_dir / 'sentiment_summary_latest.csv'
        
        if not sentiment_file.exists():
            print("❌ No sentiment data found after analysis")
            return False
        
        df = pd.read_csv(sentiment_file)
        print(f"📊 Loaded sentiment data for {len(df)} stocks")
        
        # Send test email
        sender = SentimentEmailSender()
        success = sender.send_email(df, test_mode=True)
        
        if success:
            print("✅ Email test completed successfully!")
            print("📧 Check results/test_email.html for email preview")
        else:
            print("❌ Email test failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

def display_results():
    """Display the results of the 2-stock test"""
    try:
        print("\n📊 RESULTS SUMMARY:")
        print("=" * 50)
        
        # Load sentiment data
        sentiment_file = Path('results/sentiment_summary_latest.csv')
        if sentiment_file.exists():
            df = pd.read_csv(sentiment_file)
            
            for _, row in df.iterrows():
                ticker = row['ticker']
                company = row['company']
                sentiment = row.get('average_sentiment', 0)
                articles = row.get('total_articles', 0)
                
                sentiment_emoji = "📈" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
                
                print(f"{sentiment_emoji} {ticker} ({company})")
                print(f"   Sentiment: {sentiment:.3f}")
                print(f"   Articles: {articles}")
                print()
        
        # Check for generated files
        results_dir = Path('results')
        files_generated = []
        
        if (results_dir / 'sentiment_report_latest.html').exists():
            files_generated.append('📊 Dashboard report')
        if (results_dir / 'test_email.html').exists():
            files_generated.append('📧 Email preview')
        if (results_dir / 'articles_AAPL_latest.html').exists():
            files_generated.append('🍎 AAPL article page')
        if (results_dir / 'articles_TSLA_latest.html').exists():
            files_generated.append('🚗 TSLA article page')
        
        print("📁 Generated files:")
        for file_desc in files_generated:
            print(f"   ✅ {file_desc}")
            
    except Exception as e:
        print(f"❌ Error displaying results: {e}")

def main():
    """Main test function"""
    logger = setup_logging()
    logger.info("Starting 2-stock email automation test...")
    
    print("🧪 TIGRO EMAIL AUTOMATION TEST")
    print("Testing with AAPL and TSLA")
    print("=" * 50)
    
    try:
        # Step 1: Backup and create test ticker file
        print("\n1️⃣ Setting up test environment...")
        backup_success = backup_master_tickers()
        if backup_success:
            print("✅ Original ticker file backed up")
        create_test_ticker_file()
        
        # Step 2: Run sentiment analysis
        print("\n2️⃣ Running sentiment analysis...")
        sentiment_success = run_sentiment_analysis()
        
        if not sentiment_success:
            print("❌ Sentiment analysis failed, stopping test")
            return
        
        # Step 3: Run dashboard generation
        print("\n3️⃣ Generating dashboard...")
        dashboard_success = run_dashboard_generation()
        
        if not dashboard_success:
            print("❌ Dashboard generation failed, stopping test")
            return
            
        # Step 4: Test email functionality
        print("\n4️⃣ Testing email automation...")
        email_success = test_email_sending()
        
        # Step 5: Display results
        display_results()
        
        # Final summary
        print("\n🎯 TEST SUMMARY:")
        print("=" * 50)
        print(f"✅ Sentiment Analysis: {'PASSED' if sentiment_success else 'FAILED'}")
        print(f"✅ Dashboard Generation: {'PASSED' if dashboard_success else 'FAILED'}")
        print(f"✅ Email Automation: {'PASSED' if email_success else 'FAILED'}")
        
        if all([sentiment_success, dashboard_success, email_success]):
            print("\n🎉 ALL TESTS PASSED!")
            print("Ready for full 97-stock automation!")
        else:
            print("\n⚠️ Some tests failed - check logs above")
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
    
    finally:
        # Step 6: Cleanup - restore original ticker file
        print("\n🧹 Cleaning up...")
        restore_master_tickers()
        print("✅ Test completed!")

if __name__ == "__main__":
    main() 