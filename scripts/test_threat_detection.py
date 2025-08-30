#!/usr/bin/env python3
"""
Test script for threat detection system
"""

import json
from threat_integration import process_threat_request

# Test cases with different threat levels
test_cases = [
    {
        "name": "Safe Content",
        "data": {
            "title": "Weather Forecast for Today",
            "content": "Today's weather will be sunny with a high of 75°F and low of 60°F. Perfect for outdoor activities.",
            "url": "https://weather.com/forecast"
        }
    },
    {
        "name": "Phishing Attempt",
        "data": {
            "title": "Urgent: Verify Your Account",
            "content": "Your account has been suspended due to suspicious activity. Click here immediately to verify your identity and restore access. You have 24 hours before permanent suspension.",
            "url": "https://secure-bank-update.com/verify"
        }
    },
    {
        "name": "Scam Content",
        "data": {
            "title": "Make $5000 Working From Home",
            "content": "Guaranteed money making opportunity! Work from home and make $5000 per week with no experience required. This get rich quick method is 100% legitimate. Limited time offer - act now!",
            "url": "https://easymoney.biz"
        }
    },
    {
        "name": "Malware Distribution",
        "data": {
            "title": "Critical Security Alert",
            "content": "Virus detected on your computer! Your system is infected with malware. Download our security software now to clean your computer and remove all threats. Install immediately!",
            "url": "https://security-alert.net/download"
        }
    }
]

def run_tests():
    """Run all test cases and display results."""
    print("SafeSearch Threat Detection Test Suite")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        result = process_threat_request(test_case['data'])
        
        print(f"Status: {result['status']}")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Threats Detected: {result['threat_count']}")
        print(f"Risk Score: {result.get('total_risk_score', 0)}")
        
        if result['threats_detected']:
            print("Threat Details:")
            for threat in result['threats_detected']:
                print(f"  • {threat['type'].replace('_', ' ').title()}: {threat['count']} matches")
                print(f"    {threat['description']}")
        else:
            print("No threats detected - content appears safe")
    
    print("\n" + "=" * 50)
    print("Test suite completed!")

if __name__ == "__main__":
    run_tests()
