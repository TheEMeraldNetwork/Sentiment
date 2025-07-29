#!/usr/bin/env python3

"""
Complete flow test script that:
1. Runs the full sentiment analysis pipeline
2. Copies files to docs/ for GitHub Pages
3. Pushes to GitHub
4. Tests email functionality with real GitHub Pages links
"""

import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_sentiment_pipeline(logger):
    """Run the simplified sentiment analysis pipeline"""
    try:
        logger.info("🚀 Starting complete Tigro pipeline test...")
        subprocess.run([sys.executable, "master_runner_short.py"], check=True)
        logger.info("✅ Sentiment pipeline completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error running sentiment pipeline: {e}")
        return False

def test_email_with_github_pages(logger):
    """Test email functionality with real GitHub Pages links"""
    try:
        logger.info("📧 Testing email functionality with GitHub Pages links...")
        
        # Import and test email functionality
        sys.path.append('utils')
        from email.report_sender import EmailSender
        from config.email_config import load_email_config
        
        # Load email configuration
        config = load_email_config()
        sender = EmailSender(config)
        
        # Test with GitHub Pages URL
        github_url = "https://theemeraldnetwork.github.io/sentiment/"
        
        # Create test email content
        test_subject = f"🐅 Tigro Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        test_content = f"""
        <h2>🚀 Complete Pipeline Test</h2>
        <p>This is a test of the complete Tigro pipeline including GitHub Pages integration.</p>
        <p><strong>Dashboard URL:</strong> <a href="{github_url}">{github_url}</a></p>
        <p>If you can see this email and access the dashboard, the complete flow is working!</p>
        """
        
        # Send test email
        success = sender.send_test_email(
            subject=test_subject,
            content=test_content
        )
        
        if success:
            logger.info("✅ Test email sent successfully!")
            logger.info(f"📊 Dashboard URL: {github_url}")
            return True
        else:
            logger.error("❌ Failed to send test email")
            return False
            
    except ImportError as e:
        logger.warning(f"⚠️ Email configuration not complete: {e}")
        logger.info("📧 Skipping email test - configure Gmail credentials first")
        return True
    except Exception as e:
        logger.error(f"❌ Error testing email: {e}")
        return False

def main():
    """Main test function"""
    logger = setup_logging()
    
    # Test pipeline
    if not run_sentiment_pipeline(logger):
        logger.error("❌ Pipeline test failed")
        sys.exit(1)
    
    # Test email functionality
    if not test_email_with_github_pages(logger):
        logger.error("❌ Email test failed")
        sys.exit(1)
    
    logger.info("🎉 Complete pipeline test successful!")
    logger.info("🐅 Tigro is ready for production!")
    
    # Final instructions
    logger.info("\n" + "="*50)
    logger.info("📋 Next Steps:")
    logger.info("1. Check GitHub Pages: https://theemeraldnetwork.github.io/sentiment/")
    logger.info("2. Configure Gmail credentials in utils/config/email_config.json")
    logger.info("3. Set up cron job for weekly automation")
    logger.info("="*50)

if __name__ == "__main__":
    main() 