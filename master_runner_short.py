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
        
        # Copy latest sentiment report
        latest_report = results_dir / "sentiment_report_latest.html"
        if latest_report.exists():
            shutil.copy2(latest_report, docs_dir / "sentiment_report_latest.html")
            
        # Copy all article HTML files
        for article_file in results_dir.glob("articles_*_latest.html"):
            shutil.copy2(article_file, docs_dir / article_file.name)
            
        logger.info("Successfully copied latest files to docs directory")
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
            push_to_github(logger)
    
    logger.info("Pipeline execution completed!")

if __name__ == "__main__":
    main() 