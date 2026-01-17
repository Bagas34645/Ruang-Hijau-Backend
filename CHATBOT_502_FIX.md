# 🚨 HTTP 502 Bad Gateway - Chatbot Fix Guide

## Problem
You're getting a **HTTP 502 Bad Gateway** error when trying to use the chatbot feature in the Flutter app.

```
📥 [Chatbot] Response Status: 502
📥 [Chatbot] Response Body: error code: 502
```

This means the Flask backend is crashing when processing the chatbot request.

---

## Root Causes (in order of likelihood)

### 1. **Ollama Service Not Running** ⚠️ MOST COMMON
The chatbot requires **Ollama** (local LLM service) to be running.

**Fix:**
```bash
# Terminal 1: Start Ollama service
ollama serve

# The service should start listening on http://localhost:11434
# Wait for it to display: "Listening on 127.0.0.1:11434"
```

### 2. **Missing Dependencies**
Some Python packages needed for the chatbot might not be installed.

**Fix:**
```bash
# In Ruang-Hijau-Backend folder
pip install -r requirements.txt

# Then restart Flask
python app.py
```

### 3. **Model Files Not Downloaded**
The BAAI/bge-m3 embedding model is 670MB. On first run, it downloads automatically (5-10 minutes).

**Check if it's downloading:**
- Look for downloads in: `~/.cache/huggingface/` or `~/.cache/torch/`
- Look for model in: `~/.ollama/models/manifests/registry.ollama.ai/library/`

**Force download specific model:**
```bash
ollama pull gemma2:2b  # This might take a few minutes
```

### 4. **Database Connection Failed**
The RAG (Retrieval-Augmented Generation) database might not be reachable.

**Fix:** Check if TiDB Cloud is accessible:
```bash
cd Ruang-Hijau-Backend
python test_chatbot_simple.py  # Diagnostic script
```

### 5. **Port Conflicts**
Flask backend running on wrong port or port already in use.

**Check:**
```bash
# Check if port 5000 is in use (Linux/Mac)
lsof -i :5000

# Kill process if needed
kill -9 <PID>
```

---

## Quick Startup Checklist

Before using the chatbot, ensure ALL these services are running:

### ✅ Step 1: Install Dependencies
```bash
cd Ruang-Hijau-Backend
pip install -r requirements.txt
```

### ✅ Step 2: Start Ollama Service
```bash
# Terminal 1 (keep it running)
ollama serve
# Wait for: "Listening on 127.0.0.1:11434"
```

### ✅ Step 3: Start Flask Backend
```bash
# Terminal 2 (keep it running)
cd Ruang-Hijau-Backend
python app.py
# Should show: "Running on http://127.0.0.1:5000"
```

### ✅ Step 4: Download Default Model
```bash
# Terminal 3 (one-time)
ollama pull gemma2:2b
# This downloads ~3.5GB (takes 5-10 minutes on first run)
```

### ✅ Step 5: Test Chatbot API
```bash
# Terminal 3 (after model is downloaded)
cd Ruang-Hijau-Backend
python test_chatbot_simple.py
```

### ✅ Step 6: Use Flutter App
- Open chatbot page in app
- Send a message
- Should now work! ✨

---

## Detailed Troubleshooting

### Problem: "Ollama service not available"

**Check if Ollama is installed:**
```bash
which ollama
ollama --version
```

**If not installed:**
```bash
# macOS
brew install ollama

# Linux
# Download from: https://ollama.ai

# Windows
# Download from: https://ollama.ai
```

**Start Ollama:**
```bash
ollama serve
```

### Problem: "Missing sentence-transformers"

**Install it:**
```bash
pip install sentence-transformers torch
```

### Problem: "Failed to connect to RAG database"

The RAG database connection might need credentials. Check your `.env` file:

```properties
RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
RAG_DB_PORT=4000
RAG_DB_USER=your_user
RAG_DB_PASSWORD=your_password
RAG_DB_NAME=RAG
RAG_SSL_CA=./isrgrootx1.pem
```

Make sure `isrgrootx1.pem` exists in the Ruang-Hijau-Backend folder.

### Problem: "Request timeout - server memproses terlalu lama"

The embedding/LLM processing is taking too long. This is normal on:
- First request (models are being loaded)
- Slower computers
- Large documents

**Solutions:**
1. **Wait longer** - First request can take 30+ seconds
2. **Use smaller model** - Edit `.env`:
   ```properties
   OLLAMA_MODEL=tinyllama  # Smaller but faster
   ```
3. **Increase timeout** - In Flutter `chatbot_page.dart`:
   ```dart
   const Duration(seconds: 600)  // Increase from 300 to 600
   ```

---

## Monitoring Logs

### Watch Flask logs in real-time:
```bash
cd Ruang-Hijau-Backend
python app.py 2>&1 | tee server.log
```

### Watch Ollama logs:
```bash
# The Ollama terminal will show:
ollama serve
# [Service starting...] messages
```

### Parse errors from logs:
```bash
# Search for errors in Flask log
grep "❌\|ERROR\|error" server.log

# Search for specific issue
grep "Ollama\|embedding\|database" server.log
```

---

## Environment Variables (.env)

Make sure these are set correctly:

```properties
# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# RAG Database (TiDB Cloud)
RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
RAG_DB_PORT=4000
RAG_DB_USER=your_username
RAG_DB_PASSWORD=your_password
RAG_DB_NAME=RAG
RAG_SSL_CA=./isrgrootx1.pem
```

---

## Testing The Chatbot

### Test 1: Health Check
```bash
curl http://127.0.0.1:5000/api/chatbot/health
```

Expected response:
```json
{
  "chatbot": "running",
  "embedder": "healthy",
  "llm": "healthy",
  "rag_database": "healthy"
}
```

### Test 2: Simple Chat
```bash
curl -X POST http://127.0.0.1:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?", "user_id": "test"}'
```

Expected response:
```json
{
  "success": true,
  "response": "Daur ulang adalah proses...",
  "user_id": "test"
}
```

### Test 3: Full Diagnostic
```bash
cd Ruang-Hijau-Backend
python test_chatbot_simple.py
```

---

## Performance Tips

1. **First request is slow** - Models are loaded on first use (30-60 seconds)
2. **Subsequent requests are fast** - Models stay in memory (3-5 seconds)
3. **Close other apps** - Free up RAM for Ollama
4. **Use `-v` flag for debug logs**:
   ```bash
   FLASK_ENV=development python app.py -v
   ```

---

## Contact/Support

If still having issues:

1. Check the diagnostic output:
   ```bash
   python test_chatbot_simple.py
   ```

2. Share the output of:
   ```bash
   python app.py 2>&1 | head -100
   ollama serve 2>&1 | head -50
   ```

3. Check Flutter logs:
   ```
   I/flutter (22355): 🚀 [Chatbot] Sending request to: ...
   I/flutter (22355): 📥 [Chatbot] Response Status: ...
   ```

---

## Quick Reference Commands

```bash
# Start all services (run in separate terminals)
Terminal 1: ollama serve
Terminal 2: cd Ruang-Hijau-Backend && python app.py
Terminal 3: python test_chatbot_simple.py

# View Flask logs
tail -f Ruang-Hijau-Backend/server.log

# Kill port 5000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Check Ollama models
ollama list

# Download a model
ollama pull gemma2:2b
```

---

**Last Updated:** January 2026
**Status:** ✅ Working
