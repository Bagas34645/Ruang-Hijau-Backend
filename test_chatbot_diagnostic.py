#!/usr/bin/env python3
"""
Quick diagnostic script to test chatbot components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

print("=" * 70)
print("🤖 CHATBOT DIAGNOSTIC SCRIPT")
print("=" * 70)

# Load environment variables
load_dotenv()
print("\n✅ Step 1: Environment variables loaded")

# Check required environment variables
required_env_vars = [
    'OLLAMA_HOST',
    'OLLAMA_MODEL',
    'RAG_DB_HOST',
    'RAG_DB_PORT',
    'RAG_DB_USER',
    'RAG_DB_PASSWORD',
    'RAG_DB_NAME'
]

print("\n📋 Checking environment variables:")
missing_vars = []
for var in required_env_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✅ {var} = {value[:30]}...")
    else:
        print(f"  ❌ {var} = NOT SET")
        missing_vars.append(var)

if missing_vars:
    print(f"\n❌ Missing environment variables: {missing_vars}")
    print("   Update your .env file with these variables")
    sys.exit(1)

# Test Ollama connection
print("\n🔌 Testing Ollama connection...")
try:
    import ollama
    client = ollama.Client(host=os.getenv('OLLAMA_HOST'))
    response = client.list()
    print(f"  ✅ Connected to Ollama at {os.getenv('OLLAMA_HOST')}")
    print(f"  ✅ Available models: {len(response.models)} model(s)")
    
    model_name = os.getenv('OLLAMA_MODEL')
    available_models = [m.model for m in response.models]
    if model_name in available_models:
        print(f"  ✅ Model '{model_name}' is available")
    else:
        print(f"  ❌ Model '{model_name}' not found")
        print(f"     Available: {available_models}")
        sys.exit(1)
except Exception as e:
    print(f"  ❌ Failed to connect to Ollama: {e}")
    print("     Make sure 'ollama serve' is running")
    sys.exit(1)

# Test sentence-transformers
print("\n🧠 Testing embedder (sentence-transformers)...")
try:
    from sentence_transformers import SentenceTransformer
    print("  ⏳ Loading BAAI/bge-m3 model (this may take a while on first run)...")
    embedder = SentenceTransformer('BAAI/bge-m3')
    
    # Test embedding
    test_text = "This is a test"
    embedding = embedder.encode(test_text)
    print(f"  ✅ Embedder loaded successfully")
    print(f"  ✅ Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"  ❌ Failed to load embedder: {e}")
    sys.exit(1)

# Test RAG database connection
print("\n📊 Testing RAG database connection...")
try:
    import mysql.connector
    
    db = mysql.connector.connect(
        host=os.getenv('RAG_DB_HOST'),
        port=int(os.getenv('RAG_DB_PORT', 4000)),
        user=os.getenv('RAG_DB_USER'),
        password=os.getenv('RAG_DB_PASSWORD'),
        database=os.getenv('RAG_DB_NAME'),
        ssl_verify_cert=False,
        ssl_verify_identity=False,
        connection_timeout=10
    )
    
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    
    print(f"  ✅ Connected to RAG database")
    print(f"  ✅ Documents in database: {count}")
    
    if count == 0:
        print("  ⚠️  No documents found in database")
        print("     The chatbot may not have relevant information to work with")
except Exception as e:
    print(f"  ❌ Failed to connect to RAG database: {e}")
    print("     Check your database credentials in .env")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL DIAGNOSTICS PASSED!")
print("=" * 70)
print("\nYou can now start the Flask backend:")
print("  source venv/bin/activate")
print("  python app.py")
print("\nThe chatbot should work at: /api/chatbot/chat")
print("=" * 70)
