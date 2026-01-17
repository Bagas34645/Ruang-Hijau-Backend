# Chatbot Architecture & Service Dependencies

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RUANG HIJAU APPLICATION                        │
└─────────────────────────────────────────────────────────────────────┘
                                ▼
                        ┌───────────────┐
                        │ FLUTTER APP   │
                        │ (chatbot_page)│
                        └───────────────┘
                                ▼
                    HTTP POST /api/chatbot/chat
                                ▼
        ┌───────────────────────────────────────────────┐
        │          FLASK BACKEND (app.py)              │
        │  Port: 5000                                  │
        │  Status: 🟢 Need to start                    │
        └───────────────────────────────────────────────┘
                    ▼                      ▼
        ┌─────────────────────┐  ┌──────────────────┐
        │ OLLAMA SERVICE      │  │ RAG DATABASE     │
        │ (Local LLM)         │  │ (TiDB Cloud)     │
        │ Port: 11434         │  │ Host: gateway... │
        │ Status: 🟢 Need     │  │ Port: 4000       │
        │         to start    │  │ Status: ✅ Cloud │
        └─────────────────────┘  └──────────────────┘
                ▼                         ▼
        ┌─────────────────────┐  ┌──────────────────┐
        │ EMBEDDING MODEL     │  │ DOCUMENTS TABLE  │
        │ (BAAI/bge-m3)       │  │ (knowledge base) │
        │ Size: 670MB         │  │                  │
        │ Auto-download: ✅   │  │                  │
        └─────────────────────┘  └──────────────────┘
```

## 🎯 Services Status Checklist

### ✅ Already Working (Cloud Services)
- **TiDB Cloud Database** - RAG knowledge base
- **Hugging Face Models** - Will auto-download

### 🔧 Need to Start (Local Services)

```
┌─────────────────────────────────────────────────────┐
│  SERVICE 1: OLLAMA (LLM Service)                   │
├─────────────────────────────────────────────────────┤
│  Command: ollama serve                             │
│  Port: 11434                                       │
│  Status: 🔴 NOT RUNNING (need to start)           │
│  Role: Provides the AI language model              │
│  Time to start: 5-10 seconds                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  SERVICE 2: FLASK (Backend API)                    │
├─────────────────────────────────────────────────────┤
│  Command: python app.py                            │
│  Port: 5000                                        │
│  Status: 🔴 NOT RUNNING (need to start)           │
│  Role: Handles chatbot requests, orchestrates RAG  │
│  Time to start: 2-3 seconds                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  SERVICE 3: EMBEDDING MODEL (First Time Only)      │
├─────────────────────────────────────────────────────┤
│  Command: ollama pull gemma2:2b                    │
│  Size: ~3.5GB                                      │
│  Status: ⏳ Need to download (first request auto)  │
│  Role: Local LLM model for processing requests     │
│  Time to download: 5-10 minutes                    │
└─────────────────────────────────────────────────────┘
```

## 📊 Request Flow Diagram

```
1. User sends message in Flutter app
   │
   ▼
2. FLUTTER APP
   │ HTTP POST: {"message": "Apa itu daur ulang?"}
   ▼
3. FLASK BACKEND receives request
   │ - Parse JSON
   │ - Log request
   ▼
4. Load LLM & Embedder (first time only, slow)
   │ - sentence-transformers (BAAI/bge-m3)
   │ - ollama client
   ▼
5. Connect to RAG Database
   │ - TiDB Cloud connection
   │ - Prepare SQL query
   ▼
6. Embed the user query
   │ - Convert text to vector
   ▼
7. Search for relevant documents
   │ - Vector similarity search in TiDB
   │ - Find top-5 most relevant documents
   ▼
8. Build context
   │ - Combine retrieved documents
   ▼
9. Send prompt to Ollama
   │ - Combine context + question
   │ - Ollama processes and generates response
   ▼
10. Return response to Flask
    │ - JSON format
    ▼
11. Flask returns to Flutter app
    │ HTTP 200: {"response": "Daur ulang adalah..."}
    ▼
12. Flutter displays in chat UI
```

## ⏱️ Expected Timing

```
First Request (with model loading):
├── Ollama load model: 20-30 seconds
├── Embedding model load: 10-15 seconds
├── Database connection: 2-3 seconds
├── Vector search: 1-2 seconds
├── LLM generation: 5-10 seconds
└── Total: 40-60 seconds ⏳ (normal!)

Subsequent Requests (models cached):
├── Database connection: 1-2 seconds
├── Vector search: 1-2 seconds
├── LLM generation: 3-5 seconds
└── Total: 5-10 seconds ⚡ (fast!)
```

## 🚀 Startup Sequence

```
Step 1: Open Terminal 1
  $ ollama serve
  
  Output should show:
  ✅ Listening on 127.0.0.1:11434
  
  (Keep this terminal running)

Step 2: Open Terminal 2
  $ cd Ruang-Hijau-Backend
  $ python app.py
  
  Output should show:
  ✅ Running on http://127.0.0.1:5000
  
  (Keep this terminal running)

Step 3: (Optional) Open Terminal 3
  $ ollama pull gemma2:2b
  
  (Downloads the model, ~5-10 minutes)
  After completion, you're ready to test!

Step 4: Use Flutter App
  - Open chatbot page
  - Send first message
  - Wait 40-60 seconds for first response
  - Subsequent messages should be faster
```

## 🔍 How to Monitor

```bash
# Terminal 1 (Ollama)
# Watch for:
# - "Listening on 127.0.0.1:11434" ✅
# - Model loading messages
# - No "error" or "connection refused" ❌

# Terminal 2 (Flask)
# Watch for:
# - "Running on http://127.0.0.1:5000" ✅
# - "[1/4] Connecting to database..." ✅
# - "[2/4] Generating response..." ✅
# - "❌ Runtime error" = Issue with Ollama or embedder
# - "❌ Database error" = Issue with TiDB

# Terminal 3 (Diagnostic)
# Run: python diagnose_chatbot.py
# Should show all components as "healthy" ✅
```

## 🐛 Troubleshooting Quick Map

```
Error: 502 Bad Gateway
├─ Ollama not running?
│  └─ Run: ollama serve
├─ Flask crashed?
│  └─ Check Flask terminal for errors
└─ Dependencies missing?
   └─ Run: pip install -r requirements.txt

Error: Request Timeout (300 seconds)
├─ First request?
│  └─ Wait 40-60 seconds, that's normal
├─ Model downloading?
│  └─ Run: ollama pull gemma2:2b
└─ System resources low?
   └─ Close other apps, increase timeout

Error: 503 Service Unavailable
├─ Ollama unavailable?
│  └─ Run: ollama serve
├─ Missing packages?
│  └─ Run: pip install sentence-transformers torch
└─ Database unavailable?
   └─ Check TiDB Cloud account
```

## 📋 Dependency Summary

```
Python Packages:
├─ Flask >= 2.3.0 ✅
├─ Flask-CORS >= 4.0.0 ✅
├─ mysql-connector-python >= 8.0.0 ✅
├─ python-dotenv >= 1.0.0 ✅
├─ sentence-transformers >= 2.2.0 ✅ (Heavy - 2GB+)
├─ torch >= 1.9.0 ✅ (Heavy - 2GB+)
└─ ollama >= 0.1.0 ✅

System Services:
├─ Ollama Local Server 🔴 (MUST START)
├─ Flask Python App 🔴 (MUST START)
├─ TiDB Cloud Database ✅ (Already running)
└─ Internet Connection ✅ (For model downloads)

Database Files:
├─ .env (Configuration) ✅
├─ isrgrootx1.pem (SSL cert) ✅
└─ knowledge_base.csv (Optional docs) ✅
```

## ✨ Success Indicators

```
✅ Ollama Terminal
   [✓] "Listening on 127.0.0.1:11434"

✅ Flask Terminal  
   [✓] "Running on http://127.0.0.1:5000"
   
✅ First Chat Message
   [✓] ~40-60 second wait (first time)
   [✓] Response appears in chat
   [✓] No error messages

✅ Second Chat Message
   [✓] ~3-5 second wait
   [✓] Much faster!
   
✅ Diagnostic Script
   $ python diagnose_chatbot.py
   [✓] "ALL CHECKS PASSED!"
```

---

**Last Updated:** January 2026
**Quick Links:**
- Full Guide: `CHATBOT_502_FIX.md`
- Quick Fix: `CHATBOT_QUICK_FIX.md`
- Diagnostic: `python diagnose_chatbot.py`
- Startup Helper: `bash start_chatbot.sh`
