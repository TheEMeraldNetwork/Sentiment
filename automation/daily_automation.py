#!/usr/bin/env python3
"""
Daily Automation Script for Tigro Sentiment Analysis Pipeline
Runs daily at specified time with comprehensive error handling and logging.

This script:
1. Activates the Python virtual environment
2. Runs sentiment analysis
3. Generates dashboard
4. Pushes to GitHub
5. Sends email report
6. Handles all errors gracefully with retries
"""

import os
import sys
import subprocess
import logging
import time
import json
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil

# Project configuration
PROJECT_ROOT = Path(__file__).parent
VENV_PATH = PROJECT_ROOT / "venv"
LOGS_DIR = PROJECT_ROOT / "logs"
RESULTS_DIR = PROJECT_ROOT / "results"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Setup comprehensive logging for daily automation"""
    log_file = LOGS_DIR / f"daily_automation_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('tigro_daily')
    logger.info("="*60)
    logger.info("🐅 TIGRO DAILY AUTOMATION STARTED")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Project Root: {PROJECT_ROOT}")
    logger.info(f"🐍 Python Virtual Environment: {VENV_PATH}")
    logger.info("="*60)
    
    return logger

def get_python_executable():
    """Get the correct Python executable from virtual environment"""
    if sys.platform == "win32":
        python_exec = VENV_PATH / "Scripts" / "python.exe"
    else:
        python_exec = VENV_PATH / "bin" / "python"
    
    if not python_exec.exists():
        raise FileNotFoundError(f"Python executable not found at {python_exec}")
    
    return str(python_exec)

def run_with_retry(command, max_retries=3, delay=5, logger=None):
    """Run a command with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Command completed successfully")
                if result.stdout:
                    logger.info(f"📤 Output: {result.stdout[:500]}...")
                return True
            else:
                logger.error(f"❌ Command failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"🔥 Error: {result.stderr}")
                
                if attempt < max_retries - 1:
                    logger.info(f"⏰ Retrying in {delay} seconds...")
                    time.sleep(delay)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Command timed out after 20 minutes")
            if attempt < max_retries - 1:
                logger.info(f"⏰ Retrying in {delay} seconds...")
                time.sleep(delay)
        except Exception as e:
            logger.error(f"💥 Unexpected error: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"⏰ Retrying in {delay} seconds...")
                time.sleep(delay)
    
    return False

def check_prerequisites(logger):
    """Check all prerequisites are met"""
    logger.info("🔍 Checking prerequisites...")
    
    # Check Python virtual environment
    python_exec = get_python_executable()
    logger.info(f"🐍 Python executable: {python_exec}")
    
    # Check API keys
    api_keys_file = PROJECT_ROOT / "utils" / "config" / "api_keys.json"
    if not api_keys_file.exists():
        logger.error(f"❌ API keys file not found: {api_keys_file}")
        return False
    
    # Check email configuration
    email_config_file = PROJECT_ROOT / "utils" / "config" / "email_config.json"
    if not email_config_file.exists():
        logger.error(f"❌ Email config file not found: {email_config_file}")
        return False
    
    # Check master ticker file
    ticker_file = PROJECT_ROOT / "master name ticker.csv"
    if not ticker_file.exists():
        logger.error(f"❌ Master ticker file not found: {ticker_file}")
        return False
    
    logger.info("✅ All prerequisites checked successfully")
    return True

def run_sentiment_analysis(logger):
    """Run sentiment analysis with retry logic"""
    logger.info("📊 Starting sentiment analysis...")
    
    python_exec = get_python_executable()
    command = [python_exec, "scripts/a_collect_sentiment.py"]
    
    success = run_with_retry(command, max_retries=3, delay=10, logger=logger)
    
    if success:
        logger.info("✅ Sentiment analysis completed successfully")
        return True
    else:
        logger.error("❌ Sentiment analysis failed after all retries")
        return False

def generate_dashboard(logger):
    """Generate dashboard with retry logic"""
    logger.info("📈 Generating dashboard...")
    
    python_exec = get_python_executable()
    command = [python_exec, "scripts/e_generate_dashboard.py"]
    
    success = run_with_retry(command, max_retries=3, delay=10, logger=logger)
    
    if success:
        logger.info("✅ Dashboard generation completed successfully")
        return True
    else:
        logger.error("❌ Dashboard generation failed after all retries")
        return False

def copy_to_docs(logger):
    """Copy results to docs directory for GitHub Pages"""
    logger.info("📋 Copying results to docs directory...")
    
    try:
        docs_dir = PROJECT_ROOT / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Copy main dashboard
        main_dashboard = RESULTS_DIR / "sentiment_report_latest.html"
        if main_dashboard.exists():
            shutil.copy2(main_dashboard, docs_dir / "index.html")
            logger.info("✅ Main dashboard copied to docs/index.html")
        
        # Copy individual stock articles
        for article_file in RESULTS_DIR.glob("articles_*_latest.html"):
            shutil.copy2(article_file, docs_dir / article_file.name)
        
        logger.info("✅ All files copied to docs directory")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error copying files to docs: {str(e)}")
        return False

def push_to_github(logger):
    """Push changes to GitHub with retry logic"""
    logger.info("🚀 Pushing changes to GitHub...")
    
    try:
        # Add all changes
        git_add = ["git", "add", "-A"]
        if not run_with_retry(git_add, max_retries=2, delay=5, logger=logger):
            logger.error("❌ Git add failed")
            return False
        
        # Commit changes
        commit_message = f"Daily Tigro update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        git_commit = ["git", "commit", "-m", commit_message]
        if not run_with_retry(git_commit, max_retries=2, delay=5, logger=logger):
            logger.warning("⚠️ Git commit failed (might be no changes)")
        
        # Push to GitHub
        git_push = ["git", "push", "origin", "main"]
        if not run_with_retry(git_push, max_retries=3, delay=10, logger=logger):
            logger.error("❌ Git push failed")
            return False
        
        logger.info("✅ Successfully pushed to GitHub")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error pushing to GitHub: {str(e)}")
        return False

def send_email_report(logger):
    """Send email report with enhanced error handling"""
    logger.info("📧 Sending email report...")
    
    try:
        # Import email modules
        sys.path.append(str(PROJECT_ROOT))
        from utils.email.report_sender import SentimentEmailSender
        import pandas as pd
        
        # Load latest sentiment summary
        latest_file = RESULTS_DIR / "sentiment_summary_latest.csv"
        if not latest_file.exists():
            # Find most recent dated file
            summary_files = list(RESULTS_DIR.glob("sentiment_summary_*.csv"))
            if not summary_files:
                logger.error("❌ No sentiment summary files found")
                return False
            
            latest_file = max(summary_files, key=lambda f: f.stat().st_mtime)
        
        summary_df = pd.read_csv(latest_file)
        logger.info(f"📊 Loaded sentiment data for {len(summary_df)} stocks")
        
        # Send email
        sender = SentimentEmailSender()
        success = sender.send_email(summary_df, test_mode=False)
        
        if success:
            logger.info("✅ Email report sent successfully")
            return True
        else:
            logger.error("❌ Email sending failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error sending email report: {str(e)}")
        return False

def send_error_notification(logger, error_message):
    """Send error notification email"""
    logger.info("🚨 Sending error notification...")
    
    try:
        # Load email config
        email_config_file = PROJECT_ROOT / "utils" / "config" / "email_config.json"
        with open(email_config_file) as f:
            config = json.load(f)
        
        # Create error email
        msg = MIMEMultipart()
        msg['From'] = f"Tigro Error Alert <{config['email_address']}>"
        msg['To'] = config['recipient_email']
        msg['Subject'] = f"🚨 Tigro Daily Automation Failed - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
        <html>
        <body>
        <h2>🚨 Tigro Daily Automation Failed</h2>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Error:</strong> {error_message}</p>
        <p><strong>Log File:</strong> Check logs/daily_automation_{datetime.now().strftime('%Y%m%d')}.log</p>
        <p><strong>Next Steps:</strong> Check system and try running manually with: python master_runner_short.py</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_address'], config['app_password'])
        server.send_message(msg)
        server.quit()
        
        logger.info("✅ Error notification sent")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send error notification: {str(e)}")
        return False

def cleanup_old_logs(logger):
    """Clean up old log files (keep last 30 days)"""
    logger.info("🧹 Cleaning up old log files...")
    
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for log_file in LOGS_DIR.glob("daily_automation_*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                logger.info(f"🗑️ Deleted old log file: {log_file.name}")
        
        logger.info("✅ Log cleanup completed")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error cleaning up logs: {str(e)}")
        return False

def main():
    """Main daily automation function"""
    logger = setup_logging()
    
    start_time = datetime.now()
    success = True
    error_message = ""
    
    try:
        # Check prerequisites
        if not check_prerequisites(logger):
            raise Exception("Prerequisites check failed")
        
        # Run sentiment analysis
        if not run_sentiment_analysis(logger):
            raise Exception("Sentiment analysis failed")
        
        # Generate dashboard
        if not generate_dashboard(logger):
            raise Exception("Dashboard generation failed")
        
        # Copy to docs
        if not copy_to_docs(logger):
            raise Exception("Copying to docs failed")
        
        # Push to GitHub
        if not push_to_github(logger):
            raise Exception("GitHub push failed")
        
        # Send email report
        if not send_email_report(logger):
            raise Exception("Email report failed")
        
        # Cleanup old logs
        cleanup_old_logs(logger)
        
        # Success summary
        duration = datetime.now() - start_time
        logger.info("="*60)
        logger.info("🎉 DAILY AUTOMATION COMPLETED SUCCESSFULLY")
        logger.info(f"⏱️  Total Duration: {duration}")
        logger.info(f"📊 Dashboard: https://theemeraldnetwork.github.io/tigro/")
        logger.info(f"📧 Email Report: Sent to {logger.info('configured recipient')}")
        logger.info("="*60)
        
    except Exception as e:
        success = False
        error_message = str(e)
        duration = datetime.now() - start_time
        
        logger.error("="*60)
        logger.error("💥 DAILY AUTOMATION FAILED")
        logger.error(f"⏱️  Duration Before Failure: {duration}")
        logger.error(f"🚨 Error: {error_message}")
        logger.error("="*60)
        
        # Send error notification
        send_error_notification(logger, error_message)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 