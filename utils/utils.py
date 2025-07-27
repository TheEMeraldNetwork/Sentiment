import yfinance as yf
import re
import pandas as pd
from typing import Optional
import sys
import os
from pathlib import Path

# Load master ticker mappings
MASTER_MAPPINGS_PATH = Path(__file__).parent / "master name ticker.csv"
MASTER_MAPPINGS = {}

try:
    master_df = pd.read_csv(MASTER_MAPPINGS_PATH)
    # Create mapping from company name to ticker
    MASTER_MAPPINGS = dict(zip(master_df['Name'].str.upper(), master_df['Ticker']))
    print(f"Loaded {len(MASTER_MAPPINGS)} ticker mappings from master file")
except Exception as e:
    print(f"Warning: Could not load master ticker mappings: {str(e)}")

def clean_company_name(name: str) -> str:
    """Clean company name for better matching"""
    if not name:
        return ""
    # Remove special characters and extra spaces
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.upper()  # Convert to uppercase for matching
    
    # Remove common suffixes
    suffixes = [
        '-A', 'RG-A', 'CV-A', 'ADR', 'HOLD', 'INC', 'PLC', 'LTD', 
        'TECH', 'GROUP', 'COM', 'RG', 'SP ADS', 'TU'
    ]
    for suffix in suffixes:
        name = re.sub(f'{suffix}$', '', name, flags=re.IGNORECASE)
    
    return name.strip()

def get_ticker_symbol(isin: str, company_name: str) -> Optional[str]:
    """Get ticker symbol using master mappings"""
    # Clean the company name
    cleaned_name = clean_company_name(company_name)
    
    print(f"\nDEBUG: Looking for match for: {company_name}")
    print(f"DEBUG: Cleaned name: {cleaned_name}")
    
    # Try exact match first
    if company_name.upper() in MASTER_MAPPINGS:
        ticker = MASTER_MAPPINGS[company_name.upper()]
        print(f"DEBUG: Found exact match -> {ticker}")
        return ticker
    else:
        print("DEBUG: No exact match found")
    
    # Try cleaned name match
    print("\nDEBUG: Trying cleaned name matches...")
    for master_name, ticker in MASTER_MAPPINGS.items():
        master_cleaned = clean_company_name(master_name)
        print(f"DEBUG: Comparing with: {master_name} (cleaned: {master_cleaned})")
        
        if cleaned_name == master_cleaned:
            print(f"DEBUG: Found cleaned match -> {ticker}")
            return ticker
        
        # Try partial match
        if cleaned_name in master_cleaned or master_cleaned in cleaned_name:
            print(f"DEBUG: Found partial match -> {ticker}")
            return ticker
    
    print(f"DEBUG: No matches found for {company_name}")
    return None
