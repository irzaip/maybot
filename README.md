# MayBot - Chatbot WhatsApp dengan Integrasi AI

MayBot adalah sistem chatbot WhatsApp berbasis Python yang menggabungkan FastAPI untuk layanan web, Ollama untuk pemrosesan AI lokal, dan SQLite untuk penyimpanan data. Bot ini mendukung berbagai persona dan tipe percakapan untuk berbagai kasus penggunaan, dengan kemampuan penanganan media untuk mengirim gambar dan dokumen kepada pengguna.

## Fitur

- **Dukungan Multi-Persona**: Konfigurasi persona AI yang berbeda untuk konteks percakapan yang berbeda
- **Respons Bertenaga AI**: Pemrosesan AI lokal menggunakan Ollama untuk privasi dan kecepatan
- **Lampiran Media**: Kirim gambar (JPG, PNG) dan dokumen PDF ke pengguna
- **Manajemen Percakapan**: Penyimpanan berbasis SQLite untuk riwayat chat dan data pengguna
- **REST API**: Endpoint FastAPI untuk integrasi dan pengujian
- **Pesan Real-time**: Integrasi WhatsApp-web.js untuk pengiriman pesan yang andal

## Arsitektur

```
maybot/
├── wa.py                    # Aplikasi FastAPI utama dan integrasi WhatsApp
├── backend/
│   └── media_helpers.py     # Utilitas encoding media (Base64)
├── media/                   # Direktori untuk file media pengujian
├── waworks/                 # Klien WhatsApp-web.js (Node.js)
├── config.toml              # Konfigurasi aplikasi
├── cr.sql                   # Skema database
├── cipibot.db               # Database SQLite (dibuat saat pertama dijalankan)
└── requirements.txt         # Dependensi Python
```

## Prasyarat

- **Python**: 3.11 atau lebih tinggi
- **Node.js**: 18+ (untuk klien WhatsApp-web.js)
- **Ollama**: Server AI lokal berjalan (default: localhost:11434)
- **SQLite**: Bawaan (tidak memerlukan instalasi terpisah)

## Memulai

### 1. Setup Environment

```bash
# Membuat dan mengaktifkan virtual environment
.\env\Scripts\activate

# Menginstal dependensi Python
pip install -r requirements.txt
```

### 2. Inisialisasi Database

```bash
# Membuat database dengan skema
sqlite3 cipibot.db < cr.sql
```

### 3. Menjalankan Ollama (jika menggunakan fitur AI)

```bash
# Mengunduh model (contoh: llama3.2)
ollama pull llama3.2

# Menjalankan server Ollama
ollama serve
```

### 4. Menjalankan Aplikasi

```bash
# Metode 1: Perintah langsung
uvicorn wa:app --port 8998 --host 192.168.30.50

# Metode 2: File batch (termasuk layanan Node.js)
run.bat

# Metode 3: File batch Maya backend
maya_be.bat
```

## Konfigurasi

Semua konfigurasi dikelola melalui `config.toml`:

```toml
[CONFIG]
LOGDIR = "logs/"
DEBUG = true

[OLLAMA]
BASE_URL = "http://localhost:11434"
MODEL = "llama3.2"

[PERSONAS]
default = "asistent"
asistent = "Anda adalah asisten yang membantu."
fun = "Anda adalah chatbot yang menyenangkan."
```

### Konfigurasi Persona

Definisikan persona di bagian `[PERSONAS]` dalam `config.toml`:

```toml
[PERSONAS]
default = "Anda adalah asisten yang membantu."
support = "Anda adalah agen dukungan pelanggan. Bersikap profesional dan sopan."
fun = "Anda adalah chatbot yang menyenangkan. Gunakan humor dan emoji dengan tepat."
```

## Endpoint API

### Kesehatan & Pengujian

| Metode | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/ping` | Endpoint pemeriksaan kesehatan |
| GET | `/messages/media` | Pengujian respons media (mengembalikan teks + lampiran) |
| GET | `/test_send/{number}` | Pengujian pengiriman pesan ke nomor WhatsApp |

### Penanganan Pesan

| Metode | Endpoint | Deskripsi |
|--------|----------|-------------|
| POST | `/messages` | Endpoint utama pemrosesan pesan |
| POST | `/messages/webhook` | Webhook WhatsApp untuk pesan masuk |

### Format Respons Media

Endpoint `/messages/media` mengembalikan JSON dengan struktur berikut:

```json
{
  "text": "Halo! Ini pesan teks.",
  "attachments": [
    {
      "mimetype": "image/jpeg",
      "data": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
      "filename": "test.jpg"
    }
  ]
}
```

**Jenis Lampiran yang Didukung:**
- `image/jpeg` - Gambar JPEG
- `image/png` - Gambar PNG
- `application/pdf` - Dokumen PDF

**Batas Ukuran File:** Maksimum 10MB per file

## Penanganan Media

### Direktori Media

Tempatkan file media di direktori `media/`:

```
media/
├── test.jpg       # Gambar pengujian (merah 100x100 piksel)
└── test.pdf       # Dokumen PDF pengujian
```

### Membuat Media Pengujian

**Gambar (Python/PIL):**
```python
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('media/test.jpg', 'JPEG')
```

**PDF (Minimal):**
```python
content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 24 Tf 100 700 Td (Test PDF Document) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer << /Size 5 /Root 1 0 R >>
startxref
306
%%EOF"""
with open('media/test.pdf', 'wb') as f:
    f.write(content)
```

### Utilitas Media Backend

Modul `backend/media_helpers.py` menyediakan fungsi encoding:

```python
from backend.media_helpers import make_media_response, encode_file

# Membuat respons media
response = make_media_response(
    text="Periksa gambar ini!",
    image_path="media/test.jpg",
    pdf_path="media/test.pdf"
)

# Encoding file tunggal ke base64
base64_data, mimetype, filename = encode_file("media/test.jpg")
```

## Pengembangan

### Gaya Kode

- **Versi Python**: 3.11+
- **Panduan Gaya**: PEP 8
- **Linter**: Ruff (dikonfigurasi di requirements.txt)
- **Panjang Baris**: 88 karakter

### Linting & Formatting

```bash
# Memeriksa masalah
python -m ruff check .

# Memperbaiki masalah secara otomatis
python -m ruff check --fix .
```

### Pengujian

```bash
# Menjalankan file pengujian
python test_agent.py

# Pengujian endpoint manual
curl http://192.168.30.50:8998/ping
curl http://192.168.30.50:8998/messages/media
curl http://192.168.30.50:8998/test_send/6285775300227@c.us
```

### Operasi Database

```bash
# Melihat isi database
sqlite3 cipibot.db "SELECT * FROM conversations LIMIT 10;"

# Ekspor ke SQL
sqlite3 cipibot.db .dump > backup.sql
```

## Struktur Proyek

### Komponen Inti

| File | Deskripsi |
|------|-----------|
| `wa.py` | Aplikasi FastAPI utama dan integrasi WhatsApp |
| `backend/media_helpers.py` | Utilitas encoding media untuk pemrosesan Base64 |
| `config.toml` | Konfigurasi aplikasi dan definisi persona |
| `cr.sql` | Skema database SQLite |
| `requirements.txt` | Dependensi Python |

### Modul Pendukung

| File | Deskripsi |
|------|-----------|
| `conversations.py` | Model data dan manajemen percakapan |
| `ollama_api.py` | Integrasi AI/LLM menggunakan Ollama |
| `db_oper.py` | Operasi database dan manajemen SQLite |
| `agent[1-8].py` | Implementasi agen khusus |
| `persona_func.py` | Fungsi manajemen persona |
| `conv_func.py` | Utilitas pemrosesan percakapan |
| `Msgproc.py` | Logika pemrosesan pesan |
| `reduksi.py` | Reduksi teks/manajemen token |
| `trans_id.py` | Penanganan transaksi/ID |
| `counting.py` | Pelacakan penggunaan dan analitik |

### Klien WhatsApp

| Direktori | Deskripsi |
|-----------|-----------|
| `waworks/` | Klien WhatsApp-web.js Node.js |
| `waworks/index.js` | Logika utama klien dengan penanganan pesan |

## Dependensi

### Dependensi Python

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0
toml>=0.10.2
ollama>=0.1.0
ruff>=0.1.0
```

### Dependensi Node.js (waworks/)

```json
{
  "whatsapp-web.js": "^1.23.0",
  "localtunnel": "^2.0.2",
  "qrcode-terminal": "^0.12.0"
}
```

## Contoh Penggunaan

### Mengirim Pesan Sederhana

```python
import requests

response = requests.post(
    "http://192.168.30.50:8998/test_send/6285775300227@c.us",
    json={"message": "Halo dari MayBot!"}
)
print(response.json())
```

### Mengirim Lampiran Media

```python
import requests

response = requests.post(
    "http://192.168.30.50:8998/messages/media"
)
# Respons berisi teks + lampiran Base64
data = response.json()
print(data["text"])           # Teks pesan
print(len(data["attachments"]))  # Jumlah lampiran
```

### Pemeriksaan Kesehatan

```bash
curl http://192.168.30.50:8998/ping
# Respons yang diharapkan: {"status": "ok"}
```

## Pemecahan Masalah

### Port Sudah Digunakan

```bash
# Mencari proses yang menggunakan port 8998
netstat -ano | findstr :8998

# Menghentikan proses (ganti PID)
taskkill /PID <PID> /F
```

### QR Code Tidak Terbentuk

Pastikan klien WhatsApp-web.js berjalan dan periksa izin browser. QR code ditampilkan di terminal Node.js.

### Pesan Tidak Terkirim

1. Periksa apakah server wa.py berjalan
2. Verifikasi WhatsApp sudah terautentikasi (periksa konsol Node.js)
3. Periksa log di direktori `logs/`
4. Pastikan format nomor telepon benar (dengan akhiran @c.us)

### File Media Tidak Berhasil Dikencode

1. Verifikasi file ada di direktori `media/`
2. Periksa ukuran file di bawah 10MB
3. Pastikan file valid (tidak kosong/rusak)
4. Periksa log server untuk kesalahan encoding

## Lisensi

Proyek ini adalah perangkat lunak proprietary. Semua hak dilindungi undang-undang.

## Berkontribusi

1. Fork repositori
2. Buat branch fitur
3. Buat perubahan sesuai panduan gaya kode
4. Jalankan linting: `python -mruff check --fix .`
5. Kirim pull request

## Dukungan

Untuk masalah dan permintaan fitur, silakan laporkan di repositori proyek.
