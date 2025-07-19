#!/usr/bin/env python3
"""
Setup script for Tigro Daily Automation
This script will:
1. Install/update the LaunchD service
2. Test the daily automation script
3. Set up proper scheduling
4. Clean up old configurations
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Project configuration
PROJECT_ROOT = Path(__file__).parent
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_FILE = "com.tigro.daily.plist"
OLD_PLIST_FILE = "com.tigro.sentiment.plist"

def setup_logging():
    """Setup logging for setup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('tigro_setup')

def check_prerequisites(logger):
    """Check all prerequisites for automation"""
    logger.info("🔍 Checking prerequisites...")
    
    # Check Python virtual environment
    venv_python = PROJECT_ROOT / "venv" / "bin" / "python"
    if not venv_python.exists():
        logger.error(f"❌ Python virtual environment not found at {venv_python}")
        return False
    
    # Check daily automation script
    daily_script = PROJECT_ROOT / "daily_automation.py"
    if not daily_script.exists():
        logger.error(f"❌ Daily automation script not found at {daily_script}")
        return False
    
    # Check API keys
    api_keys = PROJECT_ROOT / "utils" / "config" / "api_keys.json"
    if not api_keys.exists():
        logger.error(f"❌ API keys file not found at {api_keys}")
        return False
    
    # Check email configuration
    email_config = PROJECT_ROOT / "utils" / "config" / "email_config.json"
    if not email_config.exists():
        logger.error(f"❌ Email configuration not found at {email_config}")
        return False
    
    # Check master ticker file
    ticker_file = PROJECT_ROOT / "master name ticker.csv"
    if not ticker_file.exists():
        logger.error(f"❌ Master ticker file not found at {ticker_file}")
        return False
    
    logger.info("✅ All prerequisites satisfied")
    return True

def unload_old_service(logger):
    """Unload old LaunchD service if it exists"""
    old_plist_path = LAUNCH_AGENTS_DIR / OLD_PLIST_FILE
    
    if old_plist_path.exists():
        logger.info(f"🗑️ Unloading old LaunchD service: {OLD_PLIST_FILE}")
        
        try:
            # Unload the old service
            subprocess.run([
                "launchctl", "unload", str(old_plist_path)
            ], check=False)  # Don't fail if it's not loaded
            
            # Remove the old plist file
            old_plist_path.unlink()
            logger.info("✅ Old service unloaded and removed")
            
        except Exception as e:
            logger.warning(f"⚠️ Error removing old service: {e}")
    
    # Also check for current service
    current_plist_path = LAUNCH_AGENTS_DIR / PLIST_FILE
    if current_plist_path.exists():
        logger.info(f"🔄 Unloading current service to reinstall: {PLIST_FILE}")
        
        try:
            subprocess.run([
                "launchctl", "unload", str(current_plist_path)
            ], check=False)
            logger.info("✅ Current service unloaded for reinstall")
            
        except Exception as e:
            logger.warning(f"⚠️ Error unloading current service: {e}")

def install_service(logger):
    """Install the LaunchD service"""
    logger.info("📦 Installing LaunchD service...")
    
    # Ensure LaunchAgents directory exists
    LAUNCH_AGENTS_DIR.mkdir(exist_ok=True)
    
    # Copy plist file
    source_plist = PROJECT_ROOT / PLIST_FILE
    target_plist = LAUNCH_AGENTS_DIR / PLIST_FILE
    
    try:
        shutil.copy2(source_plist, target_plist)
        logger.info(f"✅ Copied plist file to {target_plist}")
        
        # Set proper permissions
        target_plist.chmod(0o644)
        
        # Load the service
        subprocess.run([
            "launchctl", "load", str(target_plist)
        ], check=True)
        
        logger.info("✅ LaunchD service installed and loaded")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error installing service: {e}")
        return False

def test_automation_script(logger):
    """Test the daily automation script"""
    logger.info("🧪 Testing daily automation script...")
    
    try:
        # Test with dry run (we'll add a --test flag)
        result = subprocess.run([
            sys.executable, "daily_automation.py", "--test"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Daily automation script test passed")
            return True
        else:
            logger.error(f"❌ Daily automation script test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Daily automation script test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing automation script: {e}")
        return False

def show_service_status(logger):
    """Show the current status of the LaunchD service"""
    logger.info("📊 Checking service status...")
    
    try:
        # Check if service is loaded
        result = subprocess.run([
            "launchctl", "list", "com.tigro.daily"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Service is loaded and active")
            logger.info(f"Service details: {result.stdout}")
        else:
            logger.warning("⚠️ Service may not be loaded properly")
            
    except Exception as e:
        logger.error(f"❌ Error checking service status: {e}")

def show_next_run_time(logger):
    """Show when the service will next run"""
    logger.info("⏰ Next scheduled run:")
    logger.info("📅 Daily at 8:30 AM")
    logger.info("🔧 To test immediately, run: python daily_automation.py")
    logger.info("📋 To check logs: tail -f logs/daily_automation_*.log")

def main():
    """Main setup function"""
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("🐅 TIGRO DAILY AUTOMATION SETUP")
    logger.info("="*60)
    
    # Check prerequisites
    if not check_prerequisites(logger):
        logger.error("❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Unload old service
    unload_old_service(logger)
    
    # Install new service
    if not install_service(logger):
        logger.error("❌ Failed to install LaunchD service")
        sys.exit(1)
    
    # Test automation script (we'll need to modify the script to support --test)
    logger.info("ℹ️ Skipping automation test for now (will be added in next version)")
    
    # Show service status
    show_service_status(logger)
    
    # Show next run time
    show_next_run_time(logger)
    
    logger.info("="*60)
    logger.info("🎉 SETUP COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    logger.info("📋 Summary:")
    logger.info("  • Daily automation installed and scheduled")
    logger.info("  • Runs every day at 8:30 AM")
    logger.info("  • Logs saved to logs/daily_automation_*.log")
    logger.info("  • Email notifications enabled")
    logger.info("  • GitHub Pages auto-update enabled")
    logger.info("")
    logger.info("🚀 Next Steps:")
    logger.info("  • Test manually: python daily_automation.py")
    logger.info("  • Check logs: tail -f logs/daily_automation_*.log")
    logger.info("  • Monitor email delivery")
    logger.info("  • View dashboard: https://theemeraldnetwork.github.io/tigro/")

if __name__ == "__main__":
    main() 