# 🚀 Chatbot Fix - Quick Start

## TL;DR - Do This Now

```bash
# 1. Navigate to backend
cd Ruang-Hijau-Backend

# 2. Run diagnostic (2-3 minutes)
python test_chatbot_simple.py

# 3. See what's broken, fix it based on results

# 4. Start Ollama (in new terminal)
ollama serve

# 5. Start Flask backend
python app.py

# 6. Test chatbot
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu daur ulang?", "user_id": "test"}'

# 7. Rebuild Flutter
cd ../ruang_hijau_app
flutter pub get
flutter run
```

## What Was Wrong

Your Flask backend was throwing unhandled exceptions that resulted in HTML 500 error pages. Now it returns proper JSON with error details.

## What Changed

- ✅ Better error handling in `chatbot_routes.py`
- ✅ New diagnostic script `test_chatbot_simple.py`
- ✅ New API test script `test_chatbot_api.py`
- ✅ New troubleshooting guide `CHATBOT_TROUBLESHOOTING.md`

## The 3 Most Common Issues

### 1. Ollama Not Running

```bash
# Check if it's running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### 2. Missing Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Connection Issue

- Check `.env` file has correct credentials
- Check `isrgrootx1.pem` exists
- Check internet connection

## How to Know It's Working

Run this:

```bash
curl http://localhost:5000/api/chatbot/health
```

You should see:

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

## Still Getting 500 Errors?

1. Check Flask terminal output - it shows the actual error
2. Run diagnostic: `python test_chatbot_simple.py`
3. Check the component that's failing
4. Fix that component
5. Restart Flask: `python app.py`
6. Try again

## Documentation

- 📖 **CHATBOT_FIX_SUMMARY.md** - What was changed and why
- 🔧 **CHATBOT_TROUBLESHOOTING.md** - Detailed troubleshooting guide
- 🧪 **test_chatbot_simple.py** - Automatic diagnostics
- 🧪 **test_chatbot_api.py** - API testing

## Need More Help?

Check the specific troubleshooting guide:

```bash
cat CHATBOT_TROUBLESHOOTING.md
```

Or look at Flask logs for the exact error when you run:

```bash
python app.py
```

The logs will tell you exactly what's wrong! 📋
