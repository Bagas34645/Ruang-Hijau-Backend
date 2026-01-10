#!/usr/bin/env python3
"""
Test script to verify the fetch posts fix
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_fetch_posts_response():
    """Verify fetch posts returns correct response structure"""
    
    print("=" * 60)
    print("TEST: Fetch Posts Response Structure")
    print("=" * 60)
    
    try:
        res = requests.get(
            f'{BASE_URL}/api/posts/',
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nStatus Code: {res.status_code}")
        
        if res.status_code == 200:
            body = res.json()
            print(f"\nResponse Structure:")
            print(f"  - status: {body.get('status')}")
            print(f"  - data type: {type(body.get('data'))}")
            print(f"  - data length: {len(body.get('data', []))}")
            print(f"  - pagination keys: {list(body.get('pagination', {}).keys())}")
            
            # Check data structure
            if body.get('data') and len(body['data']) > 0:
                first_post = body['data'][0]
                print(f"\nFirst Post Structure:")
                for key, value in first_post.items():
                    print(f"  - {key}: {type(value).__name__} = {value if key != 'text' else value[:50] + '...'}")
                
                # Check required fields
                required_fields = ['id', 'user_id', 'author_name', 'text', 'image', 'likes', 'created_at', 'comment_count']
                missing_fields = [f for f in required_fields if f not in first_post]
                
                if missing_fields:
                    print(f"\n⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"\n✅ All required fields present!")
                    print(f"✅ Response structure is CORRECT!")
                    return True
            else:
                print(f"\n✅ Response structure is CORRECT (no posts in database)")
                return True
        else:
            print(f"❌ Failed with status {res.status_code}")
            print(f"Response: {json.dumps(res.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_frontend_compatibility():
    """Test that response is compatible with frontend parsing"""
    
    print("\n" + "=" * 60)
    print("TEST: Frontend Compatibility")
    print("=" * 60)
    
    try:
        res = requests.get(
            f'{BASE_URL}/api/posts/',
            headers={'Content-Type': 'application/json'}
        )
        
        if res.status_code != 200:
            print(f"❌ Status code is not 200: {res.status_code}")
            return False
        
        body = res.json()
        
        # Simulate frontend parsing
        if body.get('data') and isinstance(body['data'], list):
            print(f"✅ body['data'] is accessible and is a list")
            
            # Try parsing each post like the frontend does
            for i, post in enumerate(body['data']):
                try:
                    post_data = {
                        'id': post['id'],
                        'username': post.get('author_name', 'Unknown'),
                        'imageUrl': f"http://127.0.0.1:5000/uploads/{post['image']}" if post.get('image') else "default",
                        'caption': post.get('text', ''),
                        'likesCount': post.get('likes', 0),
                        'commentsCount': post.get('comment_count', 0),
                    }
                except KeyError as e:
                    print(f"❌ Post {i} missing field: {e}")
                    return False
            
            print(f"✅ All {len(body['data'])} posts can be parsed by frontend")
            print(f"✅ Frontend compatibility is OK!")
            return True
        else:
            print(f"❌ body['data'] is not a list or accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    
    print("\n" + "=" * 80)
    print("FETCH POSTS FIX - VERIFICATION TESTS")
    print("=" * 80)
    
    results = []
    results.append(("Response Structure", test_fetch_posts_response()))
    results.append(("Frontend Compatibility", test_frontend_compatibility()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + f"Total: {passed}/{total} tests passed\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
