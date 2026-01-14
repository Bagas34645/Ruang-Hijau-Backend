#!/usr/bin/env python3
"""
Test chatbot API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("🤖 CHATBOT API TEST SUITE")
print("="*60)

# Test 1: Health Check
print("\n1️⃣  Testing /api/chatbot/health endpoint:")
try:
    response = requests.get(f"{BASE_URL}/api/chatbot/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Make sure Flask is running: python app.py")

# Test 2: Diagnostic
print("\n2️⃣  Testing /api/chatbot/diagnose endpoint:")
try:
    response = requests.get(f"{BASE_URL}/api/chatbot/diagnose", timeout=10)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Timestamp: {data.get('timestamp')}")
    print(f"   Components:")
    for component, status in data.get('components', {}).items():
        available = "✅" if status.get('available') else "❌"
        print(f"      {available} {component}: {status}")
    print(f"   Configuration:")
    for key, value in data.get('configuration', {}).items():
        print(f"      - {key}: {value}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Chat API
print("\n3️⃣  Testing /api/chatbot/chat endpoint:")
test_message = "Apa itu daur ulang?"
print(f"   Sending message: '{test_message}'")
print(f"   (This may take a minute while Ollama processes)")

try:
    payload = {
        "message": test_message,
        "user_id": "api_test"
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/chatbot/chat",
        json=payload,
        timeout=300,  # 5 minute timeout for LLM
        headers={"Content-Type": "application/json"}
    )
    elapsed = time.time() - start_time
    
    print(f"   Status: {response.status_code}")
    print(f"   Time taken: {elapsed:.1f} seconds")
    
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"   Body: {response.text[:500]}")
        
except requests.Timeout:
    print(f"   ⏱️  Request timed out (took more than 300 seconds)")
    print(f"      This might mean:")
    print(f"      - Ollama is still loading the model")
    print(f"      - PC is slow")
    print(f"      - Model is too large")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"      Make sure Flask is running on {BASE_URL}")

# Test 4: Invalid request
print("\n4️⃣  Testing error handling (empty message):")
try:
    payload = {"message": "", "user_id": "test"}
    response = requests.post(
        f"{BASE_URL}/api/chatbot/chat",
        json=payload,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Search endpoint
print("\n5️⃣  Testing /api/chatbot/search endpoint:")
try:
    payload = {
        "query": "daur ulang",
        "k_top": 3
    }
    response = requests.post(
        f"{BASE_URL}/api/chatbot/search",
        json=payload,
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"   Found {data.get('count', 0)} results")
        for i, result in enumerate(data.get('results', []), 1):
            text = result.get('text', '')[:100]
            distance = result.get('distance', 0)
            print(f"      {i}. (distance: {distance:.2f}) {text}...")
    else:
        print(f"   Error: {data.get('error')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("✅ Test complete!")
print("="*60)
