#!/usr/bin/env python3
"""
Test script untuk fitur kampanye
Tests: fetch campaigns, create campaign dengan image, get campaign details
"""
import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
USER_ID = 2  # Ganti dengan user ID yang valid

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def test_fetch_campaigns():
    """Test GET /api/campaigns/"""
    print_header("TEST 1: Fetch Campaigns")

    try:
        # Test without filter
        print_info("Fetching all campaigns (page 1, limit 20)...")
        response = requests.get(
            f"{BASE_URL}/api/campaigns/?limit=20&page=1",
            timeout=10
        )
        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Berhasil mengambil campaigns")
            print(f"  - Total campaigns: {data.get('pagination', {}).get('total', 0)}")
            print(f"  - Campaigns dalam response: {len(data.get('data', []))}")
            print(f"  - Pages: {data.get('pagination', {}).get('pages', 0)}")

            if data.get('data'):
                campaign = data['data'][0]
                print(f"\n  Contoh campaign:")
                print(f"    - ID: {campaign.get('id')}")
                print(f"    - Title: {campaign.get('title')}")
                print(f"    - Category: {campaign.get('category')}")
                print(f"    - Target: Rp {campaign.get('target_amount', 0):,}")
                print(f"    - Current: Rp {campaign.get('current_amount', 0):,}")
                print(f"    - Image: {campaign.get('image')}")

            return True
        else:
            print_error(f"Failed to fetch campaigns: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print_error(f"Error fetching campaigns: {e}")
        return False


def test_fetch_campaigns_by_category():
    """Test GET /api/campaigns/ dengan category filter"""
    print_header("TEST 2: Fetch Campaigns by Category")

    try:
        category = "Lingkungan"
        print_info(f"Fetching campaigns with category={category}...")
        response = requests.get(
            f"{BASE_URL}/api/campaigns/?limit=20&page=1&category={category}",
            timeout=10
        )
        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            print_success(f"Berhasil mengambil campaigns dengan kategori '{category}'")
            print(f"  - Total: {data.get('pagination', {}).get('total', 0)}")
            print(f"  - Dalam response: {len(campaigns)}")

            if campaigns:
                for i, campaign in enumerate(campaigns[:2]):
                    print(f"\n  Campaign {i + 1}:")
                    print(f"    - Title: {campaign.get('title')}")
                    print(f"    - Category: {campaign.get('category')}")

            return True
        else:
            print_error(f"Failed to fetch campaigns: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_get_campaign_detail():
    """Test GET /api/campaigns/<id>"""
    print_header("TEST 3: Get Campaign Detail")

    try:
        # First get a campaign from list
        print_info("Mengambil campaign dari list terlebih dahulu...")
        response = requests.get(f"{BASE_URL}/api/campaigns/?limit=5&page=1", timeout=10)

        if response.status_code != 200:
            print_error("Gagal mengambil campaign list")
            return False

        data = response.json()
        campaigns = data.get('data', [])

        if not campaigns:
            print_error("Tidak ada campaign untuk ditest")
            return False

        campaign_id = campaigns[0]['id']
        print_info(f"Testing detail campaign ID: {campaign_id}")

        # Get campaign detail
        response = requests.get(
            f"{BASE_URL}/api/campaigns/{campaign_id}",
            timeout=10
        )
        print_info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            campaign = data.get('data', {})
            print_success(f"Berhasil mengambil detail campaign")
            print(f"  - ID: {campaign.get('id')}")
            print(f"  - Title: {campaign.get('title')}")
            print(f"  - Description: {campaign.get('description')[:50]}...")
            print(f"  - Category: {campaign.get('category')}")
            print(f"  - Location: {campaign.get('location')}")
            print(f"  - Contact: {campaign.get('contact')}")
            print(f"  - Target: Rp {campaign.get('target_amount', 0):,}")
            print(f"  - Current: Rp {campaign.get('current_amount', 0):,}")
            print(f"  - Duration: {campaign.get('duration_days')} hari")
            print(f"  - Donors: {campaign.get('donor_count', 0)}")
            print(f"  - Volunteers: {campaign.get('volunteer_count', 0)}")
            print(f"  - Image: {campaign.get('image')}")

            return True
        else:
            print_error(f"Failed to get campaign detail: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_create_campaign():
    """Test POST /api/campaigns/ dengan image"""
    print_header("TEST 4: Create Campaign with Image")

    try:
        # Prepare image file
        image_path = Path(__file__).parent / "uploads" / "test_campaign.jpg"

        # Create dummy image if not exists
        if not image_path.exists():
            print_info("Creating dummy image for testing...")
            try:
                import base64
                # 1x1 white pixel JPEG
                jpg_data = base64.b64decode(
                    '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a'
                    'HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy'
                    'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEB'
                    'AxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEB'
                    'AQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A'
                    '/9k='
                )
                image_path.parent.mkdir(parents=True, exist_ok=True)
                with open(image_path, 'wb') as f:
                    f.write(jpg_data)
                print_success("Dummy image created")
            except Exception as e:
                print_error(f"Failed to create dummy image: {e}")
                print_info("Using image from test file if available...")

        # Prepare form data
        campaign_data = {
            'creator_id': str(USER_ID),
            'title': f'Campaign Test {int(time.time())}',
            'description': 'Ini adalah kampanye test untuk memastikan API bekerja dengan baik.',
            'target_amount': '50000000',
            'category': 'Lingkungan',
            'location': 'Jakarta, Indonesia',
            'contact': '081234567890',
            'duration_days': '30',
            'need_volunteers': 'true',
        }

        print_info(f"Creating campaign with data:")
        for key, value in campaign_data.items():
            print(f"  - {key}: {value}")

        # Prepare multipart request
        files = {}
        if image_path.exists():
            files['image'] = ('test_campaign.jpg', open(image_path, 'rb'), 'image/jpeg')
            print_info(f"Image file added: {image_path}")
        else:
            print_info("No image file found, sending without image")

        response = requests.post(
            f"{BASE_URL}/api/campaigns/",
            data=campaign_data,
            files=files,
            timeout=10
        )

        print_info(f"Response status: {response.status_code}")
        print_info(f"Response: {response.text[:200]}")

        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Berhasil membuat campaign")
            print(f"  - Message: {data.get('message')}")
            print(f"  - Campaign ID: {data.get('campaign_id')}")
            return True
        else:
            print_error(f"Failed to create campaign: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False
    finally:
        # Close file if opened
        try:
            for key, file_tuple in files.items():
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
        except:
            pass


def test_database_check():
    """Check if database has campaigns"""
    print_header("TEST 5: Database Check")

    try:
        response = requests.get(f"{BASE_URL}/api/campaigns/?limit=100", timeout=10)

        if response.status_code == 200:
            data = response.json()
            total = data.get('pagination', {}).get('total', 0)

            if total > 0:
                print_success(f"Database memiliki {total} kampanye")
                print(f"\nTop 3 campaigns:")
                for i, campaign in enumerate(data.get('data', [])[:3]):
                    print(f"  {i + 1}. {campaign.get('title')}")
                    print(f"     Target: Rp {campaign.get('target_amount', 0):,}")
                    print(f"     Status: {campaign.get('status', 'N/A')}")
                return True
            else:
                print_error("Database kosong, tidak ada kampanye")
                return False
        else:
            print_error(f"Failed to check database: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║         RUANG HIJAU - CAMPAIGN API TEST SUITE             ║{RESET}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"User ID: {USER_ID}")

    results = []

    # Run tests
    results.append(("Fetch Campaigns", test_fetch_campaigns()))
    results.append(("Fetch by Category", test_fetch_campaigns_by_category()))
    results.append(("Get Campaign Detail", test_get_campaign_detail()))
    results.append(("Database Check", test_database_check()))
    results.append(("Create Campaign", test_create_campaign()))

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {test_name}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{BLUE}{'='*60}{RESET}")

    if passed == total:
        print(f"{GREEN}🎉 All tests passed!{RESET}")
        return 0
    else:
        print(f"{YELLOW}⚠️  Some tests failed{RESET}")
        return 1


if __name__ == "__main__":
    exit(main())
