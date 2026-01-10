#!/usr/bin/env python3
"""
Quick API Test Script
Test basic functionality of Ruang Hijau API
"""

import requests
import json
import sys

API_BASE = "http://localhost:5000/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Print colored status message"""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
    elif status == "test":
        print(f"{Colors.YELLOW}🧪 {message}{Colors.END}")

def test_api_health():
    """Test if API is running"""
    print_status("Testing API Health...", "test")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print_status(f"API running: {data.get('message', 'OK')}", "success")
            return True
        else:
            print_status(f"API returned status {response.status_code}", "error")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to API. Is it running on port 5000?", "error")
        return False
    except Exception as e:
        print_status(f"Error testing API: {str(e)}", "error")
        return False

def test_endpoints_info():
    """Get list of available endpoints"""
    print_status("Getting API Endpoints Info...", "test")
    try:
        response = requests.get(f"{API_BASE}")
        if response.status_code == 200:
            data = response.json()
            print_status(f"Available endpoints: {', '.join(data.get('endpoints', {}).keys())}", "success")
            return True
        return False
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return False

def test_register_user():
    """Test user registration"""
    print_status("Testing User Registration...", "test")
    test_email = "testuser@example.com"
    test_data = {
        "name": "Test User",
        "email": test_email,
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('status') == 'success':
                user_id = data.get('user', {}).get('id')
                print_status(f"User registered: {test_email} (ID: {user_id})", "success")
                return user_id
            else:
                print_status(f"Registration failed: {data.get('message')}", "error")
                return None
        elif response.status_code == 400:
            print_status("Registration validation error (email might already exist)", "error")
            return None
        else:
            print_status(f"Registration failed with status {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return None

def test_login_user():
    """Test user login"""
    print_status("Testing User Login...", "test")
    test_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                user_id = data.get('user', {}).get('id')
                print_status(f"Login successful: {test_data['email']}", "success")
                return user_id
            else:
                print_status(f"Login failed: {data.get('message')}", "error")
                return None
        else:
            print_status(f"Login failed with status {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return None

def test_get_posts():
    """Test getting posts"""
    print_status("Testing Get Posts...", "test")
    try:
        response = requests.get(
            f"{API_BASE}/posts?limit=5&page=1"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                posts_count = len(data.get('data', []))
                pagination = data.get('pagination', {})
                print_status(f"Retrieved {posts_count} posts (Total: {pagination.get('total')})", "success")
                return True
            else:
                print_status(f"Failed: {data.get('message')}", "error")
                return False
        else:
            print_status(f"Failed with status {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return False

def test_get_campaigns():
    """Test getting campaigns"""
    print_status("Testing Get Campaigns...", "test")
    try:
        response = requests.get(
            f"{API_BASE}/campaigns?limit=5&page=1"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                campaigns_count = len(data.get('data', []))
                pagination = data.get('pagination', {})
                print_status(f"Retrieved {campaigns_count} campaigns (Total: {pagination.get('total')})", "success")
                return True
            else:
                print_status(f"Failed: {data.get('message')}", "error")
                return False
        else:
            print_status(f"Failed with status {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return False

def test_error_handling():
    """Test error handling"""
    print_status("Testing Error Handling...", "test")
    
    # Test invalid endpoint
    try:
        response = requests.get(f"{API_BASE}/invalid-endpoint")
        if response.status_code == 404:
            print_status("404 error handling working", "success")
        else:
            print_status(f"Expected 404, got {response.status_code}", "error")
    except Exception as e:
        print_status(f"Error testing 404: {str(e)}", "error")
    
    # Test invalid login
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrong"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 401:
            print_status("401 error handling working", "success")
        else:
            print_status(f"Expected 401, got {response.status_code}", "error")
    except Exception as e:
        print_status(f"Error testing 401: {str(e)}", "error")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Ruang Hijau API - Quick Test Script")
    print("="*60 + "\n")
    
    # Run tests
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: API Health
    if test_api_health():
        tests_passed += 1
    else:
        tests_failed += 1
        print_status("Cannot continue without running API server", "error")
        print_status("Run: python app.py", "info")
        sys.exit(1)
    
    print()
    
    # Test 2: Endpoints Info
    if test_endpoints_info():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # Test 3: Register
    if test_register_user():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # Test 4: Login
    if test_login_user():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # Test 5: Get Posts
    if test_get_posts():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # Test 6: Get Campaigns
    if test_get_campaigns():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # Test 7: Error Handling
    test_error_handling()
    
    print()
    print("="*60)
    print(f"Tests Summary: {Colors.GREEN}{tests_passed} passed{Colors.END}, {Colors.RED}{tests_failed} failed{Colors.END}")
    print("="*60 + "\n")
    
    if tests_failed == 0:
        print_status("All tests passed! API is working correctly ✅", "success")
        return 0
    else:
        print_status(f"Some tests failed. Check error messages above", "error")
        return 1

if __name__ == "__main__":
    exit(main())
