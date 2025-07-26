#!/usr/bin/env python3

"""
Simplified master runner script that:
1. Collects sentiment data
2. Generates and opens the dashboard
3. Pushes changes to GitHub
4. Sends email report with declining stocks
"""

import os
import sys
import subprocess
from datetime import datetime
import logging
from pathlib import Path
import shutil

def setup_logging():
    """Setup comprehensive logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging with detailed format
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / 'tigro_master_detailed.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_command_with_logging(command: list, description: str, logger: logging.Logger, max_retries: int = 3) -> bool:
    """Run a command with detailed logging and retry logic"""
    # Set up environment with PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())  # Add current directory to PYTHONPATH
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Attempt {attempt}/{max_retries}: {' '.join(command)}")
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd(),
                env=env  # Pass environment with PYTHONPATH
            )
            logger.info(f"✅ Command completed successfully")
            if result.stdout.strip():
                logger.info(f"📤 Output: {result.stdout.strip()}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Attempt {attempt} failed: {e}")
            if e.stdout:
                logger.error(f"📤 STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"📤 STDERR: {e.stderr}")
            
            if attempt == max_retries:
                logger.error(f"🚨 All {max_retries} attempts failed for: {description}")
                return False
            else:
                logger.info(f"🔄 Retrying in 5 seconds...")
                import time
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"🚨 Unexpected error in {description}: {e}")
            return False
    
    return False

def copy_to_docs(logger: logging.Logger) -> bool:
    """Copy latest results to docs directory for GitHub Pages"""
    try:
        docs_dir = Path('docs')
        results_dir = Path('results')
        
        # Ensure docs directory exists
        docs_dir.mkdir(exist_ok=True)
        
        # Copy latest sentiment report as both index.html and sentiment_report_latest.html
        latest_report = results_dir / "sentiment_report_latest.html"
        if latest_report.exists():
            # Copy as index.html for GitHub Pages root
            shutil.copy2(latest_report, docs_dir / "index.html")
            # Also keep as sentiment_report_latest.html for direct links
            shutil.copy2(latest_report, docs_dir / "sentiment_report_latest.html")
            logger.info("✅ Copied main dashboard as index.html and sentiment_report_latest.html")
        else:
            logger.warning("⚠️ No sentiment report found to copy")
            
        # Copy all article HTML files
        article_count = 0
        for article_file in results_dir.glob("articles_*_latest.html"):
            shutil.copy2(article_file, docs_dir / article_file.name)
            article_count += 1
            
        logger.info(f"✅ Copied {article_count} individual stock article pages")
        logger.info(f"📊 Tigro dashboard will be available at: https://theemeraldnetwork.github.io/tigro/")
        
        return True
    except Exception as e:
        logger.error(f"Error copying files to docs: {e}")
        return False

def push_to_github(logger: logging.Logger) -> bool:
    """Push changes to GitHub"""
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Git commands
        commands = [
            ['git', 'add', 'results/*'],
            ['git', 'add', 'docs/*'],
            ['git', 'commit', '-m', f'Update sentiment analysis and dashboard - {timestamp}'],
            ['git', 'push']
        ]
        
        for cmd in commands:
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
        logger.info("Successfully pushed changes to GitHub")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error pushing to GitHub: {e}")
        return False

def send_email_report(logger: logging.Logger) -> bool:
    """Send email report with sentiment analysis"""
    try:
        logger.info("Sending email report...")
        from utils.email.report_sender import SentimentEmailSender
        import pandas as pd
        
        # Load latest sentiment summary
        results_dir = Path('results')
        
        # Try to use the latest symlink first, then fall back to dated files
        latest_symlink = results_dir / 'sentiment_summary_latest.csv'
        if latest_symlink.exists():
            summary_df = pd.read_csv(latest_symlink)
        else:
            # Find dated files (not symlinks with spaces)
            summary_files = [f for f in results_dir.glob('sentiment_summary_*.csv') 
                           if f.name.count('_') == 2 and 'latest' not in f.name]
            
            if not summary_files:
                logger.warning("No sentiment summary files found")
                return False
                
            latest_file = max(summary_files, key=lambda f: f.stat().st_mtime)
            summary_df = pd.read_csv(latest_file)
        
        # Initialize email sender
        sender = SentimentEmailSender()
        
        # Send the email (test_mode=False for real emails)
        sender.send_email(summary_df, test_mode=False)
        logger.info("✅ Email report sent successfully")
        return True
    except Exception as e:
        logger.error(f"Error sending email report: {e}")
        return False

def main():
    """Main execution function with comprehensive logging"""
    start_time = datetime.now()
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("🐅 TIGRO DAILY AUTOMATION STARTED")
    logger.info(f"📅 Date: {start_time}")
    logger.info(f"📁 Project Root: {os.getcwd()}")
    logger.info(f"🐍 Python Executable: {sys.executable}")
    logger.info(f"🐍 Python Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'Not activated')}")
    logger.info("=" * 60)
    
    # Check prerequisites
    logger.info("🔍 Checking prerequisites...")
    # Use virtual environment's Python if available
    venv_python = Path('venv/bin/python')
    if venv_python.exists():
        python_path = str(venv_python.absolute())
    else:
        python_path = sys.executable
    logger.info(f"🐍 Python executable: {python_path}")
    
    if not Path('scripts/a_collect_sentiment.py').exists():
        logger.error("🚨 Missing sentiment script!")
        return False
        
    if not Path('scripts/e_generate_dashboard.py').exists():
        logger.error("🚨 Missing dashboard script!")
        return False
        
    logger.info("✅ All prerequisites checked successfully")
    
    # Step 1: Sentiment Analysis
    logger.info("📊 Starting sentiment analysis...")
    if not run_command_with_logging(
        [python_path, 'scripts/a_collect_sentiment.py'],
        "sentiment analysis",
        logger
    ):
        logger.error("🚨 Sentiment analysis failed!")
        return False
    logger.info("✅ Sentiment analysis completed successfully")
    
    # Step 2: Dashboard Generation
    logger.info("📈 Generating dashboard...")
    if not run_command_with_logging(
        [python_path, 'scripts/e_generate_dashboard.py'],
        "dashboard generation",
        logger
    ):
        logger.error("🚨 Dashboard generation failed!")
        return False
    logger.info("✅ Dashboard generation completed successfully")
    
    # Step 3: Copy to docs
    logger.info("📋 Copying results to docs directory...")
    if copy_to_docs(logger):
        logger.info("✅ All files copied to docs directory")
    else:
        logger.warning("⚠️ Some files may not have been copied to docs")
    
    # Step 4: Git operations
    logger.info("🚀 Pushing changes to GitHub...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Git add
    if not run_command_with_logging(['git', 'add', '-A'], "git add", logger, max_retries=2):
        logger.error("🚨 Git add failed!")
        return False
    
    # Git commit
    if not run_command_with_logging(
        ['git', 'commit', '-m', f'Daily Tigro update - {timestamp}'],
        "git commit",
        logger,
        max_retries=2
    ):
        logger.warning("⚠️ Git commit failed - possibly no changes")
    
    # Git push
    if not run_command_with_logging(['git', 'push', 'origin', 'main'], "git push", logger, max_retries=3):
        logger.error("🚨 Git push failed!")
        return False
    
    logger.info("✅ Successfully pushed to GitHub")
    
    # Step 5: Email Report
    logger.info("📧 Sending email report...")
    try:
        from utils.email.report_sender import SentimentEmailSender
        import pandas as pd
        
        # Load latest sentiment data
        sentiment_file = Path('results/sentiment_summary_latest.csv')
        if sentiment_file.exists():
            df = pd.read_csv(sentiment_file)
            logger.info(f"📊 Loaded sentiment data for {len(df)} stocks")
            
            email_sender = SentimentEmailSender()
            success = email_sender.send_email(df, test_mode=False)
            
            if success:
                logger.info("✅ Email report sent successfully")
            else:
                logger.error("🚨 Email report failed to send")
        else:
            logger.error("🚨 No sentiment data file found for email")
            
    except Exception as e:
        logger.error(f"🚨 Email error: {e}")
        import traceback
        logger.error(f"🚨 Email traceback: {traceback.format_exc()}")
    
    # Step 6: Cleanup
    logger.info("🧹 Cleaning up old log files...")
    cleanup_old_logs(logger)
    logger.info("✅ Log cleanup completed")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("🎉 DAILY AUTOMATION COMPLETED SUCCESSFULLY")
    logger.info(f"⏱️  Total Duration: {duration}")
    logger.info(f"📊 Dashboard: https://theemeraldnetwork.github.io/tigro/")
    logger.info(f"📧 Email Report: Sent to configured recipient")
    logger.info("=" * 60)
    
    return True

def cleanup_old_logs(logger: logging.Logger):
    """Clean up old log files to prevent disk space issues"""
    try:
        logs_dir = Path('logs')
        if not logs_dir.exists():
            return
            
        # Keep only last 30 days of logs
        import time
        current_time = time.time()
        thirty_days_ago = current_time - (30 * 24 * 60 * 60)
        
        for log_file in logs_dir.glob('*.log'):
            if log_file.stat().st_mtime < thirty_days_ago:
                log_file.unlink()
                logger.info(f"🗑️ Deleted old log: {log_file.name}")
                
    except Exception as e:
        logger.warning(f"⚠️ Log cleanup warning: {e}")

if __name__ == "__main__":
    main() 