"""
Email report sender module for Tigro sentiment analysis.
Sends weekly sentiment reports via Gmail SMTP with alerts for declining stocks.
"""

import smtplib
import json
import logging
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import pandas as pd

class SentimentEmailSender:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_path = Path('utils/config/email_config.json')
        self.config = self._load_email_config()
        
    def _load_email_config(self) -> dict:
        """Load email configuration from file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Email config not found at {self.config_path}. "
                "Please copy email_config.template.json to email_config.json and configure it."
            )
        
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                
            # Validate required fields
            required_fields = ['smtp_server', 'smtp_port', 'email_address', 'app_password', 'recipient_email']
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required email config fields: {missing_fields}")
                
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading email config: {e}")
            raise
    
    def extract_declining_stocks(self, summary_df: pd.DataFrame) -> List[Dict]:
        """Extract stocks with declining sentiment trends"""
        try:
            # Try to load historical trends from database
            from utils.db.sentiment_history import SentimentHistoryDB
            history_db = SentimentHistoryDB()
            trends_df = history_db.get_sentiment_trends()
            
            if not trends_df.empty:
                # Use historical trend data
                declining_stocks = trends_df[trends_df['trend'] == 'DOWN'].copy()
                declining_stocks = declining_stocks.sort_values('sentiment_change', ascending=True)
                
                # Merge with current summary data for additional info
                merged_df = pd.merge(declining_stocks, summary_df[['ticker', 'total_articles']], 
                                   on='ticker', how='left')
                
                alerts = []
                for _, row in merged_df.head(5).iterrows():
                    alert = {
                        'ticker': row['ticker'],
                        'company': row['company'],
                        'sentiment_change': row['sentiment_change'],
                        'current_sentiment': row['current_sentiment'],
                        'total_articles': row.get('total_articles', 0)
                    }
                    alerts.append(alert)
                
                self.logger.info(f"Found {len(alerts)} declining stocks from historical trends")
                return alerts
            
        except Exception as e:
            self.logger.warning(f"Could not load historical trends: {e}")
        
        # Fallback: Use current sentiment data to find lowest performers
        self.logger.info("Using fallback method: identifying lowest sentiment stocks")
        
        # Get stocks with sentiment data and sort by current sentiment (lowest first)
        valid_stocks = summary_df[summary_df['average_sentiment'].notna()].copy()
        if valid_stocks.empty:
            return []
        
        # Sort by average sentiment (most negative first)
        declining_stocks = valid_stocks.sort_values('average_sentiment', ascending=True)
        
        # Take the bottom 5 stocks as "declining" (most negative sentiment)
        alerts = []
        for _, row in declining_stocks.head(5).iterrows():
            # Calculate a synthetic "change" based on distance from neutral
            sentiment_change = row['average_sentiment'] - 0.0  # Distance from neutral
            
            alert = {
                'ticker': row['ticker'],
                'company': row['company'],
                'sentiment_change': sentiment_change,
                'current_sentiment': row['average_sentiment'],
                'total_articles': row.get('total_articles', 0)
            }
            alerts.append(alert)
        
        # Only return alerts for stocks with negative sentiment
        negative_alerts = [alert for alert in alerts if alert['current_sentiment'] < -0.1]
        
        self.logger.info(f"Found {len(negative_alerts)} stocks with negative sentiment")
        return negative_alerts
    
    def generate_summary_stats(self, summary_df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the email"""
        stats = {
            'total_stocks': len(summary_df),
            'stocks_with_data': len(summary_df[summary_df['average_sentiment'].notna()]),
            'trending_up': 0,
            'trending_down': 0,
            'average_sentiment': 0,
            'report_date': datetime.now().strftime('%B %d, %Y')
        }
        
        # Try to calculate trend statistics from historical data
        try:
            from utils.db.sentiment_history import SentimentHistoryDB
            history_db = SentimentHistoryDB()
            trends_df = history_db.get_sentiment_trends()
            
            if not trends_df.empty:
                stats['trending_up'] = len(trends_df[trends_df['trend'] == 'UP'])
                stats['trending_down'] = len(trends_df[trends_df['trend'] == 'DOWN'])
                self.logger.info(f"Trend stats from history: {stats['trending_up']} up, {stats['trending_down']} down")
            else:
                # Fallback: Use sentiment thresholds to estimate trends
                sentiment_data = summary_df[summary_df['average_sentiment'].notna()]
                if not sentiment_data.empty:
                    positive_threshold = 0.1
                    negative_threshold = -0.1
                    stats['trending_up'] = len(sentiment_data[sentiment_data['average_sentiment'] > positive_threshold])
                    stats['trending_down'] = len(sentiment_data[sentiment_data['average_sentiment'] < negative_threshold])
                    self.logger.info(f"Estimated trends from sentiment: {stats['trending_up']} positive, {stats['trending_down']} negative")
                    
        except Exception as e:
            self.logger.warning(f"Could not calculate trend stats: {e}")
            # Fallback: Use sentiment thresholds
            sentiment_data = summary_df[summary_df['average_sentiment'].notna()]
            if not sentiment_data.empty:
                positive_threshold = 0.1
                negative_threshold = -0.1
                stats['trending_up'] = len(sentiment_data[sentiment_data['average_sentiment'] > positive_threshold])
                stats['trending_down'] = len(sentiment_data[sentiment_data['average_sentiment'] < negative_threshold])
        
        # Calculate average sentiment
        sentiment_data = summary_df[summary_df['average_sentiment'].notna()]
        if not sentiment_data.empty:
            stats['average_sentiment'] = sentiment_data['average_sentiment'].mean()
        
        return stats
    
    def generate_html_email(self, summary_df: pd.DataFrame) -> str:
        """Generate HTML email content"""
        alerts = self.extract_declining_stocks(summary_df)
        stats = self.generate_summary_stats(summary_df)
        
        # Determine overall market sentiment
        avg_sentiment = stats['average_sentiment']
        if avg_sentiment > 0.1:
            sentiment_emoji = "📈"
            sentiment_text = "Positive"
            sentiment_color = "#28a745"
        elif avg_sentiment < -0.1:
            sentiment_emoji = "📉"
            sentiment_text = "Negative" 
            sentiment_color = "#dc3545"
        else:
            sentiment_emoji = "➡️"
            sentiment_text = "Neutral"
            sentiment_color = "#6c757d"
        
        # Generate alerts section
        alerts_html = ""
        if alerts:
            for i, alert in enumerate(alerts, 1):
                change_pct = alert['sentiment_change'] * 100
                alerts_html += f"""
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 12px; font-weight: 500;">{i}.</td>
                    <td style="padding: 12px; font-weight: 600; color: #dc3545;">{alert['ticker']}</td>
                    <td style="padding: 12px;">{alert['company']}</td>
                    <td style="padding: 12px; color: #dc3545; font-weight: 500;">↓{abs(change_pct):.1f}%</td>
                    <td style="padding: 12px; color: #6c757d;">{alert['total_articles']} articles</td>
                </tr>
                """
        else:
            alerts_html = """
            <tr>
                <td colspan="5" style="padding: 20px; text-align: center; color: #28a745; font-weight: 500;">
                    ✅ No declining stocks detected this week!
                </td>
            </tr>
            """
        
        # GitHub Pages URL
        github_url = self.config.get('github_base_url', '#')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tigro Weekly Sentiment Report</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f8f9fa;">
            
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 600;">🐅 Tigro Sentiment Report</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9; font-size: 16px;">{stats['report_date']}</p>
                </div>
                
                <!-- Summary Section -->
                <div style="padding: 30px;">
                    <h2 style="color: #2c3e50; margin: 0 0 20px; font-size: 20px; border-bottom: 2px solid #e9ecef; padding-bottom: 10px;">
                        📊 Weekly Summary
                    </h2>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-bottom: 25px;">
                        <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: 600; color: #2c3e50;">{stats['total_stocks']}</div>
                            <div style="font-size: 12px; color: #6c757d; text-transform: uppercase;">Total Stocks</div>
                        </div>
                        
                        <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: 600; color: #28a745;">{stats['trending_up']}</div>
                            <div style="font-size: 12px; color: #6c757d; text-transform: uppercase;">Trending Up</div>
                        </div>
                        
                        <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: 600; color: #dc3545;">{stats['trending_down']}</div>
                            <div style="font-size: 12px; color: #6c757d; text-transform: uppercase;">Trending Down</div>
                        </div>
                        
                        <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 6px;">
                            <div style="font-size: 18px; font-weight: 600; color: {sentiment_color};">{sentiment_emoji} {sentiment_text}</div>
                            <div style="font-size: 12px; color: #6c757d; text-transform: uppercase;">Market Sentiment</div>
                        </div>
                    </div>
                </div>
                
                <!-- Alerts Section -->
                <div style="padding: 0 30px 30px;">
                    <h2 style="color: #dc3545; margin: 0 0 20px; font-size: 20px; border-bottom: 2px solid #e9ecef; padding-bottom: 10px;">
                        🚨 Declining Stocks Alert ({len(alerts)} stocks)
                    </h2>
                    
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <thead>
                                <tr style="background-color: #f8f9fa;">
                                    <th style="padding: 15px 12px; text-align: left; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;">#</th>
                                    <th style="padding: 15px 12px; text-align: left; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;">Ticker</th>
                                    <th style="padding: 15px 12px; text-align: left; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;">Company</th>
                                    <th style="padding: 15px 12px; text-align: left; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;">Change</th>
                                    <th style="padding: 15px 12px; text-align: left; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;">Coverage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {alerts_html}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Call to Action -->
                <div style="padding: 30px; background-color: #f8f9fa; text-align: center;">
                    <h3 style="color: #2c3e50; margin: 0 0 15px; font-size: 18px;">📈 View Full Interactive Report</h3>
                    <a href="{github_url}" style="display: inline-block; background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                        Open Tigro Dashboard
                    </a>
                    <p style="margin: 15px 0 0; color: #6c757d; font-size: 14px;">
                        Interactive charts, historical trends, and detailed analysis for all {stats['total_stocks']} stocks
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="padding: 20px; text-align: center; border-top: 1px solid #e9ecef; color: #6c757d; font-size: 12px;">
                    <p style="margin: 0;">Automated by Tigro Sentiment Analysis Pipeline</p>
                    <p style="margin: 5px 0 0;">Powered by FinBERT • Data from Finnhub</p>
                </div>
                
            </div>
            
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(self, summary_df: pd.DataFrame, test_mode: bool = True) -> bool:
        """Send the sentiment report email"""
        try:
            # Generate email content
            html_content = self.generate_html_email(summary_df)
            alerts = self.extract_declining_stocks(summary_df)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['email_address']}>"
            msg['To'] = self.config['recipient_email']
            
            # Create subject with alert count
            alert_count = len(alerts)
            if alert_count > 0:
                subject = f"{self.config['subject_prefix']} - {datetime.now().strftime('%B %d, %Y')} - 🚨 {alert_count} Declining Stock{'s' if alert_count != 1 else ''}"
            else:
                subject = f"{self.config['subject_prefix']} - {datetime.now().strftime('%B %d, %Y')} - ✅ All Clear"
            
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            if test_mode:
                self.logger.info("🧪 TEST MODE: Email content generated successfully")
                self.logger.info(f"Subject: {subject}")
                self.logger.info(f"Recipient: {self.config['recipient_email']}")
                self.logger.info(f"Alerts found: {alert_count}")
                
                # Save email to file for review
                test_file = Path('results/test_email.html')
                with open(test_file, 'w') as f:
                    f.write(html_content)
                self.logger.info(f"Email preview saved to: {test_file}")
                return True
            
            # Send actual email
            self.logger.info("Connecting to Gmail SMTP...")
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_address'], self.config['app_password'])
            
            # Send message
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"✅ Email sent successfully to {self.config['recipient_email']}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Alerts included: {alert_count}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending email: {e}")
            return False

def main():
    """Test function for email sender"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test with current sentiment data
    try:
        sender = SentimentEmailSender()
        
        # Load current sentiment data
        results_dir = Path('results')
        sentiment_file = results_dir / 'sentiment_summary_latest.csv'
        
        if not sentiment_file.exists():
            print("❌ No sentiment data found. Run sentiment analysis first.")
            return
        
        df = pd.read_csv(sentiment_file)
        print(f"📊 Loaded sentiment data for {len(df)} stocks")
        
        # Send test email
        success = sender.send_email(df, test_mode=True)
        
        if success:
            print("✅ Email test completed successfully!")
        else:
            print("❌ Email test failed!")
            
    except Exception as e:
        print(f"❌ Error during email test: {e}")

if __name__ == "__main__":
    main() 