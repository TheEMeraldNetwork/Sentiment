"""
Master runner script that executes sentiment analysis and generates consolidated output.
"""

import subprocess
from pathlib import Path
import sys
import time
from datetime import datetime
from scripts.e_open_html import open_report

def get_user_choice() -> str:
    """Get user's choice for analysis type"""
    while True:
        print("\nSelect analysis type:")
        print("1. Analyst Consensus only (faster)")
        print("2. Full analysis (Sentiment + Analyst Consensus)")
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
    
def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status"""
    print(f"\n{'='*80}")
    print(f"Running {description}...")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run analysis based on user choice"""
    start_time = time.time()
    print(f"\nStarting analysis run at {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    # Get user's choice
    choice = get_user_choice()
    
    # Ensure results directory exists
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    # Always run analyst consensus
    if not run_script('scripts/c_external_forecast.py', 'Analyst Consensus Analysis'):
        print("\nERROR: Analyst consensus analysis failed!")
        return
    
    # Run sentiment analysis if requested
    if choice == '2':
        if not run_script('scripts/a_sentiment_analysis.py', 'Sentiment Analysis'):
            print("\nERROR: Sentiment analysis failed!")
            return
        
        # Generate consolidated output
        if not run_script('scripts/d_master_output.py', 'Consolidated Output Generation'):
            print("\nERROR: Consolidated output generation failed!")
            return
    
    # Print summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*80}")
    print("Analysis Run Complete!")
    print(f"{'='*80}")
    print(f"Duration: {duration:.1f} seconds")
    
    # Open HTML report
    open_report()

if __name__ == "__main__":
    main() 