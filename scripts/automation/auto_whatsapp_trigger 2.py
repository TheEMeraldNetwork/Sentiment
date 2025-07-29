#!/usr/bin/env python3
"""
WhatsApp Trigger System for Tigro Sentiment Analysis
Uses Flask to create a webhook that can be triggered via WhatsApp
"""

import os
import sys
import subprocess
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

# Add the project root to sys.path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = Flask(__name__)
CORS(app, origins=["https://theemeraldnetwork.github.io"])

# Simple authentication token (you can change this)
WEBHOOK_TOKEN = "tigro_2025_secure"

def run_sentiment_analysis():
    """Run the sentiment analysis pipeline in a separate thread"""
    try:
        # Change to project directory
        os.chdir(project_root)
        
        # Run the master script
        result = subprocess.run([
            sys.executable, 
            'master_runner_short.py'
        ], capture_output=True, text=True)
        
        print(f"Pipeline completed. Return code: {result.returncode}")
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"Error running sentiment analysis: {e}")

def send_email_only():
    """Send email report only without running full pipeline"""
    try:
        # Change to project directory
        os.chdir(project_root)
        
        # Import required modules
        from utils.email.report_sender import SentimentEmailSender
        import pandas as pd
        from pathlib import Path
        
        # Load latest sentiment summary
        results_dir = Path('results')
        latest_symlink = results_dir / 'sentiment_summary_latest.csv'
        
        if latest_symlink.exists():
            summary_df = pd.read_csv(latest_symlink)
            print(f"Loaded sentiment data: {len(summary_df)} stocks")
        else:
            # Find dated files as fallback
            summary_files = [f for f in results_dir.glob('sentiment_summary_*.csv') 
                           if f.name.count('_') == 2 and 'latest' not in f.name]
            
            if not summary_files:
                print("No sentiment summary files found")
                return
                
            latest_file = max(summary_files, key=lambda f: f.stat().st_mtime)
            summary_df = pd.read_csv(latest_file)
            print(f"Loaded sentiment data from {latest_file.name}: {len(summary_df)} stocks")
        
        # Send the email
        sender = SentimentEmailSender()
        sender.send_email(summary_df, test_mode=False)
        print("✅ Email report sent successfully")
        
    except Exception as e:
        print(f"Error sending email report: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests"""
    try:
        # Get the request data
        data = request.get_json()
        
        # Simple authentication check
        if request.headers.get('Authorization') != f'Bearer {WEBHOOK_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Check if this is a trigger request
        message = data.get('message', '').lower()
        
        if any(keyword in message for keyword in ['tigro', 'report', 'sentiment', 'analysis']):
            print(f"Received trigger request: {message}")
            
            # Start the sentiment analysis in a separate thread
            thread = threading.Thread(target=run_sentiment_analysis)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'status': 'success',
                'message': 'Tigro sentiment analysis started! You will receive an email report shortly.',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'ignored',
                'message': 'Message does not contain trigger keywords'
            })
            
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Tigro WhatsApp Trigger',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/trigger', methods=['POST'])
def manual_trigger():
    """Manual trigger endpoint for testing"""
    try:
        # Simple authentication check
        if request.headers.get('Authorization') != f'Bearer {WEBHOOK_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        
        print("Manual trigger received")
        
        # Start the sentiment analysis in a separate thread
        thread = threading.Thread(target=run_sentiment_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Tigro sentiment analysis started!',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Manual trigger error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/email-only', methods=['POST'])
def email_only_trigger():
    """Email-only trigger endpoint for instant reports"""
    try:
        # Simple authentication check
        if request.headers.get('Authorization') != f'Bearer {WEBHOOK_TOKEN}':
            return jsonify({'error': 'Unauthorized'}), 401
        
        print("Email-only trigger received")
        
        # Start the email sending in a separate thread
        thread = threading.Thread(target=send_email_only)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Instant email report sent!',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Email-only trigger error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Tigro WhatsApp Trigger Service...")
    print(f"Project root: {project_root}")
    print(f"Webhook token: {WEBHOOK_TOKEN}")
    print("Service will run on http://localhost:5001")
    print("Endpoints:")
    print("  - POST /webhook (for WhatsApp integration)")
    print("  - POST /trigger (for manual testing)")
    print("  - GET /status (health check)")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 