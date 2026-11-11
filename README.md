# 🔗 Resource Link Hub

> **Studi Kasus 9 — Repositori Tautan Modul Praktikum**  
> Cloud Computing · Semester 7 · Telkom University

Aplikasi web full-stack untuk menyimpan dan mengelola tautan referensi modul praktikum, dibangun dengan **Python murni** (tanpa framework), **Nginx**, dan **Docker Compose**, serta terintegrasi dengan **Jenkins CI/CD Pipeline**.

---

## 📐 Arsitektur Sistem

```
                        ┌─────────────────────────────┐
  Browser               │     Docker Bridge: app-net   │
  :8081 ───────────────►│                              │
                        │  ┌─────────────────────────┐ │
                        │  │  frontend (nginx:alpine) │ │
                        │  │  container_name:         │ │
                        │  │  resource-link-frontend  │ │
                        │  │  Port: 8081:80           │ │
                        │  │                          │ │
                        │  │  GET /      → index.html │ │
                        │  │  /links  ──► proxy_pass  │ │
                        │  └────────────┬────────────┘ │
                        │               │               │
                        │  ┌────────────▼────────────┐ │
                        │  │  backend (python:3.11)  │ │
                        │  │  container_name:        │ │
                        │  │  resource-link-backend  │ │
                        │  │  Port: 5000:5000         │ │
                        │  │                          │ │
                        │  │  GET    /links           │ │
                        │  │  POST   /links           │ │
                        │  │  DELETE /links?index=X   │ │
                        │  └────────────┬────────────┘ │
                        │               │               │
                        └───────────────┼───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │   Named Volume: link-hub-data  │
                        │   /var/lib/backend_data/       │
                        │   links.json  (persistent)     │
                        └────────────────────────────────┘
```

### Komponen

| Komponen | Teknologi | Port | Peran |
|---|---|---|---|
| **Backend** | Python 3.11 `http.server` | `5000` | REST API, baca/tulis JSON |
| **Frontend** | Nginx Alpine + Vanilla JS | `8081` | Serve UI, reverse proxy |
| **Storage** | Named Volume Docker | — | Persistensi data `links.json` |
| **CI/CD** | Jenkins Declarative Pipeline | — | Otomasi build & deploy |

---

## 📁 Struktur Proyek

```
project/
├── app.py               # REST API backend (pure Python, no framework)
├── Dockerfile           # Build image backend
├── index.html           # UI single-page (HTML5 + CSS dark mode + Vanilla JS)
├── nginx.conf           # Konfigurasi reverse proxy Nginx
├── docker-compose.yml   # Orkestrasi seluruh layanan
├── Jenkinsfile          # CI/CD Declarative Pipeline (5 stage)
└── README.md            # Dokumentasi ini
```

---

## 🔌 Endpoint API

Base URL: `http://localhost:5000`

### `GET /links`
Ambil seluruh daftar tautan yang tersimpan.

```bash
curl http://localhost:5000/links
```

**Response `200 OK`:**
```json
[
  {
    "title": "Panduan Docker Compose",
    "category": "DevOps",
    "url": "https://docs.docker.com/compose/",
    "description": "Dokumentasi resmi Docker Compose."
  }
]
```

---

### `POST /links`
Tambah tautan baru. Semua field wajib diisi.

```bash
curl -X POST http://localhost:5000/links \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Panduan Docker Compose",
    "category": "DevOps",
    "url": "https://docs.docker.com/compose/",
    "description": "Dokumentasi resmi Docker Compose."
  }'
```

**Response `201 Created`:**
```json
{
  "message": "Link added successfully",
  "link": {
    "title": "Panduan Docker Compose",
    "category": "DevOps",
    "url": "https://docs.docker.com/compose/",
    "description": "Dokumentasi resmi Docker Compose."
  }
}
```

**Response `400 Bad Request`** (field kosong atau body tidak valid):
```json
{ "error": "Missing required fields: description, url" }
```

---

### `DELETE /links?index=X`
Hapus tautan berdasarkan indeks (mulai dari `0`).

```bash
curl -X DELETE "http://localhost:5000/links?index=0"
```

**Response `200 OK`:**
```json
{
  "message": "Link deleted successfully",
  "deleted": { "title": "Panduan Docker Compose", "..." : "..." }
}
```

**Response `404 Not Found`** (indeks tidak valid):
```json
{ "error": "Index 99 out of range. Valid range: 0 – 2" }
```

**Response `400 Bad Request`** (parameter tidak ada / bukan integer):
```json
{ "error": "Missing query parameter: index (e.g., DELETE /links?index=0)" }
```

---

## 🚀 Cara Menjalankan dengan Docker Compose

### Prasyarat
- Docker Desktop terinstal dan **sudah Running**
- Port `5000` dan `8081` tidak dipakai proses lain

### 1. Clone & Masuk ke Direktori
```bash
git clone <URL_REPO> resource-link-hub
cd resource-link-hub
```

### 2. Build & Jalankan Semua Layanan
```bash
docker compose up --build -d
```

### 3. Verifikasi Status Container
```bash
docker compose ps
```

Output yang diharapkan:
```
NAME                       IMAGE               STATUS
resource-link-backend      project-backend     Up (healthy)
resource-link-frontend     nginx:alpine        Up
```

### 4. Akses Aplikasi
| Layanan | URL |
|---|---|
| **UI Web** | http://localhost:8081 |
| **API Backend** | http://localhost:5000/links |

### 5. Lihat Log Real-time
```bash
docker compose logs -f
docker compose logs -f backend    # hanya backend
docker compose logs -f frontend   # hanya frontend
```

### 6. Hentikan Layanan
```bash
docker compose down
```

---

## 🛡️ Simulasi Data Immunity (Persistensi Volume)

Eksperimen ini membuktikan bahwa data **tidak hilang** meski container backend dihapus paksa, karena tersimpan di **Named Volume** `link-hub-data`.

### Langkah Simulasi

**Step 1 — Tambahkan beberapa tautan melalui UI** di http://localhost:8081  
atau via curl:
```bash
curl -X POST http://localhost:5000/links \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Link","category":"Test","url":"https://example.com","description":"Uji persistensi data"}'
```

**Step 2 — Verifikasi data tersimpan:**
```bash
curl http://localhost:5000/links
```

**Step 3 — Hapus paksa container backend (simulasi crash/failure):**
```bash
docker rm -f resource-link-backend
```

**Step 4 — Verifikasi container mati:**
```bash
docker compose ps
# STATUS backend → Exited / tidak ada
```

**Step 5 — Hidupkan kembali backend:**
```bash
docker compose up -d backend
```

**Step 6 — Verifikasi data MASIH ADA (Data Immunity terbukti ✅):**
```bash
curl http://localhost:5000/links
# Data yang ditambah di Step 1 masih muncul
```

> **Mengapa data tidak hilang?**  
> Named Volume `link-hub-data` bersifat independen dari lifecycle container.  
> File `links.json` di `/var/lib/backend_data/` tetap ada di volume meski container dihapus.

---

## ⚙️ Jenkins CI/CD Pipeline

### Alur Pipeline (5 Stage)

```
┌──────────┐   ┌──────────────┐   ┌─────────────┐   ┌────────────────┐   ┌──────────────┐
│ Checkout │──►│ Syntax Check │──►│ Build Image │──►│   Automated    │──►│ Health Check │
│ (scm)    │   │ py_compile + │   │ docker comp │   │   Deployment   │   │ curl :5000   │
│          │   │ compose -q   │   │ build --no- │   │ compose up -d  │   │ curl :8081   │
│          │   │              │   │ cache       │   │ --remove-orph. │   │ (5s delay)   │
└──────────┘   └──────────────┘   └─────────────┘   └────────────────┘   └──────────────┘
```

| Stage | Perintah Utama | Tujuan |
|---|---|---|
| **Checkout** | `checkout scm` | Ambil kode dari repository |
| **Syntax Check** | `python3 -m py_compile app.py` + `docker compose config -q` | Validasi sintaks Python & Compose |
| **Build Image** | `docker compose build --no-cache backend` | Build ulang image bersih |
| **Automated Deployment** | `docker compose up -d --remove-orphans` | Deploy ke Docker host |
| **Health Check** | `curl -f http://localhost:5000/links` + `curl -f http://localhost:8081` | Pastikan layanan responsif |

---

## 🔗 Setup GitHub Webhook ke Jenkins

### Prasyarat
- Jenkins sudah terinstal dan dapat diakses dari internet (atau menggunakan **ngrok** untuk lokal)
- Plugin Jenkins: **Git**, **GitHub Integration**
- Repository GitHub sudah ada dengan kode proyek ini

---

### Langkah 1 — Buat Pipeline Job di Jenkins

1. Buka Jenkins → **New Item**
2. Masukkan nama, pilih **Pipeline** → **OK**
3. Di bagian **Build Triggers**, centang:  
   ☑ **GitHub hook trigger for GITScm polling**
4. Di bagian **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/<username>/<repo>.git`
   - Branch: `*/main` (atau `*/master`)
   - Script Path: `Jenkinsfile`
5. Klik **Save**

---

### Langkah 2 — Dapatkan URL Webhook Jenkins

Format URL webhook Jenkins:
```
http://<JENKINS_HOST>/github-webhook/
```

Jika Jenkins berjalan lokal, gunakan **ngrok** untuk expose:
```bash
ngrok http 8080
# Contoh output: https://abc123.ngrok.io → http://localhost:8080
# Webhook URL: https://abc123.ngrok.io/github-webhook/
```

---

### Langkah 3 — Tambahkan Webhook di GitHub

1. Buka repository GitHub → **Settings** → **Webhooks** → **Add webhook**
2. Isi form:

   | Field | Nilai |
   |---|---|
   | **Payload URL** | `http://<JENKINS_HOST>/github-webhook/` |
   | **Content type** | `application/json` |
   | **Secret** | *(opsional, direkomendasikan)* |
   | **Which events?** | ☑ **Just the push event** |
   | **Active** | ☑ |

3. Klik **Add webhook**
4. GitHub akan mengirim ping → cek tanda ✅ hijau di daftar webhook

---

### Langkah 4 — Verifikasi Integrasi

Push perubahan ke branch `main`:
```bash
git add .
git commit -m "feat: trigger Jenkins via webhook"
git push origin main
```

Jenkins akan otomatis:
1. Menerima notifikasi dari GitHub
2. Menjalankan seluruh 5 stage pipeline
3. Menampilkan status build ✅ / ❌ di dashboard

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---|---|
| `port is already allocated` | `docker compose down` lalu coba lagi |
| Backend `unhealthy` | `docker compose logs backend` untuk lihat error |
| Data hilang setelah `docker compose down -v` | Flag `-v` **menghapus volume** — hindari kecuali ingin reset total |
| Webhook tidak terpicu | Pastikan Jenkins accessible dari internet & URL diakhiri `/` |
| `py_compile` gagal di Jenkins | Pastikan `python3` tersedia di Jenkins agent |

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik Studi Kasus 9 Cloud Computing.

