# 🚀 Ruang Hijau Backend - Quick Setup Guide

## Problem Summary
Your systemd Flask service was using gunicorn with **default 30-second timeout**, but chatbot requests take 30-60 seconds on the first request (loading embedder model), causing 500 errors.

## Quick Fix (3 Steps)

### Step 1: Update the Service File
```bash
sudo cp /home/ubuntu/Ruang-Hijau-Backend/flask.service /etc/systemd/system/flask.service
```

### Step 2: Reload and Restart
```bash
sudo systemctl daemon-reload
sudo systemctl restart flask
```

### Step 3: Verify It's Working
```bash
# Check service status
sudo systemctl status flask

# Test the API (should return JSON)
curl http://localhost:8000/api/

# Test the chatbot (wait 30-60 seconds for first request)
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?"}'
```

## What Was Changed
| Aspect | Before | After |
|--------|--------|-------|
| Timeout | 30s (default) | **120s** ✅ |
| Workers | 1 (default) | **2** ✅ |
| Logging | None | File-based ✅ |
| Auto-restart | No | **Yes** ✅ |

## Key Configuration
```ini
ExecStart=/home/ubuntu/Ruang-Hijau-Backend/venv/bin/gunicorn \
    app:app \
    --bind 0.0.0.0:8000 \
    --timeout 120 \         ← THIS WAS MISSING!
    --workers 2 \
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

## Useful Commands

```bash
# View service status
sudo systemctl status flask

# View live logs
sudo journalctl -u flask -f

# Restart service
sudo systemctl restart flask

# Stop service
sudo systemctl stop flask

# Start service
sudo systemctl start flask
```

## Testing

### Test 1: API Endpoint (Fast)
```bash
curl http://localhost:8000/api/
```

Expected response: API info in JSON

### Test 2: Chatbot - First Request (SLOW - Wait 30-60 seconds)
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?"}'
```

### Test 3: Chatbot - Second Request (FAST - 2-5 seconds)
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa manfaat pohon?"}'
```

## Important Notes

### ⏱️ First Request Timing
- The first chatbot request will take **30-60 seconds**
- This is normal - it's loading the BAAI/bge-m3 embedder model
- Subsequent requests will be much faster (2-5 seconds)
- The old gunicorn configuration (30-second timeout) was killing the process before it could finish

### 🔄 Auto-Restart
- The service is configured to auto-restart on failure
- If the process crashes, systemd will restart it automatically

### 📝 Logging
- Access logs: `/home/ubuntu/Ruang-Hijau-Backend/logs/access.log`
- Error logs: `/home/ubuntu/Ruang-Hijau-Backend/logs/error.log`
- Systemd logs: `sudo journalctl -u flask -f`

### 🎯 Concurrency
- Currently using 2 workers
- Each worker can handle one request at a time
- With 2 workers, you can handle 2 concurrent requests
- If you have high traffic, increase workers to match CPU cores

## Automated Setup (Alternative)

Instead of manual steps, you can run:
```bash
cd /home/ubuntu/Ruang-Hijau-Backend
sudo bash setup_service.sh
```

This will do all 3 steps automatically plus create the logs directory and set permissions.

## Detailed Documentation
For more information, see: `GUNICORN_TIMEOUT_FIX.md`

---
**Status:** ✅ Ready to Deploy
**Tested:** January 15, 2026
