#!/usr/bin/env python3
"""
Test Chatbot Components
Diagnose which component is causing HTTP 502 error
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("CHATBOT COMPONENTS DIAGNOSTIC TEST")
print("=" * 70)

# Test 1: Embedder (Sentence Transformer)
print("\n[1/4] Testing Sentence Transformer Embedder...")
print("-" * 70)
try:
    from sentence_transformers import SentenceTransformer
    print("  ✓ Sentence Transformers module imported")
    
    print("  ⏳ Loading BAAI/bge-m3 model (this may take a while)...")
    embedder = SentenceTransformer('BAAI/bge-m3')
    print("  ✓ Model loaded successfully")
    
    test_text = "Halo, apa kabar?"
    test_embedding = embedder.encode(test_text)
    print(f"  ✓ Encoding works: generated {len(test_embedding)} dimensions")
    print(f"  ✓ EMBEDDER STATUS: ✅ HEALTHY")
    
except ImportError as e:
    print(f"  ✗ EMBEDDER STATUS: ❌ FAILED (Import Error)")
    print(f"     Error: {e}")
    print(f"     Fix: pip install sentence-transformers torch")
    
except Exception as e:
    print(f"  ✗ EMBEDDER STATUS: ❌ FAILED")
    print(f"     Error: {type(e).__name__}: {e}")
    print(f"     Common causes:")
    print(f"     - Model download failed (try: pip install -U sentence-transformers)")
    print(f"     - Not enough disk space")
    print(f"     - GPU/CUDA issues (try CPU-only mode)")

# Test 2: Ollama LLM Connection
print("\n[2/4] Testing Ollama LLM Connection...")
print("-" * 70)
try:
    import requests
    
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    print(f"  ℹ Connecting to: {OLLAMA_HOST}")
    
    # Test basic connection
    response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
    print(f"  ✓ Ollama service is running")
    
    tags = response.json().get('models', [])
    print(f"  ✓ Found {len(tags)} models")
    
    # Check for required model
    model_names = [m['name'].split(':')[0] for m in tags]
    print(f"  ℹ Available models: {', '.join(model_names)}")
    
    if any('gemma2' in m or 'gemma' in m for m in model_names):
        print(f"  ✓ Gemma2 model found")
    else:
        print(f"  ⚠ Gemma2 model not found - download with: ollama pull gemma2:2b")
    
    # Try a simple chat
    print(f"  ⏳ Testing chat endpoint...")
    import ollama
    client = ollama.Client(host=OLLAMA_HOST)
    chat_response = client.chat(
        model='gemma2:2b',
        messages=[{'role': 'user', 'content': 'Halo'}],
        stream=False
    )
    print(f"  ✓ Chat works: '{chat_response['message']['content'][:50]}...'")
    print(f"  ✓ OLLAMA STATUS: ✅ HEALTHY")
    
except requests.exceptions.ConnectionError:
    print(f"  ✗ OLLAMA STATUS: ❌ FAILED (Connection refused)")
    print(f"     Ollama service is not running at {OLLAMA_HOST}")
    print(f"     Fix: Start Ollama with: ollama serve")
    
except Exception as e:
    print(f"  ✗ OLLAMA STATUS: ❌ FAILED")
    print(f"     Error: {type(e).__name__}: {e}")
    print(f"     Common causes:")
    print(f"     - Ollama not running (start with: ollama serve)")
    print(f"     - Model not downloaded (download with: ollama pull gemma2:2b)")
    print(f"     - Connection timeout (check OLLAMA_HOST env var)")

# Test 3: Database Connection
print("\n[3/4] Testing TiDB Cloud Database Connection...")
print("-" * 70)
try:
    import mysql.connector
    
    RAG_DB_HOST = os.getenv('RAG_DB_HOST', 'gateway01.eu-central-1.prod.aws.tidbcloud.com')
    RAG_DB_PORT = int(os.getenv('RAG_DB_PORT', 4000))
    RAG_DB_USER = os.getenv('RAG_DB_USER', 'mi3fQyPy1G6E9Jx.root')
    RAG_DB_PASSWORD = os.getenv('RAG_DB_PASSWORD', 'NKFZCVf7VuaM2WFv')
    RAG_DB_NAME = os.getenv('RAG_DB_NAME', 'RAG')
    RAG_SSL_CA = os.getenv('RAG_SSL_CA', os.path.join(os.path.dirname(__file__), 'isrgrootx1.pem'))
    
    print(f"  ℹ Host: {RAG_DB_HOST}:{RAG_DB_PORT}")
    print(f"  ℹ User: {RAG_DB_USER}")
    print(f"  ℹ Database: {RAG_DB_NAME}")
    
    print(f"  ⏳ Connecting to database...")
    conn = mysql.connector.connect(
        host=RAG_DB_HOST,
        port=RAG_DB_PORT,
        user=RAG_DB_USER,
        password=RAG_DB_PASSWORD,
        database=RAG_DB_NAME,
        ssl_ca=RAG_SSL_CA if os.path.exists(RAG_SSL_CA) else None,
        ssl_verify_cert=False,
        ssl_verify_identity=False,
        autocommit=True,
        connection_timeout=10
    )
    print(f"  ✓ Connected to database")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as doc_count FROM documents")
    result = cursor.fetchone()
    doc_count = result[0] if result else 0
    print(f"  ✓ Query works: {doc_count} documents in database")
    
    if doc_count == 0:
        print(f"  ⚠ WARNING: No documents in database. RAG might not work properly.")
    
    cursor.close()
    conn.close()
    print(f"  ✓ DATABASE STATUS: ✅ HEALTHY")
    
except FileNotFoundError as e:
    print(f"  ✗ DATABASE STATUS: ❌ FAILED (Certificate not found)")
    print(f"     Error: {e}")
    print(f"     Tip: Check if isrgrootx1.pem exists in backend folder")
    
except mysql.connector.Error as e:
    print(f"  ✗ DATABASE STATUS: ❌ FAILED (Connection error)")
    print(f"     Error Code: {e.errno}")
    print(f"     Error Message: {e.msg}")
    print(f"     Common causes:")
    print(f"     - Wrong credentials (check .env file)")
    print(f"     - Database offline or unreachable")
    print(f"     - Wrong SSL certificate")
    print(f"     - Network/firewall blocking connection")
    
except Exception as e:
    print(f"  ✗ DATABASE STATUS: ❌ FAILED")
    print(f"     Error: {type(e).__name__}: {e}")

# Test 4: Flask & Routes
print("\n[4/4] Testing Flask Setup & Routes...")
print("-" * 70)
try:
    from flask import Flask
    print(f"  ✓ Flask imported")
    
    # Try importing chatbot routes
    from routes.chatbot_routes import chatbot_bp
    print(f"  ✓ Chatbot blueprint imported")
    print(f"  ✓ FLASK STATUS: ✅ HEALTHY")
    
except ImportError as e:
    print(f"  ✗ FLASK STATUS: ❌ FAILED (Import error)")
    print(f"     Error: {e}")
    print(f"     Fix: Make sure you're in the Ruang-Hijau-Backend folder")
    
except Exception as e:
    print(f"  ✗ FLASK STATUS: ❌ FAILED")
    print(f"     Error: {type(e).__name__}: {e}")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

print("""
NEXT STEPS:

1. If any component shows ❌ FAILED:
   - Read the error message and recommended fix
   - Implement the fix (e.g., install missing package, start service)
   - Re-run this script to verify

2. Once all show ✅ HEALTHY:
   - Start the backend: python app.py
   - Try sending a message in the chatbot
   - If still getting 502, check Flask output for errors

3. For persistent issues:
   - Check backend terminal output while sending chat
   - Look for stack traces and error messages
   - Ensure no other process is using ports 5000, 11434, 4000

For more detailed troubleshooting, see: CHATBOT_502_ERROR_DIAGNOSIS.md
""")

print("=" * 70)
