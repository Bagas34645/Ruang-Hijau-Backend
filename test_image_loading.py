"""
Image Loading Fix - Verification Tests
Tests image serving and URL construction
"""

import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"


def test_image_serving():
    """Test that images can be served from /uploads endpoint"""
    print("\n" + "=" * 70)
    print("TEST: Image File Serving")
    print("=" * 70)

    # Get list of uploaded images
    uploads_dir = os.path.join(
        os.path.dirname(__file__), 'uploads'
    )
    if not os.path.exists(uploads_dir):
        print("⚠️ Uploads directory not found")
        return False

    image_files = [f for f in os.listdir(uploads_dir)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    if not image_files:
        print("⚠️ No image files found in uploads directory")
        return False

    print(f"\nFound {len(image_files)} image files:")
    all_ok = True

    for img in image_files[:3]:  # Test first 3 images
        url = f"{BASE_URL}/uploads/{img}"
        print(f"\n  Testing: {img}")
        print(f"  URL: {url}")

        try:
            r = requests.get(url, timeout=5)
            print(f"  Status: {r.status_code}")
            print(f"  Content-Type: {r.headers.get('Content-Type', 'Unknown')}")
            print(f"  Size: {len(r.content)} bytes")

            if r.status_code == 200:
                print(f"  ✅ OK")
            else:
                print(f"  ❌ FAILED - Status {r.status_code}")
                all_ok = False

        except requests.exceptions.RequestException as e:
            print(f"  ❌ ERROR: {e}")
            all_ok = False

    return all_ok


def test_posts_with_images():
    """Test that posts API returns image filenames correctly"""
    print("\n" + "=" * 70)
    print("TEST: Posts API Returns Image Filenames")
    print("=" * 70)

    url = f"{BASE_URL}/api/posts/"
    print(f"\nFetching posts from: {url}")

    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")

        if r.status_code != 200:
            print(f"❌ FAILED - Status {r.status_code}")
            return False

        data = r.json()
        posts = data.get('data', [])

        print(f"Posts count: {len(posts)}")

        posts_with_images = [p for p in posts if p.get('image')]
        print(f"Posts with images: {len(posts_with_images)}")

        if posts_with_images:
            print("\nSample posts with images:")
            for i, post in enumerate(posts_with_images[:2], 1):
                print(f"\n  Post {i}:")
                print(f"    - ID: {post.get('id')}")
                print(f"    - Image: {post.get('image')}")
                print(f"    - Author: {post.get('author_name', 'Unknown')}")
                print(f"    - Text: {post.get('text', '')[:50]}...")

                # Test if image URL is accessible
                img_filename = post.get('image')
                img_url = f"{BASE_URL}/uploads/{img_filename}"
                img_r = requests.get(img_url, timeout=5)

                if img_r.status_code == 200:
                    print(f"    - Image URL: ✅ Accessible")
                else:
                    print(f"    - Image URL: ❌ Not found (Status {img_r.status_code})")

            print("\n✅ Posts API returning image filenames correctly")
            return True
        else:
            print("⚠️ No posts with images found")
            return True

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False


def test_url_construction():
    """Test that image URL construction is correct"""
    print("\n" + "=" * 70)
    print("TEST: Image URL Construction")
    print("=" * 70)

    print("\nURL construction pattern:")
    print(f"  Base: {BASE_URL}")
    print(f"  Endpoint: /uploads/{{filename}}")
    print(f"  Full URL: {BASE_URL}/uploads/{{filename}}")

    # Test with a known image
    test_filename = "1767586522_hutan.jpg"
    test_url = f"{BASE_URL}/uploads/{test_filename}"

    print(f"\nExample:")
    print(f"  Filename: {test_filename}")
    print(f"  URL: {test_url}")

    try:
        r = requests.head(test_url, timeout=5)
        if r.status_code == 200:
            print(f"  Status: {r.status_code}")
            print(f"  Content-Type: {r.headers.get('Content-Type', 'Unknown')}")
            print(f"  Content-Length: {r.headers.get('Content-Length', 'Unknown')} bytes")
            print(f"  ✅ URL construction is correct")
            return True
        else:
            print(f"  ❌ Status {r.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ File not found: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("IMAGE LOADING FIX - VERIFICATION TESTS")
    print("=" * 70)

    results = {
        "Image File Serving": test_image_serving(),
        "Posts API with Images": test_posts_with_images(),
        "URL Construction": test_url_construction(),
    }

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All image loading tests passed!")
        print("Backend is correctly serving images.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check backend configuration.")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
