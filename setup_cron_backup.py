#!/usr/bin/env python3
"""
Backup Cron Setup for Tigro Daily Automation
Alternative to LaunchD if it continues to have issues
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# Project configuration
PROJECT_ROOT = Path(__file__).parent

def setup_logging():
    """Setup logging for cron setup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('tigro_cron_setup')

def create_cron_wrapper():
    """Create a wrapper script for cron"""
    wrapper_script = PROJECT_ROOT / "run_daily_automation.sh"
    
    wrapper_content = f"""#!/bin/bash
# Tigro Daily Automation Cron Wrapper
# This script ensures proper environment for cron execution

# Set working directory
cd "{PROJECT_ROOT}"

# Set environment variables
export PATH="/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="{PROJECT_ROOT}"

# Activate virtual environment and run automation
source venv/bin/activate
python daily_automation.py >> logs/cron_daily.log 2>&1
"""
    
    with open(wrapper_script, 'w') as f:
        f.write(wrapper_content)
    
    # Make executable
    wrapper_script.chmod(0o755)
    
    return wrapper_script

def get_current_crontab():
    """Get current crontab content"""
    try:
        result = subprocess.run(['crontab', '-l'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return ""
    except Exception:
        return ""

def setup_cron_job(logger, wrapper_script):
    """Setup the cron job"""
    logger.info("📅 Setting up cron job...")
    
    # Get current crontab
    current_crontab = get_current_crontab()
    
    # Remove any existing tigro entries
    lines = current_crontab.split('\n')
    filtered_lines = [line for line in lines if 'tigro' not in line.lower() and 'daily_automation' not in line.lower()]
    
    # Add new cron job (8:30 AM daily)
    new_cron_line = f"30 8 * * * {wrapper_script}"
    filtered_lines.append(new_cron_line)
    
    # Write new crontab
    new_crontab = '\n'.join(filtered_lines)
    
    try:
        process = subprocess.Popen(['crontab', '-'], 
                                  stdin=subprocess.PIPE, 
                                  text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            logger.info("✅ Cron job installed successfully")
            return True
        else:
            logger.error("❌ Failed to install cron job")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error setting up cron job: {e}")
        return False

def show_cron_status(logger):
    """Show current cron status"""
    logger.info("📊 Current cron jobs:")
    
    try:
        result = subprocess.run(['crontab', '-l'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'tigro' in line.lower() or 'daily_automation' in line.lower():
                    logger.info(f"  📅 {line}")
        else:
            logger.warning("⚠️ No crontab found")
            
    except Exception as e:
        logger.error(f"❌ Error checking cron status: {e}")

def main():
    """Main cron setup function"""
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("🐅 TIGRO CRON BACKUP SETUP")
    logger.info("="*60)
    
    # Create wrapper script
    logger.info("📝 Creating cron wrapper script...")
    wrapper_script = create_cron_wrapper()
    logger.info(f"✅ Wrapper script created: {wrapper_script}")
    
    # Setup cron job
    if not setup_cron_job(logger, wrapper_script):
        logger.error("❌ Failed to setup cron job")
        sys.exit(1)
    
    # Show status
    show_cron_status(logger)
    
    logger.info("="*60)
    logger.info("🎉 CRON BACKUP SETUP COMPLETED!")
    logger.info("="*60)
    logger.info("📋 Summary:")
    logger.info("  • Cron job installed for daily automation")
    logger.info("  • Runs every day at 8:30 AM")
    logger.info("  • Logs saved to logs/cron_daily.log")
    logger.info("  • Wrapper script ensures proper environment")
    logger.info("")
    logger.info("🚀 Next Steps:")
    logger.info("  • Test manually: ./run_daily_automation.sh")
    logger.info("  • Check logs: tail -f logs/cron_daily.log")
    logger.info("  • Monitor cron: crontab -l")
    logger.info("")
    logger.info("ℹ️ Note: This is a backup to LaunchD. Use only if LaunchD fails.")

if __name__ == "__main__":
    main() 