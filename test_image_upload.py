#!/usr/bin/env python3
"""
Test script untuk verify image upload functionality
"""
import requests
import os
import sys

BASE_URL = 'http://127.0.0.1:5000'

def test_image_upload():
    """Test image upload endpoint"""
    print("=" * 60)
    print("Testing Image Upload Functionality")
    print("=" * 60)
    
    # Create a dummy image file
    test_image_path = 'test_image.jpg'
    
    # Create a minimal JPEG file
    minimal_jpg = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
        0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
    ])
    
    with open(test_image_path, 'wb') as f:
        f.write(minimal_jpg)
    
    try:
        # Test upload
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'user_id': '1',
                'text': 'Test post dengan image'
            }
            
            print(f"\n1. POST to {BASE_URL}/api/posts/add")
            print(f"   Data: {data}")
            print(f"   Files: image file")
            
            response = requests.post(
                f'{BASE_URL}/api/posts/add',
                files=files,
                data=data
            )
            
            print(f"\n   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("\n   ✓ Upload successful!")
            else:
                print("\n   ✗ Upload failed!")
        
        # Test GET posts to verify response
        print(f"\n2. GET {BASE_URL}/api/posts/")
        response = requests.get(f'{BASE_URL}/api/posts/')
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                post = data['data'][0]
                print(f"\n   First post image field: {post.get('image')}")
                if post.get('image'):
                    print(f"   ✓ Image field exists!")
                    
                    # Test image serving
                    image_url = f"{BASE_URL}/uploads/{post['image']}"
                    print(f"\n3. GET {image_url}")
                    img_response = requests.get(image_url)
                    print(f"   Status Code: {img_response.status_code}")
                    
                    if img_response.status_code == 200:
                        print(f"   ✓ Image can be served!")
                    else:
                        print(f"   ✗ Image serving failed!")
                else:
                    print(f"   ✗ Image field is empty/null!")
            else:
                print(f"\n   ✗ No posts found!")
        
        # Check if uploads directory exists
        print(f"\n4. Check uploads directory")
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"   ✓ Uploads directory exists")
            print(f"   Files: {files}")
        else:
            print(f"   ✗ Uploads directory does not exist!")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == '__main__':
    test_image_upload()
