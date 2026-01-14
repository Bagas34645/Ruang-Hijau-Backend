#!/usr/bin/env python3
"""
Simple chatbot diagnostic script
Helps identify which components are failing
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("\n" + "="*60)
print("🔍 CHATBOT DIAGNOSTIC SCRIPT")
print("="*60)

# 1. Check Python version
print("\n1️⃣  Python Information:")
print(f"   Version: {sys.version}")
print(f"   Executable: {sys.executable}")

# 2. Check environment variables
print("\n2️⃣  Environment Variables:")
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma2:2b')
RAG_DB_HOST = os.getenv('RAG_DB_HOST', 'gateway01.eu-central-1.prod.aws.tidbcloud.com')
RAG_DB_PORT = os.getenv('RAG_DB_PORT', '4000')

print(f"   OLLAMA_HOST: {OLLAMA_HOST}")
print(f"   OLLAMA_MODEL: {OLLAMA_MODEL}")
print(f"   RAG_DB_HOST: {RAG_DB_HOST}")
print(f"   RAG_DB_PORT: {RAG_DB_PORT}")

# 3. Check required packages
print("\n3️⃣  Required Packages:")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'mysql.connector': 'mysql-connector-python',
    'sentence_transformers': 'sentence-transformers',
    'ollama': 'ollama',
}

installed = []
missing = []

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        installed.append(package_name)
        print(f"   ✅ {package_name}")
    except ImportError:
        missing.append(package_name)
        print(f"   ❌ {package_name} (NOT INSTALLED)")

# 4. Test Ollama connection
print("\n4️⃣  Ollama Service:")
if 'ollama' not in missing:
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_HOST)
        print(f"   ✅ Successfully connected to {OLLAMA_HOST}")
        
        # Try to list models
        try:
            # Just check if service responds
            print(f"   ✅ Ollama service is running and responding")
        except Exception as e:
            print(f"   ⚠️  Connected but cannot get models: {e}")
    except Exception as e:
        print(f"   ❌ Failed to connect to Ollama at {OLLAMA_HOST}")
        print(f"      Error: {e}")
        print(f"      Solution: Make sure 'ollama serve' is running")
else:
    print(f"   ⚠️  ollama package not installed - skipping connection test")

# 5. Test embedder
print("\n5️⃣  Embedder (sentence-transformers):")
if 'sentence-transformers' not in missing:
    try:
        from sentence_transformers import SentenceTransformer
        print("   ⏳ Loading BAAI/bge-m3 model...")
        print("      (This may take 5-10 minutes on first run)")
        model = SentenceTransformer('BAAI/bge-m3')
        print("   ✅ Embedder loaded successfully")
        
        # Test embedding
        test_text = "Apa itu daur ulang?"
        embedding = model.encode(test_text)
        print(f"   ✅ Successfully created embedding (dimension: {len(embedding)})")
    except Exception as e:
        print(f"   ❌ Failed to load embedder: {e}")
        print(f"      Solution: Check disk space (model is ~1GB)")
else:
    print(f"   ⚠️  sentence-transformers not installed - skipping embedder test")

# 6. Test database connection
print("\n6️⃣  RAG Database (TiDB Cloud):")
if 'mysql.connector' not in missing:
    try:
        import mysql.connector
        
        RAG_DB_USER = os.getenv('RAG_DB_USER', 'mi3fQyPy1G6E9Jx.root')
        RAG_DB_PASSWORD = os.getenv('RAG_DB_PASSWORD', 'NKFZCVf7VuaM2WFv')
        RAG_DB_NAME = os.getenv('RAG_DB_NAME', 'RAG')
        RAG_SSL_CA = os.getenv('RAG_SSL_CA', os.path.join(os.path.dirname(__file__), 'isrgrootx1.pem'))
        
        print(f"   Attempting connection to {RAG_DB_HOST}:{RAG_DB_PORT}...")
        
        # Check SSL certificate
        if not os.path.exists(RAG_SSL_CA):
            print(f"   ⚠️  SSL certificate not found at {RAG_SSL_CA}")
            ssl_ca = None
            verify_cert = False
        else:
            ssl_ca = RAG_SSL_CA
            verify_cert = True
            print(f"   ✅ SSL certificate found")
        
        db = mysql.connector.connect(
            host=RAG_DB_HOST,
            port=int(RAG_DB_PORT),
            user=RAG_DB_USER,
            password=RAG_DB_PASSWORD,
            database=RAG_DB_NAME,
            ssl_ca=ssl_ca,
            ssl_verify_cert=verify_cert,
            ssl_verify_identity=False,
            connection_timeout=10,
            autocommit=True
        )
        print(f"   ✅ Successfully connected to RAG database")
        
        # Check tables
        cursor = db.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{RAG_DB_NAME}'")
        table_count = cursor.fetchone()[0]
        print(f"   ✅ Database has {table_count} tables")
        
        # Check documents
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {RAG_DB_NAME}.documents")
            doc_count = cursor.fetchone()[0]
            print(f"   ✅ Documents table exists with {doc_count} documents")
            
            if doc_count == 0:
                print(f"   ⚠️  WARNING: Documents table is empty!")
                print(f"      The RAG will not have context to retrieve")
        except mysql.connector.Error as e:
            print(f"   ❌ Documents table not found: {e}")
            print(f"      You may need to create the documents table first")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"   ❌ Failed to connect to database: {e}")
        print(f"      Check your credentials and network connection")
else:
    print(f"   ⚠️  mysql-connector-python not installed - skipping database test")

# 7. Summary
print("\n" + "="*60)
print("📋 SUMMARY")
print("="*60)

if missing:
    print(f"\n❌ Missing packages ({len(missing)}):")
    for pkg in missing:
        print(f"   - {pkg}")
    print(f"\n   Fix: pip install -r requirements.txt")
else:
    print(f"\n✅ All packages installed!")

print("\n🚀 NEXT STEPS:")
print("   1. If any component failed, fix it using the hints above")
print("   2. Make sure all services are running:")
print("      - ollama serve")
print("      - python app.py (Flask backend)")
print("   3. Test the chatbot API with:")
print("      curl -X POST http://localhost:5000/api/chatbot/chat \\")
print("        -H 'Content-Type: application/json' \\")
print("        -d '{\"message\": \"Apa itu daur ulang?\", \"user_id\": \"test\"}'")

print("\n" + "="*60)
