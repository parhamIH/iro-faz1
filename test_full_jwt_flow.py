#!/usr/bin/env python3
"""
Comprehensive end-to-end test for JWT + SMS authentication flow
"""
import requests
import random
import string

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/account"

# Generate a random phone number for testing
random_digits = ''.join(random.choices(string.digits, k=8))
test_phone = f"+98912{random_digits}"
test_email = f"testuser{random_digits}@example.com"
test_full_name = "تست کاربر"
test_password = "TestPass123!"

def safe_json_response(resp):
    """Safely get JSON response or return text if not JSON"""
    try:
        return resp.json()
    except:
        return f"Non-JSON response: {resp.text}"

def register_user():
    print(f"\n[1] Registering user {test_phone} ...")
    url = f"{API_BASE}/register/"
    data = {
        "full_name": test_full_name,
        "phone_number": test_phone,
        "email": test_email,
        "password": test_password
    }
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    return resp.status_code in (200, 201)

def request_sms_code():
    print(f"\n[2] Requesting SMS code for {test_phone} ...")
    url = f"{API_BASE}/sms-verification-request/"
    data = {"phone_number": test_phone}
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    if resp.status_code == 200:
        response_data = safe_json_response(resp)
        if isinstance(response_data, dict):
            code = response_data.get("verification_code")
            return code
    return None

def jwt_login(verification_code):
    print(f"\n[3] Logging in with code {verification_code} ...")
    url = f"{API_BASE}/jwt-login/"
    data = {
        "phone_number": test_phone,
        "verification_code": verification_code,
        "device_info": {"device_name": "TestDevice", "device_type": "mobile"}
    }
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    if resp.status_code == 200:
        response_data = safe_json_response(resp)
        if isinstance(response_data, dict):
            tokens = response_data.get("tokens", {})
            return tokens.get("access"), tokens.get("refresh"), tokens.get("device_id")
    return None, None, None

def get_devices(access_token):
    print(f"\n[4] Getting active devices ...")
    url = f"{API_BASE}/devices/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    return resp.status_code == 200

def refresh_token(refresh_token):
    print(f"\n[5] Refreshing token ...")
    url = f"{API_BASE}/jwt-refresh/"
    data = {"refresh": refresh_token}
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    if resp.status_code == 200:
        response_data = safe_json_response(resp)
        if isinstance(response_data, dict):
            return response_data.get("access")
    return None

def logout(access_token):
    print(f"\n[6] Logging out ...")
    url = f"{API_BASE}/logout/"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"revoke_all": False}
    resp = requests.post(url, json=data, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {safe_json_response(resp)}")
    return resp.status_code == 200

def main():
    print("\n🚀 Starting FULL JWT Auth Flow Test")
    print("="*60)
    
    # 1. Register user
    register_user()
    
    # 2. Request SMS code
    code = request_sms_code()
    if not code:
        print("❌ Could not get verification code. Aborting.")
        return
    
    # 3. Login with code
    access, refresh, device_id = jwt_login(code)
    if not access or not refresh:
        print("❌ Login failed. Aborting.")
        return
    
    # 4. Get devices
    get_devices(access)
    
    # 5. Refresh token
    new_access = refresh_token(refresh)
    if new_access:
        print("✅ Token refreshed successfully.")
    else:
        print("❌ Token refresh failed.")
    
    # 6. Logout
    logout(access)
    print("\n✅ Full flow test completed!")

if __name__ == "__main__":
    main() 