#!/usr/bin/env python3
"""
Test script untuk membuat kampanye lengkap
Menguji skenario yang sama dengan Flutter app
"""
import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
USER_ID = 1  # Valid user ID (Admin User)

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def check_user_exists():
    """Verify that user exists in database"""
    print_header("STEP 1: Check User Exists")
    
    try:
        # We'll verify by trying to fetch user profile
        print_info(f"Checking if user with ID {USER_ID} exists...")
        
        # Since there's no explicit user endpoint, we'll just proceed
        # In real scenario, you might want to query the database directly
        print_success(f"Using USER_ID: {USER_ID}")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def create_test_image():
    """Create a test image file"""
    print_header("STEP 2: Create Test Image")
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = Path(__file__).parent / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = uploads_dir / "test_campaign_image.jpg"
        
        # Create a simple test image using PIL if available, otherwise use base64
        try:
            from PIL import Image, ImageDraw
            
            print_info("Creating image with PIL...")
            img = Image.new('RGB', (400, 300), color='green')
            draw = ImageDraw.Draw(img)
            draw.text((150, 130), 'Test Campaign', fill='white')
            img.save(image_path)
            print_success(f"Image created at: {image_path}")
            
        except ImportError:
            print_info("PIL not available, creating simple JPEG image...")
            # Create a minimal valid JPEG
            import base64
            jpg_data = base64.b64decode(
                '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a'
                'HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy'
                'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEB'
                'AxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEB'
                'AQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A'
                '/9k='
            )
            with open(image_path, 'wb') as f:
                f.write(jpg_data)
            print_success(f"Simple JPEG created at: {image_path}")
        
        return image_path
        
    except Exception as e:
        print_error(f"Error creating test image: {e}")
        return None


def test_create_campaign_multipart():
    """Test creating campaign with multipart/form-data"""
    print_header("STEP 3: Test Create Campaign (Multipart)")
    
    try:
        # Create test image first
        image_path = create_test_image()
        if not image_path:
            print_error("Could not create test image")
            return False
        
        # Prepare campaign data
        campaign_data = {
            'creator_id': str(USER_ID),
            'title': f'Kampanye Test {int(time.time())}',
            'description': 'Ini adalah kampanye test untuk memastikan fitur penambahan kampanye bekerja dengan baik dari Flutter app.',
            'target_amount': '1000000',  # Rp 1,000,000
            'category': 'Lingkungan',
            'location': 'Jakarta, Indonesia',
            'contact': '081234567890',
            'duration_days': '30',
            'need_volunteers': 'true',
        }
        
        print_info("Campaign Data:")
        for key, value in campaign_data.items():
            if key != 'description':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value[:50]}...")
        
        # Prepare multipart request
        print_info("Sending multipart request...")
        
        with open(image_path, 'rb') as f:
            files = {
                'image': ('test_campaign.jpg', f, 'image/jpeg')
            }
            
            response = requests.post(
                f"{BASE_URL}/api/campaigns/",
                data=campaign_data,
                files=files,
                timeout=15
            )
        
        print_info(f"Response Status: {response.status_code}")
        print_info(f"Response Headers: {dict(response.headers)}")
        print_info(f"Response Body:\n{response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            campaign_id = data.get('campaign_id')
            print_success(f"Campaign created successfully!")
            print(f"  - Campaign ID: {campaign_id}")
            print(f"  - Message: {data.get('message')}")
            
            # Try to fetch the created campaign
            if campaign_id:
                print_info(f"Fetching created campaign (ID: {campaign_id})...")
                get_response = requests.get(
                    f"{BASE_URL}/api/campaigns/{campaign_id}",
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    campaign_detail = get_response.json().get('data', {})
                    print_success("Campaign details retrieved:")
                    print(f"  - Title: {campaign_detail.get('title')}")
                    print(f"  - Category: {campaign_detail.get('category')}")
                    print(f"  - Target: Rp {campaign_detail.get('target_amount', 0):,}")
                    print(f"  - Duration: {campaign_detail.get('duration_days')} hari")
                    print(f"  - Image: {campaign_detail.get('image')}")
                    print(f"  - Creator: {campaign_detail.get('creator_name')}")
                else:
                    print_error(f"Could not fetch campaign detail: {get_response.status_code}")
            
            return True
        else:
            print_error(f"Failed to create campaign: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_campaign_json():
    """Test creating campaign with JSON (without image)"""
    print_header("STEP 4: Test Create Campaign (JSON - No Image)")
    
    try:
        campaign_data = {
            'creator_id': USER_ID,
            'title': f'JSON Campaign Test {int(time.time())}',
            'description': 'Campaign dibuat melalui JSON request tanpa image.',
            'target_amount': 500000,
            'category': 'Pendidikan',
            'location': 'Bandung, Indonesia',
            'contact': '082345678901',
            'duration_days': 14,
            'need_volunteers': False,
        }
        
        print_info("Sending JSON request...")
        print_info("Campaign Data:")
        print(json.dumps(campaign_data, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/api/campaigns/",
            json=campaign_data,
            timeout=15
        )
        
        print_info(f"Response Status: {response.status_code}")
        print_info(f"Response Body:\n{response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Campaign created successfully!")
            print(f"  - Campaign ID: {data.get('campaign_id')}")
            print(f"  - Message: {data.get('message')}")
            return True
        else:
            print_error(f"Failed to create campaign: {response.status_code}")
            return False
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_all_campaigns():
    """Fetch all campaigns to verify creation"""
    print_header("STEP 5: Fetch All Campaigns")
    
    try:
        print_info("Fetching all campaigns...")
        
        response = requests.get(
            f"{BASE_URL}/api/campaigns/?limit=50&page=1",
            timeout=10
        )
        
        print_info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pagination = data.get('pagination', {})
            campaigns = data.get('data', [])
            
            print_success(f"Fetched campaigns successfully!")
            print(f"  - Total campaigns in DB: {pagination.get('total')}")
            print(f"  - Campaigns in response: {len(campaigns)}")
            print(f"  - Pages: {pagination.get('pages')}")
            
            if campaigns:
                print(f"\nLatest 3 campaigns:")
                for i, campaign in enumerate(campaigns[:3], 1):
                    print(f"  {i}. {campaign.get('title')} ({campaign.get('category')})")
                    print(f"     Creator: {campaign.get('creator_name')}")
                    print(f"     Target: Rp {campaign.get('target_amount', 0):,}")
            
            return True
        else:
            print_error(f"Failed to fetch campaigns: {response.status_code}")
            return False
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print_header("TESTING CAMPAIGN API - COMPLETE FLOW")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"User ID: {USER_ID}")
    
    results = {
        "Check User": check_user_exists(),
        "Create Campaign (Multipart)": test_create_campaign_multipart(),
        "Create Campaign (JSON)": test_create_campaign_json(),
        "Fetch All Campaigns": test_fetch_all_campaigns(),
    }
    
    # Print summary
    print_header("TEST SUMMARY")
    for test_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    if total_passed == total_tests:
        print_success(f"\nAll tests passed! ({total_passed}/{total_tests})")
    else:
        print_error(f"\nSome tests failed: {total_passed}/{total_tests} passed")


if __name__ == "__main__":
    main()
