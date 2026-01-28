# 📋 DOKUMENTASI ARSITEKTUR SISTEM RUANG HIJAU

## Platform Komunitas Lingkungan Terintegrasi

**Last Updated:** January 2026  
**Project Status:** Capstone Project - Semester 5  
**Version:** 1.0

---

## 📑 DAFTAR ISI

1. [Executive Summary](#executive-summary)
2. [Arsitektur Sistem Keseluruhan](#arsitektur-sistem-keseluruhan)
3. [Komponen Utama](#komponen-utama)
4. [Data Flow & Integration](#data-flow--integration)
5. [Tahapan Proses Sistem](#tahapan-proses-sistem)
6. [Diagram Alur Lengkap](#diagram-alur-lengkap)
7. [Deployment Architecture](#deployment-architecture)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Security Architecture](#security-architecture)

---

## Executive Summary

**Ruang Hijau** adalah platform komunitas lingkungan yang menghubungkan:

- 👥 **Pengguna** (komunitas, volunteer, donator)
- 🌱 **Kampanye lingkungan** (reforestation, waste management, clean energy)
- 💰 **Sistem donasi** (untuk mendukung kampanye hijau)
- 🤖 **AI Chatbot** dengan RAG (Retrieval-Augmented Generation)
- 📸 **Waste Detection** menggunakan Computer Vision
- 💬 **Social Features** (posts, comments, discussions)
- 📊 **Admin Dashboard** untuk monitoring dan management

### Teknologi Stack

```
┌─────────────────────────────────────────────────────────┐
│                      TECH STACK                          │
├─────────────────────────────────────────────────────────┤
│ Frontend:          Flutter (Cross-platform Mobile)      │
│ Backend:           Flask (Python Web Framework)         │
│ Main Database:     MySQL (Relational Data)              │
│ Vector Database:   TiDB Cloud (Embeddings/RAG)          │
│ LLM Server:        Ollama (Local AI Model)              │
│ Embedder Model:    BAAI/bge-m3 (Multi-lingual)          │
│ Vision Model:      MobileNetV2 (Waste Detection)        │
│ Deployment:        Gunicorn + Systemd (Linux)           │
│ NLP:               Custom Sentiment Analyzer             │
└─────────────────────────────────────────────────────────┘
```

---

## Arsitektur Sistem Keseluruhan

### 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                                   │
│  ┌──────────────────┐          ┌──────────────────┐              │
│  │  Flutter Mobile  │          │   Web Browser    │              │
│  │  (Android/iOS)   │          │  (Admin Panel)   │              │
│  └────────┬─────────┘          └────────┬─────────┘              │
└───────────┼─────────────────────────────┼──────────────────────┘
            │ HTTP/HTTPS (REST API)      │
            │                             │
┌───────────┴─────────────────────────────┴──────────────────────┐
│                    API GATEWAY LAYER                             │
│  Port 8000 (Production) / Port 5000 (Development)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Gunicorn (WSGI Server) / Flask Dev Server              │  │
│  │  - CORS Enabled                                          │  │
│  │  - File Upload Handler (Max 16MB)                        │  │
│  │  - Session Management (24h timeout)                      │  │
│  │  - Error Handling & Logging                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────────────────────────────┘
            │
┌───────────┴──────────────────────────────────────────────────────┐
│                  APPLICATION LAYER (Flask)                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              11 Blueprint Routes (APIs)                      │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │ auth_routes          - Login, Register, OAuth Google  │ │ │
│  │  │ post_routes          - Feed, Create, Edit Posts       │ │ │
│  │  │ comment_routes       - Comments Management            │ │ │
│  │  │ campaign_routes      - Campaign CRUD                  │ │ │
│  │  │ donation_routes      - Donation Processing            │ │ │
│  │  │ volunteer_routes     - Volunteer Registration         │ │ │
│  │  │ chatbot_routes       - RAG Chatbot (AI)               │ │ │
│  │  │ waste_detection_routes - Waste Classification (CV)   │ │ │
│  │  │ feedback_routes      - Feedback + Sentiment Analysis  │ │ │
│  │  │ admin_routes         - Admin Dashboard & Management   │ │ │
│  │  │ google_auth_routes   - Google OAuth Integration       │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │         Business Logic Layer (Models & Utils)                │ │
│  │  ┌────────────────┐  ┌──────────────────┐                  │ │
│  │  │ Models:        │  │ Utilities:       │                  │ │
│  │  │ - user_model   │  │ - sentiment_     │                  │ │
│  │  │ - post_model   │  │   analyzer       │                  │ │
│  │  │ - comment_mdl  │  │ - db_helper      │                  │ │
│  │  └────────────────┘  │ - file_handler   │                  │ │
│  │                      └──────────────────┘                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────┬──────────────────────────────────────────────────────┘
            │
     ┌──────┴──────────────────────┬─────────────────────┬──────────┐
     │                              │                     │          │
┌────┴─────┐              ┌────────┴────────┐    ┌──────┴────┐  ┌──┴───┐
│  MySQL   │              │  TiDB Cloud     │    │  Ollama   │  │Local │
│ (Main    │              │  (Vector DB)    │    │  (LLM)    │  │Files │
│Database) │              │  (Embeddings)   │    │           │  │Upld  │
└──────────┘              └─────────────────┘    └───────────┘  └──────┘
```

### 2. LAYERED ARCHITECTURE

```
┌──────────────────────────────────────────────────────┐
│           PRESENTATION LAYER                          │
│  • Flutter Mobile App (Screens, UI Components)      │
│  • Web Admin Dashboard (HTML/JS/CSS)                │
│  • REST API JSON Responses                          │
└──────────────────────────────────────────────────────┘
                       ↓ HTTP/REST
┌──────────────────────────────────────────────────────┐
│           API LAYER (Flask Blueprints)               │
│  • Request Validation & Authentication              │
│  • Error Handling & Response Formatting             │
│  • CORS & Session Management                        │
│  • File Upload Processing                           │
└──────────────────────────────────────────────────────┘
                       ↓ Function Calls
┌──────────────────────────────────────────────────────┐
│       BUSINESS LOGIC LAYER (Models & Utils)          │
│  • User Management & Authentication                 │
│  • Post/Comment Operations                          │
│  • Campaign & Donation Logic                        │
│  • Sentiment Analysis                               │
│  • Volunteer Management                             │
└──────────────────────────────────────────────────────┘
                       ↓ Database Queries
┌──────────────────────────────────────────────────────┐
│         DATA LAYER (Database Access)                 │
│  • MySQL Connector (Main Database)                  │
│  • TiDB Cloud Connector (Vector Embeddings)         │
│  • Connection Pooling                               │
│  • Query Execution & Transaction Management         │
└──────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│      DATABASE LAYER (Persistent Storage)             │
│  • MySQL Database (ruang_hijau)                     │
│  • TiDB Cloud Database (RAG - Vector Embeddings)    │
│  • File Storage (/uploads)                          │
└──────────────────────────────────────────────────────┘
```

---

## Komponen Utama

### 1. Backend Flask Application (app.py)

**Fungsi Utama:**

```
Bootstrap Flask → Load Config → Register Blueprints → Setup CORS → Start Server
```

**Konfigurasi Critical:**

```python
Configuration Points:
├── SECRET_KEY          → Session encryption key
├── MAX_CONTENT_LENGTH  → File upload limit (16MB)
├── UPLOAD_FOLDER       → File storage directory
├── SESSION_PERMANENT   → 24 hours session timeout
├── SESSION_COOKIE_SECURE → HTTPS only (production)
├── SESSION_COOKIE_SAMESITE → CSRF protection
└── CORS_ORIGINS        → Allowed domains
```

### 2. Database Layer

#### MySQL (Main Database)

```
Database: ruang_hijau
├── Authentication & Users
│   └── users (id, email, password, profile, created_at)
├── Social Features
│   ├── posts (id, user_id, title, content, image, created_at)
│   ├── comments (id, post_id, user_id, content, created_at)
│   └── likes (id, post_id, user_id)
├── Environmental Campaigns
│   ├── campaigns (id, title, description, goal, current_donation)
│   ├── donations (id, campaign_id, user_id, amount, date)
│   └── volunteers (id, campaign_id, user_id, status, joined_at)
├── User Feedback & Analytics
│   ├── feedback (id, user_id, content, sentiment, created_at)
│   ├── notifications (id, user_id, type, content, read)
│   └── admin_logs (id, admin_id, action, details, timestamp)
└── Admin Management
    └── admin_users (id, email, password, role, permissions)
```

#### TiDB Cloud (Vector Database - RAG)

```
Database: RAG
├── embeddings
│   ├── id (Primary Key)
│   ├── document_text (Knowledge base content)
│   ├── embedding (Vector - 768 dimensions)
│   ├── category (waste/environment/tips)
│   └── created_at
└── qa_pairs (optional)
    ├── question
    ├── answer
    └── embedding
```

### 3. AI/ML Components

#### A. Chatbot RAG Pipeline

```
FLOW: User Question → Embedder → Vector Search → LLM → Response

User Input: "Bagaimana cara mengurangi sampah plastik?"
    ↓
[1] EMBEDDER PHASE (BAAI/bge-m3)
    ├── Load model (lazy - first request only)
    ├── Tokenize input
    ├── Generate 768-dimensional vector
    └── Result: [0.234, -0.156, 0.892, ..., 0.145]
    ↓
[2] VECTOR SEARCH PHASE (TiDB Cloud)
    ├── Similarity search in embeddings table
    ├── Find top-5 most similar documents
    └── Retrieved documents: [
        "Panduan mengurangi plastik di rumah",
        "Alternatif pengganti plastik",
        "Waste management dan sorting",
        "Eco-friendly shopping tips",
        "Plastik dan dampak lingkungan"
    ]
    ↓
[3] PROMPT ENGINEERING PHASE
    ├── System prompt: "Anda adalah chatbot ahli lingkungan"
    ├── Context: <Retrieved documents>
    ├── Few-shot examples
    └── User question: "Bagaimana cara mengurangi..."
    ↓
[4] LLM INFERENCE PHASE (Ollama - gemma2:2b)
    ├── Model: gemma2:2b (running locally)
    ├── Processing time: 2-5 seconds (cached)
    └── Generate contextual response
    ↓
[5] RESPONSE FORMATTING
    └── JSON Response: {
        "response": "Untuk mengurangi sampah plastik...",
        "confidence": 0.87,
        "sources": ["doc_id_1", "doc_id_2"],
        "timestamp": "2025-01-28T10:30:00Z"
    }
```

**Performance Characteristics:**

| Skenario            | Waktu     | Catatan                    |
| ------------------- | --------- | -------------------------- |
| First request       | 30-60s    | Model loading + processing |
| Subsequent requests | 2-5s      | Model cached in memory     |
| Timeout             | 120s      | Gunicorn timeout setting   |
| Vector search       | 500-800ms | TiDB cloud latency         |

#### B. Waste Detection Pipeline

```
FLOW: Image Upload → Image Processing → Model Inference → Classification

User Upload: sampah.jpg (file binary)
    ↓
[1] IMAGE VALIDATION & LOADING
    ├── Check file extension (.jpg, .png, .webp)
    ├── Verify file size (< 16MB)
    ├── Load with PIL/Pillow
    └── Convert to RGB (if needed)
    ↓
[2] IMAGE PREPROCESSING
    ├── Resize to 224x224 (MobileNetV2 input)
    ├── Normalize pixel values
    │   └── (image - 127.5) / 127.5
    ├── Convert to tensor
    └── Add batch dimension: (1, 224, 224, 3)
    ↓
[3] MODEL INFERENCE (MobileNetV2)
    ├── Load pre-trained model (ImageNet weights)
    ├── Forward pass through network
    ├── Get softmax probabilities
    └── Top-5 predictions: [
        {"class": "banana", "confidence": 0.45},
        {"class": "apple", "confidence": 0.25},
        {"class": "leaf", "confidence": 0.15},
        ...
    ]
    ↓
[4] CLASSIFICATION MAPPING
    ├── Map predictions to local categories:
    │   ├── "banana", "apple", "leaf" → ORGANIK 🟢
    │   ├── "plastic", "bottle" → ANORGANIK 🟡
    │   ├── "paper", "cardboard" → KERTAS 🔵
    │   ├── "glass", "jar" → KACA ⚪
    │   └── "metal", "can" → LOGAM ⚫
    └── Calculate weighted confidence
    ↓
[5] RESPONSE FORMATTING
    └── JSON Response: {
        "category": "organik",
        "bin_color": "Hijau",
        "confidence": 0.92,
        "alternatives": [...],
        "tips": "Simpan di tempat kering..."
    }
```

**Supported Waste Categories:**

```
┌──────────────────────────────────────────────────────┐
│         WASTE CLASSIFICATION SYSTEM                   │
├──────────────────────────────────────────────────────┤
│ 🟢 ORGANIK (Green Bin)                               │
│   Contoh: Sisa makanan, daun, ranting, sayur        │
│   Pemrosesan: Kompos, pengurai biologis             │
│   Masa hancur: 1-3 bulan                            │
│                                                      │
│ 🟡 ANORGANIK (Yellow Bin)                            │
│   Contoh: Plastik, styrofoam, tas plastik           │
│   Pemrosesan: Daur ulang, pengecilan                │
│   Masa hancur: 100+ tahun                           │
│                                                      │
│ 🔵 KERTAS (Blue Bin)                                │
│   Contoh: Kardus, koran, majalah, kemasan           │
│   Pemrosesan: Daur ulang pulp                       │
│   Masa hancur: 2-6 bulan                            │
│                                                      │
│ ⚪ KACA (White Bin)                                  │
│   Contoh: Botol, gelas, kemasan kaca               │
│   Pemrosesan: Daur ulang atau pengecilan           │
│   Masa hancur: 1000+ tahun                          │
│                                                      │
│ ⚫ LOGAM (Gray Bin)                                  │
│   Contoh: Kaleng, besi, aluminium                   │
│   Pemrosesan: Daur ulang lebur                      │
│   Masa hancur: 50-100 tahun                         │
└──────────────────────────────────────────────────────┘
```

#### C. Sentiment Analysis Pipeline

```
FLOW: Text Input → Preprocessing → Analysis → Classification

User Feedback: "Aplikasi ini sangat bagus dan membantu!"
    ↓
[1] TEXT PREPROCESSING
    ├── Lowercase: "aplikasi ini sangat bagus dan membantu!"
    ├── Remove special characters
    ├── Remove extra spaces
    └── Tokenization: ["aplikasi", "ini", "sangat", "bagus", ...]
    ↓
[2] LEXICON MATCHING
    ├── Positive lexicon (100+ words):
    │   └── "bagus" → +0.7 score
    ├── Negative lexicon (100+ words):
    │   └── (no negative words found)
    └── Intensifiers:
        └── "sangat" → multiplier 1.2x
    ↓
[3] NEGATION HANDLING
    ├── Check for negation words: [tidak, bukan, tak, gak]
    ├── Rule: negation + positive = neutral
    ├── Rule: negation + negative = positive
    └── No negation found → proceed
    ↓
[4] SCORE CALCULATION
    ├── Base score: 0.7 (bagus)
    ├── Intensifier boost: 0.7 × 1.2 = 0.84
    ├── Negation check: N/A
    └── Final score: 0.84
    ↓
[5] CLASSIFICATION
    ├── If score > 0.5 → POSITIVE 😊
    ├── If -0.5 ≤ score ≤ 0.5 → NEUTRAL 😐
    └── If score < -0.5 → NEGATIVE 😞
    ↓
[6] RESPONSE
    └── {
        "sentiment": "positive",
        "score": 0.84,
        "keywords": ["bagus", "membantu"],
        "suggestion": "Terima kasih atas feedback!"
    }
```

---

## Data Flow & Integration

### 1. Complete User Registration & Login Flow

```
┌─────────────────────────────────────────────────────────┐
│           USER REGISTRATION FLOW                         │
└─────────────────────────────────────────────────────────┘

[CLIENT]
  ↓ POST /api/auth/register
  ├── email: user@example.com
  ├── password: secure_password123
  ├── username: userhandle
  └── full_name: Full Name

[BACKEND - auth_routes.py]
  ↓ Input Validation
  ├── Validate email format
  ├── Check password strength (min 8 chars)
  ├── Check username availability
  └── Return error if invalid

  ↓ Duplicate Check
  └── Query: SELECT * FROM users WHERE email = ?

  ↓ Password Hashing
  └── Hash using werkzeug.security.generate_password_hash

  ↓ Database Insert
  └── INSERT INTO users (email, password_hash, username, full_name, created_at) VALUES (...)

  ↓ Session Management
  └── Create session token

[RESPONSE]
  ← 201 Created
  {
    "success": true,
    "user_id": 123,
    "message": "Pendaftaran berhasil",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }

[CLIENT]
  → Save token to local storage
  → Redirect to login or home page
```

### 2. Post Creation with Image Upload Flow

```
┌─────────────────────────────────────────────────────────┐
│         POST CREATION WITH IMAGE FLOW                    │
└─────────────────────────────────────────────────────────┘

[CLIENT]
  ↓ POST /api/posts/create (multipart/form-data)
  ├── title: "Sampah plastik di pantai"
  ├── content: "Kita perlu aksi nyata..."
  ├── image: <binary file>
  └── token: <auth token>

[BACKEND - post_routes.py]
  ↓ Authentication Check
  ├── Verify token validity
  ├── Extract user_id from token
  └── Return 401 if invalid

  ↓ File Validation
  ├── Check file type (JPEG, PNG, WebP only)
  ├── Check file size (< 16MB)
  ├── Scan for malware (optional)
  └── Return 400 if invalid

  ↓ File Processing
  ├── Generate unique filename: post_123_xyz.jpg
  ├── Compress image (quality: 85%)
  ├── Save to /uploads/posts/
  └── Store path: /uploads/posts/post_123_xyz.jpg

  ↓ Database Transaction
  BEGIN TRANSACTION
    ├── INSERT INTO posts (user_id, title, content, image_url, created_at)
    │   VALUES (user_id, title, content, image_url, NOW())
    ├── Get inserted post_id (last_insert_id)
    └── Retrieve created post details
  COMMIT

  ↓ Cache Update (optional)
  └── Invalidate feed cache for followers

[RESPONSE]
  ← 201 Created
  {
    "success": true,
    "post_id": 456,
    "image_url": "https://api.ruanghijau.com/uploads/posts/post_123_xyz.jpg",
    "created_at": "2025-01-28T10:30:00Z"
  }

[CLIENT]
  → Display post in feed
  → Show success notification
```

### 3. Chatbot Interaction with RAG

```
┌──────────────────────────────────────────────────────────┐
│        CHATBOT RAG INTERACTION FLOW                       │
└──────────────────────────────────────────────────────────┘

[CLIENT]
  ↓ POST /api/chatbot/chat
  {
    "message": "Bagaimana cara membuat kompos?",
    "user_id": 123,
    "session_id": "session_xyz"
  }

[BACKEND - chatbot_routes.py]
  ↓ Input Validation & Logging
  ├── Validate message length (1-500 chars)
  ├── Log user message for analytics
  └── Check user quota (max 50 questions/day)

  ↓ Embedder Loading (if not cached)
  ├── IF model not in memory:
  │   ├── Download BAAI/bge-m3 (1.2GB)
  │   ├── Load to GPU (or CPU if no GPU)
  │   └── Cache in memory for reuse
  └── Time: first request 30-60s, subsequent 0s

  ↓ Query Embedding
  ├── Tokenize message
  ├── Generate embedding (768-dim vector)
  └── Result: [0.234, -0.156, 0.892, ..., 0.145]

  ↓ Vector Search in TiDB Cloud
  ├── CONNECT: gateway01.eu-central-1.prod.aws.tidbcloud.com:4000
  ├── QUERY: SELECT document_text FROM embeddings
  │   WHERE vector_similarity(embedding, query_emb) > 0.7
  │   ORDER BY similarity DESC
  │   LIMIT 5
  ├── Retrieved documents: [
  │   "Panduan kompos organik",
  │   "Waste management terpadu",
  │   "Bahan-bahan kompos",
  │   "Proses dekomposisi alami",
  │   "Tips mempercepat kompos"
  │ ]
  └── Execution time: 500-800ms

  ↓ Prompt Engineering
  ├── System Role: "Kamu adalah chatbot ahli lingkungan Indonesia"
  ├── Retrieved Context: <5 documents>
  ├── Few-shot examples (2-3 examples)
  └── Final Prompt:
      """
      [SYSTEM]
      Kamu adalah chatbot ahli lingkungan...
      [CONTEXT]
      Informasi relevan:
      1. Panduan kompos organik: ...
      2. Waste management: ...
      ...
      [USER]
      Bagaimana cara membuat kompos?
      [ASSISTANT]
      """

  ↓ LLM Inference (Ollama)
  ├── MODEL: gemma2:2b
  ├── API: POST http://localhost:11434/api/generate
  ├── Parameters:
  │   ├── temperature: 0.7
  │   ├── top_p: 0.9
  │   ├── max_tokens: 512
  │   └── timeout: 60s
  └── Time: 2-5 seconds

  ↓ Response Generation
  └── Generated text:
      "Untuk membuat kompos, Anda bisa:
       1. Kumpulkan sampah organik...
       2. Siapkan wadah/pit...
       3. Lapisi dengan tanah...
       ..."

  ↓ Post-processing
  ├── Clean response (remove extra whitespace)
  ├── Extract key points
  ├── Generate confidence score (0-1)
  └── Format source attribution

  ↓ Database Logging
  └── INSERT INTO chatbot_history (user_id, question, answer, sources, confidence, timestamp)

[RESPONSE]
  ← 200 OK
  {
    "response": "Untuk membuat kompos...",
    "confidence": 0.87,
    "sources": [
      {"id": "doc_1", "title": "Panduan kompos organik", "relevance": 0.95},
      {"id": "doc_2", "title": "Waste management", "relevance": 0.88}
    ],
    "follow_up_suggestions": [
      "Berapa lama proses kompos?",
      "Apa manfaat kompos?"
    ],
    "timestamp": "2025-01-28T10:30:00Z"
  }

[CLIENT]
  → Display response in chat UI
  → Show source citations
  → Enable user feedback (helpful/not helpful)
  → Offer follow-up questions
```

### 4. Waste Detection Image Classification Flow

```
┌──────────────────────────────────────────────────────────┐
│      WASTE DETECTION CLASSIFICATION FLOW                  │
└──────────────────────────────────────────────────────────┘

[CLIENT]
  ↓ POST /api/waste/detect (multipart/form-data)
  {
    "image": <binary file>,
    "user_id": 123
  }

[BACKEND - waste_detection_routes.py]
  ↓ File Validation
  ├── Check extension: [.jpg, .jpeg, .png, .webp]
  ├── Check size: < 5MB
  ├── Verify MIME type
  └── Reject if invalid

  ↓ Image Loading & Basic Preprocessing
  ├── Load with PIL: Image.open(file)
  ├── Convert to RGB (if RGBA)
  ├── Resize to 224x224 (MobileNetV2 input)
  └── Log processing start

  ↓ Model Loading (if not cached)
  ├── IF model not in memory:
  │   ├── Load MobileNetV2 (ImageNet weights)
  │   ├── Load to GPU (or CPU)
  │   └── Cache for reuse
  └── First request: 2-5s load time

  ↓ Image Normalization
  ├── Convert to numpy array
  ├── Apply ImageNet normalization:
  │   ├── mean = [0.485, 0.456, 0.406]
  │   ├── std = [0.229, 0.224, 0.225]
  │   └── normalized = (image - mean) / std
  ├── Add batch dimension: (1, 224, 224, 3)
  └── Convert to float32

  ↓ Model Inference
  ├── Pass through MobileNetV2
  ├── Get 1000 ImageNet class probabilities
  ├── Apply softmax normalization
  └── Extract top-5 predictions: [
      {"class_id": 954, "class": "banana", "prob": 0.45},
      {"class_id": 953, "class": "apple", "prob": 0.25},
      ...
    ]

  ↓ Category Mapping
  ├── Define mapping dictionary:
  │   {
  │     "ORGANIK": ["apple", "banana", "leaf", "carrot", ...],
  │     "ANORGANIK": ["plastic", "bottle", "styrofoam", ...],
  │     "KERTAS": ["paper", "cardboard", "newspaper", ...],
  │     "KACA": ["glass", "jar", "bottle", ...],
  │     "LOGAM": ["can", "metal", "aluminum", ...]
  │   }
  └── Match predictions to categories

  ↓ Classification Logic
  ├── For each top-5 prediction:
  │   ├── Check if class matches any category
  │   ├── If match found, accumulate confidence
  │   └── Else, continue to next prediction
  ├── Select category with highest accumulated confidence
  └── Calculate certainty score

  ↓ Category Details Retrieval
  ├── Query database for category info:
  │   ├── bin_color: 🟢 (green)
  │   ├── sorting_instructions: "Simpan di tempat kering..."
  │   ├── recyclability: "Dapat didaur ulang"
  │   └── estimated_decomposition: "1-3 bulan"

  ↓ Alternative Classifications
  ├── Get top-2 alternative categories
  ├── Calculate confidence for each
  └── Format for user information

  ↓ AI Tips Generation (optional)
  ├── IF confidence < 0.8:
  │   └── Generate helpful tips based on category
  ├── Tips include:
  │   ├── How to dispose properly
  │   ├── Environmental impact
  │   └── Recycling options

  ↓ Database Logging
  ├── INSERT INTO waste_detections
  │   (user_id, image_path, detected_category, confidence, timestamp)
  ├── Optionally store for analytics
  └── Track classification accuracy

[RESPONSE]
  ← 200 OK
  {
    "success": true,
    "classification": {
      "primary_category": "organik",
      "bin_color": "Hijau",
      "confidence": 0.92,
      "confidence_percentage": "92%"
    },
    "alternatives": [
      {
        "category": "kertas",
        "confidence": 0.06,
        "bin_color": "Biru"
      },
      {
        "category": "anorganik",
        "confidence": 0.02,
        "bin_color": "Kuning"
      }
    ],
    "tips": {
      "disposal": "Simpan di wadah tertutup sebelum proses kompos",
      "environmental_impact": "Bahan organik dapat terurai secara alami dalam 1-3 bulan",
      "recycling_options": "Bisa dikompos atau digunakan sebagai pupuk organik"
    },
    "predictions": [
      {"class": "apple", "confidence": 0.45},
      {"class": "banana", "confidence": 0.25},
      {"class": "leaf", "confidence": 0.15}
    ],
    "processed_time_ms": 850,
    "timestamp": "2025-01-28T10:30:00Z"
  }

[CLIENT]
  → Display classification with bin color
  → Show tips and recommendations
  → Enable photo retake if unsure
  → Log for user's waste classification history
```

### 5. Donation & Campaign Management Flow

```
┌──────────────────────────────────────────────────────────┐
│       DONATION & CAMPAIGN INTEGRATION FLOW                │
└──────────────────────────────────────────────────────────┘

[CLIENT]
  ↓ POST /api/donations/donate
  {
    "campaign_id": 5,
    "amount": 100000,  // in IDR
    "payment_method": "gopay",
    "donor_id": 123
  }

[BACKEND - donation_routes.py]
  ↓ Campaign Validation
  ├── Query: SELECT * FROM campaigns WHERE id = ?
  ├── Verify campaign is active
  ├── Check if goal already reached
  └── Return error if inactive

  ↓ Donor Verification
  ├── Verify donor authentication
  ├── Check donor status (banned/active)
  └── Validate minimum donation (min 10k IDR)

  ↓ Payment Gateway Integration
  ├── API Call: Midtrans / GoPay API
  ├── Create transaction:
  │   ├── order_id: donation_123_2025_01_28
  │   ├── gross_amount: 100000
  │   ├── payment_method: gopay
  │   └── customer: {name, email}
  ├── Get payment token / URL
  └── Return to client for payment

[CLIENT]
  ↓ Redirect to payment page
  → User completes payment

[PAYMENT CALLBACK]
  ↓ Webhook: POST /api/donations/callback
  {
    "order_id": "donation_123_...",
    "transaction_status": "settlement",
    "gross_amount": 100000
  }

[BACKEND - donation_routes.py]
  ↓ Verify Payment Status
  ├── Validate webhook signature
  ├── Verify transaction with payment gateway
  └── Check status: settlement/pending/failed

  ↓ Update Database
  BEGIN TRANSACTION
    ├── UPDATE donations SET status = 'completed', payment_date = NOW()
    ├── UPDATE campaigns SET current_donation = current_donation + 100000
    ├── INSERT INTO admin_logs (action, details, timestamp)
    ├── IF campaign goal reached:
    │   ├── UPDATE campaigns SET status = 'completed'
    │   └── Notify campaign creator
    └── COMMIT

  ↓ Notification & Rewards
  ├── Send confirmation email to donor
  ├── Create notification: "Donasi berhasil"
  ├── Update donor's donation history
  └── Award badges (if applicable)

  ↓ Analytics Update
  └── Log donation for campaign analytics

[RESPONSE]
  ← 200 OK
  {
    "success": true,
    "donation_id": 789,
    "message": "Terima kasih atas donasi Anda",
    "campaign_name": "Program Penghijauan",
    "amount_donated": 100000,
    "campaign_progress": "45%"
  }

[CLIENT]
  → Show success screen
  → Display donation certificate
  → Offer social sharing
```

---

## Tahapan Proses Sistem

### FASE 1: INITIALIZATION (Server Startup)

```
START SERVER
  ↓
[1] Load Environment Variables (.env)
    ├── DB credentials
    ├── API keys (Google, Payment gateway)
    ├── LLM model names
    ├── Session secret
    └── CORS allowed origins
    ↓
[2] Initialize Flask Application
    ├── Create Flask app instance
    ├── Set configuration:
    │   ├── SECRET_KEY = env['SECRET_KEY']
    │   ├── MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    │   ├── UPLOAD_FOLDER = './uploads'
    │   └── SESSION_PERMANENT = False
    ├── Create upload folder if not exists
    └── Set error handlers
    ↓
[3] Enable CORS
    ├── Configure CORS with allowed origins
    ├── Set credentials: True
    └── Allow headers: Content-Type, Authorization
    ↓
[4] Register Database Connections
    ├── Test MySQL connection
    ├── Test TiDB Cloud connection
    └── Log connection status
    ↓
[5] Import & Register 11 Blueprints
    ├── from routes import:
    │   ├── auth_bp
    │   ├── post_bp
    │   ├── comment_bp
    │   ├── campaign_bp
    │   ├── donation_bp
    │   ├── volunteer_bp
    │   ├── chatbot_bp
    │   ├── waste_detection_bp
    │   ├── feedback_bp
    │   ├── admin_bp
    │   └── google_auth_bp
    ├── Register with app:
    │   └── app.register_blueprint(auth_bp, url_prefix='/api/auth')
    └── Register all blueprints similarly
    ↓
[6] Initialize Lazy-Load Components
    ├── Embedder model: BAAI/bge-m3 (on demand)
    ├── LLM model: gemma2:2b via Ollama (on demand)
    ├── Vision model: MobileNetV2 (on demand)
    └── Sentiment analyzer: Load lexicons to memory
    ↓
[7] Start Gunicorn/Flask Server
    ├── Bind to 0.0.0.0:8000 (production) or 0.0.0.0:5000 (dev)
    ├── Set workers: 2-4 (production)
    ├── Set timeout: 120 seconds (for AI tasks)
    ├── Enable logging
    └── Log: "Server running on..."
    ↓
SERVER READY FOR REQUESTS
```

### FASE 2: REQUEST PROCESSING (Per API Call)

```
INCOMING REQUEST
  ↓
[1] ROUTING & MIDDLEWARE
    ├── Flask matches URL to blueprint
    ├── Apply middleware:
    │   ├── CORS headers check
    │   ├── Content-Type validation
    │   └── Request logging
    └── Route to correct handler
    ↓
[2] AUTHENTICATION (if required)
    ├── Extract token from header
    ├── Validate token signature
    ├── Check token expiration
    ├── Extract user_id from claims
    └── Attach user context to request
    ↓
[3] INPUT VALIDATION
    ├── Validate JSON schema
    ├── Sanitize input strings
    ├── Verify enum values
    ├── Check numeric ranges
    └── Return 400 if invalid
    ↓
[4] BUSINESS LOGIC EXECUTION
    ├── Call appropriate model/service
    ├── Execute database queries
    ├── Handle external API calls
    ├── Process file uploads (if any)
    └── Execute AI/ML (if needed)
    ↓
[5] DATABASE TRANSACTION
    ├── BEGIN TRANSACTION
    ├── Execute queries
    ├── Commit or rollback
    └── Handle transaction errors
    ↓
[6] RESPONSE FORMATTING
    ├── Serialize data to JSON
    ├── Add metadata (timestamps, IDs)
    ├── Add status codes
    └── Set response headers
    ↓
[7] ERROR HANDLING
    ├── IF exception occurs:
    │   ├── Log error details
    │   ├── Format error response
    │   ├── Return appropriate HTTP status
    │   └── Avoid exposing sensitive info
    └── ELSE continue to response
    ↓
SEND RESPONSE TO CLIENT
```

### FASE 3: AI/ML TASK EXECUTION

```
AI REQUEST RECEIVED (Chatbot or Waste Detection)
  ↓
[1] MODEL LOADING (First Request Only)
    ├── Check if model in memory
    ├── IF NOT in memory:
    │   ├── Download model weights (if needed)
    │   ├── Load to RAM/VRAM
    │   ├── Compile model
    │   └── Cache in memory
    └── Execution time: 5-60 seconds
    ↓
[2] INPUT PREPROCESSING
    ├── For Chatbot:
    │   └── Tokenize text input
    ├── For Waste Detection:
    │   ├── Load image file
    │   ├── Resize to model input size
    │   └── Normalize pixel values
    └── Execution time: 100-500ms
    ↓
[3] VECTOR GENERATION / INFERENCE
    ├── For Chatbot (Embedder):
    │   ├── Convert text to embedding vector
    │   ├── Output: 768-dimensional vector
    │   └── Time: 500-1000ms
    ├── For Waste (Vision Model):
    │   ├── Forward pass through network
    │   ├── Get softmax probabilities
    │   └── Time: 100-500ms
    └── For external APIs:
        └── Call Ollama / TiDB / other services
    ↓
[4] POST-PROCESSING
    ├── Decode predictions
    ├── Filter by confidence threshold
    ├── Sort by relevance
    └── Time: 50-200ms
    ↓
[5] CONTEXT RETRIEVAL (for RAG)
    ├── Query vector database
    ├── Retrieve top-K similar items
    ├── Format as context
    └── Time: 500-800ms
    ↓
[6] LLM GENERATION (if needed)
    ├── Format prompt with context
    ├── Call Ollama API
    ├── Stream or batch response
    └── Time: 2-5 seconds
    ↓
[7] RESPONSE COMPILATION
    ├── Format results
    ├── Add confidence scores
    ├── Add metadata
    └── Prepare JSON response
    ↓
RETURN AI RESPONSE
```

### FASE 4: DATABASE PERSISTENCE

```
DATABASE OPERATION
  ↓
[1] CONNECTION HANDLING
    ├── Get connection from pool
    ├── Create cursor
    └── Set transaction level
    ↓
[2] QUERY EXECUTION
    ├── Parse query
    ├── Bind parameters
    ├── Execute query
    ├── Handle SQL errors
    └── Check query performance
    ↓
[3] TRANSACTION MANAGEMENT
    ├── BEGIN TRANSACTION (if needed)
    ├── Execute multiple queries
    ├── IF all successful: COMMIT
    ├── IF error: ROLLBACK
    └── Handle lock timeouts
    ↓
[4] RESULT PROCESSING
    ├── Fetch results
    ├── Convert to Python objects
    ├── Format for API response
    └── Close cursor
    ↓
[5] CONNECTION CLEANUP
    ├── Return connection to pool
    ├── Log operation metrics
    └── Monitor query performance
```

---

## Diagram Alur Lengkap

### System Sequence Diagram - User Registration & Login

```
┌──────────┐            ┌──────────┐            ┌──────────┐
│  Client  │            │  Flask   │            │  MySQL   │
│(Mobile)  │            │ Backend  │            │ Database │
└────┬─────┘            └────┬─────┘            └────┬─────┘
     │                        │                       │
     │ POST /auth/register    │                       │
     │ email, password        │                       │
     ├───────────────────────>│                       │
     │                        │ Validate input        │
     │                        │─┐                     │
     │                        │ │ (crypto)            │
     │                        │<┘                     │
     │                        │                       │
     │                        │ SELECT * FROM users   │
     │                        │ WHERE email=?         │
     │                        ├──────────────────────>│
     │                        │                       │
     │                        │ Result: Not found ✓   │
     │                        │<──────────────────────┤
     │                        │                       │
     │                        │ INSERT new user       │
     │                        │ (hashed password)     │
     │                        ├──────────────────────>│
     │                        │                       │
     │                        │ user_id: 123 ✓        │
     │                        │<──────────────────────┤
     │ 201 Created + Token    │                       │
     │<───────────────────────┤                       │
     │ {user_id, token}       │                       │
     │                        │                       │
     │ POST /auth/login       │                       │
     │ email, password        │                       │
     ├───────────────────────>│                       │
     │                        │ SELECT * FROM users   │
     │                        │ WHERE email=?         │
     │                        ├──────────────────────>│
     │                        │ user data + hash      │
     │                        │<──────────────────────┤
     │                        │                       │
     │                        │ verify password ✓     │
     │                        │─┐                     │
     │                        │ │ (crypto)            │
     │                        │<┘                     │
     │                        │                       │
     │                        │ Create session token  │
     │                        │─┐                     │
     │                        │ │ (JWT signing)       │
     │                        │<┘                     │
     │ 200 OK + Token         │                       │
     │<───────────────────────┤                       │
     │ {token, user_data}     │                       │
     │                        │                       │
```

### System Sequence Diagram - Chatbot RAG Interaction

```
┌──────────┐          ┌────────────┐         ┌──────────┐         ┌─────────┐
│  Client  │          │   Flask    │         │ TiDB     │         │ Ollama  │
│ (Mobile) │          │  Backend   │         │ Cloud    │         │  LLM    │
└────┬─────┘          └─────┬──────┘         └─────┬────┘         └────┬────┘
     │                      │                      │                    │
     │ POST /chatbot/chat   │                      │                    │
     │ message              │                      │                    │
     ├─────────────────────>│                      │                    │
     │                      │ Load embedder       │                    │
     │                      │ (first time only)   │                    │
     │                      │─┐                   │                    │
     │                      │ │ (30-60s)          │                    │
     │                      │<┘                   │                    │
     │                      │                      │                    │
     │                      │ Generate embedding  │                    │
     │                      │─┐                   │                    │
     │                      │ │ (500ms)           │                    │
     │                      │<┘                   │                    │
     │                      │                      │                    │
     │                      │ Vector similarity   │                    │
     │                      │ search (top-5)      │                    │
     │                      ├─────────────────────>│                    │
     │                      │                      │ Execute query      │
     │                      │                      │─┐                  │
     │                      │                      │ │ (500-800ms)      │
     │                      │                      │<┘                  │
     │                      │ 5 docs (context)    │                    │
     │                      │<─────────────────────┤                    │
     │                      │                      │                    │
     │                      │ Format prompt       │                    │
     │                      │ + context           │                    │
     │                      │─┐                   │                    │
     │                      │ │ (prompt eng)      │                    │
     │                      │<┘                   │                    │
     │                      │                      │                    │
     │                      │ LLM inference       │                    │
     │                      │ (prompt + context)  │                    │
     │                      ├───────────────────────────────────────────>│
     │                      │                      │                    │
     │                      │                      │ Generate response  │
     │                      │                      │                    │
     │                      │                      │ (2-5s)             │
     │                      │ response text       │                    │
     │                      │<───────────────────────────────────────────┤
     │                      │                      │                    │
     │                      │ Log to database     │                    │
     │                      │ (chatbot history)   │                    │
     │                      │─┐                   │                    │
     │                      │ │ (INSERT)          │                    │
     │                      │<┘                   │                    │
     │ 200 OK               │                      │                    │
     │ {response, sources}  │                      │                    │
     │<─────────────────────┤                      │                    │
     │                      │                      │                    │
```

### System Sequence Diagram - Waste Detection

```
┌──────────┐           ┌─────────────┐           ┌──────────────┐
│  Client  │           │    Flask    │           │  TensorFlow  │
│ (Mobile) │           │   Backend   │           │   /MobileNet │
└────┬─────┘           └──────┬──────┘           └───────┬──────┘
     │                        │                          │
     │ POST /waste/detect     │                          │
     │ (image file)           │                          │
     ├───────────────────────>│                          │
     │                        │ Validate file           │
     │                        │─┐                        │
     │                        │ │ (check extension)     │
     │                        │<┘                        │
     │                        │                          │
     │                        │ Load image              │
     │                        │─┐                        │
     │                        │ │ (PIL.Image.open)      │
     │                        │<┘                        │
     │                        │                          │
     │                        │ Resize & normalize      │
     │                        │─┐                        │
     │                        │ │ (224x224, scale)      │
     │                        │<┘                        │
     │                        │                          │
     │                        │ Load model              │
     │                        │ (first time: 2-5s)      │
     │                        ├─────────────────────────>│
     │                        │                          │
     │                        │ Run inference           │
     │                        │ (forward pass)          │
     │                        ├─────────────────────────>│
     │                        │                          │
     │                        │ Top-5 predictions       │
     │                        │<─────────────────────────┤
     │                        │                          │
     │                        │ Map to categories       │
     │                        │─┐ (organik/anorganik/   │
     │                        │ │  kertas/kaca/logam)   │
     │                        │<┘                        │
     │                        │                          │
     │                        │ Get category details    │
     │                        │─┐ (color, tips)         │
     │                        │ │ (local config)        │
     │                        │<┘                        │
     │ 200 OK                 │                          │
     │ {category, confidence} │                          │
     │<───────────────────────┤                          │
     │ {bin_color, tips}      │                          │
     │                        │                          │
```

### Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────┐
│                  FLUTTER CLIENT                             │
│  (Screens, State Management, UI Components)                │
└─────────────────────┬──────────────────────────────────────┘
                      │ HTTP/REST API
                      │ (JSON)
                      ↓
┌────────────────────────────────────────────────────────────┐
│                  FLASK BACKEND                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ REQUEST HANDLING                                      │ │
│  │  • Route Matching (URL → Blueprint)                  │ │
│  │  • CORS Validation                                   │ │
│  │  • Authentication (JWT Token)                        │ │
│  │  • Input Validation                                  │ │
│  └───────┬─────────────────────────────────────────────┘ │
│          ↓                                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 11 BLUEPRINT ROUTES                                  │ │
│  │  [auth_bp, post_bp, comment_bp, campaign_bp, ...]   │ │
│  └───────┬──────────────────┬──────────────────┬────────┘ │
│          ↓                  ↓                  ↓           │
│  ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ BUSINESS LOGIC   │ │ FILE HANDLER │ │ AI/ML BRIDGE │  │
│  │                  │ │              │ │              │  │
│  │ • Models (CRUD)  │ │ • Upload     │ │ • Embedder   │  │
│  │ • Auth Service   │ │ • Save       │ │ • Inference  │  │
│  │ • Donation Logic │ │ • Compress   │ │ • Post-proc  │  │
│  │ • Campaign Mgmt  │ │              │ │              │  │
│  └────────┬─────────┘ └──────┬───────┘ └────────┬──────┘  │
│           ↓                  ↓                  ↓          │
│  ┌────────────────────────────────────────────────────┐   │
│  │        DATABASE LAYER (db.py)                      │   │
│  │  • MySQL Connection Pool                           │   │
│  │  • TiDB Cloud Connection                           │   │
│  │  • Query Execution                                 │   │
│  │  • Transaction Management                          │   │
│  └────────┬──────────────────┬───────────────────────┘   │
│           ↓                  ↓                            │
│  ┌──────────────────┐ ┌───────────────────────────────┐  │
│  │ MYSQL DATABASE   │ │ TIDB CLOUD (RAG)              │  │
│  │ (ruang_hijau)    │ │ (Vector Embeddings)           │  │
│  │                  │ │                               │  │
│  │ Tables:          │ │ Tables:                       │  │
│  │ • users          │ │ • embeddings (768-dim)        │  │
│  │ • posts          │ │ • documents                   │  │
│  │ • comments       │ │ • qa_pairs                    │  │
│  │ • campaigns      │ │                               │  │
│  │ • donations      │ │ Vector Similarity Search:     │  │
│  │ • feedback       │ │ SELECT ... WHERE distance ... │  │
│  └──────────────────┘ └───────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Ollama (LLM) │  │ Embedder     │  │ Payment Gateway │  │
│  │              │  │ (BAAI/bge-m3)│  │ (Midtrans/etc)  │  │
│  │ • Chat API   │  │              │  │                 │  │
│  │ • Generate   │  │ • Embedding  │  │ • Process       │  │
│  │   responses  │  │   generation │  │   donations     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Production Deployment Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    USER DEVICES                              │
│         (Android, iOS, Web Browser)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS/TLS
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              CLOUD / VPS SERVER                              │
│  (Linux Ubuntu 20.04 LTS)                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SYSTEMD SERVICE MANAGER                               │ │
│  │  • Service: flask.service                              │ │
│  │  • Auto-restart on failure                             │ │
│  │  • Run as unprivileged user                            │ │
│  └─────────────────────┬────────────────────────────────┘ │
│                        ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REVERSE PROXY (Optional: Nginx)                       │ │
│  │  • Load balancing (if multiple backends)               │ │
│  │  • SSL/TLS termination                                 │ │
│  │  • Static file serving                                 │ │
│  │  • Caching                                             │ │
│  └─────────────────────┬────────────────────────────────┘ │
│                        ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GUNICORN (WSGI Application Server)                    │ │
│  │  • Bind: 0.0.0.0:8000                                  │ │
│  │  • Workers: 2-4 (CPU * 2)                              │ │
│  │  • Worker class: sync                                  │ │
│  │  • Timeout: 120 seconds                                │ │
│  │  • Max requests: 1000                                  │ │
│  └─────────────────────┬────────────────────────────────┘ │
│                        ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FLASK APPLICATION LAYER                               │ │
│  │  • app.py (main application)                           │ │
│  │  • 11 blueprint routes                                 │ │
│  │  • Middleware & error handlers                         │ │
│  └─────────────────────┬────────────────────────────────┘ │
│                        ↓                                   │
│  ┌────────────┬──────────────────┬──────────┬──────────┐  │
│  │ MySQL      │ TiDB Cloud       │ Ollama   │ Files    │  │
│  │ Connector  │ Connector        │ Client   │ Handler  │  │
│  └────┬───────┴────────┬─────────┴──────┬───┴─────┬────┘  │
│       ↓                 ↓                ↓         ↓       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LOGGING & MONITORING                                  │ │
│  │  • Application logs → /var/log/flask/                  │ │
│  │  • Access logs → Gunicorn                              │ │
│  │  • Error tracking → Sentry (optional)                  │ │
│  │  • Performance monitoring → New Relic (optional)       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
        ↓                 ↓                ↓         ↓
┌───────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│   MySQL       │ │ TiDB Cloud   │ │ Ollama   │ │  /uploads│
│   Database    │ │ (RAG DB)     │ │ (LLM)    │ │  Storage │
│   Localhost   │ │ AWS/Cloud    │ │ Local    │ │  Local   │
│   Port: 3306  │ │ Port: 4000   │ │ Port:    │ │ /var/    │
│               │ │ (SSL/TLS)    │ │ 11434    │ │ uploads/ │
└───────────────┘ └──────────────┘ └──────────┘ └──────────┘
```

### Deployment Configuration Files

```
PRODUCTION SETUP FILES:
├── gunicorn_config.py
│   ├── bind = "0.0.0.0:8000"
│   ├── workers = 2
│   ├── worker_class = "sync"
│   ├── timeout = 120
│   ├── accesslog = "/var/log/flask/access.log"
│   └── errorlog = "/var/log/flask/error.log"
│
├── flask.service (Systemd Service)
│   ├── [Unit]
│   ├── Description = "Ruang Hijau Backend"
│   │
│   ├── [Service]
│   ├── ExecStart = "/path/venv/bin/gunicorn app:app -c gunicorn_config.py"
│   ├── Restart = "always"
│   ├── RestartSec = "10"
│   ├── User = "flask"
│   ├── Group = "www-data"
│   │
│   └── [Install]
│       └── WantedBy = "multi-user.target"
│
├── .env (Environment Variables)
│   ├── DB_HOST = "localhost"
│   ├── DB_USER = "root"
│   ├── DB_PASSWORD = "***"
│   ├── RAG_DB_HOST = "gateway01...."
│   ├── OLLAMA_HOST = "http://localhost:11434"
│   └── SECRET_KEY = "***"
│
└── Nginx configuration (Optional)
    ├── server_name = "api.ruanghijau.com"
    ├── listen = 443 (SSL)
    ├── upstream gunicorn = "127.0.0.1:8000"
    └── proxy_pass = "http://gunicorn"
```

---

## Database Schema

### MySQL (ruang_hijau) - Main Database

```sql
/* AUTHENTICATION & USERS */
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url VARCHAR(500),
    bio TEXT,
    phone_number VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    role ENUM('user', 'volunteer', 'ambassador', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

/* SOCIAL: POSTS */
CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255),
    content LONGTEXT NOT NULL,
    image_url VARCHAR(500),
    likes_count INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    shares_count INT DEFAULT 0,
    category VARCHAR(50),
    status ENUM('draft', 'published', 'archived') DEFAULT 'published',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

/* SOCIAL: COMMENTS */
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_comment_id INT,
    content TEXT NOT NULL,
    likes_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id)
);

/* CAMPAIGNS */
CREATE TABLE campaigns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    creator_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description LONGTEXT NOT NULL,
    image_url VARCHAR(500),
    category VARCHAR(100),
    goal_amount DECIMAL(12, 2) NOT NULL,
    current_amount DECIMAL(12, 2) DEFAULT 0,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    INDEX idx_creator_id (creator_id),
    INDEX idx_status (status)
);

/* DONATIONS */
CREATE TABLE donations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    campaign_id INT NOT NULL,
    donor_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY (donor_id) REFERENCES users(id),
    INDEX idx_campaign_id (campaign_id),
    INDEX idx_donor_id (donor_id),
    INDEX idx_status (status)
);

/* VOLUNTEERS */
CREATE TABLE volunteers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    campaign_id INT NOT NULL,
    user_id INT NOT NULL,
    hours_contributed INT DEFAULT 0,
    status ENUM('joined', 'active', 'completed') DEFAULT 'joined',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_vol (campaign_id, user_id)
);

/* FEEDBACK & SENTIMENT ANALYSIS */
CREATE TABLE feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    sentiment ENUM('negative', 'neutral', 'positive') DEFAULT 'neutral',
    sentiment_score FLOAT,
    category VARCHAR(100),
    status ENUM('new', 'reviewed', 'resolved') DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_sentiment (sentiment)
);

/* NOTIFICATIONS */
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type VARCHAR(50),
    title VARCHAR(255),
    content TEXT,
    related_id INT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_read (user_id, is_read)
);

/* WASTE DETECTIONS (Analytics) */
CREATE TABLE waste_detections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    image_url VARCHAR(500),
    detected_category VARCHAR(50),
    confidence FLOAT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (detected_category),
    INDEX idx_user (user_id)
);

/* ADMIN LOGS */
CREATE TABLE admin_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT NOT NULL,
    action VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id),
    INDEX idx_admin (admin_id),
    INDEX idx_timestamp (timestamp)
);
```

### TiDB Cloud (RAG) - Vector Database

```sql
/* VECTOR DATABASE FOR RAG CHATBOT */
CREATE TABLE embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    document_id VARCHAR(100) UNIQUE NOT NULL,
    document_title VARCHAR(500),
    document_text LONGTEXT NOT NULL,
    embedding VECTOR(768),  /* 768-dimensional vector from BAAI/bge-m3 */
    category VARCHAR(100),   /* waste, environment, tips, etc */
    source VARCHAR(255),     /* Where the document came from */
    tokens INT,              /* Token count for cost estimation */
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    VECTOR KEY idx_embedding (embedding),
    INDEX idx_category (category),
    INDEX idx_source (source)
);

/* KNOWLEDGE BASE DOCUMENTS (optional) */
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(500),
    content LONGTEXT,
    type ENUM('guide', 'tutorial', 'fact', 'faq'),
    category VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* QUERY-ANSWER PAIRS (optional) */
CREATE TABLE qa_pairs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question VARCHAR(500),
    answer LONGTEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

### Authentication API

```
POST /api/auth/register
├── Input: {email, password, username, full_name}
├── Output: {user_id, token, message}
└── Status: 201 Created

POST /api/auth/login
├── Input: {email, password}
├── Output: {user_id, token, user_data}
└── Status: 200 OK

POST /api/auth/logout
├── Input: {token}
├── Output: {message}
└── Status: 200 OK

POST /api/auth/google
├── Input: {google_token}
├── Output: {user_id, token, is_new_user}
└── Status: 200 OK
```

### Posts & Feed API

```
POST /api/posts/create
├── Input: {title, content, image_file, token}
├── Output: {post_id, image_url, created_at}
└── Status: 201 Created

GET /api/posts/feed
├── Input: {token, page, limit}
├── Output: {posts: [...], total, page}
└── Status: 200 OK

GET /api/posts/{id}
├── Input: {id}
├── Output: {post_data, comments_count}
└── Status: 200 OK

PUT /api/posts/{id}
├── Input: {id, title, content, token}
├── Output: {success, updated_post}
└── Status: 200 OK

DELETE /api/posts/{id}
├── Input: {id, token}
├── Output: {success, message}
└── Status: 200 OK
```

### Comments API

```
POST /api/comments/add
├── Input: {post_id, content, token}
├── Output: {comment_id, created_at}
└── Status: 201 Created

GET /api/comments/{post_id}
├── Input: {post_id, page, limit}
├── Output: {comments: [...], total}
└── Status: 200 OK

DELETE /api/comments/{id}
├── Input: {id, token}
├── Output: {success}
└── Status: 200 OK
```

### Campaigns & Donations API

```
POST /api/campaigns/create
├── Input: {title, description, goal, image, token}
├── Output: {campaign_id, created_at}
└── Status: 201 Created

GET /api/campaigns/list
├── Input: {page, limit, category}
├── Output: {campaigns: [...], total}
└── Status: 200 OK

GET /api/campaigns/{id}
├── Input: {id}
├── Output: {campaign_data, donors_count, volunteers}
└── Status: 200 OK

POST /api/donations/donate
├── Input: {campaign_id, amount, payment_method, token}
├── Output: {donation_id, payment_url}
└── Status: 201 Created

POST /api/donations/callback
├── Input: {webhook from payment gateway}
├── Output: {success}
└── Status: 200 OK
```

### Volunteer API

```
POST /api/volunteers/join
├── Input: {campaign_id, token}
├── Output: {volunteer_id, status}
└── Status: 201 Created

GET /api/volunteers/my
├── Input: {token}
├── Output: {campaigns: [...]}
└── Status: 200 OK
```

### Chatbot RAG API

```
POST /api/chatbot/chat
├── Input: {message, user_id, session_id}
├── Output: {response, confidence, sources, follow_up}
├── Status: 200 OK
└── Timeout: 120 seconds

GET /api/chatbot/history
├── Input: {user_id, limit}
├── Output: {messages: [...]}
└── Status: 200 OK
```

### Waste Detection API

```
POST /api/waste/detect
├── Input: {image_file, user_id}
├── Output: {
│   category, bin_color, confidence,
│   alternatives, tips, predictions
│ }
├── Status: 200 OK
└── Time: 1-3 seconds

GET /api/waste/history
├── Input: {user_id}
├── Output: {detections: [...]}
└── Status: 200 OK
```

### Feedback API

```
POST /api/feedback/submit
├── Input: {content, category, token}
├── Output: {feedback_id, sentiment, score}
├── Status: 201 Created
└── Sentiment Analysis: Automatic

GET /api/feedback/my
├── Input: {token, page}
├── Output: {feedback: [...]}
└── Status: 200 OK
```

### Admin API

```
GET /api/admin/dashboard
├── Input: {token (admin only)}
├── Output: {stats, charts, recent_activity}
└── Status: 200 OK

GET /api/admin/users
├── Input: {token, page, filter}
├── Output: {users: [...], total}
└── Status: 200 OK

POST /api/admin/ban-user
├── Input: {user_id, reason, token}
├── Output: {success}
└── Status: 200 OK
```

---

## Security Architecture

### Authentication & Authorization

```
REQUEST ARRIVES
    ↓
[1] EXTRACT TOKEN
    ├── From Authorization header
    ├── Format: "Bearer <token>"
    └── If missing → 401 Unauthorized
    ↓
[2] VERIFY JWT SIGNATURE
    ├── Use SECRET_KEY
    ├── Check expiration
    ├── Check payload integrity
    └── If invalid → 401 Unauthorized
    ↓
[3] EXTRACT CLAIMS
    ├── user_id
    ├── user_role
    ├── issued_at
    └── expiration
    ↓
[4] CHECK AUTHORIZATION
    ├── Does user_role have permission?
    ├── For admin endpoints: role == 'admin'?
    ├── For user endpoint: user_id matches?
    └── If no permission → 403 Forbidden
    ↓
[5] ATTACH CONTEXT TO REQUEST
    └── request.user_id = decoded_user_id
    ↓
PROCEED TO BUSINESS LOGIC
```

### Data Protection

```
SENSITIVE DATA PROTECTION:
├── Passwords
│   └── Hash with Werkzeug (bcrypt)
│
├── Authentication Tokens
│   ├── JWT signed with SECRET_KEY
│   ├── Short expiration (1-7 days)
│   └── Refresh token mechanism
│
├── File Uploads
│   ├── Scan for malware
│   ├── Validate MIME type
│   ├── Rename to random filename
│   └── Store outside web root
│
├── Database Connections
│   ├── Use .env for credentials
│   ├── Never hardcode secrets
│   ├── Use connection pooling
│   └── SSL/TLS for TiDB Cloud
│
├── API Communications
│   ├── HTTPS only (production)
│   ├── CORS restricted origins
│   ├── Rate limiting
│   └── Request validation

└── Logs & Monitoring
    ├── Don't log sensitive data
    ├── Rotate logs regularly
    └── Secure log storage
```

---

## Performance & Scalability

### Response Time SLA

```
API Endpoint                    | Target Time   | p95 Time
───────────────────────────────────────────────────────────
Standard CRUD (Posts, Comments) | 50-200ms      | 300ms
User Authentication             | 100-300ms     | 500ms
Feed Fetching (with pagination) | 200-500ms     | 1s
Campaign Management             | 50-200ms      | 300ms
Donation Processing             | 500-1000ms    | 2s
───────────────────────────────────────────────────────────
Chatbot (first request)         | 30-60s        | 90s
Chatbot (cached)                | 2-5s          | 10s
Waste Detection                 | 1-3s          | 5s
Sentiment Analysis              | 100-300ms     | 500ms
```

### Caching Strategy

```
CACHING LAYERS:
├── In-Memory Cache (optional: Redis)
│   ├── Frequently accessed campaigns
│   ├── User profile data
│   ├── Feed pagination (max 1 hour)
│   └── AI model weights
│
├── Database Query Optimization
│   ├── Indexes on frequently queried columns
│   ├── Pagination (limit 50 max)
│   ├── Connection pooling
│   └── Query result caching
│
├── AI Model Caching
│   ├── Embedder model → Keep in memory
│   ├── Vision model → Keep in memory
│   ├── LLM → Call Ollama (persistent)
│   └── TTL: Lifetime or until redeploy
│
└── Browser Caching
    ├── Static assets: 1 month
    ├── API responses: No cache (dynamic)
    └── Cache headers: Set appropriate directives
```

---

## Error Handling & Logging

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input format",
    "details": [
      {
        "field": "email",
        "message": "Email must be valid"
      }
    ]
  },
  "request_id": "req_123xyz"
}
```

### Logging Strategy

```
LOGGING LEVELS:
├── DEBUG   → Development only, detailed execution flow
├── INFO    → Important events (login, campaign created)
├── WARNING → Potential issues (slow query, high error rate)
├── ERROR   → Exception occurred, request failed
└── CRITICAL→ System failure, immediate action needed

LOG DESTINATIONS:
├── Application logs → /var/log/flask/app.log
├── Access logs      → /var/log/flask/access.log
├── Error logs       → /var/log/flask/error.log
├── Chatbot debug    → /var/log/flask/chatbot.log
└── Waste detection  → /var/log/flask/waste.log

LOG RETENTION:
├── Active logs: 7 days
├── Archive: 30 days
└── Long-term: Delete after 90 days
```

---

## Monitoring & Maintenance

### Health Check Endpoints

```
GET /api/health
├── Returns: {
│   "status": "healthy",
│   "database": "connected",
│   "redis": "connected",
│   "ollama": "running",
│   "timestamp": "2025-01-28T10:30:00Z"
│ }
└── Status: 200 OK

GET /api/health/detailed
├── Returns: {
│   "system": {...},
│   "database_response_time": "50ms",
│   "chatbot_availability": "true",
│   "waste_detection_available": "true"
│ }
└── Status: 200 OK
```

### Maintenance Tasks

```
DAILY:
├── Monitor error logs
├── Check API response times
├── Verify database backups
└── Monitor disk usage

WEEKLY:
├── Analyze user engagement metrics
├── Review chatbot accuracy
├── Check security logs
└── Database optimization

MONTHLY:
├── Update dependencies
├── Security patches
├── Performance review
├── Disaster recovery drill
```

---

## Kesimpulan Arsitektur

Ruang Hijau Backend adalah sistem yang **scalable**, **maintainable**, dan **feature-rich** dengan:

✅ **Modular Architecture** - 11 independent blueprints  
✅ **Integrated AI/ML** - Chatbot RAG, Waste Detection, Sentiment Analysis  
✅ **Secure** - JWT auth, password hashing, CORS, file validation  
✅ **High Performance** - Caching, lazy loading, optimized queries  
✅ **Production Ready** - Gunicorn, Systemd, logging, monitoring  
✅ **Scalable** - Database connection pooling, vector search, horizontal scaling

---

**Dokumentasi ini dibuat pada:** January 28, 2026  
**Last Updated:** January 28, 2026  
**Version:** 1.0

Untuk pertanyaan atau updates, silakan hubungi tim development.
