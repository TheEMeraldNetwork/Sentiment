#!/usr/bin/env python3
"""
FINANCIAL AUDIT REVIEW - Senior Quantitative Finance Perspective
Reviewing Tigro Portfolio Analysis for Mathematical Rigor
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

class FinancialAuditReviewer:
    """Rigorous financial audit of portfolio analysis"""
    
    def __init__(self):
        self.audit_results = []
        self.critical_issues = []
        self.risk_free_rate = None  # Must be calculated from real data
        
    def audit_issue(self, category, severity, description, recommendation):
        """Log audit issues"""
        self.audit_results.append({
            'category': category,
            'severity': severity,
            'description': description,
            'recommendation': recommendation
        })
        
        if severity == "CRITICAL":
            self.critical_issues.append(description)
    
    def review_portfolio_calculations(self):
        """Audit portfolio return calculations"""
        print("🔍 AUDITING PORTFOLIO CALCULATIONS")
        print("="*60)
        
        # Check if portfolio return is mathematically derived
        try:
            df = pd.read_csv('actual-portfolio-master.csv', sep=';', skiprows=2, nrows=14)
            
            # Check the "Totale" row calculation
            total_row = None
            for _, row in df.iterrows():
                if pd.notna(row.get('Simbolo')) and row['Simbolo'] == 'Totale':
                    total_row = row
                    break
            
            if total_row is not None:
                portfolio_return = float(str(total_row['Var%']).replace(',', '.'))
                print(f"✅ Portfolio return extracted from source: {portfolio_return:.2f}%")
                
                # Verify this matches mathematical calculation
                total_current = 0
                total_cost = 0
                
                for _, row in df.iterrows():
                    if pd.notna(row.get('Simbolo')) and row['Simbolo'] != 'Totale':
                        current_val = float(str(row['Valore di mercato €']).replace(',', '.').replace('.', ''))
                        cost_val = float(str(row['Valore di carico']).replace(',', '.').replace('.', ''))
                        total_current += current_val
                        total_cost += cost_val
                
                calculated_return = ((total_current - total_cost) / total_cost) * 100
                
                if abs(calculated_return - portfolio_return) < 0.01:
                    print(f"✅ Mathematical verification: {calculated_return:.2f}% matches source")
                else:
                    self.audit_issue("CALCULATION", "CRITICAL", 
                                   f"Portfolio return mismatch: Source {portfolio_return:.2f}% vs Calculated {calculated_return:.2f}%",
                                   "Recalculate portfolio returns using proper mathematical formula")
            else:
                self.audit_issue("DATA", "CRITICAL", 
                               "Cannot find 'Totale' row in portfolio data",
                               "Ensure portfolio data contains proper totals row")
                
        except Exception as e:
            self.audit_issue("DATA", "CRITICAL", f"Portfolio data loading error: {e}", "Fix data loading issues")
    
    def review_risk_free_rate(self):
        """Audit risk-free rate assumption"""
        print("\n🔍 AUDITING RISK-FREE RATE")
        print("="*40)
        
        # CRITICAL: Risk-free rate was hardcoded as 5%
        self.audit_issue("ASSUMPTION", "CRITICAL", 
                        "Risk-free rate hardcoded as 5% without market data justification",
                        "Fetch current risk-free rate from Federal Reserve or Treasury data")
        
        # Get current risk-free rate
        try:
            # Fetch 3-month Treasury rate as proxy
            treasury = yf.Ticker("^IRX")
            hist = treasury.history(period="5d")
            if not hist.empty:
                current_rf_rate = hist['Close'].iloc[-1] / 100  # Convert percentage
                print(f"📊 Current 3-month Treasury rate: {current_rf_rate:.3f}")
                self.risk_free_rate = current_rf_rate
            else:
                print("⚠️ Could not fetch Treasury rate")
                self.risk_free_rate = 0.05  # Fallback
        except:
            print("⚠️ Error fetching risk-free rate")
            self.risk_free_rate = 0.05
    
    def review_sharpe_calculations(self):
        """Audit Sharpe ratio calculations"""
        print("\n🔍 AUDITING SHARPE RATIO CALCULATIONS") 
        print("="*45)
        
        # CRITICAL: Sharpe ratios in KPI table were estimated, not calculated
        self.audit_issue("CALCULATION", "CRITICAL",
                        "Sharpe ratios marked as 'estimated' rather than calculated from real data",
                        "Calculate Sharpe ratios using: (Portfolio Return - Risk Free Rate) / Portfolio Standard Deviation")
        
        # CRITICAL: Portfolio volatility not properly calculated
        self.audit_issue("CALCULATION", "CRITICAL",
                        "Portfolio volatility not calculated using covariance matrix",
                        "Implement proper portfolio volatility: sqrt(w^T * Σ * w) where Σ is covariance matrix")
    
    def review_forward_projections(self):
        """Audit forward-looking projections"""
        print("\n🔍 AUDITING FORWARD PROJECTIONS")
        print("="*40)
        
        # CRITICAL: Projections were simplified estimates
        self.audit_issue("METHODOLOGY", "CRITICAL",
                        "Forward projections used simple linear scaling rather than proper time-series models",
                        "Implement proper forecasting: Monte Carlo, GARCH, or mean-reversion models")
        
        # CRITICAL: No confidence intervals based on statistical models
        self.audit_issue("STATISTICS", "HIGH",
                        "Confidence intervals not derived from proper statistical distributions",
                        "Calculate confidence intervals using t-distribution or bootstrap methods")
    
    def review_portfolio_optimization(self):
        """Audit portfolio optimization methodology"""
        print("\n🔍 AUDITING PORTFOLIO OPTIMIZATION")
        print("="*42)
        
        # CRITICAL: No proper Markowitz optimization
        self.audit_issue("METHODOLOGY", "CRITICAL",
                        "Portfolio recommendations not based on Modern Portfolio Theory optimization",
                        "Implement Markowitz mean-variance optimization with proper constraints")
        
        # CRITICAL: Target return achievement not mathematically proven
        self.audit_issue("CALCULATION", "CRITICAL",
                        "Target return of 6.80% not derived from mathematical optimization",
                        "Use quadratic programming to find optimal weights for target return")
        
        # HIGH: Sentiment integration not quantitatively modeled
        self.audit_issue("METHODOLOGY", "HIGH",
                        "Sentiment scores integrated qualitatively rather than as quantitative factor",
                        "Model sentiment as additional risk factor in covariance matrix")
    
    def review_position_sizing(self):
        """Audit position sizing methodology"""
        print("\n🔍 AUDITING POSITION SIZING")
        print("="*35)
        
        # MEDIUM: Position sizes based on fixed dollar amounts
        self.audit_issue("METHODOLOGY", "MEDIUM",
                        "Position sizes based on fixed $2K rather than risk-based sizing",
                        "Implement risk parity or Kelly criterion for optimal position sizing")
        
        # HIGH: No correlation adjustment in position sizing
        self.audit_issue("RISK", "HIGH",
                        "Position sizes don't account for correlation between assets",
                        "Adjust position sizes based on correlation matrix and risk contributions")
    
    def check_hardcoded_values(self):
        """Identify all hardcoded values in the system"""
        print("\n🔍 IDENTIFYING HARDCODED VALUES")
        print("="*38)
        
        hardcoded_values = [
            ("Risk-free rate", "5%", "Should fetch from market data"),
            ("Standard position size", "$2K", "Could be risk-based"),
            ("Stop loss percentage", "8%", "Could be volatility-based"),
            ("Target return improvement", "+2pp", "User specified - acceptable"),
            ("Sharpe ratio estimates", "0.66, 0.75", "Must be calculated"),
            ("Forward projection ranges", "±5%, ±8%", "Should be statistical"),
            ("Sector concentration limit", "40%", "User specified - acceptable")
        ]
        
        for value, amount, recommendation in hardcoded_values:
            severity = "HIGH" if "calculated" in recommendation or "fetch" in recommendation else "MEDIUM"
            self.audit_issue("HARDCODING", severity, f"{value}: {amount}", recommendation)
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("📋 FINANCIAL AUDIT REPORT - MATHEMATICAL RIGOR REVIEW")
        print("="*80)
        
        # Count issues by severity
        critical_count = len([a for a in self.audit_results if a['severity'] == 'CRITICAL'])
        high_count = len([a for a in self.audit_results if a['severity'] == 'HIGH'])
        medium_count = len([a for a in self.audit_results if a['severity'] == 'MEDIUM'])
        
        print(f"\n📊 AUDIT SUMMARY:")
        print(f"   🔴 CRITICAL Issues: {critical_count}")
        print(f"   🟠 HIGH Issues: {high_count}")
        print(f"   🟡 MEDIUM Issues: {medium_count}")
        print(f"   📋 Total Issues: {len(self.audit_results)}")
        
        if critical_count > 0:
            print(f"\n🚨 CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION:")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        print(f"\n📋 DETAILED AUDIT FINDINGS:")
        for category in ['CRITICAL', 'HIGH', 'MEDIUM']:
            category_issues = [a for a in self.audit_results if a['severity'] == category]
            if category_issues:
                print(f"\n{category} SEVERITY ({len(category_issues)} issues):")
                for i, issue in enumerate(category_issues, 1):
                    print(f"   {i}. [{issue['category']}] {issue['description']}")
                    print(f"      → Recommendation: {issue['recommendation']}")
        
        print(f"\n💡 AUDIT CONCLUSION:")
        if critical_count > 0:
            print("   ❌ ANALYSIS FAILS MATHEMATICAL RIGOR STANDARDS")
            print("   🔧 REQUIRES SUBSTANTIAL REWORK BEFORE USE")
        elif high_count > 3:
            print("   ⚠️ ANALYSIS HAS SIGNIFICANT METHODOLOGICAL GAPS")
            print("   🔧 REQUIRES MAJOR IMPROVEMENTS")
        else:
            print("   ✅ ANALYSIS MEETS BASIC STANDARDS WITH MINOR IMPROVEMENTS NEEDED")
        
        return {
            'total_issues': len(self.audit_results),
            'critical_issues': critical_count,
            'high_issues': high_count,
            'medium_issues': medium_count,
            'audit_results': self.audit_results
        }

def main():
    """Run comprehensive financial audit"""
    print("🔍 FINANCIAL AUDIT REVIEW - MATHEMATICAL RIGOR CHECK")
    print("=" * 60)
    print("Reviewer: Senior Quantitative Finance Specialist")
    print("Scope: Tigro Portfolio Analysis Mathematical Foundations")
    print("=" * 60)
    
    auditor = FinancialAuditReviewer()
    
    # Run all audit checks
    auditor.review_portfolio_calculations()
    auditor.review_risk_free_rate()
    auditor.review_sharpe_calculations()
    auditor.review_forward_projections()
    auditor.review_portfolio_optimization()
    auditor.review_position_sizing()
    auditor.check_hardcoded_values()
    
    # Generate final report
    audit_summary = auditor.generate_audit_report()
    
    return audit_summary

if __name__ == "__main__":
    audit_results = main() 