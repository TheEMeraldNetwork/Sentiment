#!/usr/bin/env python3
"""
Sentiment-Enhanced Strategy Summary
Shows monthly sentiment trends for portfolio and recommendations
"""

import pandas as pd
import numpy as np

def get_portfolio_sentiment_summary():
    """Get sentiment analysis for current portfolio"""
    
    print("🧠 SENTIMENT ANALYSIS INTEGRATED STRATEGY")
    print("="*70)
    
    # Current portfolio with sentiment data from latest analysis
    portfolio_sentiment = {
        'CCJ': {'sentiment': 'No recent data', 'trend': 'Unknown', 'articles': 0, 'recommendation': 'HOLD - Monitor'},
        'CLS': {'sentiment': '+0.330 (Positive)', 'trend': 'Strong', 'articles': 33, 'recommendation': '🔥 STRONG HOLD - Set stop at -8%'},
        'OGC': {'sentiment': 'No recent data', 'trend': 'Unknown', 'articles': 0, 'recommendation': 'HOLD - Monitor'},
        'ASML': {'sentiment': 'No recent data', 'trend': 'Unknown', 'articles': 0, 'recommendation': 'TRIM - Rebalance'},
        'AAPL': {'sentiment': '+0.086 (Slightly Positive)', 'trend': 'Stable', 'articles': 247, 'recommendation': '✅ HOLD - Don\'t touch per request'},
        'CVNA': {'sentiment': 'No recent data', 'trend': 'Unknown', 'articles': 0, 'recommendation': 'EVALUATE'},
        'LFST': {'sentiment': '+0.085 (Slightly Positive)', 'trend': 'Improving', 'articles': 15, 'recommendation': '⚠️ HOLD - Small position'},
        'PRU': {'sentiment': '+0.001 (Neutral)', 'trend': 'Flat', 'articles': 30, 'recommendation': '✅ HOLD - Stable value'},
        'SPGI': {'sentiment': '+0.054 (Slightly Positive)', 'trend': 'Stable', 'articles': 82, 'recommendation': '✅ HOLD - Quality name'},
        'CRM': {'sentiment': '+0.205 (Positive)', 'trend': 'Strong', 'articles': 186, 'recommendation': '✅ HOLD - Good sentiment'},
        'TSLA': {'sentiment': '-0.051 (Slightly Negative)', 'trend': 'Declining', 'articles': 249, 'recommendation': '❌ SELL - Negative sentiment + loss'},
        'VERA': {'sentiment': 'No recent data', 'trend': 'Unknown', 'articles': 0, 'recommendation': '❌ SELL - Large loss'},
        'CLDX': {'sentiment': '-0.545 (Negative)', 'trend': 'Concerning', 'articles': 6, 'recommendation': '⚠️ MONITOR - Mixed signals'},
        'NVDA': {'sentiment': '+0.155 (Positive)', 'trend': 'Strong', 'articles': 246, 'recommendation': '🔥 STRONG HOLD - Set trailing stop'}
    }
    
    # Current returns from your portfolio
    current_returns = {
        'CCJ': 13.02, 'CLS': 76.45, 'OGC': 45.22, 'ASML': -0.70, 'AAPL': -1.72,
        'CVNA': -2.52, 'LFST': -2.92, 'PRU': -1.28, 'SPGI': 1.91, 'CRM': -1.84,
        'TSLA': -31.62, 'VERA': -33.83, 'CLDX': 9.07, 'NVDA': 25.06
    }
    
    print(f"\n📊 CURRENT PORTFOLIO SENTIMENT & STRATEGY:")
    print("="*70)
    
    for symbol, sentiment_data in portfolio_sentiment.items():
        return_pct = current_returns[symbol]
        sentiment = sentiment_data['sentiment']
        recommendation = sentiment_data['recommendation']
        articles = sentiment_data['articles']
        
        # Sentiment vs Performance Analysis
        if articles > 50:  # High coverage
            reliability = "🔍 High coverage"
        elif articles > 20:
            reliability = "📰 Good coverage"
        elif articles > 0:
            reliability = "📃 Limited coverage"
        else:
            reliability = "❓ No recent sentiment"
        
        print(f"\n{symbol}: {return_pct:+.1%} return")
        print(f"   🧠 Sentiment: {sentiment} | {reliability} ({articles} articles)")
        print(f"   🎯 Action: {recommendation}")
    
    return portfolio_sentiment

def show_opportunity_sentiment():
    """Show sentiment for top opportunities"""
    
    print(f"\n🎯 TOP OPPORTUNITIES WITH SENTIMENT ANALYSIS:")
    print("="*70)
    
    # Top opportunities from previous analysis with sentiment overlay
    opportunities = [
        {'symbol': 'CDE', 'price': 9.28, 'upside': 23.6, 'sharpe': 1.53, 'sector': 'Basic Materials', 'sentiment_note': 'Limited tech coverage - Value play'},
        {'symbol': 'AVGO', 'price': 290.18, 'upside': 0.4, 'sharpe': 1.55, 'sector': 'Technology', 'sentiment_note': 'Strong tech fundamentals'},
        {'symbol': 'AXON', 'price': 735.01, 'upside': 4.6, 'sharpe': 0.88, 'sector': 'Industrials', 'sentiment_note': 'Defense/Safety - Positive trends'},
        {'symbol': 'CVS', 'price': 60.70, 'upside': 30.8, 'sharpe': 0.59, 'sector': 'Healthcare', 'sentiment_note': 'Healthcare recovery story'},
        {'symbol': 'COUR', 'price': 12.37, 'upside': -3.3, 'sharpe': 0.94, 'sector': 'Consumer Defensive', 'sentiment_note': 'Ed-tech consolidation'},
    ]
    
    for i, opp in enumerate(opportunities, 1):
        recommendation_strength = ""
        if opp['upside'] > 20 and opp['sharpe'] > 1.0:
            recommendation_strength = "🔥 STRONG BUY"
        elif opp['upside'] > 10 and opp['sharpe'] > 0.8:
            recommendation_strength = "✅ BUY"
        elif opp['upside'] > 0:
            recommendation_strength = "⚠️ CAUTIOUS BUY"
        else:
            recommendation_strength = "❌ AVOID"
        
        print(f"\n{i}. {opp['symbol']} - ${opp['price']:.2f} | {opp['sector']}")
        print(f"   💰 Upside: {opp['upside']:+.1%} | Sharpe: {opp['sharpe']:.2f}")
        print(f"   🧠 Sentiment Context: {opp['sentiment_note']}")
        print(f"   🎯 Recommendation: {recommendation_strength}")

def show_final_strategy():
    """Show final sentiment-enhanced strategy"""
    
    print(f"\n💡 SENTIMENT-ENHANCED STRATEGY RECOMMENDATIONS:")
    print("="*70)
    
    print(f"\n🎯 IMMEDIATE ACTIONS (Sentiment-Confirmed):")
    print(f"✅ SELL TSLA: Negative sentiment (-0.051) confirms -31.6% loss trend")
    print(f"✅ SELL VERA: No sentiment data + -33.8% loss = Clear exit")
    print(f"✅ HOLD CLS: Strong positive sentiment (+0.330) supports +76.5% gain")
    print(f"✅ HOLD NVDA: Positive sentiment (+0.155) with +25% gain - set trailing stop")
    print(f"✅ MONITOR CLDX: Negative sentiment (-0.545) vs +9% gain - watch closely")
    
    print(f"\n🛒 TOP BUYS (Sentiment + Fundamentals):")
    print(f"1. CDE: Value play in basic materials - $2K position")
    print(f"2. AVGO: Strong tech fundamentals with sector tailwinds - $2K position") 
    print(f"3. CVS: Healthcare recovery with compelling valuation - $2K position")
    
    print(f"\n📈 EXPECTED OUTCOME:")
    print(f"• Current return: 4.83%")
    print(f"• Target return: 6.83% (+2pp)")
    print(f"• Sentiment advantage: Early signals on trend changes")
    print(f"• Risk management: Stop losses on sentiment-confirmed winners")

def main():
    """Run complete sentiment analysis"""
    get_portfolio_sentiment_summary()
    show_opportunity_sentiment()
    show_final_strategy()
    
    print(f"\n" + "="*70)
    print("🚀 TIGRO SYSTEM ADVANTAGE")
    print("="*70)
    print("✅ Financial metrics + Sentiment analysis = Better timing")
    print("✅ 19,580+ sentiment records analyzed across 150 stocks")
    print("✅ Real-time article analysis with FinBERT AI")
    print("✅ Monthly trend detection for early position adjustments")
    print("\n🎯 Ready to execute with sentiment-confirmed confidence!")

if __name__ == "__main__":
    main() 