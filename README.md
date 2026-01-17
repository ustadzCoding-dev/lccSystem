# LCCS System

LCCS System adalah aplikasi web berbasis Flask untuk manajemen lomba (tim, babak, penilaian) dengan ekspor hasil ke Excel. Aplikasi ini memakai SQLite untuk pengembangan lokal dan mendukung pengaturan koneksi database untuk produksi (mis. MySQL/PythonAnywhere) melalui variabel lingkungan.

## Fitur utama

- CRUD tim (tambahkan, edit, hapus)
- Konfigurasi babak (jumlah soal per babak, aktif/nonaktif)
- Input dan penghitungan nilai per soal per tim
- Export hasil ke file Excel (.xlsx)
- Pencarian tim berdasarkan nama atau anggota

## Struktur proyek (ringkasan)

- `app.py` — aplikasi Flask utama (routes, models, logic export)
- `config.py` — konfigurasi aplikasi (development/production)
- `requirements.txt` — dependensi Python
- `run_server.py`, `start_server.bat`, `wsgi.py` — runner / deployment helpers
- `templates/` — Jinja2 templates untuk tampilan
- `static/` — aset statis (css, logo, dll)
- `instance/` — folder runtime (sebaiknya di-ignore; berisi `lccs.db` lokal)

## Quick start (Windows / PowerShell)

1. Clone repo:

```powershell
git clone <repo-url>
cd LCCS_System
```

2. Buat virtual environment dan aktifkan (disarankan):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependensi:

```powershell
pip install -r requirements.txt
```

4. Atur variabel lingkungan (development):

```powershell
# Windows PowerShell
$env:FLASK_ENV = "development"
# Optional: set SECRET_KEY jika ingin mengganti nilai default
$env:SECRET_KEY = "your-secret-key"
```

5. Jalankan aplikasi:

```powershell
# Jalankan langsung
python app.py
# Atau gunakan helper jika ada
python run_server.py
```

Aplikasi akan berjalan di `http://127.0.0.1:5000` secara default.

## Variabel lingkungan yang penting

- `FLASK_ENV` — `development` atau `production`. Default adalah `development`.
- `SECRET_KEY` — kunci rahasia Flask; jangan gunakan kunci default di produksi.
- `DATABASE_URL` / `DB_USERNAME`, `DB_PASSWORD`, `DB_HOSTNAME`, `DB_NAME` — digunakan jika `ProductionConfig` memakai MySQL atau service lain.

Catatan: jangan menyimpan nilai-nilai sensitif (SECRET_KEY, credentials) di repo. Gunakan `.env` (di-dev) dan pastikan `.env` tercantum di `.gitignore`.

## Deployment

- Untuk server seperti PythonAnywhere atau VPS, set `FLASK_ENV=production` dan atur `SECRET_KEY` serta connection string database melalui environment variables.
- Gunakan `wsgi.py` atau `run_server.py` sebagai entrypoint bagi WSGI server (Gunicorn, uWSGI) jika diperlukan.

## Testing & Development tips

- Untuk development, aktifkan `DEBUG=True` di `DevelopmentConfig` (sudah diset di `config.py`).
- Gunakan `python-dotenv` untuk mempermudah variabel lingkungan di development, tetapi pastikan `.env` di-ignore.

## Contributing

1. Buat branch baru: `git checkout -b feat/my-change`
2. Buat perubahan, tambahkan test bila perlu.
3. Commit dengan pesan yang jelas, lalu buka pull request.