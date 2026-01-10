#!/usr/bin/env python3
"""
Diagnostic script untuk verify image access dari database dan file system
"""
import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_uploads_folder():
    """Check if uploads folder exists dan writable"""
    print("\n" + "="*60)
    print("1. CHECKING UPLOADS FOLDER")
    print("="*60)
    
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    
    if os.path.exists(uploads_dir):
        print(f"✅ Uploads folder exists: {uploads_dir}")
        
        # Check if writable
        if os.access(uploads_dir, os.W_OK):
            print("✅ Uploads folder is writable")
        else:
            print("❌ Uploads folder is NOT writable")
            return False
        
        # List files
        files = os.listdir(uploads_dir)
        if files:
            print(f"✅ Found {len(files)} files in uploads:")
            for f in files[:10]:  # Show first 10
                file_path = os.path.join(uploads_dir, f)
                size = os.path.getsize(file_path)
                print(f"   - {f} ({size} bytes)")
        else:
            print("❌ Uploads folder is EMPTY")
            return False
    else:
        print(f"❌ Uploads folder does NOT exist: {uploads_dir}")
        return False
    
    return True

def check_database():
    """Check database posts with images"""
    print("\n" + "="*60)
    print("2. CHECKING DATABASE POSTS")
    print("="*60)
    
    try:
        from db import get_db
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT id, user_id, text, image, created_at FROM posts WHERE image IS NOT NULL LIMIT 5")
        posts = cursor.fetchall()
        cursor.close()
        db.close()
        
        if posts:
            print(f"✅ Found {len(posts)} posts with images:")
            for post in posts:
                print(f"\n   Post ID: {post['id']}")
                print(f"   User ID: {post['user_id']}")
                print(f"   Text: {post['text'][:50]}..." if post['text'] else "   Text: (none)")
                print(f"   Image: {post['image']}")
                print(f"   Created: {post['created_at']}")
                
                # Check if file exists
                file_path = os.path.join(os.path.dirname(__file__), 'uploads', post['image'])
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   ✅ File exists ({size} bytes)")
                else:
                    print(f"   ❌ File does NOT exist: {file_path}")
        else:
            print("❌ No posts with images found in database")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def check_api_endpoints():
    """Check if API endpoints work"""
    print("\n" + "="*60)
    print("3. CHECKING API ENDPOINTS")
    print("="*60)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test if backend is running
        print(f"\nTesting connection to {base_url}")
        response = requests.get(f"{base_url}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
        
        # Test GET /api/posts/
        print(f"\nTesting GET {base_url}/api/posts/")
        response = requests.get(f"{base_url}/api/posts/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                posts_count = len(data['data'])
                print(f"✅ GET /api/posts/ works. Found {posts_count} posts")
                
                # Check posts with images
                posts_with_images = [p for p in data['data'] if p.get('image')]
                if posts_with_images:
                    print(f"✅ Found {len(posts_with_images)} posts with images")
                    
                    # Test image URL access
                    first_image = posts_with_images[0]['image']
                    print(f"\nTesting image URL: {base_url}/uploads/{first_image}")
                    
                    img_response = requests.head(f"{base_url}/uploads/{first_image}", timeout=5)
                    if img_response.status_code == 200:
                        print(f"✅ Image URL is accessible (status {img_response.status_code})")
                        print(f"   Content-Type: {img_response.headers.get('Content-Type', 'unknown')}")
                        print(f"   Content-Length: {img_response.headers.get('Content-Length', 'unknown')}")
                    else:
                        print(f"❌ Image URL returned status {img_response.status_code}")
                else:
                    print("❌ No posts with images found via API")
            else:
                print("❌ API response missing 'data' field")
        else:
            print(f"❌ GET /api/posts/ returned status {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {base_url}")
        print("   Make sure backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "IMAGE ACCESS DIAGNOSTIC SCRIPT" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Uploads Folder": check_uploads_folder(),
        "Database": check_database(),
        "API Endpoints": check_api_endpoints(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check}: {status}")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if not results["Uploads Folder"]:
        print("❌ Issue: Uploads folder problem")
        print("   Fix:")
        print("   1. Create uploads folder: mkdir uploads")
        print("   2. Set permissions: chmod 755 uploads")
    
    if not results["Database"]:
        print("❌ Issue: Database problem")
        print("   Fix:")
        print("   1. Verify database is initialized")
        print("   2. Check posts table has image field")
        print("   3. Upload some posts with images")
    
    if not results["API Endpoints"]:
        print("❌ Issue: API endpoint problem")
        print("   Fix:")
        print("   1. Start backend: python app.py")
        print("   2. Check CORS configuration")
        print("   3. Verify uploads route is registered")
    
    print("\n" + "="*60)
    
    # Overall status
    all_pass = all(results.values())
    if all_pass:
        print("✅ ALL CHECKS PASSED - Image access should work!")
    else:
        print("❌ Some checks failed - see recommendations above")
    
    print("="*60 + "\n")
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
