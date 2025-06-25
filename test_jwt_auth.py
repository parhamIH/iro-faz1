#!/usr/bin/env python3
"""
Test script for JWT Authentication with SMS verification
This script demonstrates how to use the JWT authentication API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/account"

def test_sms_verification_request():
    """Test SMS verification request"""
    print("🔐 Testing SMS Verification Request...")
    
    url = f"{API_BASE}/sms-verification-request/"
    data = {
        "phone_number": "+989123456789"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 500:
            print("\n⚠️  Kavenegar API Error Detected!")
            print("This is likely due to:")
            print("1. Invalid/expired Kavenegar API key")
            print("2. Unauthorized sender number")
            print("3. Test number not in authorized list")
            print("\nTo fix this:")
            print("1. Check your KAVENEGAR_API_KEY in settings.py")
            print("2. Verify your sender number in Kavenegar dashboard")
            print("3. Add test numbers to your Kavenegar account")
            print("4. Or use a real phone number for testing")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_with_real_number():
    """Test with a real phone number (you need to provide this)"""
    print("\n📱 Testing with Real Phone Number...")
    print("Enter a real phone number for testing (or press Enter to skip):")
    phone_number = input("Phone number (+989xxxxxxxxx): ").strip()
    
    if not phone_number:
        print("Skipping real number test.")
        return False
    
    url = f"{API_BASE}/sms-verification-request/"
    data = {
        "phone_number": phone_number
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting JWT Authentication Tests...")
    print("=" * 50)
    
    # Test 1: SMS Verification Request (with test number)
    sms_success = test_sms_verification_request()
    
    if not sms_success:
        print("\n" + "=" * 50)
        print("❌ Test failed due to Kavenegar API issues.")
        print("Let's try with a real phone number...")
        
        # Test with real number
        real_sms_success = test_with_real_number()
        
        if not real_sms_success:
            print("\n❌ All tests failed. Please check your Kavenegar configuration.")
            return
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 