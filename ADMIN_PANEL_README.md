# Admin Panel - Ruang Hijau

## Deskripsi
Admin panel untuk mengelola aplikasi Ruang Hijau dengan fitur login, dashboard, dan manajemen data.

## Fitur
- ✅ Halaman login dengan autentikasi
- ✅ Dashboard dengan statistik real-time
- ✅ Manajemen Pengguna
- ✅ Manajemen Postingan
- ✅ Manajemen Kampanye
- ✅ Manajemen Donasi
- ✅ Session management
- ✅ Responsive design

## Akses Admin Panel

### URL
- Login: `http://localhost:5000/admin/login`
- Dashboard: `http://localhost:5000/admin/dashboard`

### Kredensial Default
Berdasarkan database schema, gunakan akun admin yang sudah ada:
- Email: `admin@ruanghijau.com`
- Password: `admin123` (atau sesuai dengan yang ada di database)

**Catatan**: Pastikan password di database sudah di-hash dengan `werkzeug.security.generate_password_hash()`

## Struktur File

```
Ruang-Hijau-Backend/
├── templates/
│   ├── login.html              # Halaman login
│   └── admin_dashboard.html    # Dashboard admin
├── static/
│   ├── css/
│   │   └── admin.css           # Styling admin panel
│   └── js/
│       ├── login.js            # JavaScript untuk login
│       └── admin.js            # JavaScript untuk dashboard
└── routes/
    └── admin_routes.py         # Route admin dengan session management
```

## API Endpoints Admin

### Authentication
- `GET /admin/login` - Halaman login
- `POST /admin/login` - Proses login
- `GET /admin/check-auth` - Cek autentikasi
- `POST /admin/logout` - Logout
- `GET /admin/dashboard` - Halaman dashboard

### Statistics
- `GET /api/admin/stats/users` - Total pengguna
- `GET /api/admin/stats/posts` - Total postingan
- `GET /api/admin/stats/campaigns` - Total kampanye
- `GET /api/admin/stats/donations` - Total donasi
- `GET /api/admin/recent-activity` - Aktivitas terbaru
- `GET /api/admin/monthly-stats` - Statistik bulanan

### Management
- `GET /api/admin/users` - Daftar pengguna
- `GET /api/admin/posts` - Daftar postingan
- `DELETE /api/admin/posts/<id>` - Hapus postingan
- `GET /api/admin/campaigns` - Daftar kampanye
- `GET /api/admin/donations` - Daftar donasi

## Konfigurasi

### Session Configuration
Session dikonfigurasi di `app.py`:
- `SECRET_KEY`: Diambil dari environment variable atau default key
- `SESSION_PERMANENT`: True
- `PERMANENT_SESSION_LIFETIME`: 24 jam

### Environment Variables
Tambahkan ke file `.env`:
```
SECRET_KEY=your-secret-key-here
```

## Keamanan

1. **Session Management**: Menggunakan Flask session dengan secret key
2. **Admin Only**: Hanya user dengan role 'admin' yang dapat mengakses
3. **Password Hashing**: Menggunakan werkzeug.security untuk hashing password
4. **CSRF Protection**: Disarankan untuk menambahkan CSRF protection di production

## Cara Menggunakan

1. Pastikan server Flask berjalan
2. Buka browser dan akses `http://localhost:5000/admin/login`
3. Login dengan kredensial admin
4. Setelah login, akan diarahkan ke dashboard
5. Gunakan menu sidebar untuk navigasi antar section

## Catatan Penting

- Pastikan user admin sudah ada di database dengan role 'admin'
- Password harus di-hash menggunakan `generate_password_hash()`
- Untuk production, ganti `SECRET_KEY` dengan key yang aman
- Semua endpoint admin memerlukan autentikasi

## Troubleshooting

### Tidak bisa login
- Pastikan email dan password benar
- Pastikan user memiliki role 'admin' di database
- Cek console browser untuk error JavaScript
- Cek server logs untuk error backend

### Session tidak persist
- Pastikan `SECRET_KEY` sudah di-set
- Cek browser settings untuk cookies
- Pastikan CORS configuration sudah benar

### Data tidak muncul
- Pastikan database sudah terisi data
- Cek koneksi database
- Cek server logs untuk error SQL
