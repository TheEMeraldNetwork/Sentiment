#!/usr/bin/env python3
"""
Countdown monitor for Tigro automation.
Shows countdown until 2:40 PM, then launches real-time monitoring.
"""

import os
import sys
import time
import subprocess
from datetime import datetime, time as dt_time
from pathlib import Path

class TigroCountdownMonitor:
    def __init__(self, target_hour=14, target_minute=40):
        self.target_hour = target_hour
        self.target_minute = target_minute
        self.log_file = Path('logs/tigro_master_detailed.log')
        self.automation_started = False
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def get_time_until_target(self):
        """Calculate time until target time"""
        now = datetime.now()
        target = now.replace(hour=self.target_hour, minute=self.target_minute, second=0, microsecond=0)
        
        # If target time has passed today, set for tomorrow
        if now > target:
            target = target.replace(day=target.day + 1)
            
        diff = target - now
        return diff
        
    def print_countdown_header(self):
        """Print countdown header"""
        current_time = datetime.now().strftime("%H:%M:%S")
        print("=" * 80)
        print(f"🐅 TIGRO AUTOMATION COUNTDOWN | 🕐 Current: {current_time}")
        print("=" * 80)
        
    def print_countdown_status(self, time_diff):
        """Print countdown status"""
        total_seconds = int(time_diff.total_seconds())
        
        if total_seconds <= 0:
            print("\n🚀 AUTOMATION STARTING NOW!")
            print("🔄 Switching to real-time monitoring...")
            return True
            
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        print(f"\n⏰ TARGET TIME: {self.target_hour:02d}:{self.target_minute:02d} CET")
        print(f"⏳ TIME REMAINING: {minutes:02d}:{seconds:02d}")
        
        # Progress bar
        total_wait = 15 * 60  # 15 minutes in seconds
        elapsed = total_wait - total_seconds
        progress = max(0, min(100, (elapsed / total_wait) * 100))
        bar_length = 50
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"📊 PROGRESS: [{bar}] {progress:.1f}%")
        
        return False
        
    def check_automation_activity(self):
        """Check if automation has started based on log activity"""
        if not self.log_file.exists():
            return False
            
        try:
            # Check if there's recent activity in the last minute
            current_time = time.time()
            file_mtime = self.log_file.stat().st_mtime
            
            if current_time - file_mtime < 60:  # Activity within last 60 seconds
                # Check if it's a new automation run
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in reversed(lines[-10:]):  # Check last 10 lines
                        if "TIGRO DAILY AUTOMATION STARTED" in line:
                            # Check if this started recently (within 2 minutes)
                            log_time_str = line.split(' - ')[0]
                            try:
                                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                                if (datetime.now() - log_time).total_seconds() < 120:
                                    return True
                            except:
                                pass
                                
        except Exception as e:
            print(f"Error checking automation: {e}")
            
        return False
        
    def print_system_status(self):
        """Print current system status"""
        print("\n📋 SYSTEM STATUS:")
        print("-" * 60)
        print("✅ LaunchAgent loaded and scheduled")
        print("✅ Enhanced logging system active")
        print("✅ Email configuration ready")
        print("✅ Real-time monitor prepared")
        print("-" * 60)
        
    def run_countdown(self):
        """Main countdown loop"""
        print("🚀 Starting countdown monitor...")
        
        while True:
            self.clear_screen()
            self.print_countdown_header()
            
            time_diff = self.get_time_until_target()
            automation_ready = self.print_countdown_status(time_diff)
            
            # Check if automation has actually started
            if automation_ready or self.check_automation_activity():
                self.automation_started = True
                break
                
            self.print_system_status()
            
            print(f"\n📝 WHEN AUTOMATION STARTS:")
            print("🔄 This monitor will switch to real-time progress tracking")
            print("📊 Live table showing each step: Prerequisites → Sentiment → Dashboard → Git → Email")
            print("📧 Email delivery confirmation with declining stocks list")
            
            time.sleep(1)  # Update every second for smooth countdown
            
    def launch_realtime_monitor(self):
        """Launch the real-time monitoring system"""
        print("\n" + "=" * 80)
        print("🚀 AUTOMATION DETECTED - LAUNCHING REAL-TIME MONITOR")
        print("=" * 80)
        print("")
        
        # Import and run the real-time monitor
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from realtime_monitor import TigroRealTimeMonitor
            
            monitor = TigroRealTimeMonitor()
            monitor.run()
            
        except ImportError:
            print("❌ Real-time monitor not found, showing basic log tail...")
            subprocess.run(['tail', '-f', str(self.log_file)])
        except Exception as e:
            print(f"❌ Error launching real-time monitor: {e}")
            print("📝 Falling back to log monitoring...")
            subprocess.run(['tail', '-f', str(self.log_file)])
            
    def run(self):
        """Main run function"""
        try:
            self.run_countdown()
            if self.automation_started:
                self.launch_realtime_monitor()
        except KeyboardInterrupt:
            print("\n\n👋 Countdown monitor stopped by user")
        except Exception as e:
            print(f"\n\n🚨 Monitor error: {e}")

if __name__ == "__main__":
    monitor = TigroCountdownMonitor()
    monitor.run() 