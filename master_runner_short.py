#!/usr/bin/env python3

"""
Simplified master runner script that:
1. Collects sentiment data
2. Generates and opens the dashboard
3. Pushes changes to GitHub
"""

import os
import sys
import subprocess
from datetime import datetime
import logging
from pathlib import Path
import shutil

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_script(script_path: str, logger: logging.Logger) -> bool:
    """Run a Python script and return success status"""
    try:
        logger.info(f"Running {script_path}...")
        subprocess.run([sys.executable, script_path], check=True)
        logger.info(f"Successfully completed {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_path}: {e}")
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
    """Main execution function"""
    logger = setup_logging()
    logger.info("Starting simplified analysis pipeline...")
    
    # Get the project root directory
    root_dir = Path(__file__).parent
    
    # Define script paths
    scripts = [
        root_dir / 'scripts' / 'a_collect_sentiment.py',
        root_dir / 'scripts' / 'e_generate_dashboard.py'
    ]
    
    # Run each script
    success = True
    for script in scripts:
        if not run_script(script, logger):
            success = False
            break
    
    # Copy files to docs and push to GitHub if all scripts succeeded
    if success:
        if copy_to_docs(logger):
            if push_to_github(logger):
                # Send email report after successful GitHub push
                send_email_report(logger)
    
    logger.info("Pipeline execution completed!")

if __name__ == "__main__":
    main() 