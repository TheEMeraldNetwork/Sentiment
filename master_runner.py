"""
Master runner script that executes the entire market analysis workflow:
1. Market Data Collection
2. Data Consolidation
3. Dashboard Generation
"""

import subprocess
from pathlib import Path
import sys
import logging
from datetime import datetime
import time
import pandas as pd
from tabulate import tabulate

def setup_logging():
    """Setup logging configuration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'master_run_{timestamp}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_module(script_path: str, logger: logging.Logger) -> tuple[bool, float, dict]:
    """Run a Python script and log its output"""
    try:
        logger.info(f"\nExecuting {script_path}...")
        start_time = time.time()
        
        # Run script and capture output
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        # Log output
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
            
        duration = time.time() - start_time
        logger.info(f"Completed {script_path} in {duration:.1f} seconds")
        
        # Extract metrics from output
        metrics = {}
        output = result.stdout.lower()
        
        if 'sentiment_analysis' in script_path:
            if 'total articles processed:' in output:
                articles = output.split('total articles processed:')[1].split('\n')[0].strip()
                metrics['Articles Processed'] = int(articles)
            if 'companies analyzed:' in output:
                companies = output.split('companies analyzed:')[1].split('\n')[0].strip()
                metrics['Companies with News'] = int(companies)
                
        elif 'market_data' in script_path:
            if 'companies with analyst data:' in output:
                analysts = output.split('companies with analyst data:')[1].split('\n')[0].strip()
                metrics['Companies with Analyst Data'] = int(analysts)
            if 'average target return:' in output:
                return_val = output.split('average target return:')[1].split('%')[0].strip()
                metrics['Average Target Return'] = f"{float(return_val):.1f}%"
                
        elif 'consolidate_data' in script_path:
            if 'companies with complete data:' in output:
                complete = output.split('companies with complete data:')[1].split('\n')[0].strip()
                metrics['Companies with Complete Data'] = int(complete)
        
        return result.returncode == 0, duration, metrics
        
    except Exception as e:
        logger.error(f"Error running {script_path}: {e}")
        return False, 0, {}

def print_summary_table(workflow_results: list, total_duration: float, logger: logging.Logger):
    """Print a summary table of the workflow execution"""
    # Prepare data for the summary table
    summary_data = []
    all_metrics = {}
    
    for script, duration, success, metrics in workflow_results:
        script_name = Path(script).name
        status = '✓' if success else '✗'
        summary_data.append([
            script_name,
            status,
            f"{duration:.1f}s"
        ])
        all_metrics.update(metrics)
    
    # Add total duration
    summary_data.append(['Total', '', f"{total_duration:.1f}s"])
    
    # Print workflow summary
    logger.info("\n=== Workflow Summary ===")
    logger.info("\nExecution Results:")
    logger.info(tabulate(summary_data, headers=['Module', 'Status', 'Duration'], tablefmt='grid'))
    
    # Print metrics summary if any
    if all_metrics:
        metrics_data = [[k, v] for k, v in all_metrics.items()]
        logger.info("\nKey Metrics:")
        logger.info(tabulate(metrics_data, headers=['Metric', 'Value'], tablefmt='grid'))

def main():
    """Execute the complete market analysis workflow"""
    logger = setup_logging()
    scripts_dir = Path('scripts')
    
    # Define workflow steps - Skip sentiment analysis
    workflow = [
        ('b_collect_market.py', True),
        ('d_consolidate_data.py', True),
        ('e_generate_dashboard.py', True)     # Required for HTML report
    ]
    
    logger.info("Starting market analysis workflow...")
    start_time = time.time()
    
    # Execute each step and collect results
    workflow_results = []
    for script, required in workflow:
        script_path = scripts_dir / script
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            if required:
                logger.error("Required script missing. Aborting workflow.")
                return False
            continue
            
        success, duration, metrics = run_module(str(script_path), logger)
        workflow_results.append((script, duration, success, metrics))
        
        if not success and required:
            logger.error(f"Required step {script} failed. Aborting workflow.")
            return False
            
        # Brief pause between steps
        time.sleep(1)
    
    total_duration = time.time() - start_time
    
    # Print summary table
    print_summary_table(workflow_results, total_duration, logger)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 