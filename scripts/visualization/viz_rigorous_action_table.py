#!/usr/bin/env python3
"""
Rigorous Action Table Generator - Component F2
Creates final HTML action table with all portfolio recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional

# Import our rigorous components
from optimization.opt_rigorous_portfolio_master import RigorousPortfolioOptimizer
from optimization.opt_position_sizer import PositionSizer

class RigorousActionTableGenerator:
    """Generate comprehensive HTML action table with all recommendations"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize action table generator"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Initialize components
        self.optimizer = RigorousPortfolioOptimizer(log_level)
        self.position_sizer = PositionSizer(log_level)
    
    def run_complete_analysis(self, include_universe: bool = False) -> Dict:
        """
        Run complete portfolio analysis and optimization
        
        Args:
            include_universe: Whether to include universe stocks
            
        Returns:
            Complete analysis results
        """
        self.logger.info("🚀 Running complete portfolio analysis")
        
        # Step 1: Run optimization
        opt_results = self.optimizer.optimize_portfolio(include_universe)
        
        if not opt_results['success']:
            return opt_results
        
        # Step 2: Load current positions
        current_positions = self.position_sizer.load_current_positions()
        
        if not current_positions:
            return {'success': False, 'message': 'Failed to load current positions'}
        
        # Step 3: Calculate position sizing
        sizing_results = self.position_sizer.calculate_target_positions(
            opt_results['optimization_result']['weights'],
            opt_results['market_data'],
            current_positions,
            opt_results['sentiment_data']
        )
        
        # Step 4: Calculate dynamic stop losses
        final_recommendations = self.position_sizer.calculate_dynamic_stop_losses(
            sizing_results['recommendations']
        )
        
        # Step 5: Compile complete results
        complete_results = {
            'success': True,
            'optimization': opt_results,
            'current_positions': current_positions,
            'sizing': sizing_results,
            'recommendations': final_recommendations,
            'action_summary': self.position_sizer.generate_action_summary(final_recommendations),
            'timestamp': datetime.now()
        }
        
        self.logger.info("✅ Complete analysis finished")
        return complete_results
    
    def generate_html_table(self, analysis_results: Dict, filename: str = "rigorous_portfolio_action_table.html") -> str:
        """
        Generate comprehensive HTML action table
        
        Args:
            analysis_results: Complete analysis results
            filename: Output filename
            
        Returns:
            Path to generated HTML file
        """
        if not analysis_results['success']:
            self.logger.error("❌ Cannot generate table: analysis failed")
            return None
        
        # Extract data
        recommendations = analysis_results['recommendations']
        opt_results = analysis_results['optimization']
        sizing_summary = analysis_results['sizing']['portfolio_summary']
        action_summary = analysis_results['action_summary']
        
        # Generate HTML
        html_content = self._generate_html_content(
            recommendations, opt_results, sizing_summary, action_summary
        )
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"✅ HTML table generated: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Failed to write HTML file: {e}")
            return None
    
    def _generate_html_content(self, recommendations: Dict, opt_results: Dict, 
                              sizing_summary: Dict, action_summary: Dict) -> str:
        """Generate the complete HTML content"""
        
        # Calculate cash status for display
        # Net cash position represents cash outflow (positive = cash going out)
        net_cash = sizing_summary['net_cash_used']
        available_cash = sizing_summary['new_cash_usd']
        
        # Status is green if net cash outflow is within available cash
        if abs(net_cash) <= available_cash:
            cash_status_class = "positive"
            cash_status_icon = "✅"
        else:
            cash_status_class = "negative" 
            cash_status_icon = "❌"
        
        # Header and CSS
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐅 TIGRO Rigorous Portfolio Action Table</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .header {{
            text-align: center;
            background: #2a2a2a;
            color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid #404040;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: #2a2a2a;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border-left: 5px solid #666666;
            text-align: center;
            border: 1px solid #404040;
        }}
        
        .kpi-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #ffffff;
            margin: 0;
        }}
        
        .kpi-label {{
            color: #b0b0b0;
            font-size: 0.9em;
            margin: 5px 0 0 0;
        }}
        
        .kpi-improvement {{
            color: #4CAF50;
            font-size: 0.8em;
            margin: 5px 0 0 0;
        }}
        
        .action-summary {{
            background: #2a2a2a;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            border: 1px solid #404040;
        }}
        
        .action-summary h2 {{
            margin-top: 0;
            color: #ffffff;
            border-bottom: 2px solid #666666;
            padding-bottom: 10px;
        }}
        
        .cash-flow-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .cash-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #404040;
            border-radius: 8px;
            border: 1px solid #505050;
        }}
        
        .cash-item.total {{
            grid-column: 1 / -1;
            background: #333333;
            border: 2px solid #666666;
            font-size: 1.1em;
        }}
        
        .cash-label {{
            color: #b0b0b0;
            font-weight: 500;
        }}
        
        .cash-value {{
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .cash-value.positive {{
            color: #4CAF50;
        }}
        
        .cash-value.negative {{
            color: #F44336;
        }}
        
        .action-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .action-item {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }}
        
        .action-buy {{ background: #d4edda; color: #155724; }}
        .action-add {{ background: #cce7ff; color: #004085; }}
        .action-hold {{ background: #f8f9fa; color: #495057; }}
        .action-trim {{ background: #fff3cd; color: #856404; }}
        .action-sell {{ background: #f8d7da; color: #721c24; }}
        
        .main-table {{
            background: #2a2a2a;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #404040;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th {{
            background: #404040;
            color: #ffffff;
            padding: 15px 10px;
            text-align: center;
            font-weight: bold;
            border-bottom: 2px solid #666666;
            position: sticky;
            top: 0;
            z-index: 10;
            cursor: pointer;
            user-select: none;
            transition: background-color 0.2s;
        }}
        
        th:hover {{
            background: #505050;
        }}
        
        th::after {{
            content: ' ↕️';
            font-size: 0.8em;
            opacity: 0.7;
        }}
        
        th.sort-asc::after {{
            content: ' ↑';
            color: #ffd700;
        }}
        
        th.sort-desc::after {{
            content: ' ↓';
            color: #ffd700;
        }}
        
        td {{
            padding: 12px 10px;
            text-align: center;
            border-bottom: 1px solid #404040;
            color: #e0e0e0;
        }}
        
        tr:nth-child(even) {{
            background: #333333;
        }}
        
        tr:hover {{
            background: #404040;
        }}
        
        .stock-info {{
            text-align: left;
            font-weight: bold;
            color: #ffffff;
        }}
        
        .stock-name {{
            font-size: 0.85em;
            color: #b0b0b0;
            font-weight: normal;
        }}
        
        .action-buy-cell {{ color: #4CAF50; font-weight: bold; }}
        .action-add-cell {{ color: #2196F3; font-weight: bold; }}
        .action-hold-cell {{ color: #9E9E9E; font-weight: bold; }}
        .action-trim-cell {{ color: #FF9800; font-weight: bold; }}
        .action-sell-cell {{ color: #F44336; font-weight: bold; }}
        
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .neutral {{ color: #95a5a6; }}
        
        .footer {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            color: #666;
        }}
        
        .methodology {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #17a2b8;
        }}
        
        .methodology h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        
        @media (max-width: 768px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            
            .action-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            table {{
                font-size: 12px;
            }}
            
            th, td {{
                padding: 8px 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐅 TIGRO</h1>
    </div>
    
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{opt_results['optimization_result']['portfolio_return']:.1%}</div>
            <div class="kpi-label">Expected Return</div>
            <div class="kpi-improvement">+{opt_results['target_achieved']['return_improvement']:.1%} vs current</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{opt_results['optimization_result']['portfolio_volatility']:.1%}</div>
            <div class="kpi-label">Portfolio Volatility</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{opt_results['sharpe_ratio']:.3f}</div>
            <div class="kpi-label">Sharpe Ratio</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{opt_results['var_97']:.2%}</div>
            <div class="kpi-label">97% VaR</div>
        </div>
    </div>
    
    <div class="action-summary">
        <h2>💰 Cash Position Summary</h2>
        <div class="cash-flow-container">
            <div class="cash-item">
                <span class="cash-label">New Cash Available:</span>
                <span class="cash-value positive">${sizing_summary['new_cash_usd']:,.0f}</span>
            </div>
            <div class="cash-item">
                <span class="cash-label">Cash from Trim:</span>
                <span class="cash-value positive">${sizing_summary.get('trim_proceeds', 0):,.0f}</span>
            </div>
            <div class="cash-item">
                <span class="cash-label">Cash from Sell:</span>
                <span class="cash-value positive">${sizing_summary.get('sell_proceeds', 0):,.0f}</span>
            </div>
            <div class="cash-item">
                <span class="cash-label">Total Purchases:</span>
                <span class="cash-value negative">-${sizing_summary.get('total_purchases', 0):,.0f}</span>
            </div>
            <div class="cash-item total">
                <span class="cash-label"><strong>Net Cash Position:</strong></span>
                <span class="cash-value {cash_status_class}">-${sizing_summary['net_cash_used']:,.0f} {cash_status_icon}</span>
            </div>
        </div>
    </div>
    
    <div class="main-table">
        <table id="portfolioTable">
            <thead>
                <tr>
                    <th data-column="stock">Stock</th>
                    <th data-column="current_shares">Current<br>Shares</th>
                    <th data-column="action">Action</th>
                    <th data-column="target_shares">Target<br>Shares</th>
                    <th data-column="shares_change">Shares<br>Change</th>
                    <th data-column="current_weight">Current<br>Weight</th>
                    <th data-column="target_weight">Target<br>Weight</th>
                    <th data-column="value_change">Value<br>Change ($)</th>
                    <th data-column="sentiment">Monthly<br>Sentiment</th>
                    <th data-column="trend">Sentiment<br>Trend</th>
                    <th data-column="stop_loss">Stop Loss<br>Price ($)</th>
                    <th data-column="stop_recommendation">Stop Loss<br>Recommendation</th>
                    <th data-column="rationale">AI Analysis</th>
                </tr>
            </thead>
            <tbody>"""
        
        # Add table rows
        sentiment_data = opt_results.get('sentiment_data', {})
        
        for symbol, rec in recommendations.items():
            # Get sentiment info
            sentiment_info = sentiment_data.get(symbol, {'sentiment_score': 0.0, 'trend': 'neutral'})
            sentiment_score = sentiment_info['sentiment_score']
            sentiment_trend = sentiment_info['trend']
            
            # Format sentiment display - ALWAYS show the actual value
            if sentiment_score > 0.05:
                sentiment_display = f"+{sentiment_score:.3f}"
                sentiment_class = "positive"
            elif sentiment_score < -0.05:
                sentiment_display = f"{sentiment_score:.3f}"
                sentiment_class = "negative"
            else:
                sentiment_display = f"{sentiment_score:.3f}"
                sentiment_class = "neutral"
            
            # Format trend
            trend_emoji = {
                'improving': '📈',
                'declining': '📉',
                'stable': '→',
                'neutral': '→'
            }.get(sentiment_trend, '→')
            
            # Format numbers
            shares_change = rec['shares_change']
            shares_change_display = f"+{shares_change:.1f}" if shares_change > 0 else f"{shares_change:.1f}"
            
            value_change = rec['value_change_usd']
            value_change_display = f"+${value_change:,.0f}" if value_change > 0 else f"-${abs(value_change):,.0f}"
            value_change_class = "positive" if value_change > 0 else "negative" if value_change < 0 else "neutral"
            
            # Generate stop loss recommendation
            stop_loss_pct = rec.get('stop_loss_pct', 0.08)
            if rec['action'] in ['HOLD', 'ADD', 'TRIM'] and rec['current_shares'] > 0:
                if stop_loss_pct > 0.10:
                    stop_recommendation = f"🔴 Tight stop at -{stop_loss_pct:.1%} (high vol)"
                elif stop_loss_pct > 0.08:
                    stop_recommendation = f"🟡 Standard stop at -{stop_loss_pct:.1%}"
                else:
                    stop_recommendation = f"🟢 Conservative stop at -{stop_loss_pct:.1%}"
            elif rec['action'] == 'BUY':
                stop_recommendation = f"🟢 Set stop at -{stop_loss_pct:.1%} after purchase"
            else:
                stop_recommendation = "— Not applicable"
            
            html += f"""
                <tr data-symbol="{symbol}">
                    <td class="stock-info">
                        <strong>{symbol}</strong><br>
                        <span class="stock-name">{rec['name']}</span>
                    </td>
                    <td data-value="{rec['current_shares']}">{rec['current_shares']:.1f}</td>
                    <td class="action-{rec['action'].lower()}-cell" data-value="{rec['action']}">{rec['action']}</td>
                    <td data-value="{rec['target_shares']}">{rec['target_shares']:.1f}</td>
                    <td data-value="{rec['shares_change']}">{shares_change_display}</td>
                    <td data-value="{rec['current_weight']}">{rec['current_weight']:.1%}</td>
                    <td data-value="{rec['target_weight']}">{rec['target_weight']:.1%}</td>
                    <td class="{value_change_class}" data-value="{rec['value_change_usd']}">{value_change_display}</td>
                    <td class="{sentiment_class}" data-value="{sentiment_score}">{sentiment_display}</td>
                    <td data-value="{sentiment_trend}">{trend_emoji} {sentiment_trend.title()}</td>
                    <td data-value="{rec['final_stop_price']}">${rec['final_stop_price']:.2f}</td>
                    <td style="font-size: 12px;" data-value="{stop_loss_pct}">{stop_recommendation}</td>
                    <td style="text-align: left; font-size: 12px;" data-value="{rec['rationale']}">{rec['rationale']}</td>
                </tr>"""
        
        html += f"""
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <div class="methodology">
            <h3>🔬 Methodology</h3>
            <p><strong>Mathematical Foundation:</strong> Markowitz mean-variance optimization with quadratic programming</p>
            <p><strong>Risk-Free Rate:</strong> {opt_results['risk_free_rate']:.3%} (3-month Treasury from yfinance)</p>
            <p><strong>Historical Data:</strong> 2 years of daily returns for covariance matrix calculation</p>
            <p><strong>Sentiment Integration:</strong> 80% financial metrics + 20% FinBERT sentiment analysis</p>
            <p><strong>Constraints:</strong> 20% max individual position, 40% max sector concentration</p>
            <p><strong>Target:</strong> 7% expected return, 20% volatility, 97% VaR optimization</p>
        </div>
        
        <p style="margin-top: 30px;">
            <strong>🐅 TIGRO Portfolio Optimization System</strong><br>
            Advanced Portfolio Management with AI-Powered Sentiment Analysis<br>
            <em>Where Mathematical Rigor Meets Modern AI</em>
        </p>
    </div>
    
    <script>
        // Sortable table functionality
        class SortableTable {{
            constructor(tableId) {{
                this.table = document.getElementById(tableId);
                this.headers = this.table.querySelectorAll('th[data-column]');
                this.tbody = this.table.querySelector('tbody');
                this.rows = Array.from(this.tbody.querySelectorAll('tr'));
                this.currentSort = {{ column: null, direction: 'asc' }};
                
                this.init();
            }}
            
            init() {{
                this.headers.forEach(header => {{
                    header.addEventListener('click', () => {{
                        const column = header.dataset.column;
                        this.sort(column, header);
                    }});
                }});
                
                // Add row interactions
                this.addRowInteractions();
            }}
            
            sort(column, header) {{
                const direction = this.currentSort.column === column && this.currentSort.direction === 'asc' ? 'desc' : 'asc';
                
                // Update header classes
                this.headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                header.classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');
                
                // Sort rows
                this.rows.sort((a, b) => {{
                    const aValue = this.getCellValue(a, column);
                    const bValue = this.getCellValue(b, column);
                    
                    if (aValue === bValue) return 0;
                    
                    const result = aValue > bValue ? 1 : -1;
                    return direction === 'asc' ? result : -result;
                }});
                
                // Re-append sorted rows
                this.rows.forEach(row => this.tbody.appendChild(row));
                
                // Update current sort
                this.currentSort = {{ column, direction }};
            }}
            
            getCellValue(row, column) {{
                const cell = row.querySelector(`td[data-value]`);
                const index = Array.from(this.headers).findIndex(h => h.dataset.column === column);
                const targetCell = row.cells[index];
                
                if (targetCell && targetCell.dataset.value !== undefined) {{
                    const value = targetCell.dataset.value;
                    
                    // Try to convert to number if possible
                    const numValue = parseFloat(value);
                    if (!isNaN(numValue)) {{
                        return numValue;
                    }}
                    
                    return value.toLowerCase();
                }}
                
                return targetCell ? targetCell.textContent.toLowerCase() : '';
            }}
            
            addRowInteractions() {{
                this.rows.forEach(row => {{
                    row.addEventListener('mouseenter', function() {{
                        this.style.transform = 'scale(1.01)';
                        this.style.transition = 'transform 0.2s ease';
                        this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                    }});
                    
                    row.addEventListener('mouseleave', function() {{
                        this.style.transform = 'scale(1)';
                        this.style.boxShadow = 'none';
                    }});
                    
                    row.addEventListener('click', function() {{
                        const symbol = this.dataset.symbol;
                        const action = this.querySelector('[class*="action-"][class*="-cell"]').textContent;
                        const rationale = this.cells[this.cells.length - 1].textContent;
                        
                        alert(`🐅 TIGRO Recommendation\\n\\nStock: ${{symbol}}\\nAction: ${{action}}\\n\\nAnalysis: ${{rationale}}\\n\\nClick OK to continue.`);
                    }});
                }});
            }}
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            new SortableTable('portfolioTable');
            
            // Add some visual feedback
            console.log('🐅 TIGRO Portfolio Table loaded - Click column headers to sort!');
            
            // Auto-sort by action initially to group recommendations
            setTimeout(() => {{
                const actionHeader = document.querySelector('th[data-column="action"]');
                if (actionHeader) {{
                    actionHeader.click();
                }}
            }}, 500);
        }});
    </script>
</body>
</html>"""
        
        return html

def main():
    """Generate rigorous portfolio action table"""
    print("📊 RIGOROUS ACTION TABLE GENERATOR")
    print("=" * 60)
    
    # Initialize generator
    generator = RigorousActionTableGenerator()
    
    # Run complete analysis
    print("🚀 Running complete portfolio analysis...")
    results = generator.run_complete_analysis(include_universe=False)
    
    if results['success']:
        print("✅ Analysis completed successfully")
        
        # Generate HTML table
        print("🎨 Generating HTML action table...")
        filename = generator.generate_html_table(results)
        
        if filename:
            print(f"✅ HTML table generated: {filename}")
            
            # Open in browser
            try:
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(filename)}')
                print("🌐 Opened in default browser")
            except:
                print("ℹ️ Open the HTML file manually in your browser")
        
        return results
    
    else:
        print(f"❌ Analysis failed: {results['message']}")
        return None

if __name__ == "__main__":
    main() 