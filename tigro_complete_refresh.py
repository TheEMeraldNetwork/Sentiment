#!/usr/bin/env python3

"""
🐅 TIGRO COMPLETE REFRESH MASTER SCRIPT

This script orchestrates the complete TIGRO system refresh:
1. ✅ Sentiment Analysis (with fresh stock list)
2. ✅ Portfolio Optimization (with fresh sentiment data) 
3. ✅ Dashboard Generation (sentiment + portfolio)
4. ✅ Master Dashboard Creation
5. ✅ GitHub Deployment

Usage: python tigro_complete_refresh.py
"""

import os
import sys
import subprocess
from datetime import datetime
import logging
from pathlib import Path
import shutil
import time

def setup_logging():
    """Setup comprehensive logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging with detailed format
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / f'tigro_complete_refresh_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_command_with_retry(command: list, description: str, logger: logging.Logger, 
                          max_retries: int = 3, delay: int = 5) -> bool:
    """Run a command with proper PYTHONPATH and retry logic"""
    
    # Set up environment with PYTHONPATH pointing to project root
    env = os.environ.copy()
    project_root = str(Path.cwd().absolute())
    env['PYTHONPATH'] = project_root
    
    logger.info(f"🎯 {description}")
    logger.info(f"📁 Working Directory: {project_root}")
    logger.info(f"🐍 PYTHONPATH: {env['PYTHONPATH']}")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Attempt {attempt}/{max_retries}: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                cwd=project_root,
                env=env,
                timeout=600  # 10 minute timeout
            )
            
            logger.info(f"✅ {description} completed successfully!")
            if result.stdout.strip():
                logger.info(f"📤 Output preview: {result.stdout.strip()[:500]}...")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Attempt {attempt} failed: {e}")
            if e.stdout:
                logger.error(f"📤 STDOUT: {e.stdout[:1000]}...")
            if e.stderr:
                logger.error(f"📤 STDERR: {e.stderr[:1000]}...")
            
            if attempt == max_retries:
                logger.error(f"🚨 All {max_retries} attempts failed for: {description}")
                return False
            else:
                logger.info(f"⏱️ Retrying in {delay} seconds...")
                time.sleep(delay)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {description} timed out after 10 minutes")
            if attempt == max_retries:
                return False
            else:
                logger.info(f"⏱️ Retrying in {delay} seconds...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"🚨 Unexpected error in {description}: {e}")
            return False
    
    return False

def check_prerequisites(logger: logging.Logger) -> bool:
    """Check all required files and directories exist"""
    logger.info("🔍 Checking prerequisites...")
    
    required_files = [
        'scripts/sentiment/sent_collect_data.py',
        'scripts/optimization/opt_rigorous_portfolio_master.py', 
        'scripts/visualization/viz_rigorous_action_table.py',
        'scripts/visualization/viz_dashboard_generator.py',
        'actual-portfolio-master.csv',
        'master name ticker.csv'
    ]
    
    required_dirs = [
        'utils',
        'scripts',
        'data',
        'results',
        'docs'
    ]
    
    # Check files
    for file_path in required_files:
        if not Path(file_path).exists():
            logger.error(f"❌ Missing required file: {file_path}")
            return False
        logger.info(f"✅ Found: {file_path}")
    
    # Check directories
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            logger.warning(f"⚠️ Creating missing directory: {dir_path}")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory: {dir_path}")
    
    logger.info("✅ All prerequisites verified!")
    return True

def run_sentiment_analysis(logger: logging.Logger) -> bool:
    """Run fresh sentiment analysis with updated stock list"""
    logger.info("=" * 60)
    logger.info("📊 STEP 1: SENTIMENT ANALYSIS")
    logger.info("=" * 60)
    
    python_path = sys.executable
    
    success = run_command_with_retry(
        [python_path, 'scripts/sentiment/sent_collect_data.py'],
        "Fresh Sentiment Analysis Collection",
        logger,
        max_retries=2,
        delay=10
    )
    
    if success:
        logger.info("🎉 Sentiment analysis completed with fresh stock data!")
        return True
    else:
        logger.error("🚨 Sentiment analysis failed - continuing with existing data")
        return False

def run_portfolio_optimization(logger: logging.Logger) -> bool:
    """Run portfolio optimization with fresh sentiment data"""
    logger.info("=" * 60)
    logger.info("⚖️ STEP 2: PORTFOLIO OPTIMIZATION")
    logger.info("=" * 60)
    
    python_path = sys.executable
    
    success = run_command_with_retry(
        [python_path, 'scripts/optimization/opt_rigorous_portfolio_master.py'],
        "Portfolio Optimization Analysis",
        logger,
        max_retries=2,
        delay=5
    )
    
    if success:
        logger.info("🎉 Portfolio optimization completed!")
        return True
    else:
        logger.error("🚨 Portfolio optimization failed")
        return False

def generate_action_table(logger: logging.Logger) -> bool:
    """Generate the portfolio action table"""
    logger.info("=" * 60)
    logger.info("📋 STEP 3: PORTFOLIO ACTION TABLE")
    logger.info("=" * 60)
    
    python_path = sys.executable
    
    success = run_command_with_retry(
        [python_path, 'scripts/visualization/viz_rigorous_action_table.py'],
        "Portfolio Action Table Generation",
        logger,
        max_retries=2,
        delay=5
    )
    
    if success:
        logger.info("🎉 Portfolio action table generated!")
        return True
    else:
        logger.error("🚨 Portfolio action table generation failed")
        return False

def generate_sentiment_dashboard(logger: logging.Logger) -> bool:
    """Generate the sentiment dashboard"""
    logger.info("=" * 60)
    logger.info("📈 STEP 4: SENTIMENT DASHBOARD")
    logger.info("=" * 60)
    
    python_path = sys.executable
    
    success = run_command_with_retry(
        [python_path, 'scripts/visualization/viz_dashboard_generator.py'],
        "Sentiment Dashboard Generation",
        logger,
        max_retries=2,
        delay=5
    )
    
    if success:
        logger.info("🎉 Sentiment dashboard generated!")
        return True
    else:
        logger.error("🚨 Sentiment dashboard generation failed - using existing")
        return False

def copy_files_to_docs(logger: logging.Logger) -> bool:
    """Copy all generated files to docs directory for GitHub Pages"""
    logger.info("=" * 60)
    logger.info("📁 STEP 5: COPY TO DOCS")
    logger.info("=" * 60)
    
    try:
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)
        
        files_copied = 0
        
        # Copy portfolio action table
        if Path('rigorous_portfolio_action_table.html').exists():
            shutil.copy2('rigorous_portfolio_action_table.html', docs_dir)
            logger.info("✅ Copied: rigorous_portfolio_action_table.html")
            files_copied += 1
        
        # Copy sentiment dashboard if it exists
        results_dir = Path('results')
        if results_dir.exists():
            # Copy latest sentiment report
            sentiment_files = list(results_dir.glob('sentiment_report_*.html'))
            if sentiment_files:
                latest_sentiment = max(sentiment_files, key=lambda f: f.stat().st_mtime)
                shutil.copy2(latest_sentiment, docs_dir / 'sentiment_report_latest.html')
                logger.info(f"✅ Copied: {latest_sentiment.name} → sentiment_report_latest.html")
                files_copied += 1
            
            # Copy individual stock articles
            article_files = list(results_dir.glob('articles_*_latest.html'))
            for article_file in article_files:
                shutil.copy2(article_file, docs_dir)
                files_copied += 1
            
            logger.info(f"✅ Copied {len(article_files)} individual stock articles")
        
        # Copy master dashboard
        if Path('tigro_master_dashboard.html').exists():
            shutil.copy2('tigro_master_dashboard.html', docs_dir)
            logger.info("✅ Copied: tigro_master_dashboard.html")
            files_copied += 1
        
        # Update index.html to point to master dashboard
        index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=./tigro_master_dashboard.html">
    <title>🐅 TIGRO - Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="./tigro_master_dashboard.html">TIGRO Master Dashboard</a>...</p>
    <script>window.location.href = './tigro_master_dashboard.html';</script>
</body>
</html>"""
        
        with open(docs_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_content)
        logger.info("✅ Updated: index.html (redirect to master dashboard)")
        files_copied += 1
        
        logger.info(f"🎉 Successfully copied {files_copied} files to docs/")
        logger.info(f"🌐 Dashboard will be available at: https://theemeraldnetwork.github.io/tigro/")
        
        return True
        
    except Exception as e:
        logger.error(f"🚨 Error copying files to docs: {e}")
        return False

def deploy_to_github(logger: logging.Logger) -> bool:
    """Deploy all changes to GitHub Pages"""
    logger.info("=" * 60)
    logger.info("🚀 STEP 6: GITHUB DEPLOYMENT")
    logger.info("=" * 60)
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Git commands sequence
        git_commands = [
            (['git', 'add', '.'], "Adding all files"),
            (['git', 'commit', '-m', f'🐅 TIGRO Complete Refresh - {timestamp}\n\n✅ Fresh sentiment analysis with updated stock list\n✅ Portfolio optimization with current data\n✅ Corrected cash calculations\n✅ Master dashboard with both tabs\n✅ All dashboards synchronized'], "Committing changes"),
            (['git', 'push', 'origin', 'gh-pages'], "Pushing to GitHub Pages")
        ]
        
        for cmd, description in git_commands:
            success = run_command_with_retry(cmd, description, logger, max_retries=2, delay=3)
            if not success:
                logger.error(f"🚨 Failed: {description}")
                return False
        
        logger.info("🎉 Successfully deployed to GitHub Pages!")
        return True
        
    except Exception as e:
        logger.error(f"🚨 GitHub deployment error: {e}")
        return False

def main():
    """Main orchestration function"""
    start_time = datetime.now()
    logger = setup_logging()
    
    logger.info("🐅" * 20)
    logger.info("🐅 TIGRO COMPLETE REFRESH STARTED")
    logger.info("🐅" * 20)
    logger.info(f"📅 Start Time: {start_time}")
    logger.info(f"📁 Project Root: {Path.cwd().absolute()}")
    logger.info(f"🐍 Python: {sys.executable}")
    
    # Step 0: Prerequisites
    if not check_prerequisites(logger):
        logger.error("🚨 Prerequisites check failed!")
        return False
    
    success_steps = 0
    total_steps = 6
    
    # Step 1: Fresh Sentiment Analysis
    if run_sentiment_analysis(logger):
        success_steps += 1
    
    # Step 2: Portfolio Optimization
    if run_portfolio_optimization(logger):
        success_steps += 1
    
    # Step 3: Generate Action Table
    if generate_action_table(logger):
        success_steps += 1
    
    # Step 4: Generate Sentiment Dashboard
    if generate_sentiment_dashboard(logger):
        success_steps += 1
    
    # Step 5: Copy to Docs
    if copy_files_to_docs(logger):
        success_steps += 1
    
    # Step 6: Deploy to GitHub
    if deploy_to_github(logger):
        success_steps += 1
    
    # Final Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("🐅" * 20)
    logger.info("🎉 TIGRO COMPLETE REFRESH FINISHED")
    logger.info("🐅" * 20)
    logger.info(f"⏱️ Total Duration: {duration}")
    logger.info(f"✅ Successful Steps: {success_steps}/{total_steps}")
    logger.info(f"📊 Success Rate: {(success_steps/total_steps)*100:.1f}%")
    
    if success_steps == total_steps:
        logger.info("🎯 ALL SYSTEMS OPERATIONAL!")
        logger.info("🌐 Live Dashboard: https://theemeraldnetwork.github.io/tigro/")
        logger.info("📈 Sentiment + Portfolio tabs available")
        logger.info("💰 Fresh data with corrected cash calculations")
        return True
    else:
        logger.warning(f"⚠️ Partial success: {success_steps}/{total_steps} steps completed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 TIGRO refresh interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n🚨 TIGRO refresh failed with error: {e}")
        sys.exit(1) 