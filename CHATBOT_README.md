# 🤖 Chatbot Fix - Complete Guide

## 📋 Overview

Your Flutter app was receiving **HTTP 500 errors** from the chatbot API because the backend wasn't properly handling exceptions.

**What we fixed:**

- ✅ All errors now return JSON (not HTML)
- ✅ Better error messages showing what's wrong
- ✅ Diagnostic tools to identify issues
- ✅ Health checks for each component
- ✅ Comprehensive troubleshooting guides

---

## 🚀 Quick Start (5 minutes)

1. **Run diagnostic:**

   ```bash
   cd Ruang-Hijau-Backend
   python test_chatbot_simple.py
   ```

2. **Fix whatever is broken** (see the output)

3. **Start services:**

   ```bash
   # Terminal 1: Ollama
   ollama serve

   # Terminal 2: Flask
   python app.py
   ```

4. **Rebuild Flutter:**
   ```bash
   cd ../ruang_hijau_app
   flutter pub get
   flutter run
   ```

---

## 📚 Documentation Files

### 🎯 **CHATBOT_QUICK_START.md** (Start here!)

- TL;DR version
- 3 most common issues
- How to know it's working

### ✅ **CHATBOT_SETUP_CHECKLIST.md** (Follow this)

- Step-by-step checklist
- What to do in each phase
- Success indicators
- Quick reference commands

### 🔧 **CHATBOT_TROUBLESHOOTING.md** (If you're stuck)

- Detailed issue analysis
- Component-specific fixes
- Testing commands for each component
- Log locations to check

### 📖 **CHATBOT_FIX_SUMMARY.md** (Technical details)

- What was changed and why
- All files that were modified
- How the fix works
- Expected behavior before/after

---

## 🛠️ Tools Provided

### `test_chatbot_simple.py`

Comprehensive diagnostic that checks:

- Python packages
- Ollama connectivity
- Embedder availability
- Database connection
- Document count

**Run:** `python test_chatbot_simple.py`

### `test_chatbot_api.py`

Tests all chatbot API endpoints:

- Health check
- Diagnostics endpoint
- Chat endpoint
- Error handling
- Search endpoint

**Run:** `python test_chatbot_api.py`

---

## 🎯 The Problem & Solution

### What Was Wrong

```
Flask Exception → HTML 500 Error Page → JSON Parse Error in Flutter → App Crash
```

### What We Fixed

```
Flask Exception → Caught & Handled → JSON Error Response → App Shows Error Message → App Stays Responsive
```

---

## ✨ Key Improvements Made

| Before                      | After                   |
| --------------------------- | ----------------------- |
| Unhandled exceptions        | Proper error handling   |
| HTML 500 error pages        | JSON error responses    |
| No error context            | Detailed error messages |
| No diagnostics              | Automatic diagnostics   |
| Manual troubleshooting      | Guided troubleshooting  |
| Repeated retries on failure | Smart error caching     |
| Unknown component failures  | Separate health checks  |

---

## 📝 Files Modified & Created

### Modified:

- `routes/chatbot_routes.py` - Enhanced error handling

### Created:

- `test_chatbot_simple.py` - Diagnostic script
- `test_chatbot_api.py` - API test script
- `CHATBOT_QUICK_START.md` - Quick start guide
- `CHATBOT_SETUP_CHECKLIST.md` - Setup checklist
- `CHATBOT_TROUBLESHOOTING.md` - Troubleshooting guide
- `CHATBOT_FIX_SUMMARY.md` - Technical summary
- `README.md` (this file) - Overview

---

## 🚀 Getting Started

### Step 1: Diagnose

```bash
cd Ruang-Hijau-Backend
python test_chatbot_simple.py
```

This tells you which component is broken.

### Step 2: Fix

Based on diagnostic output, fix:

- **Missing packages**: `pip install -r requirements.txt`
- **Ollama not running**: `ollama serve`
- **Database down**: Check TiDB Cloud
- **Documents empty**: Populate documents table

### Step 3: Verify

```bash
python test_chatbot_api.py
```

All tests should pass.

### Step 4: Test Flutter

```bash
cd ../ruang_hijau_app
flutter pub get
flutter run
```

Chatbot should work now!

---

## 🔍 How to Troubleshoot

### If Something Still Doesn't Work:

1. **Check Flask logs**

   - Look at terminal where `python app.py` runs
   - Find the error message
   - Read the traceback

2. **Run diagnostic**

   ```bash
   python test_chatbot_simple.py
   ```

3. **Check specific component**

   ```bash
   curl http://localhost:5000/api/chatbot/diagnose
   ```

4. **Read appropriate guide**
   - For setup: `CHATBOT_SETUP_CHECKLIST.md`
   - For issues: `CHATBOT_TROUBLESHOOTING.md`
   - For details: `CHATBOT_FIX_SUMMARY.md`

---

## 📊 Component Status Check

### Health Check Endpoint

```bash
curl http://localhost:5000/api/chatbot/health
```

Should return:

```json
{
  "success": true,
  "status": {
    "chatbot": "running",
    "embedder": "healthy",
    "llm": "healthy",
    "rag_database": "healthy"
  }
}
```

### Detailed Diagnostics Endpoint

```bash
curl http://localhost:5000/api/chatbot/diagnose
```

Shows configuration and component details.

---

## 🧪 Testing the API

### Test Basic Connectivity

```bash
curl http://localhost:5000/api/chatbot/health
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Apa itu daur ulang?",
    "user_id": "test"
  }'
```

### Run Full Test Suite

```bash
python test_chatbot_api.py
```

---

## 💡 Common Issues & Quick Fixes

| Issue                                                | Quick Fix                                    |
| ---------------------------------------------------- | -------------------------------------------- |
| `ConnectionError: Ollama not running`                | `ollama serve` in new terminal               |
| `ImportError: No module named sentence_transformers` | `pip install -r requirements.txt`            |
| `Database connection error`                          | Check `.env` credentials and internet        |
| `Empty documents table`                              | Populate with documents or use demo data     |
| `Slow response`                                      | Model is loading (first time ~5 min), normal |
| `Timeout error`                                      | Increase timeout, check system resources     |

---

## 🎓 Learning Resources

- **API Design**: See how endpoints handle different error scenarios
- **Error Handling**: Check how each function validates and catches errors
- **Logging**: See how diagnostic information is captured
- **Testing**: Examples of testing each component separately

---

## 📞 Support Files

If you get stuck, check these in order:

1. `CHATBOT_QUICK_START.md` - Fastest solution
2. `CHATBOT_SETUP_CHECKLIST.md` - Step-by-step guide
3. `CHATBOT_TROUBLESHOOTING.md` - Issue-specific solutions
4. `CHATBOT_FIX_SUMMARY.md` - Technical details
5. Flask console logs - The actual error message

---

## ✅ Success Criteria

You'll know the fix is working when:

- [ ] `python test_chatbot_simple.py` shows all green ✅
- [ ] `curl http://localhost:5000/api/chatbot/health` returns success
- [ ] `python test_chatbot_api.py` passes all tests
- [ ] Flutter app sends message and receives response
- [ ] No 500 errors in Flutter logs
- [ ] ChatBot page shows actual bot responses

---

## 🎯 Next Steps

1. **Read CHATBOT_QUICK_START.md** - 5 minute overview
2. **Run diagnostic** - Identify your specific issue
3. **Fix that issue** - Use troubleshooting guide
4. **Verify with tests** - Confirm it works
5. **Test in Flutter** - Make sure app works

---

## 📝 Notes

- First time loading BAAI/bge-m3 model takes 5-10 minutes (~1GB download)
- Ollama needs to be running whenever you use chatbot
- Database must be accessible and have documents table populated
- All error messages now in JSON format for proper error handling

---

## 🚀 You Got This!

The fix is complete. Follow the guides above to get your chatbot working! 🎉
