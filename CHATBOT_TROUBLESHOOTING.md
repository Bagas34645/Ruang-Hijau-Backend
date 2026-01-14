# 🚨 Chatbot 500 Error - Troubleshooting Guide

## Problem

Your Flutter app is getting a **500 Internal Server Error** when trying to use the chatbot.

## Quick Diagnosis

Run this diagnostic script to identify the problem:

```bash
cd Ruang-Hijau-Backend
python test_chatbot_simple.py
```

This will check:

- ✅ Python packages installed
- ✅ Ollama service running
- ✅ Embedder available
- ✅ Database connection
- ✅ Documents in database

---

## Most Common Issues & Solutions

### Issue 1: Ollama Not Running ⚠️

**Symptoms:**

- Diagnostic shows "❌ Failed to connect to Ollama"
- Flask logs show connection error to localhost:11434

**Fix:**

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull a model (if not already done)
ollama pull gemma2:2b
```

**Verify:**

```bash
curl http://localhost:11434/api/tags
```

---

### Issue 2: Missing Dependencies ⚠️

**Symptoms:**

- Diagnostic shows "❌ sentence-transformers" or "❌ ollama"
- Flask logs show ImportError

**Fix:**

```bash
cd Ruang-Hijau-Backend
pip install -r requirements.txt
```

Or install specific packages:

```bash
pip install sentence-transformers torch ollama mysql-connector-python flask-cors
```

---

### Issue 3: Database Not Connected ⚠️

**Symptoms:**

- Diagnostic shows "❌ Failed to connect to RAG database"
- Flask logs show database connection error

**Possible Causes:**

1. **Wrong credentials** - Check `.env` file
2. **No network** - Check internet connection
3. **Database offline** - Check TiDB Cloud status
4. **SSL certificate issue** - Missing `isrgrootx1.pem`

**Fix:**

1. Check your `.env` file has correct credentials:

```
RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
RAG_DB_PORT=4000
RAG_DB_USER=your_username.root
RAG_DB_PASSWORD=your_password
RAG_DB_NAME=RAG
```

2. Check SSL certificate exists:

```bash
# In Ruang-Hijau-Backend folder
ls -la isrgrootx1.pem
```

3. Test connection manually:

```bash
python -c "
import mysql.connector
db = mysql.connector.connect(
    host='gateway01.eu-central-1.prod.aws.tidbcloud.com',
    port=4000,
    user='YOUR_USER.root',
    password='YOUR_PASSWORD',
    database='RAG'
)
print('✅ Connected!')
db.close()
"
```

---

### Issue 4: Documents Table Empty or Missing ⚠️

**Symptoms:**

- Diagnostic shows "⚠️ Documents table is empty"
- Bot responds: "Maaf, saya tidak menemukan informasi yang relevan"

**Fix:**

You need to populate the documents table. Create a script to insert documents:

```bash
# First, check if table exists
mysql --host=gateway01.eu-central-1.prod.aws.tidbcloud.com \
      --port=4000 \
      --user=YOUR_USER.root \
      --password \
      RAG \
      -e "DESCRIBE documents;"
```

If the table doesn't exist, you need to run the setup SQL:

```bash
mysql --host=gateway01.eu-central-1.prod.aws.tidbcloud.com \
      --port=4000 \
      --user=YOUR_USER.root \
      --password \
      RAG < init_db.sql
```

---

## Step-by-Step Fix

### Step 1: Run Diagnostic

```bash
python test_chatbot_simple.py
```

### Step 2: Note Which Components Failed

### Step 3: Fix Each Component

**For Ollama:**

```bash
ollama serve  # Terminal 1
ollama pull gemma2:2b  # Terminal 2
```

**For Dependencies:**

```bash
pip install -r requirements.txt
```

**For Database:**

- Verify credentials in `.env`
- Check internet connection
- Verify TiDB Cloud cluster is running

**For Documents:**

- Populate documents table if empty

### Step 4: Restart Flask Backend

```bash
python app.py
```

### Step 5: Test Chatbot API

```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Apa itu daur ulang?",
    "user_id": "test"
  }'
```

Expected response:

```json
{
  "success": true,
  "response": "Bot response here...",
  "user_id": "test"
}
```

### Step 6: Test from Flutter

Rebuild and run the Flutter app.

---

## Testing Endpoints

### Health Check

```bash
curl http://localhost:5000/api/chatbot/health
```

Should show status of all components.

### Detailed Diagnosis

```bash
curl http://localhost:5000/api/chatbot/diagnose
```

Shows detailed information about each component.

### Send a Chat Message

```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Halo, apa kabar?",
    "user_id": "flutter_test"
  }'
```

---

## Logs to Check

### Flask Server Logs

Look at the terminal where `python app.py` is running. Check for:

- Connection errors
- Import errors
- Database errors
- Ollama connection errors

### Database Logs

If TiDB Cloud shows errors, check:

- Network access logs
- Query logs
- Connection logs

---

## Still Having Issues?

1. **Check Flask logs carefully** - They show the actual error
2. **Run diagnostic script** - It identifies the problem component
3. **Test each component separately:**
   - Ollama: `curl http://localhost:11434/api/tags`
   - Database: Use diagnostic script
   - Embedder: Run diagnostic script
4. **Check .env file** - Ensure all variables are set correctly
5. **Check internet connection** - Required for downloading embedder model and connecting to cloud DB

---

## Requirements.txt

Make sure your `requirements.txt` includes:

```
Flask==3.0.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
mysql-connector-python==8.2.0
sentence-transformers==2.2.2
torch==2.1.1
ollama==0.1.0
```

Install with:

```bash
pip install -r requirements.txt
```

---

## Quick Reference

| Component | Start Command   | Test Command                           |
| --------- | --------------- | -------------------------------------- |
| Ollama    | `ollama serve`  | `curl http://localhost:11434/api/tags` |
| Flask     | `python app.py` | `curl http://localhost:5000/api`       |
| Database  | (Cloud service) | Use diagnostic script                  |
| Embedder  | (Auto-load)     | Diagnostic script                      |

---

## Still Need Help?

Check these files for more context:

- `Ruang-Hijau-Backend/routes/chatbot_routes.py` - Chatbot API code
- `Ruang-Hijau-Backend/.env` - Configuration
- `Ruang-Hijau-Backend/requirements.txt` - Dependencies
- `ruang_hijau_app/lib/screens/chatbot_page.dart` - Flutter chatbot UI
