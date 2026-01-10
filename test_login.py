#!/usr/bin/env python3
"""
Test script for login endpoint
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_login():
    """Test login with different scenarios"""
    
    print("=" * 60)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 60)
    
    # Test 1: Login with valid credentials (created during registration test)
    print("\n[TEST 1] Login dengan email dan password yang valid")
    print("-" * 60)
    
    test_email = "testuser@example.com"
    test_password = "password123"
    
    payload = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 200:
            print("✅ Login berhasil!")
            user_data = res.json().get('user')
            if user_data:
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Name: {user_data.get('name')}")
                print(f"   Email: {user_data.get('email')}")
        else:
            print(f"❌ Login gagal dengan status {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Login with wrong password
    print("\n[TEST 2] Login dengan password yang salah")
    print("-" * 60)
    
    payload = {
        "email": test_email,
        "password": "wrongpassword"
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 401:
            print("✅ Correctly returned 401 for wrong password")
        else:
            print(f"⚠️  Expected 401, got {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Login with non-existent email
    print("\n[TEST 3] Login dengan email yang tidak terdaftar")
    print("-" * 60)
    
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 401:
            print("✅ Correctly returned 401 for non-existent user")
        else:
            print(f"⚠️  Expected 401, got {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Login with missing email
    print("\n[TEST 4] Login dengan email kosong")
    print("-" * 60)
    
    payload = {
        "email": "",
        "password": "password123"
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly returned 400 for missing email")
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Login with missing password
    print("\n[TEST 5] Login dengan password kosong")
    print("-" * 60)
    
    payload = {
        "email": test_email,
        "password": ""
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly returned 400 for missing password")
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Login with missing body
    print("\n[TEST 6] Login dengan body kosong")
    print("-" * 60)
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/auth/login',
            json={},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly returned 400 for empty body")
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_login()
