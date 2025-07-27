#!/usr/bin/env python3
"""Debug script to examine portfolio data parsing"""

import pandas as pd

def parse_european_number(value_str):
    """Parse European number format"""
    value_str = str(value_str).strip()
    if value_str == 'nan' or value_str == '':
        return 0.0
    if ',' in value_str and '.' in value_str:
        parts = value_str.split(',')
        if len(parts) == 2:
            integer_part = parts[0].replace('.', '')
            decimal_part = parts[1]
            value_str = integer_part + '.' + decimal_part
    elif ',' in value_str:
        value_str = value_str.replace(',', '.')
    return float(value_str)

def debug_portfolio():
    """Debug portfolio data parsing"""
    print("🔍 Debugging Portfolio Data...")
    
    # Load the CSV and examine structure
    df = pd.read_csv('actual-portfolio-master.csv', sep=';', skiprows=2, nrows=20)
    
    print("\nColumn names:")
    for i, col in enumerate(df.columns):
        print(f"{i}: '{col}'")
    
    print("\nFirst few rows:")
    print(df[['Titolo', 'Simbolo', 'Valore di carico', 'Valore di mercato €', 'Var%']].head())
    
    print("\nChecking each position:")
    total_current_value = 0
    total_cost_basis = 0
    
    for i, row in df.iterrows():
        if pd.notna(row['Simbolo']) and row['Simbolo'] != 'Totale':
            symbol = row['Simbolo'].split('.')[0]
            if symbol.startswith('1'):
                symbol = symbol[1:]
            
            current_value = parse_european_number(row['Valore di mercato €'])
            cost_basis = parse_european_number(row['Valore di carico'])
            return_pct = parse_european_number(row['Var%'])
            
            print(f"{symbol}: Current=€{current_value:,.2f}, Cost=€{cost_basis:,.2f}, Return={return_pct:.2f}%")
            
            total_current_value += current_value
            total_cost_basis += cost_basis
    
    print(f"\nTotals:")
    print(f"Current Value: €{total_current_value:,.2f}")
    print(f"Cost Basis: €{total_cost_basis:,.2f}")
    
    if total_cost_basis > 0:
        overall_return_pct = ((total_current_value - total_cost_basis) / total_cost_basis) * 100
        print(f"Overall Return: {overall_return_pct:.2f}%")
    else:
        print("Error: Zero cost basis!")

if __name__ == "__main__":
    debug_portfolio() 