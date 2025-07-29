#!/bin/bash

echo "🐅 TIGRO 6PM AUTOMATION TEST MONITOR"
echo "========================================"
echo "⏰ Current time: $(date)"
echo "🎯 Waiting for 18:00 CET trigger..."
echo "📊 Service status: $(launchctl list com.tigro.daily | grep Label)"
echo ""

echo "📋 MONITORING FILES:"
echo "  • LaunchD Output: logs/tigro_daily.log"
echo "  • LaunchD Errors: logs/tigro_daily_error.log"
echo "  • Automation Log: logs/daily_automation_$(date +%Y%m%d).log"
echo ""

echo "🔍 Watching for automation trigger (Press Ctrl+C to stop)..."
echo "========================================"

# Monitor multiple log files for activity
tail -f logs/tigro_daily.log logs/tigro_daily_error.log logs/daily_automation_$(date +%Y%m%d).log 2>/dev/null &
TAIL_PID=$!

# Check every 30 seconds for new processes
while true; do
    echo "⏰ $(date +%H:%M:%S) - Checking for automation activity..."
    
    # Check if automation is running
    if ps aux | grep -q "[d]aily_automation.py"; then
        echo "🚀 AUTOMATION DETECTED! Running now..."
        break
    fi
    
    # Check if we're past 18:05 (5 minutes after trigger time)
    if [ $(date +%H%M) -gt 1805 ]; then
        echo "⚠️  Past 18:05 - automation should have triggered by now"
        echo "🔍 Checking service status..."
        launchctl list com.tigro.daily
        break
    fi
    
    sleep 30
done

# Clean up
kill $TAIL_PID 2>/dev/null
echo "🏁 Monitoring complete!" 