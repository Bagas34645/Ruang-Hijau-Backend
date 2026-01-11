@echo off
echo ========================================================
echo   RUANG HIJAU BACKEND RUNNER
echo ========================================================
echo.

:: Check environment
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan! Menggunakan .env.example...
    copy .env.example .env
    echo [INFO] File .env telah dibuat. Silakan edit jika perlu.
)

:: Set environment variables for external access
set SERVER_HOST=0.0.0.0
set FLASK_DEBUG=True

echo [INFO] Menyalakan server Flask...
echo [INFO] Server akan berjalan di http://0.0.0.0:5000 (Semua Interface)
echo [INFO] Akses dari Android Emulator: http://10.0.2.2:5000
echo [INFO] Akses dari Device Fisik: http://IP_LAPTOP_ANDA:5000
echo.

python app.py

pause
