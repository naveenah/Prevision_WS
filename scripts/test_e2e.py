#!/usr/bin/env python3
"""
E2E Testing Script for AI Brand Automator
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    """Test 1.1: User Registration"""
    print("\n" + "="*60)
    print("TEST 1.1: User Registration")
    print("="*60)
    
    # Use timestamp to ensure unique email on each run
    timestamp = int(time.time())
    url = f"{BASE_URL}/auth/register/"
    payload = {
        "email": f"test_{timestamp}@brandautomator.com",
        "password": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ PASS: User registered successfully")
            return response.json()
        else:
            print(f"❌ FAIL: Expected 201, got {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_login(email=None, password="SecurePass123!"):
    """Test 1.2: User Login"""
    print("\n" + "="*60)
    print("TEST 1.2: User Login")
    print("="*60)
    
    # Use timestamp email if none provided
    if email is None:
        timestamp = int(time.time())
        email = f"test_{timestamp}@brandautomator.com"
    
    url = f"{BASE_URL}/auth/login/"
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            tokens = response.json()
            if 'access' in tokens and 'refresh' in tokens:
                print("✅ PASS: Login successful, tokens received")
                return tokens
            else:
                print("❌ FAIL: Tokens not found in response")
                return None
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_protected_endpoint(access_token):
    """Test 1.3: Protected Endpoint Access"""
    print("\n" + "="*60)
    print("TEST 1.3: Protected Endpoint Access")
    print("="*60)
    
    url = f"{BASE_URL}/companies/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 404]:
            print("✅ PASS: Authenticated access granted")
            return True
        else:
            print(f"❌ FAIL: Expected 200/404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_unauthenticated_access():
    """Test 1.4: Unauthenticated Access Blocked"""
    print("\n" + "="*60)
    print("TEST 1.4: Unauthenticated Access Blocked")
    print("="*60)
    
    url = f"{BASE_URL}/companies/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ PASS: Unauthenticated access correctly blocked")
            return True
        else:
            print(f"❌ FAIL: Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "#"*60)
    print("# AI BRAND AUTOMATOR - E2E TESTING")
    print("# Test Suite 1: Authentication Flow")
    print("#"*60)
    
    results = []
    
    # Test 1.4 first (unauthenticated)
    results.append(("Unauthenticated Access Blocked", test_unauthenticated_access()))
    
    # Test 1.1: Registration
    registration_data = test_registration()
    results.append(("User Registration", registration_data is not None))
    
    if registration_data:
        # Extract access token and user email from registration
        tokens = registration_data.get('tokens', {})
        access_token = tokens.get('access')
        user_email = registration_data.get('user', {}).get('email')
        
        # Test 1.3: Protected endpoint with token
        results.append(("Protected Endpoint Access", test_protected_endpoint(access_token)))
        
        # Test 1.2: Login with newly registered user
        print("\n🔄 Testing login with newly registered user...")
        login_tokens = test_login(email=user_email)
        results.append(("User Login (Re-authentication)", login_tokens is not None))
    else:
        # Try login if registration failed (user might already exist)
        print("\n⚠️  Registration failed, attempting login instead...")
        tokens = test_login()
        results.append(("User Login", tokens is not None))
        
        if tokens:
            access_token = tokens.get('access')
            results.append(("Protected Endpoint Access", test_protected_endpoint(access_token)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
