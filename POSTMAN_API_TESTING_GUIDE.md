# Panduan API Testing dengan POSTMAN

## Ruang Hijau Backend

---

## Daftar Isi

1. [Pengenalan](#pengenalan)
2. [Instalasi POSTMAN](#instalasi-postman)
3. [Setup Awal](#setup-awal)
4. [Membuat Koleksi API](#membuat-koleksi-api)
5. [Testing Endpoints](#testing-endpoints)
6. [Variabel dan Environment](#variabel-dan-environment)
7. [Script Pre-request dan Test](#script-pre-request-dan-test)
8. [Tips dan Trik](#tips-dan-trik)

---

## Pengenalan

**POSTMAN** adalah sebuah tool yang powerful untuk testing, dokumentasi, dan development API. Dengan POSTMAN, Anda dapat:

- Mengirim HTTP requests (GET, POST, PUT, DELETE, dll)
- Melakukan testing terhadap response
- Mengatur variabel dan environment
- Membuat dokumentasi API otomatis
- Melakukan automation testing

Dokumentasi ini akan memandu Anda dalam testing API **Ruang Hijau Backend** menggunakan POSTMAN.

---

## Instalasi POSTMAN

### Option 1: Desktop Application

1. Kunjungi [www.postman.com/downloads](https://www.postman.com/downloads)
2. Download sesuai OS Anda (Windows, Mac, Linux)
3. Install dan jalankan aplikasi
4. Sign up atau login dengan akun Postman

### Option 2: Web Version

1. Kunjungi [www.web.postman.co](https://www.web.postman.co)
2. Buat akun atau login
3. Mulai gunakan langsung di browser

---

## Setup Awal

### 1. Membuat Workspace

```
1. Klik "Workspaces" di sidebar
2. Klik "+ Create Workspace"
3. Masukkan nama: "Ruang Hijau API Testing"
4. Pilih "Personal" atau "Team"
5. Klik "Create"
```

### 2. Menentukan Base URL

Sebelum mulai testing, tentukan URL server Anda:

**Development:**

```
http://localhost:5000
```

**Production:**

```
https://api.ruanghijau.com
```

---

## Membuat Koleksi API

### Langkah 1: Membuat Koleksi

```
1. Klik tombol "+ Create" di sidebar
2. Pilih "Collection"
3. Masukkan nama: "Ruang Hijau API"
4. Klik "Create"
```

### Langkah 2: Membuat Folder untuk Setiap Modul

Dalam koleksi, buat folder untuk setiap module/route:

- Auth Routes
- User Routes
- Post Routes
- Comment Routes
- Campaign Routes
- Chatbot Routes
- Donation Routes
- Volunteer Routes
- Waste Detection Routes
- Admin Routes

**Cara membuat folder:**

```
1. Hover ke nama koleksi "Ruang Hijau API"
2. Klik "..." > "Add folder"
3. Masukkan nama folder
```

---

## Testing Endpoints

### 1. Authentication Endpoints

#### 1.1 Login

**Method:** POST  
**URL:** `{{base_url}}/api/auth/login`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Expected Response (200):**

```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

#### 1.2 Register

**Method:** POST  
**URL:** `{{base_url}}/api/auth/register`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Expected Response (201):**

```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": 2,
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

---

#### 1.3 Logout

**Method:** POST  
**URL:** `{{base_url}}/api/auth/logout`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

### 2. Post Endpoints

#### 2.1 Get All Posts

**Method:** GET  
**URL:** `{{base_url}}/api/posts`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Query Parameters (optional):**

- `page`: nomor halaman (default: 1)
- `limit`: jumlah data per halaman (default: 10)

**Expected Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Cara Menanam Pohon",
      "content": "Berikut langkah-langkah...",
      "author": "John Doe",
      "created_at": "2025-01-28T10:30:00Z",
      "image_url": "https://example.com/image.jpg",
      "likes": 5,
      "comments_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25
  }
}
```

---

#### 2.2 Create Post

**Method:** POST  
**URL:** `{{base_url}}/api/posts`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "title": "Tips Menghemat Air",
  "content": "Berikut adalah cara-cara efektif untuk menghemat air...",
  "category": "tips"
}
```

**Expected Response (201):**

```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": 26,
    "title": "Tips Menghemat Air",
    "content": "Berikut adalah cara-cara efektif untuk menghemat air...",
    "author": "John Doe",
    "created_at": "2025-01-28T11:00:00Z"
  }
}
```

---

#### 2.3 Get Post Detail

**Method:** GET  
**URL:** `{{base_url}}/api/posts/{{post_id}}`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Cara Menanam Pohon",
    "content": "Berikut langkah-langkah...",
    "author": "John Doe",
    "created_at": "2025-01-28T10:30:00Z",
    "image_url": "https://example.com/image.jpg",
    "likes": 5,
    "comments": [
      {
        "id": 1,
        "author": "Jane Doe",
        "content": "Bagus sekali artikelnya!",
        "created_at": "2025-01-28T10:45:00Z"
      }
    ]
  }
}
```

---

#### 2.4 Update Post

**Method:** PUT  
**URL:** `{{base_url}}/api/posts/{{post_id}}`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "title": "Cara Menanam Pohon (Updated)",
  "content": "Updated content..."
}
```

**Expected Response (200):**

```json
{
  "success": true,
  "message": "Post updated successfully"
}
```

---

#### 2.5 Delete Post

**Method:** DELETE  
**URL:** `{{base_url}}/api/posts/{{post_id}}`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

---

### 3. Comment Endpoints

#### 3.1 Create Comment

**Method:** POST  
**URL:** `{{base_url}}/api/posts/{{post_id}}/comments`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "content": "Terima kasih atas informasi yang sangat bermanfaat!"
}
```

**Expected Response (201):**

```json
{
  "success": true,
  "message": "Comment created successfully",
  "data": {
    "id": 10,
    "post_id": 1,
    "author": "Jane Doe",
    "content": "Terima kasih atas informasi yang sangat bermanfaat!",
    "created_at": "2025-01-28T11:15:00Z"
  }
}
```

---

#### 3.2 Get Post Comments

**Method:** GET  
**URL:** `{{base_url}}/api/posts/{{post_id}}/comments`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "post_id": 1,
      "author": "Jane Doe",
      "content": "Terima kasih atas informasi yang sangat bermanfaat!",
      "created_at": "2025-01-28T11:15:00Z"
    }
  ]
}
```

---

#### 3.3 Delete Comment

**Method:** DELETE  
**URL:** `{{base_url}}/api/comments/{{comment_id}}`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

---

### 4. Campaign Endpoints

#### 4.1 Get All Campaigns

**Method:** GET  
**URL:** `{{base_url}}/api/campaigns`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Penanaman 1000 Pohon",
      "description": "Kampanye untuk menanam 1000 pohon di Jakarta",
      "target_amount": 10000000,
      "current_amount": 5500000,
      "status": "active",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

#### 4.2 Create Campaign

**Method:** POST  
**URL:** `{{base_url}}/api/campaigns`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "title": "Pembersihan Pantai",
  "description": "Kampanye untuk membersihkan sampah plastik di pantai",
  "target_amount": 5000000,
  "category": "cleanup"
}
```

**Expected Response (201):**

```json
{
  "success": true,
  "message": "Campaign created successfully"
}
```

---

### 5. Donation Endpoints

#### 5.1 Create Donation

**Method:** POST  
**URL:** `{{base_url}}/api/donations`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "campaign_id": 1,
  "amount": 100000,
  "payment_method": "credit_card"
}
```

**Expected Response (201):**

```json
{
  "success": true,
  "message": "Donation created successfully",
  "data": {
    "id": 5,
    "campaign_id": 1,
    "amount": 100000,
    "status": "pending",
    "created_at": "2025-01-28T11:30:00Z"
  }
}
```

---

#### 5.2 Get Donation History

**Method:** GET  
**URL:** `{{base_url}}/api/donations`

**Headers:**

```
Authorization: Bearer {{token}}
```

**Expected Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "campaign_id": 1,
      "amount": 250000,
      "status": "completed",
      "created_at": "2025-01-20T08:00:00Z"
    }
  ]
}
```

---

### 6. Chatbot Endpoints

#### 6.1 Send Chat Message

**Method:** POST  
**URL:** `{{base_url}}/api/chatbot/chat`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body (JSON):**

```json
{
  "message": "Bagaimana cara menjadi volunteer?"
}
```

**Expected Response (200):**

```json
{
  "success": true,
  "response": "Untuk menjadi volunteer, Anda dapat mendaftar di halaman Volunteer kami...",
  "confidence": 0.95
}
```

---

### 7. Waste Detection Endpoints

#### 7.1 Analyze Waste Image

**Method:** POST  
**URL:** `{{base_url}}/api/waste-detection/analyze`

**Headers:**

```
Authorization: Bearer {{token}}
(Form-data, bukan JSON)
```

**Body (Form-data):**

- Key: `image`
- Type: File
- Value: [Select image file]

**Expected Response (200):**

```json
{
  "success": true,
  "data": {
    "waste_type": "plastic",
    "confidence": 0.92,
    "recommendation": "Plastik ini dapat didaur ulang"
  }
}
```

---

## Variabel dan Environment

### 1. Membuat Environment

```
1. Klik "Environments" di sidebar
2. Klik "+ Create Environment"
3. Masukkan nama: "Development"
4. Tambahkan variabel:
   - base_url: http://localhost:5000
   - token: (akan diisi setelah login)
```

### 2. Menggunakan Variabel

Gunakan sintaks `{{variable_name}}` dalam requests:

**Contoh URL:**

```
{{base_url}}/api/posts/{{post_id}}
```

**Contoh Header:**

```
Authorization: Bearer {{token}}
```

### 3. Menyimpan Response ke Variabel

Dalam tab **Tests**, gunakan script untuk menyimpan token:

```javascript
// Menyimpan token dari response
if (pm.response.code === 200) {
  var jsonData = pm.response.json();
  pm.environment.set("token", jsonData.token);
}

// Menyimpan post_id
if (pm.response.code === 201) {
  var jsonData = pm.response.json();
  pm.environment.set("post_id", jsonData.data.id);
}
```

---

## Script Pre-request dan Test

### 1. Pre-request Script

Pre-request script dijalankan sebelum request dikirim.

**Contoh: Mengatur timestamp**

```javascript
pm.environment.set("timestamp", new Date().toISOString());
```

**Contoh: Mengecek token**

```javascript
var token = pm.environment.get("token");
if (!token) {
  console.log("Warning: Token tidak ditemukan. Silakan login terlebih dahulu.");
}
```

### 2. Test Script

Test script dijalankan setelah response diterima untuk melakukan assertions.

#### Contoh 1: Testing Status Code

```javascript
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});
```

#### Contoh 2: Testing Response Content

```javascript
pm.test("Response has success property", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.success).to.equal(true);
});
```

#### Contoh 3: Testing Multiple Conditions

```javascript
pm.test("Login response is valid", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.success).to.equal(true);
  pm.expect(jsonData.token).to.be.a("string");
  pm.expect(jsonData.user.email).to.be.a("string");
});
```

#### Contoh 4: Menyimpan Data dari Response

```javascript
pm.test("Save token to environment", function () {
  var jsonData = pm.response.json();
  pm.environment.set("token", jsonData.token);
  pm.environment.set("user_id", jsonData.user.id);
});
```

#### Contoh 5: Testing Array Response

```javascript
pm.test("Posts array is not empty", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.data).to.be.an("array");
  pm.expect(jsonData.data.length).to.be.greaterThan(0);
});
```

---

## Tips dan Trik

### 1. Collection Runner

Jalankan semua request dalam satu folder secara berurutan:

```
1. Klik "..." pada folder
2. Pilih "Run folder"
3. Atur delay antar request
4. Klik "Run"
```

**Keuntungan:**

- Menjalankan test suite lengkap
- Melihat summary hasil testing
- Dapat di-export sebagai laporan

### 2. Data-driven Testing

Testing dengan multiple data set:

```
1. Buat file CSV atau JSON dengan test data
2. Di Collection Runner, pilih file tersebut
3. Postman akan menjalankan request untuk setiap baris data
```

### 3. Monitoring

Jalankan request secara berkala:

```
1. Klik "..." pada Collection
2. Pilih "Monitor this collection"
3. Atur interval monitoring (misalnya: setiap 5 menit)
4. Postman akan mengirim notifikasi jika ada error
```

### 4. Generate Documentation

Otomatis generate dokumentasi API:

```
1. Klik "View more actions" (...) pada Collection
2. Pilih "View documentation"
3. Postman akan generate dokumentasi berdasarkan requests
```

### 5. Import/Export Collection

**Export:**

```
1. Klik "..." pada Collection
2. Pilih "Export"
3. Pilih format (JSON v2.1)
4. Simpan file
```

**Import:**

```
1. Klik "Import" di workspace
2. Pilih file collection
3. Klik "Import"
```

### 6. Debugging dengan Console

Gunakan Postman Console untuk debugging:

```
1. Tekan Ctrl+Alt+C (Windows/Linux) atau Cmd+Option+C (Mac)
2. Lihat log dari pre-request dan test scripts
3. Gunakan console.log() dalam script untuk debug
```

### 7. Workflow Testing

Buat workflow otomatis menggunakan Postman scripts:

```javascript
// Setelah login berhasil, otomatis jalankan request berikutnya
pm.test("Login successful", function () {
  var jsonData = pm.response.json();
  if (jsonData.success) {
    pm.environment.set("token", jsonData.token);
    // Postman akan menggunakan token ini untuk request berikutnya
  }
});
```

### 8. Conditional Request Flow

Mengontrol alur request berdasarkan kondisi:

```javascript
var token = pm.environment.get("token");

// Jika token ada, lanjutkan testing
if (token) {
  console.log("Token tersedia, melanjutkan testing...");
} else {
  console.log("Token tidak tersedia, silakan login dulu");
  pm.execution.skipRequest();
}
```

---

## Contoh Testing Scenario

### Scenario 1: Full User Journey

1. **Register** - Membuat akun baru
2. **Login** - Login dengan akun baru
3. **Create Post** - Membuat post baru
4. **Get All Posts** - Mengambil semua posts
5. **Add Comment** - Memberikan komentar
6. **Logout** - Keluar dari aplikasi

### Scenario 2: Campaign Donation Flow

1. **Get Campaigns** - Melihat semua kampanye
2. **Get Campaign Detail** - Melihat detail campaign
3. **Create Donation** - Melakukan donasi
4. **Get Donation History** - Melihat history donasi

### Scenario 3: Error Testing

1. **Invalid Login** - Test dengan email/password salah
2. **Unauthorized Request** - Test tanpa token
3. **Not Found** - Test dengan ID yang tidak ada
4. **Validation Error** - Test dengan data invalid

---

## Troubleshooting

### Problem: "Authorization header not found"

**Solution:**

```
- Pastikan Anda telah login dan token tersimpan di environment
- Tambahkan header: Authorization: Bearer {{token}}
- Cek di tab "Headers" atau "Authorization"
```

### Problem: "Request timeout"

**Solution:**

```
- Cek apakah server sedang running
- Cek base_url yang benar
- Tingkatkan timeout di Settings
```

### Problem: "CORS error"

**Solution:**

```
- Pastikan backend sudah mengonfigurasi CORS dengan benar
- Gunakan header yang sesuai
```

### Problem: "Response not showing"

**Solution:**

```
- Pastikan request format benar (JSON, Form-data, dll)
- Cek content-type header
- Buka Postman Console untuk melihat detail error
```

---

## Best Practices

1. **Organisasi** - Kelompokkan requests dalam folder yang terstruktur
2. **Dokumentasi** - Berikan deskripsi lengkap untuk setiap request
3. **Testing** - Selalu tambahkan test scripts untuk assertions
4. **Environment** - Gunakan variabel untuk base_url dan credentials
5. **Backup** - Regularly export dan backup collection Anda
6. **Automation** - Gunakan Collection Runner untuk automated testing
7. **Monitoring** - Setup monitoring untuk critical endpoints
8. **Version Control** - Simpan collection di Git/version control

---

## Referensi

- [Postman Official Documentation](https://learning.postman.com/)
- [Postman Learning Center](https://learning.postman.com/docs/getting-started/introduction/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Last Updated:** 28 Januari 2026  
**Version:** 1.0
