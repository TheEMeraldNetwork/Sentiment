#!/usr/bin/env python3
"""
Risk-Free Rate Calculator - Component A5
Fetches current Treasury rates from yfinance for Sharpe ratio calculations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class TreasuryRateFetcher:
    """Fetch and calculate risk-free rates from Treasury data"""
    
    def __init__(self, log_level=logging.INFO):
        """Initialize Treasury rate fetcher"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Treasury symbols for different maturities
        self.treasury_symbols = {
            '3M': '^IRX',    # 3-Month Treasury
            '6M': '^FVX',    # 5-Year Treasury (closest to 6M available)
            '1Y': '^TNX',    # 10-Year Treasury (closest to 1Y available)
            '10Y': '^TNX'    # 10-Year Treasury
        }
    
    def fetch_current_treasury_rates(self):
        """
        Fetch current Treasury rates across maturities
        Returns: dict with rates by maturity
        """
        rates = {}
        
        for maturity, symbol in self.treasury_symbols.items():
            try:
                self.logger.info(f"Fetching {maturity} Treasury rate ({symbol})")
                
                # Fetch recent data
                treasury = yf.Ticker(symbol)
                hist = treasury.history(period="5d")
                
                if not hist.empty:
                    current_rate = hist['Close'].iloc[-1] / 100  # Convert percentage to decimal
                    rates[maturity] = current_rate
                    self.logger.info(f"✅ {maturity}: {current_rate:.4f} ({current_rate*100:.2f}%)")
                else:
                    self.logger.warning(f"⚠️ No data for {maturity} Treasury")
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to fetch {maturity} Treasury: {e}")
                
        return rates
    
    def get_risk_free_rate(self, period='3M'):
        """
        Get the appropriate risk-free rate for portfolio calculations
        
        Args:
            period: Maturity period ('3M', '6M', '1Y', '10Y')
            
        Returns:
            float: Risk-free rate as decimal (e.g., 0.042 for 4.2%)
        """
        rates = self.fetch_current_treasury_rates()
        
        if period in rates:
            rf_rate = rates[period]
            self.logger.info(f"📊 Using {period} Treasury rate: {rf_rate:.4f} ({rf_rate*100:.2f}%)")
            return rf_rate
        
        # Fallback hierarchy
        fallback_order = ['3M', '6M', '1Y', '10Y']
        for fallback in fallback_order:
            if fallback in rates:
                rf_rate = rates[fallback]
                self.logger.warning(f"⚠️ Using fallback {fallback} rate: {rf_rate:.4f}")
                return rf_rate
        
        # Ultimate fallback to historical average
        self.logger.error("❌ No Treasury rates available, using historical average")
        return 0.025  # 2.5% historical average
    
    def calculate_average_treasury_rate(self, days=30):
        """
        Calculate average Treasury rate over specified period
        
        Args:
            days: Number of days to average over
            
        Returns:
            float: Average risk-free rate
        """
        try:
            # Use 3-month Treasury for averaging
            treasury = yf.Ticker('^IRX')
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = treasury.history(start=start_date, end=end_date)
            
            if not hist.empty:
                avg_rate = hist['Close'].mean() / 100  # Convert to decimal
                self.logger.info(f"📊 {days}-day average Treasury rate: {avg_rate:.4f} ({avg_rate*100:.2f}%)")
                return avg_rate
            else:
                self.logger.warning("⚠️ No historical Treasury data, using current rate")
                return self.get_risk_free_rate()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate average rate: {e}")
            return self.get_risk_free_rate()
    
    def get_rate_for_timeframe(self, months=12):
        """
        Get appropriate Treasury rate based on investment timeframe
        
        Args:
            months: Investment timeframe in months
            
        Returns:
            float: Most appropriate risk-free rate
        """
        if months <= 3:
            return self.get_risk_free_rate('3M')
        elif months <= 12:
            return self.get_risk_free_rate('1Y')
        else:
            return self.get_risk_free_rate('10Y')

def main():
    """Test Treasury rate fetching"""
    fetcher = TreasuryRateFetcher()
    
    print("🏛️ TREASURY RATE ANALYSIS")
    print("=" * 50)
    
    # Get all current rates
    rates = fetcher.fetch_current_treasury_rates()
    
    # Get risk-free rate for portfolio calculations
    rf_rate = fetcher.get_risk_free_rate('3M')
    print(f"\n📊 Risk-Free Rate for Portfolio: {rf_rate:.4f} ({rf_rate*100:.2f}%)")
    
    # Calculate 30-day average
    avg_rate = fetcher.calculate_average_treasury_rate(30)
    print(f"📈 30-Day Average Rate: {avg_rate:.4f} ({avg_rate*100:.2f}%)")
    
    return rf_rate

if __name__ == "__main__":
    main() 