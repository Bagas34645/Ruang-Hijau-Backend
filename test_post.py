#!/usr/bin/env python3
"""
Test script for post creation endpoint
Tests: text-only posts, posts with images, validation errors
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = 'http://127.0.0.1:5000'

def test_create_post_text_only():
    """Test creating a post with text only"""
    
    print("\n" + "=" * 60)
    print("[TEST 1] Create Post - Text Only")
    print("=" * 60)
    
    payload = {
        "user_id": 1,
        "text": "This is a test post with text only!"
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/posts/add',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 201:
            print("✅ Text-only post created successfully!")
            return True
        else:
            print(f"❌ Failed with status {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_post_with_image():
    """Test creating a post with text and image"""
    
    print("\n" + "=" * 60)
    print("[TEST 2] Create Post - With Image")
    print("=" * 60)
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_path = 'test_image.png'
    
    # Create a minimal PNG file (1x1 transparent pixel)
    png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # bit depth, color type
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IHDR CRC, IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # IDAT data
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # IDAT CRC
        0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
        0xAE, 0x42, 0x60, 0x82                             # IEND CRC
    ])
    
    try:
        # Write test image
        with open(test_image_path, 'wb') as f:
            f.write(png_bytes)
        
        # Create multipart form data
        with open(test_image_path, 'rb') as f:
            files = {
                'image': (test_image_path, f, 'image/png')
            }
            data = {
                'user_id': 1,
                'text': 'This is a test post with an image!'
            }
            
            res = requests.post(
                f'{BASE_URL}/api/posts/add',
                data=data,
                files=files
            )
        
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 201:
            print("✅ Post with image created successfully!")
            return True
        else:
            print(f"❌ Failed with status {res.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)


def test_missing_user_id():
    """Test creating a post with missing user_id"""
    
    print("\n" + "=" * 60)
    print("[TEST 3] Validation - Missing user_id")
    print("=" * 60)
    
    payload = {
        "text": "Post without user_id"
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/posts/add',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly rejected - missing user_id (400)")
            return True
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_missing_text():
    """Test creating a post with missing text"""
    
    print("\n" + "=" * 60)
    print("[TEST 4] Validation - Missing text")
    print("=" * 60)
    
    payload = {
        "user_id": 1
    }
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/posts/add',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly rejected - missing text (400)")
            return True
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_empty_body():
    """Test creating a post with empty body"""
    
    print("\n" + "=" * 60)
    print("[TEST 5] Validation - Empty body")
    print("=" * 60)
    
    try:
        res = requests.post(
            f'{BASE_URL}/api/posts/add',
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        
        if res.status_code == 400:
            print("✅ Correctly rejected - empty body (400)")
            return True
        else:
            print(f"⚠️  Expected 400, got {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_fetch_posts():
    """Test fetching posts"""
    
    print("\n" + "=" * 60)
    print("[TEST 6] Fetch Posts")
    print("=" * 60)
    
    try:
        res = requests.get(
            f'{BASE_URL}/api/posts/',
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            total_posts = data.get('pagination', {}).get('total', 0)
            print(f"✅ Posts fetched successfully!")
            print(f"   Total posts: {total_posts}")
            
            if data.get('data'):
                print(f"   First post:")
                first_post = data['data'][0]
                print(f"     - ID: {first_post.get('id')}")
                print(f"     - Author: {first_post.get('author_name')}")
                print(f"     - Text: {first_post.get('text')[:50]}...")
                print(f"     - Created: {first_post.get('created_at')}")
            
            return True
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(f"Response: {json.dumps(res.json(), indent=2)}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    
    print("\n" + "=" * 60)
    print("POST CREATION & FETCHING TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Create Post - Text Only", test_create_post_text_only()))
    results.append(("Create Post - With Image", test_create_post_with_image()))
    results.append(("Validation - Missing user_id", test_missing_user_id()))
    results.append(("Validation - Missing text", test_missing_text()))
    results.append(("Validation - Empty body", test_empty_body()))
    results.append(("Fetch Posts", test_fetch_posts()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + f"Total: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
