#!/usr/bin/env python3
"""
Real-time monitoring script for Tigro automation.
Shows live progress table when automation is running.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
import threading

class TigroRealTimeMonitor:
    def __init__(self):
        self.log_file = Path('logs/tigro_master_detailed.log')
        self.status_table = {
            '🔍 Prerequisites': '⏸️ Pending',
            '📊 Sentiment Analysis': '⏸️ Pending', 
            '📈 Dashboard Generation': '⏸️ Pending',
            '📋 Copy to Docs': '⏸️ Pending',
            '🚀 Git Push': '⏸️ Pending',
            '📧 Email Report': '⏸️ Pending',
            '🧹 Cleanup': '⏸️ Pending'
        }
        self.start_time = None
        self.last_log_size = 0
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """Print monitoring header"""
        current_time = datetime.now().strftime("%H:%M:%S")
        elapsed = ""
        if self.start_time:
            elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
            elapsed = f" | ⏱️ {int(elapsed_seconds//60):02d}:{int(elapsed_seconds%60):02d}"
        
        print("=" * 80)
        print(f"🐅 TIGRO AUTOMATION - REAL-TIME MONITOR | 🕐 {current_time}{elapsed}")
        print("=" * 80)
        
    def print_status_table(self):
        """Print current status table"""
        print("\n📊 PROGRESS STATUS:")
        print("-" * 60)
        for step, status in self.status_table.items():
            print(f"{step:<25} | {status}")
        print("-" * 60)
        
    def parse_log_updates(self):
        """Parse new log entries and update status"""
        if not self.log_file.exists():
            return
            
        try:
            current_size = self.log_file.stat().st_size
            if current_size <= self.last_log_size:
                return
                
            with open(self.log_file, 'r') as f:
                f.seek(self.last_log_size)
                new_lines = f.read().splitlines()
                
            self.last_log_size = current_size
            
            for line in new_lines:
                self.update_status_from_log(line)
                
        except Exception as e:
            print(f"Error reading logs: {e}")
            
    def update_status_from_log(self, line):
        """Update status based on log line"""
        if not self.start_time and "TIGRO DAILY AUTOMATION STARTED" in line:
            self.start_time = datetime.now()
            
        # Prerequisites
        if "🔍 Checking prerequisites" in line:
            self.status_table['🔍 Prerequisites'] = '🔄 Running'
        elif "All prerequisites checked successfully" in line:
            self.status_table['🔍 Prerequisites'] = '✅ Complete'
            
        # Sentiment Analysis
        elif "📊 Starting sentiment analysis" in line:
            self.status_table['📊 Sentiment Analysis'] = '🔄 Running'
        elif "Sentiment analysis completed successfully" in line:
            self.status_table['📊 Sentiment Analysis'] = '✅ Complete'
        elif "Sentiment analysis failed" in line:
            self.status_table['📊 Sentiment Analysis'] = '❌ Failed'
            
        # Dashboard Generation
        elif "📈 Generating dashboard" in line:
            self.status_table['📈 Dashboard Generation'] = '🔄 Running'
        elif "Dashboard generation completed successfully" in line:
            self.status_table['📈 Dashboard Generation'] = '✅ Complete'
        elif "Dashboard generation failed" in line:
            self.status_table['📈 Dashboard Generation'] = '❌ Failed'
            
        # Copy to Docs
        elif "📋 Copying results to docs" in line:
            self.status_table['📋 Copy to Docs'] = '🔄 Running'
        elif "All files copied to docs directory" in line:
            self.status_table['📋 Copy to Docs'] = '✅ Complete'
            
        # Git Push
        elif "🚀 Pushing changes to GitHub" in line:
            self.status_table['🚀 Git Push'] = '🔄 Running'
        elif "Successfully pushed to GitHub" in line:
            self.status_table['🚀 Git Push'] = '✅ Complete'
        elif "Git push failed" in line:
            self.status_table['🚀 Git Push'] = '❌ Failed'
            
        # Email Report
        elif "📧 Sending email report" in line:
            self.status_table['📧 Email Report'] = '🔄 Running'
        elif "Email report sent successfully" in line:
            self.status_table['📧 Email Report'] = '✅ Complete'
        elif "Email report failed" in line:
            self.status_table['📧 Email Report'] = '❌ Failed'
            
        # Cleanup
        elif "🧹 Cleaning up old log files" in line:
            self.status_table['🧹 Cleanup'] = '🔄 Running'
        elif "Log cleanup completed" in line:
            self.status_table['🧹 Cleanup'] = '✅ Complete'
            
    def print_latest_logs(self, num_lines=10):
        """Print latest log entries"""
        if not self.log_file.exists():
            print("\n📝 LATEST LOGS: No logs yet...")
            return
            
        try:
            result = subprocess.run(['tail', '-n', str(num_lines), str(self.log_file)], 
                                 capture_output=True, text=True)
            if result.stdout:
                print(f"\n📝 LATEST LOGS (last {num_lines} lines):")
                print("-" * 60)
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # Truncate very long lines
                        display_line = line[:120] + "..." if len(line) > 120 else line
                        print(display_line)
                print("-" * 60)
        except Exception as e:
            print(f"\n📝 LATEST LOGS: Error reading logs: {e}")
            
    def wait_for_automation(self):
        """Wait for automation to start and monitor it"""
        print("⏳ Waiting for automation to start at 7:25 PM...")
        
        while True:
            self.clear_screen()
            self.print_header()
            
            # Check if automation is running
            if self.log_file.exists():
                current_size = self.log_file.stat().st_size
                if current_size > self.last_log_size:
                    self.parse_log_updates()
                    
            self.print_status_table()
            self.print_latest_logs(8)
            
            # Check if automation is complete
            if all(status in ['✅ Complete', '❌ Failed'] for status in self.status_table.values()):
                print("\n🎉 AUTOMATION COMPLETED!")
                break
                
            time.sleep(2)  # Update every 2 seconds
            
    def run(self):
        """Main monitoring loop"""
        try:
            self.wait_for_automation()
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
        except Exception as e:
            print(f"\n\n🚨 Monitor error: {e}")

if __name__ == "__main__":
    monitor = TigroRealTimeMonitor()
    monitor.run() 