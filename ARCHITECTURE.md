# 📋 ARSITEKTUR PROJECT FLASK "RUANG HIJAU"

## Ringkasan Umum

Project ini adalah **Backend API untuk Platform Komunitas Lingkungan** yang dibangun dengan Flask. Sistem ini mendukung berbagai fitur termasuk:

- Manajemen pengguna & autentikasi
- Media sosial (posting, komentar)
- Kampanye & donasi
- Chatbot AI dengan RAG (Retrieval-Augmented Generation)
- Deteksi jenis sampah (Machine Learning)
- Admin dashboard
- Analisis sentimen feedback

---

## 🏗️ 1. ARSITEKTUR LAYERING

```
┌─────────────────────────────────────────┐
│         CLIENT (Frontend/Web)           │
└────────────────┬────────────────────────┘
                 │ HTTP/REST API
┌─────────────────────────────────────────┐
│    ROUTES LAYER (11 Blueprint Routes)   │
├──────────────────────────────────────────┤
│ • auth_routes.py         (Login/Register)│
│ • post_routes.py         (Feed/Posts)    │
│ • comment_routes.py      (Comments)      │
│ • campaign_routes.py     (Campaigns)     │
│ • donation_routes.py     (Donations)     │
│ • volunteer_routes.py    (Volunteers)    │
│ • chatbot_routes.py      (AI Chat + RAG) │
│ • waste_detection_routes (Waste ML)      │
│ • admin_routes.py        (Admin Panel)   │
│ • feedback_routes.py     (Feedback + NLP)│
│ • google_auth_routes.py  (OAuth Google)  │
└────────────┬─────────────────────────────┘
             │
┌────────────────────────────────────────┐
│    MODELS LAYER (Data Structures)      │
├──────────────────────────────────────────┤
│ • user_model.py      (User CRUD)        │
│ • post_model.py      (Post CRUD)        │
│ • comment_model.py   (Comment CRUD)     │
└────────────┬──────────────────────────┘
             │
┌────────────────────────────────────────┐
│    UTILITIES LAYER (Business Logic)    │
├──────────────────────────────────────────┤
│ • sentiment_analyzer.py (NLP Analysis)  │
│ • db_helper.py         (Query Helpers)  │
└────────────┬──────────────────────────┘
             │
┌────────────────────────────────────────┐
│    DATABASE LAYER (Persistence)        │
├──────────────────────────────────────────┤
│ MySQL (ruang_hijau)    - Main Database  │
│ TiDB Cloud (RAG DB)    - Embeddings     │
└────────────────────────────────────────┘
```

---

## ⚙️ 2. KOMPONEN UTAMA DAN FUNGSINYA

### A. APLIKASI INTI (app.py)

**Fungsi:** Bootstrap Flask application dan konfigurasi global

```python
Konfigurasi:
├── SECRET_KEY: Session management
├── MAX_CONTENT_LENGTH: 16MB (upload file limit)
├── UPLOAD_FOLDER: Direktori untuk file user
├── SESSION_PERMANENT: 24 jam session lifetime
└── CORS: Enabled untuk cross-origin requests
```

**Blueprint Registration:**

- Semua 11 routes di-register dengan prefix khusus
- Contoh: `auth_bp` → `/api/auth`

---

### B. DATABASE LAYER

#### 1. MySQL (ruang_hijau) - Main Database

```
Tabel Utama:
├── users          (Email, Password, Profile)
├── posts          (Content, Images, Timestamps)
├── comments       (Post Comments)
├── campaigns      (Green Initiatives)
├── donations      (Campaign Donations)
├── volunteers     (Volunteer Records)
├── feedback       (User Feedback + Sentiment)
└── admin_logs     (Admin Activity)
```

#### 2. TiDB Cloud (RAG Database) - Embeddings

```
Tabel:
├── embeddings     (Vector Data untuk RAG)
├── documents      (Knowledge Base)
└── qa_pairs       (Question-Answer Pairs)
```

#### Connection (db.py)

```python
def get_db():
    # MySQL connection menggunakan mysql.connector
    # Config dari .env file
```

---

### C. ROUTES & API ENDPOINTS

| Module                        | Endpoint                     | Fungsi               |
| ----------------------------- | ---------------------------- | -------------------- |
| **auth_routes.py**            | `POST /api/auth/login`       | Login pengguna       |
|                               | `POST /api/auth/register`    | Daftar akun baru     |
| **google_auth_routes.py**     | `POST /api/auth/google`      | OAuth Google         |
| **post_routes.py**            | `POST /api/posts/create`     | Buat post            |
|                               | `GET /api/posts/feed`        | Get timeline         |
|                               | `GET /api/posts/{id}`        | Get detail post      |
| **comment_routes.py**         | `POST /api/comments/add`     | Tambah komentar      |
|                               | `GET /api/comments/{id}`     | Get comments         |
| **campaign_routes.py**        | `POST /api/campaigns/create` | Buat kampanye        |
|                               | `GET /api/campaigns/list`    | List kampanye        |
| **donation_routes.py**        | `POST /api/donations/donate` | Donasi ke kampanye   |
| **volunteer_routes.py**       | `POST /api/volunteers/join`  | Daftar volunteer     |
| **chatbot_routes.py**         | `POST /api/chatbot/chat`     | Chat dengan AI       |
| **waste_detection_routes.py** | `POST /api/waste/detect`     | Deteksi jenis sampah |
| **feedback_routes.py**        | `POST /api/feedback/submit`  | Kirim feedback       |
| **admin_routes.py**           | `GET /admin/dashboard`       | Admin dashboard      |

---

## 🤖 3. FITUR AI/ML TERINTEGRASI

### A. CHATBOT RAG (Retrieval-Augmented Generation)

**File:** `routes/chatbot_routes.py`

#### Tahapan Proses:

```
User Question
    ↓
Load Embedder (BAAI/bge-m3) [Lazy Loading]
    ↓
Convert Query to Embedding (Vector)
    ↓
Search in TiDB Cloud (Vector Similarity Search)
    ↓
Retrieve Top-K Relevant Documents
    ↓
Format as Prompt Context
    ↓
Send to Ollama (Local LLM - gemma2:2b)
    ↓
Generate Response (Augmented by Retrieved Docs)
    ↓
Return JSON Response
```

#### Keunggulan:

- ✅ Jawaban berbasis knowledge base (tidak asal hallucinate)
- ✅ Embeddings tersimpan di TiDB Cloud (scalable)
- ✅ Model lokal (privacy, no API cost)
- ✅ Lazy loading (load model hanya saat dibutuhkan)

#### Performance:

- First request: 30-60 detik (embedder loading)
- Subsequent: 2-5 detik
- Timeout: 120 detik (Gunicorn)

---

### B. WASTE DETECTION (Computer Vision + ML)

**File:** `routes/waste_detection_routes.py`

#### Tahapan Proses:

```
User Upload Gambar Sampah
    ↓
Resize/Normalize Image (Pillow + NumPy)
    ↓
Load Pre-trained Model (MobileNetV2)
    ↓
Preprocess dengan ImageNet normalization
    ↓
Run Inference
    ↓
Decode Predictions (Top-5 confidence)
    ↓
Map ke Kategori Lokal (Organik/Anorganik/Kertas/Kaca/Logam)
    ↓
Return Classification + Sorting Bin Color
```

#### 5 Kategori Sampah:

| Jenis     | Warna Bin  | Contoh             | Keywords ML                 |
| --------- | ---------- | ------------------ | --------------------------- |
| Organik   | 🟢 Hijau   | Makanan, Daun      | banana, apple, leaf         |
| Anorganik | 🟡 Kuning  | Plastik, Styrofoam | plastic, bottle, foam       |
| Kertas    | 🔵 Biru    | Kardus, Koran      | paper, cardboard, newspaper |
| Kaca      | ⚪ Putih   | Botol, Gelas       | glass, bottle, jar          |
| Logam     | ⚫ Abu-abu | Kaleng, Besi       | can, metal, aluminum        |

**Fallback:** Jika TensorFlow tidak tersedia, gunakan keyword matching

---

### C. SENTIMENT ANALYSIS (NLP)

**File:** `utils/sentiment_analyzer.py`

#### Tahapan Proses:

```
User Feedback Text (Indonesian/English)
    ↓
Text Preprocessing (Lowercase, Remove Special Chars)
    ↓
Tokenization
    ↓
Check Against Positive/Negative Lexicon
    ↓
Apply Negation Rules (tidak/no reverses sentiment)
    ↓
Apply Intensifiers (sangat/very increases strength)
    ↓
Calculate Sentiment Score (-1.0 to 1.0)
    ↓
Classify: Negative / Neutral / Positive
```

#### Lexicon Coverage:

- 100+ positive words (baik, bagus, mantap, dll)
- 100+ negative words (jelek, buruk, kecewa, dll)
- Negation: tidak, bukan, tak, gak, enggak
- Intensifiers: sangat, very, super, banget

---

## 🔄 4. TAHAPAN INTEGRASI SISTEM

### Tahap 1: INITIALIZATION (Saat Server Start)

```
app.py
├── Load .env variables
│   └── DB credentials, API keys, URLs
├── Initialize Flask app
│   ├── Set SECRET_KEY
│   ├── Set upload folder
│   └── Configure session
├── Enable CORS
│   └── Allow requests dari semua origin
├── Import & Register 11 Blueprints
│   └── Map routes ke endpoints
└── Create upload directory jika belum ada
```

### Tahap 2: USER REQUEST (Request Masuk)

```
Client Request
    ↓
Flask Route Handler
    ├── Validate Input
    ├── Check Authentication (jika diperlukan)
    ├── Call Business Logic (Model/Utility)
    │   ├── Database queries (MySQL)
    │   ├── External API calls (Ollama, TiDB)
    │   └── ML Processing (TensorFlow, Embedder)
    ├── Format Response
    └── Return JSON + HTTP Status

    ↓
Response ke Client
```

### Tahap 3: DATABASE INTEGRATION

#### Untuk Standard CRUD:

```python
# Model Query
def create_post(user_id, title, content, image_url):
    conn = get_db()  # Get MySQL connection
    cursor = conn.cursor(dictionary=True)

    query = "INSERT INTO posts (user_id, title, content, image_url, created_at) VALUES (%s, %s, %s, %s, NOW())"
    cursor.execute(query, (user_id, title, content, image_url))

    conn.commit()
    conn.close()
```

#### Untuk RAG Chatbot:

```python
# Connect ke TiDB Cloud
conn = mysql.connector.connect(
    host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
    port=4000,
    user="mi3fQyPy1G6E9Jx.root",
    database="RAG",
    ssl_ca="isrgrootx1.pem"
)

# Query embeddings dengan vector similarity
SELECT document_text FROM embeddings
WHERE vector_similarity(embedding, query_embedding) > 0.75
LIMIT 5
```

### Tahap 4: ML INFERENCE

#### Pipeline Chatbot AI:

```
User Input: "Bagaimana cara membuat kompos?"
    ↓
Embedder (BAAI/bge-m3)
├── Lazy load model (first time only)
├── Convert to 768-dim vector
└── Output: [0.234, -0.156, 0.892, ...]
    ↓
Vector Search in TiDB
├── Find 5 most similar documents
├── Retrieve: [doc1, doc2, doc3, doc4, doc5]
└── Example: Panduan kompos, Waste management, Organic waste...
    ↓
Prompt Engineering
├── System: "Kamu adalah assistant lingkungan"
├── Context: "<Retrieved Documents>"
├── User Question: "<Original Query>"
└── Format: Few-shot examples + context
    ↓
Ollama (Local LLM)
├── Model: gemma2:2b (running locally)
├── Process prompt
└── Generate response
    ↓
Return:
{
    "response": "Untuk membuat kompos, Anda bisa...",
    "confidence": 0.87,
    "sources": ["doc1", "doc2"]
}
```

#### Pipeline Waste Detection:

```
User Upload: sampah.jpg
    ↓
Image Processing
├── Load with Pillow
├── Resize to 224x224
├── Convert to RGB
└── Normalize (ImageNet: mean=0.5, std=0.5)
    ↓
MobileNetV2 Inference
├── Forward pass through model
├── Output 1000 ImageNet classes
└── Get confidence scores
    ↓
Post-Processing
├── Decode top-5 predictions
├── Map to local categories
│   ├── If "apple" → Organik
│   ├── If "plastic" → Anorganik
│   └── etc.
└── Return bin color + percentage
    ↓
Return:
{
    "category": "organik",
    "bin_color": "Hijau",
    "confidence": 0.92,
    "alternatives": [...]
}
```

---

## ⚙️ 5. KONFIGURASI & DEPLOYMENT

### Environment Variables (.env)

```env
# Database MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=ruang_hijau

# TiDB Cloud (RAG)
RAG_DB_HOST=gateway01.eu-central-1.prod.aws.tidbcloud.com
RAG_DB_PORT=4000
RAG_DB_USER=mi3fQyPy1G6E9Jx.root
RAG_DB_PASSWORD=NKFZCVf7VuaM2WFv
RAG_DB_NAME=RAG

# Ollama (Local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# Session
SECRET_KEY=dev-secret-key-change-in-production-2025
```

### Production Deployment (Gunicorn)

```bash
# Command
gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --timeout 120 \              # Penting untuk chatbot!
    --workers 2 \                # Adjust sesuai CPU
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### Systemd Service (flask.service)

```ini
[Unit]
Description=Ruang Hijau Backend

[Service]
ExecStart=/path/to/venv/bin/gunicorn app:app --bind 0.0.0.0:8000 --timeout 120

[Install]
WantedBy=multi-user.target
```

---

## 📦 6. DEPENDENCIES

```
CORE FRAMEWORK:
├── Flask >= 2.3.0           (Web framework)
├── Flask-Cors >= 4.0.0      (CORS handling)
├── Werkzeug >= 2.3.0        (WSGI utilities)
└── python-dotenv >= 1.0.0   (Environment config)

DATABASE:
└── mysql-connector-python >= 8.0.0

AI/ML MODELS:
├── sentence-transformers >= 2.2.0  (Embeddings: BAAI/bge-m3)
├── tensorflow >= 2.10.0             (Deep learning)
├── tf-keras >= 3.0.0                (Keras API)
├── Pillow >= 9.0.0                  (Image processing)
├── numpy >= 1.21.0                  (Array operations)
└── ollama >= 0.1.0                  (Local LLM client)

HTTP CLIENT:
└── requests >= 2.31.0       (API calls)
```

---

## 🚀 7. FLOW LENGKAP: CONTOH REAL-WORLD

### Use Case: User Membuat Post dengan Gambar Sampah + Chat Tentangnya

#### 1. USER UPLOAD POST WITH IMAGE

```http
POST /api/posts/create
Content-Type: multipart/form-data

title=Sampah plastik di pantai
content=Kita perlu aksi nyata
image=<file binary>
```

**Process:**

- Routes: `post_routes.py`
- Validate input
- Save image → `/uploads/post_xyz.jpg`
- Insert post → MySQL
- Return: `{post_id: 123, image_url: "/uploads/post_xyz.jpg"}`

#### 2. USER UPLOAD GAMBAR KE WASTE DETECTOR

```http
POST /api/waste/detect
Content-Type: multipart/form-data

image=<file binary>
```

**Process:**

- Routes: `waste_detection_routes.py`
- Load image
- Run MobileNetV2 inference
- Map predictions → kategori lokal
- Return:

```json
{
    "category": "anorganik",
    "bin_color": "Kuning",
    "confidence": 0.94,
    "suggestions": [...]
}
```

#### 3. USER CHAT: "Bagaimana cara kurangi sampah plastik?"

```http
POST /api/chatbot/chat
Content-Type: application/json

{
    "message": "Bagaimana cara kurangi sampah plastik?"
}
```

**Process:**

- Routes: `chatbot_routes.py`
- Load embedder (first request: 30-60 sec)
- Convert query to vector: `[0.234, -0.156, ...]`
- Search in TiDB (vector search)
- Retrieve: 5 relevant docs (plastic reduction tips, etc.)
- Format prompt dengan retrieved docs
- Call Ollama API
- Ollama menghasilkan response augmented by RAG
- Return:

```json
{
  "response": "Untuk kurangi sampah plastik, Anda bisa...",
  "confidence": 0.89,
  "sources": ["doc_plastic_reduction", "doc_eco_tips"]
}
```

#### 4. USER SUBMIT FEEDBACK

```http
POST /api/feedback/submit
Content-Type: application/json

{
    "message": "Aplikasi ini sangat bagus dan membantu!"
}
```

**Process:**

- Routes: `feedback_routes.py`
- Use SentimentAnalyzer
- Analyze text: "sangat" (intensifier) + "bagus" (positive)
- Calculate score: 0.95 (very positive)
- Store feedback → MySQL dengan sentiment
- Return:

```json
{
  "message": "Terima kasih atas feedback Anda",
  "sentiment": "positive",
  "score": 0.95
}
```

---

## 🔐 8. SECURITY & BEST PRACTICES

| Aspek                | Implementasi                              |
| -------------------- | ----------------------------------------- |
| **CORS**             | Enabled dengan proper headers             |
| **File Upload**      | Max 16MB, sanitized filenames             |
| **Session**          | 24 hours timeout, SECRET_KEY protected    |
| **Database**         | Connection pooling, parameterized queries |
| **ML Models**        | Lazy loading (reduce memory footprint)    |
| **TiDB SSL**         | Certificate pinning (isrgrootx1.pem)      |
| **Gunicorn Timeout** | 120 sec (accommodate ML inference)        |

---

## 📊 9. RINGKASAN ARSITEKTUR

```
ARCHITECTURE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tier 0 (Presentation): REST API JSON
Tier 1 (Routes):       11 Blueprints
Tier 2 (Business):     Models + Utils
Tier 3 (Data):         MySQL + TiDB Cloud
Tier 4 (ML):           Ollama + TensorFlow + Embedder

INTEGRATIONS:
├── 🗄️  MySQL (Main DB)
├── ☁️  TiDB Cloud (Vector DB)
├── 🤖 Ollama (Local LLM)
├── 🧠 BAAI/bge-m3 (Embedder)
├── 📸 MobileNetV2 (Waste Detection)
└── 📝 Sentiment Analyzer (NLP)

RESPONSE TIME ESTIMATES:
├── Standard API: 50-200ms
├── Chatbot (first): 30-60s (model loading)
├── Chatbot (cached): 2-5s
└── Waste Detection: 1-3s
```

---

## 📁 Project Structure

```
Ruang-Hijau-Backend/
├── app.py                          # Main Flask application
├── db.py                           # Database connection handler
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── gunicorn_config.py              # Gunicorn configuration
├── flask.service                   # Systemd service file
│
├── models/                         # Data models
│   ├── user_model.py
│   ├── post_model.py
│   └── comment_model.py
│
├── routes/                         # API endpoints
│   ├── auth_routes.py
│   ├── post_routes.py
│   ├── comment_routes.py
│   ├── campaign_routes.py
│   ├── donation_routes.py
│   ├── volunteer_routes.py
│   ├── chatbot_routes.py           # RAG Chatbot
│   ├── waste_detection_routes.py   # Waste ML
│   ├── feedback_routes.py          # Sentiment Analysis
│   ├── admin_routes.py
│   └── google_auth_routes.py
│
├── utils/                          # Utility functions
│   ├── sentiment_analyzer.py       # NLP Module
│   └── db_helper.py
│
├── uploads/                        # User uploaded files
├── static/                         # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                      # HTML templates
├── migrations/                     # Database migrations
└── migrations/                     # Database SQL files
    ├── init_db.sql
    ├── ruang_hijau_database.sql
    └── ruang_hijau_advanced_features.sql
```

---

## 🔧 Cara Menjalankan Project

### Development Mode

```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp contoh\ env .env

# 4. Setup database
mysql -u root -p < init_db.sql

# 5. Run development server
python app.py
# Server akan berjalan di http://localhost:5000
```

### Production Mode

```bash
# 1. Setup production environment
sudo bash setup_service.sh

# 2. Check service status
sudo systemctl status flask

# 3. View logs
sudo journalctl -u flask -f
```

---

## 📝 Dokumentasi Tambahan

Untuk informasi lebih detail, lihat file-file dokumentasi berikut:

- `README_FIX.md` - Setup & troubleshooting guide
- `QUICK_FIX.md` - Quick start guide
- `GUNICORN_TIMEOUT_FIX.md` - Deployment configuration
- `ADMIN_PANEL_README.md` - Admin panel documentation

---

## ✅ Kesimpulan

Ruang Hijau Backend adalah sistem yang terintegrasi dengan:

- **Backend Framework:** Flask dengan Blueprint architecture
- **Database:** MySQL (main) + TiDB Cloud (vector embeddings)
- **AI Features:** RAG Chatbot, Waste Detection, Sentiment Analysis
- **Deployment:** Gunicorn with proper timeout configuration
- **Security:** CORS, file upload validation, session management

Arsitektur ini dirancang untuk **scalability**, **maintainability**, dan **feature extensibility** dalam mengembangkan platform komunitas lingkungan yang powerful.
