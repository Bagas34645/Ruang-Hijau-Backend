# 🚀 Chatbot 502 Fix - Quick Reference

## TL;DR (Too Long; Didn't Read)

You're getting **HTTP 502 Bad Gateway** because the Flask backend is crashing.

### ⚡ Quick Fix (3 steps):

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
cd Ruang-Hijau-Backend
python app.py
```

**Terminal 3 (Optional - download model first time):**
```bash
ollama pull gemma2:2b
```

Then try using the chatbot in the Flutter app again. **It should work now!** ✨

---

## What Was Fixed

✅ Added missing RAG configuration to `.env` file
✅ Created comprehensive troubleshooting guide (`CHATBOT_502_FIX.md`)
✅ Created diagnostic script (`diagnose_chatbot.py`)
✅ Created startup helper script (`start_chatbot.sh`)

---

## Files to Review

1. **CHATBOT_502_FIX.md** - Full troubleshooting guide
2. **diagnose_chatbot.py** - Run this to identify issues
3. **start_chatbot.sh** - Automated startup helper
4. **.env** - Updated with RAG configuration

---

## Common Issues & Fixes

| Issue | Error | Fix |
|-------|-------|-----|
| Ollama not running | 502 Bad Gateway | `ollama serve` |
| Missing dependencies | 503 Service Unavailable | `pip install -r requirements.txt` |
| Model not downloaded | Timeout/Error | `ollama pull gemma2:2b` |
| Flask not running | Connection refused | `python app.py` |
| Wrong ports | Connection error | Check `.env` and firewall |

---

## Test Commands

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if Flask is running
curl http://localhost:5000/api

# Test chatbot directly
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test"}'

# Run diagnostic
python diagnose_chatbot.py
```

---

## Still Getting 502?

1. **Check Flask logs:** Look at the terminal where `python app.py` is running
2. **Check Ollama logs:** Look at the terminal where `ollama serve` is running
3. **Run diagnostic:** `python diagnose_chatbot.py`
4. **See full guide:** Open `CHATBOT_502_FIX.md`

---

## Next Steps

1. ✅ **Add RAG config to `.env`** - Done! ✨
2. 🔧 **Start Ollama service** - `ollama serve`
3. 🔧 **Start Flask backend** - `python app.py`
4. 📥 **Download model** (first time only) - `ollama pull gemma2:2b`
5. 🎉 **Test in Flutter app** - Use chatbot feature

---

## Resources

- **Detailed Troubleshooting:** `CHATBOT_502_FIX.md`
- **Automatic Diagnosis:** `python diagnose_chatbot.py`
- **Automated Startup:** `bash start_chatbot.sh`
- **Previous Guides:** `CHATBOT_README.md`, `CHATBOT_SETUP.md`

---

**Status:** ✅ Partially Fixed - Need to start services
**Date:** January 2026
