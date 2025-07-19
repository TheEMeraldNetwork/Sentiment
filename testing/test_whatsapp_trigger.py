#!/usr/bin/env python3
"""
Test script for WhatsApp trigger webhook system
"""

import requests
import json
import time

def test_webhook():
    """Test the WhatsApp trigger webhook system"""
    
    base_url = "http://localhost:5001"
    headers = {
        'Authorization': 'Bearer tigro_2025_secure',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing Tigro WhatsApp Trigger System...")
    print(f"🌐 Base URL: {base_url}")
    print("🔑 Using authentication token: tigro_2025_secure")
    print()
    
    # Test 1: Status endpoint
    try:
        print("1️⃣ Testing status endpoint...")
        response = requests.get(f"{base_url}/status", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Status endpoint working!")
        else:
            print("   ❌ Status endpoint failed")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to webhook service")
        print("   💡 Make sure to run: python scripts/whatsapp_trigger.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test 2: Manual trigger endpoint
    try:
        print("2️⃣ Testing manual trigger endpoint...")
        response = requests.post(f"{base_url}/trigger", headers=headers, timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            print("   ✅ Manual trigger working!")
            print("   🚀 Sentiment analysis pipeline started!")
        else:
            print(f"   ❌ Trigger failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test 3: WhatsApp webhook simulation
    try:
        print("3️⃣ Testing WhatsApp webhook simulation...")
        webhook_data = {
            "message": "Hey, please send me the Tigro report"
        }
        
        response = requests.post(f"{base_url}/webhook", 
                               headers=headers, 
                               json=webhook_data, 
                               timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            print("   ✅ WhatsApp webhook simulation working!")
        else:
            print(f"   ❌ Webhook simulation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    print("🎉 All tests passed! WhatsApp trigger system is ready!")
    print()
    print("📱 Next steps:")
    print("   1. Keep the webhook service running")
    print("   2. Use ngrok to expose it to the internet: ngrok http 5001")
    print("   3. Connect WhatsApp using Zapier/Make.com")
    print("   4. Send messages with 'tigro', 'report', 'sentiment' to trigger")
    print()
    return True

if __name__ == '__main__':
    test_webhook() 