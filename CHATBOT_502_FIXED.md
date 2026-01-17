# 🐛 Chatbot 502 Error - FIXED ✅

## Problem
The Flutter app was getting a **502 Bad Gateway error** when trying to use the chatbot feature.

## Root Cause
Your `.env` file was **missing the RAG chatbot configuration**. The chatbot requires:
1. **Ollama** LLM service configuration
2. **TiDB Cloud** RAG database credentials
3. **Sentence Transformers** for embeddings

When these configurations were missing, the Flask backend would crash silently when processing the `/api/chatbot/chat` request, resulting in a 502 error.

## Solution Applied

### 1. ✅ Updated `.env` file
Added the missing chatbot configuration:
```properties
# Ollama LLM Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# TiDB Cloud Vector Database (for RAG)
RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
RAG_DB_PORT=4000
RAG_DB_USER=mi3fQyPy1G6E9Jx.root
RAG_DB_PASSWORD=NKFZCVf7VuaM2WFv
RAG_DB_NAME=RAG
RAG_SSL_CA=isrgrootx1.pem
```

### 2. ✅ Installed Python dependencies
Created virtual environment and installed all required packages:
```bash
cd Ruang-Hijau-Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Required packages:
- `sentence-transformers` - For text embeddings
- `ollama` - For LLM integration
- `mysql-connector-python` - For RAG database
- `Flask` & `Flask-Cors` - For backend API
- `python-dotenv` - For environment configuration

### 3. ✅ Verified all components
Created diagnostic script to confirm:
- ✅ Environment variables properly loaded
- ✅ Ollama service running (http://localhost:11434)
- ✅ Gemma2:2b model available
- ✅ Sentence Transformers (BAAI/bge-m3) loaded
- ✅ RAG database connection working (20 documents in database)

## How to Test

### Option 1: Run diagnostics
```bash
cd Ruang-Hijau-Backend
source venv/bin/activate
python test_chatbot_diagnostic.py
```

### Option 2: Start the backend and test the API
```bash
cd Ruang-Hijau-Backend
source venv/bin/activate
python app.py
```

Then from another terminal, test the chatbot endpoint:
```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?"}'
```

### Option 3: Test in the Flutter app
1. Make sure backend is running
2. Launch the Flutter app on your device
3. Navigate to the Chatbot page
4. Send a message - it should now work! ✅

## Important Notes

### Keep the virtual environment active
Every time you want to run the backend, remember to activate the virtual environment:
```bash
cd Ruang-Hijau-Backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

### Ollama must be running
The chatbot requires Ollama service. Keep it running in a separate terminal:
```bash
ollama serve
```

### First request may be slow
On the first chatbot request, sentence-transformers will load the BAAI/bge-m3 model, which may take 5-10 seconds. Subsequent requests will be much faster.

### RAG Database
The chatbot uses TiDB Cloud for vector storage and retrieval. Credentials are in `.env` and should not be changed unless you switch to a different database.

## Troubleshooting

If you still get 502 errors:

1. **Check backend logs** for error messages
2. **Run diagnostics** to identify missing components
3. **Verify Ollama** is running: `curl http://localhost:11434/api/tags`
4. **Check database connectivity** using the diagnostic script
5. **Review .env file** for correct configuration

---

**Status:** ✅ Fixed and Verified
**Last Updated:** January 15, 2026
