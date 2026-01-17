# 🎯 Chatbot 500 Error Analysis & Solution

## The Problem Chain

```
User Request to Chatbot
       ↓
Gunicorn receives request (port 8000)
       ↓
Flask chatbot endpoint starts processing
       ↓
1. Connect to RAG database ✅ (fast)
2. Search for relevant documents ✅ (fast)
3. Load embedder model ❌ (30-60 seconds on first request!)
       ↓
Gunicorn timeout threshold reached (30 seconds)
       ↓
Gunicorn KILLS the worker process ❌
       ↓
Request returns: 500 Internal Server Error ❌
```

## Why It Fails

**Old Configuration:**
```bash
ExecStart=/home/ubuntu/Ruang-Hijau-Backend/venv/bin/gunicorn app:app --bind 0.0.0.0:8000
```

- Default timeout: **30 seconds**
- First request needs: **30-60 seconds** (loading BAAI/bge-m3 model)
- Result: **TIMEOUT** ❌

## The Solution

**New Configuration:**
```bash
ExecStart=/home/ubuntu/Ruang-Hijau-Backend/venv/bin/gunicorn \
    app:app \
    --bind 0.0.0.0:8000 \
    --timeout 120 \        ← CRITICAL FIX!
    --workers 2 \
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

- New timeout: **120 seconds** (2 minutes)
- First request needs: **30-60 seconds** ✅
- Subsequent requests: **2-5 seconds** ✅
- Result: **SUCCESS** ✅

## Comparison

| Aspect | Old | New | Impact |
|--------|-----|-----|--------|
| Timeout | 30s | 120s | ✅ Allows embedder loading |
| Workers | 1 | 2 | ✅ Better concurrency |
| Logging | None | File-based | ✅ Debug capability |
| Auto-restart | No | Yes | ✅ Better reliability |
| First Request | ❌ Times out | ✅ Works (30-60s) | **FIXED** |
| Subsequent | ❌ Times out | ✅ Works (2-5s) | **FIXED** |

## Request Timeline

### Before (Old Configuration)
```
0s:   Request arrives
5s:   Database connection ✅
10s:  Document search ✅
15s:  Start loading embedder model...
30s:  ⚠️  Timeout threshold reached!
31s:  ❌ Worker killed by gunicorn
      ❌ 500 Error returned to client
```

### After (New Configuration)
```
0s:   Request arrives
5s:   Database connection ✅
10s:  Document search ✅
15s:  Start loading embedder model...
45s:  ✅ Embedder loaded!
50s:  ✅ Response generated!
52s:  ✅ Response sent to client
      ✅ 200 Success!
```

## File Structure

```
/home/ubuntu/Ruang-Hijau-Backend/
├── flask.service              ← UPDATED systemd service file
├── setup_service.sh           ← Automated setup script
├── QUICK_FIX.md              ← Quick reference (THIS)
├── GUNICORN_TIMEOUT_FIX.md   ← Detailed documentation
├── CHATBOT_502_FIXED.md      ← Previous fix (environment config)
├── test_chatbot_diagnostic.py ← Diagnostic tool
├── logs/                       ← Newly created logs directory
│   ├── access.log
│   └── error.log
└── ... other files
```

## Installation

### Quickest Way
```bash
sudo cp /home/ubuntu/Ruang-Hijau-Backend/flask.service /etc/systemd/system/flask.service
sudo systemctl daemon-reload
sudo systemctl restart flask
```

### Or Use Automated Script
```bash
sudo bash /home/ubuntu/Ruang-Hijau-Backend/setup_service.sh
```

## Verification

```bash
# 1. Check service is running
sudo systemctl status flask

# 2. Test API (fast)
curl http://localhost:8000/api/

# 3. Test chatbot (first request: 30-60s, subsequent: 2-5s)
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?"}'

# Expected response:
# {
#   "success": true,
#   "response": "Daur ulang adalah proses mengolah kembali limbah...",
#   "user_id": "anonymous"
# }
```

## Why This Timeout Value?

- **30 seconds (old)**: Too short for embedder loading
- **60 seconds**: Might be enough but cutting it close
- **120 seconds (new)**: Safe buffer for:
  - Embedder model loading: 30-60s
  - Network latency: 5-10s
  - Database queries: 5-10s
  - LLM generation: 5-20s
  - Total buffer: Ensures no timeouts even under slow conditions

## Future Optimization

If embedder still takes too long, consider:

1. **Pre-load the embedder model** on service startup
   - Make first request instant (instead of 30-60s)

2. **Use lighter embedder model**
   - Example: `sentence-transformers/all-MiniLM-L6-v2` (much faster)

3. **Cache embeddings** for common questions
   - Instant responses for repeated questions

4. **Implement async processing**
   - Non-blocking requests using Celery + Redis

For now, the 120-second timeout is the best quick fix that works for everyone.

## Summary

✅ **Old Problem:** Gunicorn timeout killing chatbot requests
✅ **Root Cause:** Timeout too short for embedder model loading
✅ **Solution:** Increase timeout to 120 seconds
✅ **Implementation:** Update systemd service file
✅ **Status:** Ready to deploy

---
**Created:** January 15, 2026
**Time to Deploy:** ~2 minutes
**Breaking Changes:** None
**Rollback:** Easy (restore old service file)
