"""
Script to open the sentiment analysis HTML report in the default browser.
"""

import os
import webbrowser
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

def generate_html():
    """Generate HTML report from master output data"""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Read the master output
    df = pd.read_csv(project_root / 'results/d_master_output.csv')
    
    # Sort by 30-day sentiment to identify top/bottom stocks
    df['rank'] = df['sent_30d'].rank(method='min', ascending=False)
    total_stocks = len(df[df['sent_30d'].notna()])
    
    # Create row color coding function
    def get_row_color(rank):
        if pd.isna(rank):
            return ''
        if rank <= 10:
            return 'background-color: #e6ffe6;'  # Light green
        if rank > total_stocks - 10:
            return 'background-color: #ffe6e6;'  # Light red
        return ''

    def format_sentiment(value):
        if pd.isna(value):
            return ''
        return f"{value:.2f}"

    def get_trend_symbol(value):
        """Get trend symbol for sentiment value"""
        if pd.isna(value) or value == 'NEW':
            return ' N'  # New
        elif value == 'HIGHER':
            return ' U'  # Up
        elif value == 'LOWER':
            return ' D'  # Down
        return ' S'  # Stable

    # Generate HTML
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment Analysis Report</title>
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .dataTables_wrapper { margin-top: 20px; }
            th { 
                position: sticky; 
                top: 0; 
                background: white;
                z-index: 10;
            }
            .dataTables_filter { margin-bottom: 10px; }
            .sentiment-table { width: 100%; }
            tr:hover { background-color: #f5f5f5 !important; }
            .top-10:hover { background-color: #d6ffd6 !important; }
            .bottom-10:hover { background-color: #ffd6d6 !important; }
            .header-section {
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .legend span {
                padding: 2px 8px;
                margin-right: 10px;
                border-radius: 3px;
            }
            .refresh-btn {
                padding: 5px 10px;
                cursor: pointer;
                border-radius: 3px;
                border: 1px solid #ddd;
                background: white;
            }
            .refresh-btn:hover {
                background: #f5f5f5;
            }
        </style>
    </head>
    <body>
        <div class="header-section">
            <h2>Sentiment Analysis Report</h2>
            <div>
                <span>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                <button class="refresh-btn" onclick="window.location.reload()">Refresh</button>
            </div>
        </div>
        
        <div class="legend">
            <span style="background: #e6ffe6;">Top 10 Sentiment</span>
            <span style="background: #ffe6e6;">Bottom 10 Sentiment</span>
        </div>

        <table id="sentiment-table" class="display">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Last Week</th>
                    <th>15 Day</th>
                    <th>Last Month</th>
                    <th>Articles</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add rows
    for _, row in df.iterrows():
        row_style = get_row_color(row['rank'])
        
        # Get trend symbols if columns exist
        week_trend = get_trend_symbol(row.get('trend_7d', ''))
        day15_trend = get_trend_symbol(row.get('trend_15d', ''))
        month_trend = get_trend_symbol(row.get('trend_30d', ''))
        
        html_template += f"""
            <tr style="{row_style}">
                <td>{row['ticker']}</td>
                <td>{row['company']}</td>
                <td>{format_sentiment(row['sent_7d'])}{week_trend}</td>
                <td>{format_sentiment(row['sent_15d'])}{day15_trend}</td>
                <td>{format_sentiment(row['sent_30d'])}{month_trend}</td>
                <td>{int(row['articles_30d']) if pd.notna(row['articles_30d']) else ''}</td>
            </tr>
        """

    html_template += """
            </tbody>
        </table>
        <script>
            $(document).ready(function() {
                $('#sentiment-table').DataTable({
                    order: [[4, 'desc']],  // Sort by last month sentiment by default
                    pageLength: 25,
                    fixedHeader: true,
                    scrollY: '70vh',
                    scrollCollapse: true,
                    keys: true,  // Enable keyboard navigation
                    initComplete: function() {
                        // Focus search box with Ctrl+F
                        $(document).keydown(function(e) {
                            if (e.ctrlKey && e.keyCode == 70) {
                                e.preventDefault();
                                $('.dataTables_filter input').focus();
                            }
                        });
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    output_path = project_root / 'results/sentiment_report.html'
    with open(output_path, 'w') as f:
        f.write(html_template)
    
    return output_path

def open_report():
    """Generate and open the HTML report in default browser"""
    try:
        html_path = generate_html()
        webbrowser.open(f'file://{html_path.absolute()}')
        print(f"\nOpened sentiment report: {html_path}")
        return True
    except Exception as e:
        print(f"\nError opening sentiment report: {e}")
        return False

if __name__ == "__main__":
    open_report() 