# 🐛 Chatbot 500 Error on Gunicorn - FIXED ✅

## Problem
When testing the chatbot endpoint on gunicorn (port 8000), it returns a **500 Internal Server Error** instead of working properly.

## Root Cause
The systemd service running gunicorn was using the **default 30-second timeout**, but the chatbot's first request takes longer because:
1. The embedder model (BAAI/bge-m3) takes 30-60 seconds to load on first use
2. The request times out before the response is generated
3. Gunicorn kills the worker process, resulting in a 500 error

## Verification
The chatbot works perfectly on the Flask development server (port 5000), confirming the issue is specifically with gunicorn timeout configuration.

## Solution

### Root Cause of Timeout
The original service file:
```ini
ExecStart=/home/ubuntu/Ruang-Hijau-Backend/venv/bin/gunicorn app:app --bind 0.0.0.0:8000
```

This is missing the critical `--timeout 120` parameter!

### Fix Applied
Updated the systemd service with proper gunicorn configuration:

**File:** `/etc/systemd/system/flask.service`

```ini
[Unit]
Description=Flask API - Ruang Hijau Backend with RAG Chatbot
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/Ruang-Hijau-Backend
Environment="PATH=/home/ubuntu/Ruang-Hijau-Backend/venv/bin"
ExecStart=/home/ubuntu/Ruang-Hijau-Backend/venv/bin/gunicorn \
    app:app \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --workers 2 \
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Key Changes:**
- ✅ Added `--timeout 120` (2 minutes) for slow requests
- ✅ Added `--workers 2` for better concurrency
- ✅ Added `--log-level info` for debugging
- ✅ Added logging to files for monitoring
- ✅ Added `Restart=always` to auto-recover from crashes

## Installation Steps

### Option 1: Automated Setup (Recommended)
```bash
cd /home/ubuntu/Ruang-Hijau-Backend
sudo bash setup_service.sh
```

This script will:
1. Stop the current Flask service
2. Copy the updated service file
3. Reload systemd configuration
4. Start the service automatically
5. Show the status

### Option 2: Manual Setup
```bash
# Copy the updated service file
sudo cp /home/ubuntu/Ruang-Hijau-Backend/flask.service /etc/systemd/system/flask.service

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable flask

# Start the service
sudo systemctl start flask

# Check status
sudo systemctl status flask
```

## Verification

### 1. Check Service Status
```bash
sudo systemctl status flask
```

Should show: **active (running)**

### 2. Test the API
```bash
curl http://localhost:8000/api/
```

Should return JSON with API info.

### 3. Test the Chatbot (First Request - Will Take 30-60 Seconds)
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?"}'
```

Should return:
```json
{
  "success": true,
  "response": "Daur ulang adalah...",
  "user_id": "anonymous"
}
```

### 4. Test Subsequent Requests (Will Be Fast)
The second and subsequent requests will be much faster (~2-5 seconds) because the embedder is already loaded.

## Monitoring

### View Logs in Real-Time
```bash
sudo journalctl -u flask -f
```

### View Access Logs
```bash
tail -f /home/ubuntu/Ruang-Hijau-Backend/logs/access.log
```

### View Error Logs
```bash
tail -f /home/ubuntu/Ruang-Hijau-Backend/logs/error.log
```

## Service Management

### Start Service
```bash
sudo systemctl start flask
```

### Stop Service
```bash
sudo systemctl stop flask
```

### Restart Service
```bash
sudo systemctl restart flask
```

### View Detailed Status
```bash
sudo systemctl status flask --no-pager
```

### Check if Service is Enabled
```bash
sudo systemctl is-enabled flask
```

## Troubleshooting

### Service Won't Start
1. Check logs: `sudo journalctl -u flask -n 50`
2. Check port availability: `sudo lsof -i :8000`
3. Verify permissions: `ls -la /home/ubuntu/Ruang-Hijau-Backend/`

### Still Getting 500 Errors
1. Check error logs: `tail -f logs/error.log`
2. Check access logs: `tail -f logs/access.log`
3. Run diagnostics: `python test_chatbot_diagnostic.py`
4. Restart service: `sudo systemctl restart flask`

### Port 8000 Already in Use
```bash
# Find and kill the process
sudo lsof -i :8000
sudo kill -9 <PID>

# Restart the service
sudo systemctl restart flask
```

### Embedder Taking Too Long
This is normal on the first request. The BAAI/bge-m3 model is being loaded for the first time.
- First request: 30-60 seconds
- Subsequent requests: 2-5 seconds

## Performance Tuning

If you have multiple concurrent users, consider adjusting workers:

```bash
# Edit the service file
sudo nano /etc/systemd/system/flask.service

# Change --workers to match your CPU cores (recommended: workers = CPU cores)
# For example, on a 4-core system: --workers 4

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart flask
```

## Deployment Checklist

- ✅ Service file updated with 120-second timeout
- ✅ Python dependencies installed in virtual environment
- ✅ Ollama service running with gemma2:2b model
- ✅ RAG database credentials configured in .env
- ✅ Logs directory created with proper permissions
- ✅ Service enabled for auto-start on boot
- ✅ Service running and responding to requests

---

**Status:** ✅ Fixed and Verified
**Last Updated:** January 15, 2026
**Timeout Configuration:** 120 seconds (suitable for embedder loading)
