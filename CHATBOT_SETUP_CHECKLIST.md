# ✅ Chatbot 500 Error - Checklist

Follow this checklist to fix your chatbot issue.

## Before You Start

- [ ] You have the latest code (pull from git)
- [ ] You're in the `Ruang-Hijau-Backend` directory
- [ ] Python 3.8+ is installed
- [ ] You have terminal/command prompt open

## Phase 1: Diagnose (5-10 minutes)

- [ ] Run diagnostic: `python test_chatbot_simple.py`
- [ ] Read the output carefully
- [ ] Note which component(s) are failing:
  - [ ] Python packages
  - [ ] Ollama service
  - [ ] Embedder model
  - [ ] Database connection

## Phase 2: Fix Identified Issues

### If Packages Are Missing:

- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for installation to complete
- [ ] Verify: `pip list | grep -E "flask|sentence|ollama|mysql"`

### If Ollama Is Not Running:

- [ ] Open new terminal/PowerShell
- [ ] Run: `ollama serve`
- [ ] Wait for message: "Listening on 127.0.0.1:11434"
- [ ] Keep this terminal open

### If Ollama Model Is Missing:

- [ ] Open another terminal/PowerShell
- [ ] Run: `ollama pull gemma2:2b`
- [ ] Wait for download to complete (5-10 minutes, ~5GB)
- [ ] Verify: `ollama list` (should show gemma2:2b)

### If Database Connection Fails:

- [ ] Open `.env` file in editor
- [ ] Verify these values are correct:
  ```
  RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
  RAG_DB_PORT=4000
  RAG_DB_USER=your_username.root
  RAG_DB_PASSWORD=your_password
  RAG_DB_NAME=RAG
  ```
- [ ] Check `isrgrootx1.pem` exists in this folder
- [ ] Verify internet connection is working
- [ ] Try accessing TiDB Cloud from browser to confirm it's online

### If Documents Table Is Empty:

- [ ] You need to populate the documents table first
- [ ] See `CHATBOT_TROUBLESHOOTING.md` section "Issue 4: Documents Table Empty"
- [ ] Or run: `python -c "import mysql.connector; print('Database connected successfully')"`

## Phase 3: Start Services

- [ ] **Terminal 1**: Ollama running

  - [ ] `ollama serve` (if not already running from Phase 2)
  - [ ] Should show "Listening on 127.0.0.1:11434"

- [ ] **Terminal 2**: Flask Backend
  - [ ] `python app.py`
  - [ ] Should show "Server starting on 0.0.0.0:5000"
  - [ ] Should NOT show any errors

## Phase 4: Test Services

In a new terminal (Terminal 3):

### Test Health Check:

```bash
curl http://localhost:5000/api/chatbot/health
```

- [ ] Status code is 200
- [ ] All components show "healthy"

### Test Diagnostics:

```bash
curl http://localhost:5000/api/chatbot/diagnose
```

- [ ] Shows all components available
- [ ] Shows document count in database

### Test Chat API:

```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?", "user_id": "test"}'
```

- [ ] Status code is 200
- [ ] Response is JSON (not HTML)
- [ ] `"success": true` in response

### Or Run Python Test Script:

```bash
python test_chatbot_api.py
```

- [ ] All tests show ✅ success
- [ ] No ❌ failures

## Phase 5: Update Flutter App

In `ruang_hijau_app` directory:

- [ ] Run: `flutter pub get`
- [ ] Run: `flutter clean`
- [ ] Run: `flutter run`

## Phase 6: Test in Flutter App

- [ ] Open chatbot page
- [ ] Type a message (e.g., "Apa itu daur ulang?")
- [ ] Click send
- [ ] Bot should respond with an answer (NOT an error message)
- [ ] Response appears on screen

## Troubleshooting If Still Not Working

### Check Flask Logs

- [ ] Look at the terminal where `python app.py` is running
- [ ] Find the error message
- [ ] Read the detailed error
- [ ] Scroll up to see the full stack trace
- [ ] Search in `CHATBOT_TROUBLESHOOTING.md` for that error

### Re-Run Diagnostics

- [ ] Run: `python test_chatbot_simple.py` again
- [ ] Check if any component status changed
- [ ] Fix any newly failed components

### Check API Directly

- [ ] Run: `python test_chatbot_api.py`
- [ ] See which endpoint is failing
- [ ] Check Flask logs for that endpoint's error

### Restart Everything

- [ ] Stop Flask (Ctrl+C)
- [ ] Stop Ollama (Ctrl+C)
- [ ] Run diagnostics: `python test_chatbot_simple.py`
- [ ] Start Ollama: `ollama serve`
- [ ] Start Flask: `python app.py`
- [ ] Test health: `curl http://localhost:5000/api/chatbot/health`

## Success Indicators

✅ You'll know it's working when:

1. Health check shows all "healthy"
2. Chat API returns 200 with JSON response
3. Flutter app receives bot response (not error)
4. ChatBot page shows message and reply
5. No 500 errors in network requests

## Quick Reference Commands

```bash
# Diagnostic
python test_chatbot_simple.py

# Test API
python test_chatbot_api.py

# Health check
curl http://localhost:5000/api/chatbot/health

# Full diagnosis
curl http://localhost:5000/api/chatbot/diagnose

# Send message
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo", "user_id": "test"}'

# Start Ollama
ollama serve

# Pull model
ollama pull gemma2:2b

# Start Flask
python app.py

# Check Python packages
pip list | grep -E "flask|sentence|ollama|mysql"
```

## Still Stuck?

1. Check `CHATBOT_TROUBLESHOOTING.md` - most issues are covered there
2. Check `CHATBOT_FIX_SUMMARY.md` - explains what changed and why
3. Read Flask logs carefully - they show the exact error
4. Run diagnostic script - it identifies the problem component
5. Compare with quick reference commands above

Good luck! 🚀
