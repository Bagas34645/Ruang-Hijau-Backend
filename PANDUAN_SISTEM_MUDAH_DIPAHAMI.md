# 📚 PANDUAN SISTEM RUANG HIJAU - VERSI MUDAH DIPAHAMI

**Dibuat untuk:** Mahasiswa, Developer, dan Pengguna yang ingin memahami cara kerja Ruang Hijau  
**Tanggal:** January 28, 2026  
**Level:** Pemula → Menengah

---

## 🎯 Daftar Isi

1. [Apa itu Ruang Hijau?](#apa-itu-ruang-hijau)
2. [Bagian-Bagian Utama Sistem](#bagian-bagian-utama-sistem)
3. [Cara Kerja Sistem](#cara-kerja-sistem)
4. [Fitur-Fitur Utama](#fitur-fitur-utama)
5. [Alur Kerja Pengguna](#alur-kerja-pengguna)
6. [Teknologi yang Digunakan](#teknologi-yang-digunakan)
7. [Keamanan Data](#keamanan-data)

---

## 🌱 Apa itu Ruang Hijau?

**Ruang Hijau** adalah aplikasi yang menghubungkan orang-orang untuk bergerak bersama menjaga lingkungan.

### Bayangkan seperti ini:

Ruang Hijau itu seperti **komunitas lingkungan online**:

- 📱 Anda bisa berbagi cerita tentang lingkungan melalui postingan
- 💬 Anda bisa berkomunikasi dengan komunitas lainnya
- 🌍 Anda bisa ikut kampanye penghijauan atau pengurangan sampah
- 💰 Anda bisa mendonasikan uang untuk mendukung kampanye hijau
- 🤖 Ada chatbot AI yang bisa menjawab pertanyaan tentang lingkungan
- 📸 Anda bisa mengunggah foto sampah untuk diidentifikasi jenisnya

---

## 🏗️ Bagian-Bagian Utama Sistem

Ruang Hijau terdiri dari 4 bagian utama yang bekerja sama:

### 1. **Frontend (Aplikasi Mobile)**

```
APA ITU?
└─ Tampilan yang Anda lihat di ponsel/tablet
└─ Dibangun dengan Flutter (bisa Android dan iOS)

TUGASNYA:
├─ Menampilkan feed postingan
├─ Menampilkan kampanye
├─ Menampilkan chatbot
├─ Mengambil foto untuk deteksi sampah
└─ Mengirim data ke backend

ANALOGI:
└─ Seperti tampilan depan toko, tempat Anda berinteraksi
```

### 2. **Backend (Server - Otak Sistem)**

```
APA ITU?
└─ Program di server yang memproses semua data
└─ Dibangun dengan Flask (Python)

TUGASNYA:
├─ Menerima permintaan dari aplikasi mobile
├─ Memproses data (login, membuat post, donasi)
├─ Menyimpan data ke database
├─ Menjalankan AI (chatbot, deteksi sampah)
└─ Mengirim kembali data yang diminta

ANALOGI:
└─ Seperti staf toko yang melayani, menerima pesanan,
    dan memberikan barang yang diminta
```

### 3. **Database (Tempat Penyimpanan Data)**

```
APA ITU?
└─ Penyimpanan data seperti gudang

TERDIRI DARI:
├─ MySQL
│  └─ Menyimpan: user, postingan, komentar, kampanye, donasi
│
└─ TiDB Cloud
   └─ Menyimpan: pengetahuan untuk chatbot AI

ANALOGI:
└─ Seperti lemari arsip yang menyimpan semua dokumen penting
```

### 4. **AI/ML Models (Kecerdasan Buatan)**

```
APA ITU?
└─ Program pintar yang bisa memahami dan memproses informasi

TERDIRI DARI:
├─ CHATBOT RAG
│  ├─ Bisa menjawab pertanyaan tentang lingkungan
│  └─ Menggunakan pengetahuan dari database
│
├─ WASTE DETECTION
│  ├─ Bisa mengenali jenis sampah dari foto
│  └─ Memberitahu warna tempat sampah yang benar
│
└─ SENTIMENT ANALYZER
   ├─ Memahami perasaan dalam komentar/feedback
   └─ Menentukan positif, negatif, atau netral

ANALOGI:
└─ Seperti ahli yang bisa menjawab pertanyaan,
    mengidentifikasi sampah, dan memahami perasaan
```

---

## 🔄 Cara Kerja Sistem

### Flow Umum: Dari Permintaan hingga Respon

```
PENGGUNA DI APLIKASI
        ↓
    (Melakukan aksi: login, post, chat, upload foto)
        ↓
   KIRIM KE SERVER
   (Permintaan HTTP)
        ↓
   SERVER MENERIMA
   ├─ Memeriksa apakah data valid
   ├─ Memeriksa apakah Anda login
   └─ Memeriksa izin akses
        ↓
  PROSES PERMINTAAN
  ├─ Mencari data di database
  ├─ Menjalankan logika bisnis
  ├─ Mungkin memanggil AI
  └─ Menyimpan data baru ke database
        ↓
  SIAPKAN JAWABAN
  ├─ Kumpulkan data yang diminta
  ├─ Format menjadi JSON
  └─ Siapkan pesan sukses/error
        ↓
  KIRIM KEMBALI KE APLIKASI
  (Response JSON)
        ↓
  APLIKASI MENAMPILKAN
  (Update tampilan di layar Anda)
```

---

## 🌟 Fitur-Fitur Utama

### 1. **Sistem Sosial Media**

#### A. Posting & Feed

```
BAGAIMANA CARA KERJANYA?

1. PENGGUNA BUAT POSTINGAN
   - Menulis cerita tentang lingkungan
   - Bisa menambah foto
   - Klik "Bagikan"
        ↓
2. SERVER MENERIMA
   - Validasi data (ada konten tidak?)
   - Simpan foto ke folder /uploads
   - Simpan informasi post ke MySQL
        ↓
3. DATABASE MENYIMPAN
   - user_id: siapa yang post
   - judul: judul postingan
   - konten: isi cerita
   - image_url: lokasi foto
   - created_at: kapan dibuat
        ↓
4. FEED TERUPDATE
   - Postingan muncul di feed semua orang
   - Paling baru di atas
   - Bisa diklik untuk dibaca selengkapnya
```

#### B. Komentar

```
PENGGUNA BACA POST → KOMENTAR → SERVER SIMPAN → TAMPIL DI POST
```

### 2. **Kampanye & Donasi**

#### Alur Lengkapnya:

```
ADMIN/CREATOR BUAT KAMPANYE
├─ Judul: "Gerakan Penghijauan Jakarta"
├─ Target donasi: 100 juta rupiah
├─ Deskripsi: Rencana tanam pohon
└─ Foto kampanye
        ↓
DATABASE SIMPAN
├─ MySQL: informasi kampanye
├─ Status: aktif
└─ current_amount: 0 (belum ada donasi)
        ↓
PENGGUNA LIHAT KAMPANYE
├─ Aplikasi tampilkan semua kampanye
├─ Pengguna lihat progress (berapa yang sudah terkumpul)
└─ Ada tombol "Donasi Sekarang"
        ↓
PENGGUNA KLIK DONASI
├─ Input nominal (contoh: 100 ribu)
├─ Pilih metode bayar (GoPay, Kartu Kredit, dll)
└─ Klik Donasi
        ↓
PROSES PEMBAYARAN
├─ Server hubungi payment gateway (Midtrans)
├─ User dialihkan ke halaman pembayaran
├─ User menyelesaikan pembayaran
└─ Payment gateway kirim notifikasi sukses ke server
        ↓
SERVER CATAT DONASI
├─ Catat user yang donasi
├─ Catat nominal donasi
├─ Update total donasi kampanye (tambah)
└─ Jika sudah mencapai target: tandai kampanye "Selesai"
        ↓
DATABASE TERUPDATE
├─ donations table: tambah record baru
└─ campaigns table: current_amount ditambah
        ↓
PENGGUNA LIHAT KONFIRMASI
├─ "Donasi berhasil!"
├─ "Anda telah mendonasikan: Rp 100.000"
└─ "Terima kasih untuk lingkungan ✨"
```

### 3. **Chatbot AI (Menjawab Pertanyaan)**

#### Sistem RAG (Retrieval-Augmented Generation)

```
KONSEP DASAR:
Chatbot kami bukan chatbot biasa yang asal menjawab.
Chatbot kami mencari informasi dari database dulu,
baru menjawab pertanyaan dengan informasi yang benar.

BAGAIMANA CARANYA?

STEP 1: PENGGUNA TANYA
├─ "Bagaimana cara membuat kompos?"
└─ Pertanyaan dikirim ke server
        ↓
STEP 2: UBAH PERTANYAAN JADI VEKTOR
├─ Server menggunakan embedder (BAAI/bge-m3)
├─ Pertanyaan diubah jadi angka-angka (768 dimensi)
├─ Contoh: [0.234, -0.156, 0.892, ..., 0.145]
└─ Angka ini merepresentasikan makna pertanyaan
        ↓
STEP 3: CARI JAWABAN DI KNOWLEDGE BASE
├─ Cari dokumen di database TiDB yang mirip
├─ Sistem hitung: pertanyaan ini mirip dengan dokumen apa?
├─ Cari top 5 dokumen paling mirip:
│  1. "Panduan membuat kompos organik" - 95% mirip
│  2. "Manfaat kompos" - 88% mirip
│  3. "Bahan untuk kompos" - 82% mirip
│  4. "Proses dekomposisi" - 75% mirip
│  5. "Tips mempercepat kompos" - 70% mirip
└─ Dokumen-dokumen ini dijadikan konteks
        ↓
STEP 4: SIAPKAN PERTANYAAN DENGAN KONTEKS
├─ Format:
│  Sistem: "Kamu adalah chatbot ahli lingkungan"
│  Konteks: [5 dokumen di atas]
│  Pertanyaan: "Bagaimana cara membuat kompos?"
└─ Kirim ke LLM (Ollama)
        ↓
STEP 5: AI GENERATE JAWABAN
├─ Ollama membaca pertanyaan + konteks
├─ Generate jawaban yang relevan
├─ Contoh jawaban:
│  "Untuk membuat kompos, Anda bisa:
│   1. Kumpulkan sampah organik (daun, sisa makanan)
│   2. Siapkan wadah/pit khusus
│   3. Lapisi dengan tanah
│   4. Tunggu 1-3 bulan sampai terurai
│   5. Gunakan sebagai pupuk..."
└─ Jawaban berdasarkan informasi dari database
        ↓
STEP 6: TAMPILKAN JAWABAN
├─ Jawaban ditampilkan di aplikasi
├─ Beserta sumber dokumen yang digunakan
└─ Pengguna bisa kirim feedback (berguna/tidak)

KEUNTUNGAN SISTEM INI:
✓ Jawaban akurat (dari database)
✓ Tidak asal-asalan (tidak hallucinate)
✓ Bisa dijelaskan sumbernya
✓ Bisa diupdate pengetahuannya
```

### 4. **Deteksi Sampah (Waste Detection)**

#### Bagaimana AI Kenali Jenis Sampah

```
PENGGUNA AMBIL FOTO SAMPAH
└─ Misal: foto plastik botol
        ↓
KIRIM FOTO KE SERVER
└─ File binary dikirim
        ↓
SERVER VALIDASI FOTO
├─ Apakah file benar-benar gambar?
├─ Apakah ukuran tidak terlalu besar?
└─ Jika valid, lanjut; jika tidak, tolak
        ↓
RESIZE & NORMALISASI FOTO
├─ Ubah ukuran jadi 224x224 pixel
├─ Sesuaikan warna
└─ Persiapkan agar AI bisa membaca
        ↓
PASS KE AI (MobileNetV2)
├─ AI lihat foto
├─ AI analisis bentuk, warna, tekstur
├─ AI beri prediksi untuk 1000 kategori ImageNet
        ↓
DECODE PREDIKSI
├─ AI kembalikan: top-5 prediksi
├─ Contoh:
│  - "Plastik botol" 45% confidence
│  - "Botol minum" 25% confidence
│  - "Benda bulat" 15% confidence
│  - dst...
└─ Ambil prediksi tertinggi
        ↓
MAPPING KE KATEGORI LOKAL
├─ "Plastik botol" → ANORGANIK (Kuning)
├─ Atau jika lihat: "Daun" → ORGANIK (Hijau)
├─ Atau jika lihat: "Kardus" → KERTAS (Biru)
└─ dst...
        ↓
SIAPKAN JAWABAN
├─ Kategori sampah
├─ Warna tempat sampah yang benar
├─ Confidence/kepercayaan (92%)
├─ Alternatif kategori lain
└─ Tips pembuangan
        ↓
TAMPILKAN HASIL
├─ "Ini adalah sampah PLASTIK 🟡"
├─ "Warna tempat sampah: KUNING"
├─ "Confidence: 92%"
└─ "Tips: Plastik butuh 100+ tahun untuk terurai"

KATEGORI SAMPAH:
┌─────────────────────────────────────────────┐
│ 🟢 ORGANIK (Hijau)                          │
│   Contoh: Daun, sisa makanan, ranting      │
│   Terurai dalam: 1-3 bulan                 │
│                                             │
│ 🟡 ANORGANIK (Kuning)                       │
│   Contoh: Plastik, styrofoam, tas          │
│   Terurai dalam: 100+ tahun                │
│                                             │
│ 🔵 KERTAS (Biru)                            │
│   Contoh: Kardus, koran, majalah           │
│   Terurai dalam: 2-6 bulan                 │
│                                             │
│ ⚪ KACA (Putih)                              │
│   Contoh: Botol kaca, gelas                │
│   Terurai dalam: 1000+ tahun               │
│                                             │
│ ⚫ LOGAM (Abu-abu)                           │
│   Contoh: Kaleng, besi, aluminium          │
│   Terurai dalam: 50-100 tahun              │
└─────────────────────────────────────────────┘
```

### 5. **Analisis Sentimen (Pahami Perasaan)**

#### Bagaimana Sistem Pahami Perasaan Pengguna

```
PENGGUNA SUBMIT FEEDBACK
└─ Contoh: "Aplikasi ini sangat bagus dan membantu!"
        ↓
SERVER TERIMA FEEDBACK
└─ Text diproses oleh Sentiment Analyzer
        ↓
ANALISA KATA-KATA
├─ Cari kata positif: "bagus" = +0.7
├─ Cari kata negatif: (tidak ada)
├─ Cari kata penekan: "sangat" = multiplier 1.2x
└─ Hasil: 0.7 × 1.2 = 0.84
        ↓
TENTUKAN SENTIMEN
├─ Jika score > 0.5 → POSITIF 😊
├─ Jika -0.5 ≤ score ≤ 0.5 → NETRAL 😐
└─ Jika score < -0.5 → NEGATIF 😞
        ↓
SIMPAN KE DATABASE
├─ feedback table mendapat entry baru
├─ sentiment: "positive"
├─ sentiment_score: 0.84
└─ Admin bisa lihat dashboard feedback
        ↓
HASIL:
└─ Pengguna: "Terima kasih atas feedback Anda!"
   Admin: "Feedback positif diterima"
```

---

## 👥 Alur Kerja Pengguna

### Skenario 1: Pengguna Baru Mendaftar

```
BUKA APLIKASI
└─ Tombol "Daftar Akun"
        ↓
FILL FORM
├─ Email: user@gmail.com
├─ Password: rahasia123
├─ Username: userhandle
└─ Nama lengkap: Nama Pengguna
        ↓
KLIK DAFTAR
└─ Data dikirim ke server
        ↓
SERVER VALIDASI
├─ Email sudah terdaftar?
├─ Password kuat?
├─ Username tersedia?
└─ Jika ada error, tampilkan pesan kesalahan
        ↓
HASH PASSWORD
├─ Password tidak disimpan langsung
├─ Diubah jadi hash (karakter random panjang)
└─ Hanya hash yang disimpan
        ↓
SIMPAN KE DATABASE
├─ users table mendapat entry baru:
│  - email: user@gmail.com
│  - password_hash: $2b$12$xyz...
│  - username: userhandle
│  - full_name: Nama Pengguna
│  - created_at: 2025-01-28
│  - user_id: 123
└─ Auto-generate ID untuk pengguna
        ↓
GENERATE TOKEN
├─ Token adalah "kunci" untuk akses nanti
├─ Token ini disimpan di aplikasi
└─ Setiap permintaan harus sertakan token
        ↓
RESPONSE "DAFTAR BERHASIL"
├─ Tampilkan pesan sukses
├─ Kirim token
└─ Redirect ke halaman feed
```

### Skenario 2: Pengguna Membuat Posting

```
LOGIN BERHASIL
└─ Token sudah ada
        ↓
KLIK "BUAT POST"
└─ Buka form posting
        ↓
ISI FORM
├─ Judul: "Mengamati Sampah Plastik"
├─ Isi: "Hari ini saya melihat sampah plastik..."
├─ Foto: Upload dari galeri ponsel
└─ Token: Otomatis sudah ada
        ↓
KLIK "BAGIKAN"
└─ Data dikirim ke server dengan token
        ↓
SERVER VALIDASI TOKEN
├─ Apakah token valid?
├─ Apakah pengguna sudah login?
└─ Jika tidak valid → ERROR 401
        ↓
VALIDASI FOTO
├─ Apakah file benar foto?
├─ Apakah ukuran < 16MB?
├─ Apakah tipe file aman?
└─ Jika gagal → ERROR
        ↓
PROSES FOTO
├─ Ubah nama: post_123_xyz.jpg
├─ Compress kualitas (hemat storage)
├─ Simpan ke folder: /uploads/posts/
└─ Catat URL lokasi foto
        ↓
SIMPAN KE DATABASE
├─ INSERT INTO posts:
│  - user_id: 123 (dari token)
│  - title: "Mengamati Sampah Plastik"
│  - content: "Hari ini saya melihat..."
│  - image_url: /uploads/posts/post_123_xyz.jpg
│  - created_at: 2025-01-28 10:30:00
└─ Auto-generate post_id: 456
        ↓
RESPONSE SUKSES
├─ Kirim: post_id, image_url, created_at
└─ Status: 201 Created
        ↓
UPDATE FEED
├─ Aplikasi menampilkan posting baru
├─ Posting muncul di feed semua orang
└─ User bisa lihat jumlah like/komentar
```

### Skenario 3: Pengguna Chat dengan Chatbot

```
BUKA HALAMAN CHATBOT
└─ Ada input form untuk pertanyaan
        ↓
KETIK PERTANYAAN
└─ Contoh: "Bagaimana cara mengurangi sampah plastik?"
        ↓
KLIK KIRIM
└─ Pertanyaan dikirim ke server
        ↓
SERVER: LOAD EMBEDDER (Kali Pertama)
├─ Jika model belum ada di memory
├─ Download model BAAI/bge-m3 (1.2 GB)
├─ Load ke sistem
└─ Waktu: 30-60 detik (Hanya pertama kali!)
        ↓
SERVER: BUAT EMBEDDING
├─ Ubah pertanyaan jadi vector (768 angka)
├─ Vector ini merepresentasikan makna
└─ Waktu: 500ms
        ↓
SERVER: CARI DOKUMEN MIRIP
├─ Query TiDB: Dokumen apa yang mirip?
├─ Ambil top 5 dokumen paling mirip
├─ Contoh hasil:
│  1. "Tips mengurangi plastik" - 95% mirip
│  2. "Alternatif plastik" - 88% mirip
│  3. "Daur ulang plastik" - 82% mirip
│  4. "Eco-friendly lifestyle" - 75% mirip
│  5. "Kampanye zero waste" - 70% mirip
└─ Waktu: 500-800ms
        ↓
SERVER: SIAPKAN PERTANYAAN DENGAN KONTEKS
├─ Buat prompt:
│  "Anda ahli lingkungan Indonesia.
│   Berdasarkan informasi:
│   - Dokumen 1: ...
│   - Dokumen 2: ...
│   [dst]
│   Jawab pertanyaan: Bagaimana cara mengurangi plastik?"
└─ Kirim ke Ollama (AI local)
        ↓
OLLAMA: GENERATE JAWABAN
├─ Baca prompt + konteks
├─ Generate jawaban berkualitas
├─ Contoh jawaban:
│  "Untuk mengurangi sampah plastik:
│   1. Gunakan tas belanja yang bisa dipakai ulang
│   2. Hindari botol plastik sekali pakai
│   3. Beli produk yang kemasan minimal
│   4. Dukung bisnis yang eco-friendly
│   5. Edukasi orang lain tentang plastik"
└─ Waktu: 2-5 detik
        ↓
SERVER: SIAPKAN RESPONSE
├─ Format jawaban jadi JSON
├─ Tambahkan:
│  - response: jawaban
│  - confidence: 0.87 (kepercayaan AI)
│  - sources: referensi dokumen
│  - follow_up_suggestions: pertanyaan lanjutan
└─ Kirim ke aplikasi
        ↓
APLIKASI TAMPILKAN JAWABAN
├─ Tanya: "Bagaimana cara mengurangi plastik?"
├─ Jawab: "Untuk mengurangi sampah plastik:..."
├─ Tampilkan source dokumen
├─ Ada tombol: "Helpful" atau "Not Helpful"
└─ Pengguna bisa kirim pertanyaan lagi

CATATAN WAKTU:
├─ Pertama kali: 30-60 detik (loading model)
├─ Lain kali: 2-5 detik (model sudah di memory)
└─ Ini normal! Kecepatan akan konsisten setelah itu
```

### Skenario 4: Deteksi Jenis Sampah

```
BUKA HALAMAN "DETEKSI SAMPAH"
└─ Ada tombol kamera
        ↓
AMBIL FOTO
└─ Foto sampah, misal: sampah plastik
        ↓
UPLOAD FOTO
└─ File dikirim ke server
        ↓
SERVER VALIDASI
├─ Apakah benar gambar?
├─ Apakah tidak terlalu besar?
└─ OK, lanjut
        ↓
RESIZE & NORMALISASI FOTO
├─ Ubah ukuran 224x224 pixel
├─ Sesuaikan warna/brightness
└─ Siapkan untuk AI
        ↓
LOAD AI MODEL (Kali Pertama)
├─ Load MobileNetV2
├─ Waktu: 2-5 detik
└─ Lain kali: instant (cached)
        ↓
PROSES DENGAN AI
├─ Input: foto 224x224
├─ Output: top-5 prediksi
├─ Contoh:
│  1. "plastic" - 45%
│  2. "bottle" - 25%
│  3. "container" - 15%
│  4. "object" - 10%
│  5. "trash" - 5%
└─ Waktu: 100-500ms
        ↓
MAPPING KE KATEGORI LOKAL
├─ Lihat prediksi: "plastic" + "bottle"
├─ Mapping: → ANORGANIK
├─ Tentukan warna: KUNING 🟡
└─ Confidence: 45% (dari top prediksi)
        ↓
AMBIL INFO TAMBAHAN
├─ Warna tempat sampah
├─ Tips pembuangan
├─ Dampak lingkungan
├─ Alternatif lain
└─ Dari database lokal
        ↓
RESPONSE HASIL
├─ Kategori: ANORGANIK 🟡
├─ Confidence: 45%
├─ Warna bin: KUNING
├─ Tips: "Plastik butuh 100+ tahun terurai"
├─ Alternatif:
│  - KERTAS: 6%
│  - ORGANIK: 4%
└─ Waktu keseluruhan: 1-3 detik
        ↓
TAMPILKAN DI APLIKASI
├─ Besar gambar warna BIN KUNING
├─ Teks: "SAMPAH ANORGANIK"
├─ Confidence: 45%
├─ Tips + info
└─ Tombol: Ambil lagi / Share
```

---

## 💻 Teknologi yang Digunakan

### Daftar Teknologi Sederhana

```
APLIKASI MOBILE (Apa yang Anda lihat)
├─ Flutter
│  └─ Bahasa: Dart
│  └─ Bisa Android & iOS
│  └─ Interface yang indah & smooth
└─ Platform: Android, iOS, Web

SERVER (Otak sistem)
├─ Python (Bahasa pemrograman)
├─ Flask (Framework web)
│  └─ Membuat API (antarmuka untuk komunikasi)
└─ Gunicorn (Server untuk menjalankan Flask)

DATABASE (Penyimpanan)
├─ MySQL
│  └─ Database tradisional untuk data normal
│  └─ Menyimpan: users, posts, campaigns, donasi
│
└─ TiDB Cloud
   └─ Database khusus untuk vector (angka-angka)
   └─ Khusus untuk pengetahuan chatbot
   └─ Bisa search dengan similarity

AI/MACHINE LEARNING
├─ Ollama
│  └─ Server lokal untuk AI model
│  └─ Model: gemma2:2b
│  └─ Menjawab pertanyaan dengan RAG
│
├─ BAAI/bge-m3
│  └─ Model embedder (ubah text jadi vector)
│  └─ Untuk chatbot RAG
│
├─ MobileNetV2
│  └─ Model computer vision
│  └─ Untuk deteksi jenis sampah
│  └─ Sudah trained di ImageNet
│
└─ Sentiment Analyzer (Custom)
   └─ Program buatan sendiri
   └─ Analisis perasaan dari text

LAINNYA
├─ CORS (Cross-Origin Resource Sharing)
│  └─ Izin aplikasi berkomunikasi dengan server
│
├─ JWT (JSON Web Token)
│  └─ "Kartu identitas" untuk login
│  └─ Membuktikan Anda sudah login
│
└─ File Upload Handler
   └─ Proses upload foto/dokumen
   └─ Validasi & compress
```

### Mengapa Pilihan Ini?

```
FLUTTER
✓ Cross-platform (Android + iOS 1 kode)
✓ Performa bagus
✓ UI modern & smooth
✓ Dokumentasi lengkap

FLASK
✓ Sederhana & cepat buat API
✓ Python friendly
✓ Flexible & extensible
✓ Cocok untuk startup

MYSQL
✓ Reliable & stable
✓ Query powerful
✓ Support complex relationships

TIDB CLOUD
✓ Vector search built-in
✓ Cloud-based (no server management)
✓ Scalable

OLLAMA
✓ Local LLM (private, no cloud)
✓ Cepat
✓ Bisa customize model

BAAI/BGE-M3
✓ Multi-bahasa (termasuk Indonesian)
✓ Bagus untuk semantic search
✓ Open source
```

---

## 🔒 Keamanan Data

### Bagaimana Sistem Menjaga Keamanan Anda

```
MASALAH KEAMANAN #1: PASSWORD DICURI?

SOLUSI:
└─ Password tidak disimpan langsung
   ├─ Password diubah jadi hash (karakter random)
   ├─ Hash dienkripsi dengan algoritma Bcrypt
   ├─ Contoh:
   │  Password asli: "rahasia123"
   │  Disimpan sebagai: "$2b$12$abcdef...xyz"
   └─ Bahkan admin tidak bisa lihat password asli

CONTOH:
├─ Pengguna input: "rahasia123"
├─ Server hash: "$2b$12$abc..."
├─ Bandingkan hash di database: cocok? → LOGIN BERHASIL
└─ Tidak cocok? → LOGIN GAGAL
```

```
MASALAH KEAMANAN #2: ORANG LAIN IMPERSONATE SAYA?

SOLUSI: TOKEN (KARTU IDENTITAS DIGITAL)
├─ Saat login → dapat token unik
├─ Setiap permintaan harus kirim token
├─ Server verifikasi token
├─ Token punya "tanda tangan" digital (signature)
│  └─ Hanya server yang tahu secret keynya
│  └─ Jika token diubah → signature tidak cocok
│  └─ Server tahu token palsu
│
└─ Keuntungan:
   ├─ Hanya Anda yang punya token Anda
   ├─ Token punya masa berlaku (expire)
   ├─ Jika token dicuri → hanya berlaku sebentar
   └─ Bisa logout → token tidak valid lagi
```

```
MASALAH KEAMANAN #3: FOTO SAYA DIUBAH ORANG?

SOLUSI: FILE VALIDATION
├─ Check file type (benar-benar gambar?)
├─ Check file size (< 16MB)
├─ Scan malware (optional)
├─ Ubah nama file random
├─ Simpan di folder khusus
└─ Akses hanya lewat server (tidak publik)
```

```
MASALAH KEAMANAN #4: DATA SAYA TIDAK TERENKRIPSI?

SOLUSI: ENCRYPTION
├─ Data dari aplikasi ke server: HTTPS (encrypted)
├─ TiDB Cloud: SSL/TLS encryption
├─ Password: Hashed + salted
└─ Sensitive data: Encrypted
```

```
MASALAH KEAMANAN #5: ORANG BACA DATA SAYA?

SOLUSI: ACCESS CONTROL
├─ Setiap endpoint punya permission check
├─ Post Anda hanya bisa diedit oleh Anda
├─ Data donation Anda private
├─ Admin dashboard hanya untuk admin
│
└─ Contoh:
   ├─ Anda request: GET /api/users/456/profile
   ├─ Server check: Apakah Anda user 456?
   ├─ Jika ya → berikan data
   ├─ Jika tidak → ERROR 403 Forbidden
   └─ Tidak boleh lihat data orang lain
```

### Checklist Keamanan

```
✅ Password di-hash dengan Bcrypt
✅ Setiap request membutuhkan token valid
✅ Token punya signature digital
✅ HTTPS untuk semua komunikasi
✅ File upload di-validasi
✅ SQL Injection protection (parameterized queries)
✅ CORS hanya dari origin yang diizinkan
✅ Rate limiting (tidak boleh request terlalu banyak)
✅ Logging untuk semua aktivitas
✅ Database backup regular
```

---

## 📊 Ringkasan Arsitektur Sederhana

```
PENGGUNA (Smartphone/Web)
        ↓
FLUTTER APP / WEB BROWSER
(Interface - yang Anda lihat)
        ↓
HTTP/HTTPS (Encrypted)
        ↓
FLASK SERVER (Otak)
├─ Auth Service (Cek login)
├─ Post Service (Kelola postingan)
├─ Campaign Service (Kelola kampanye)
├─ AI Bridge (Chatbot & Waste Detection)
└─ File Handler (Kelola foto)
        ↓
3 LAYANAN EKSTERNAL
├─ MySQL (Data normal: user, post, campaign)
├─ TiDB Cloud (Data vector untuk chatbot)
└─ Ollama (AI untuk jawab pertanyaan)
        ↓
HASIL
├─ Postingan ditampilkan
├─ Chatbot menjawab
├─ Sampah teridentifikasi
└─ Donasi tercatat
```

---

## 🚀 Performance (Kecepatan)

Berapa lama setiap aksi?

```
AKSI NORMAL
├─ Login: 0.2 detik
├─ Load feed: 0.5 detik
├─ Buat post: 1-2 detik (tergantung ukuran foto)
├─ Donasi: 2-3 detik
└─ Komentar: 0.3 detik

AKSI AI
├─ Chatbot (pertama kali): 30-60 detik (loading model)
├─ Chatbot (lain kali): 2-5 detik
├─ Deteksi sampah (pertama kali): 3-5 detik
├─ Deteksi sampah (lain kali): 1-2 detik
└─ Sentimen analysis: 0.2 detik

CATATAN:
└─ "Pertama kali" lebih lama karena load model AI
└─ Setelah itu cepat (model sudah di memory)
└─ Ini normal & ok
```

---

## 📝 Contoh Request-Response

### Contoh 1: Login

```
PENGGUNA KIRIM (ke server):
POST /api/auth/login
{
  "email": "user@gmail.com",
  "password": "rahasia123"
}

SERVER BALAS:
200 OK
{
  "success": true,
  "user_id": 123,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_data": {
    "username": "userhandle",
    "full_name": "Nama Pengguna",
    "profile_picture": "http://api.ruanghijau.com/uploads/user_123.jpg"
  }
}
```

### Contoh 2: Buat Post

```
PENGGUNA KIRIM (ke server):
POST /api/posts/create
(multipart/form-data)
├─ title: "Sampah di Pantai"
├─ content: "Saya melihat sampah di pantai..."
├─ image: <file binary>
└─ token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

SERVER BALAS:
201 Created
{
  "success": true,
  "post_id": 456,
  "image_url": "http://api.ruanghijau.com/uploads/posts/post_123_abc.jpg",
  "created_at": "2025-01-28T10:30:00Z",
  "message": "Post berhasil dibuat!"
}
```

### Contoh 3: Chat dengan Chatbot

```
PENGGUNA KIRIM (ke server):
POST /api/chatbot/chat
{
  "message": "Bagaimana cara membuat kompos?",
  "user_id": 123
}

SERVER BALAS:
200 OK
{
  "response": "Untuk membuat kompos, Anda bisa:
    1. Kumpulkan sampah organik...
    2. Siapkan wadah khusus...
    3. Tunggu 1-3 bulan...",
  "confidence": 0.87,
  "sources": [
    {
      "title": "Panduan Kompos Organik",
      "relevance": "95%"
    },
    {
      "title": "Waste Management",
      "relevance": "88%"
    }
  ],
  "follow_up": [
    "Berapa lama kompos siap?",
    "Apa manfaat kompos?"
  ]
}
```

### Contoh 4: Deteksi Sampah

```
PENGGUNA KIRIM (ke server):
POST /api/waste/detect
(multipart/form-data)
├─ image: <file binary>
└─ user_id: 123

SERVER BALAS:
200 OK
{
  "success": true,
  "classification": {
    "category": "organik",
    "bin_color": "Hijau 🟢",
    "confidence": "92%"
  },
  "tips": {
    "disposal": "Simpan di wadah tertutup",
    "environment_impact": "Terurai 1-3 bulan",
    "recycling": "Bisa dibuat kompos"
  },
  "alternatives": [
    {
      "category": "kertas",
      "confidence": "5%"
    }
  ]
}
```

---

## 🎓 Kesimpulan

**Ruang Hijau adalah sistem yang:**

✅ **Mudah digunakan** - Interface sederhana & intuitif

✅ **Powerful** - Terintegrasi dengan AI/ML modern

✅ **Aman** - Password hashed, token validation, HTTPS

✅ **Cepat** - Optimasi database & caching

✅ **Scalable** - Bisa menangani banyak pengguna

✅ **Edukatif** - Chatbot membantu pengguna belajar

✅ **Actionable** - User bisa langsung ikut kampanye

---

## 📞 Pertanyaan Umum (FAQ)

### Q: Berapa lama chatbot menjawab?

**A:** Pertama kali 30-60 detik, lain kali 2-5 detik. Ini normal karena load model.

### Q: Apakah foto saya aman?

**A:** Ya, foto di-validasi & disimpan aman di server, bukan di publik.

### Q: Bagaimana jika lupa password?

**A:** Ada fitur "Lupa Password" yang kirim link reset ke email.

### Q: Apakah data saya dijual?

**A:** Tidak, data Anda adalah milik Anda. Server hanya menyimpan.

### Q: Berapa biaya pakai aplikasi?

**A:** Gratis! (tergantung kebijakan admin)

### Q: Bagaimana kalau ada bug?

**A:** Hubungi tim support atau laporkan di dalam aplikasi.

---

**Dibuat dengan 💚 untuk komunitas lingkungan Indonesia**

Last Updated: January 28, 2026
