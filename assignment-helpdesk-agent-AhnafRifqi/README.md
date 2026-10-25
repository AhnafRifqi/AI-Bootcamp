# IT Helpdesk Agent – RAG + Mini-Agent (FastAPI + Docker)

Backend API untuk IT Helpdesk Assistant yang mengintegrasikan **RAG** (untuk pertanyaan kebijakan/informasi) dan **workflow routing sederhana / mini-agent** (untuk pengecekan status tiket) dalam satu sistem. Dibangun dengan FastAPI, FAISS, Gemini AI API, dan dikemas dalam container Docker.

---

## 1. Problem Statement

Tim People & IT Operations menerima ratusan pertanyaan repetitif dari karyawan setiap harinya. Dua jenis permintaan utama:

| Jenis permintaan | Contoh | Komponen yang menangani |
|-----------------|--------|------------------------|
| **FAQ / Informasi kebijakan** | "Berapa jatah cuti tahunan saya?", "Bagaimana cara reset password VPN?" | **RAG** (retrieval dari knowledge base + LLM) |
| **Status tiket (aksi spesifik)** | "Apa status tiket TICKET-0042 saya?" | **Tool Call** (pencarian data mock tiket) |

**Objective:** Membuat satu backend API yang dapat menangani kedua jenis permintaan secara otomatis, dengan router yang menentukan intent dan mengarahkan ke komponen yang sesuai.

**Batasan / asumsi:**
- Knowledge base hanya mencakup 31 entri FAQ dari `data/it_helpdesk_knowledge_base.csv`.
- Data tiket hanya mencakup 15 tiket mock dari `data/mock_tickets.csv` (TICKET-0001 s.d. TICKET-0015).
- Intent detection menggunakan pendekatan keyword-based (baseline), bukan LLM.
- API key Gemini tidak boleh hardcode, wajib melalui environment variables.
- Aplikasi dijalankan secara lokal dalam container Docker (tidak wajib deploy ke cloud).

---

## 2. Desain Workflow

```
Query Masuk
    ↓
Intent Detection (Router)
    ├─→ intent = "ticket_status" → Tool Call (cari data mock tiket)
    │       ↓
    │   Response: status tiket (atau "tidak ditemukan")
    │
    └─→ intent = "faq" → RAG (FAISS semantic search + LLM)
            ↓
        Response: jawaban berdasarkan knowledge base
```

Kriteria intent:
- **ticket_status**: Query mengandung pola `TICKET-XXXX` atau kata kunci seperti "status tiket", "cek tiket", "lihat tiket", dll.
- **faq**: Pertanyaan yang mengandung topik dari knowledge base (cuti, password, perangkat, payroll, kebijakan kerja, dan lainnya).
- **unknown**: Query yang tidak dapat diklasifikasikan sebagai tiket atau topik FAQ (diberikan pesan maaf dan arahan).

---

## 3. Struktur Project

```
assignment-helpdesk-agent-AhnafRifqi/
├── app/
│   ├── main.py       # FastAPI backend + endpoint /ask
│   ├── router.py     # Intent detection + routing
│   ├── rag.py        # FAISS index, semantic search, LLM answer
│   └── tools.py      # Tool call: pencarian status tiket
├── tests/
│   └── test_router.py
├── data/
│   ├── it_helpdesk_knowledge_base.csv   # Knowledge base kebijakan IT
│   └── mock_tickets.csv                 # Data mock tiket
├── Dockerfile             # Konfigurasi container Docker
├── .dockerignore          # Mengecualikan .env dan file lokal dari build context
├── .env.example           # Template environment variables (API key)
├── .gitignore             # File yang diabaikan Git (termasuk .env)
├── requirements.txt       # Python dependencies
└── README.md              # Dokumentasi ini
```

---

## 4. Cara Menjalankan

### A. Secara Lokal (Tanpa Docker)

1. Masuk ke folder project:
   ```powershell
   cd assignment-helpdesk-agent-AhnafRifqi
   ```

2. Buat virtual environment dan aktifkan:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependency:
   ```powershell
   pip install -r requirements.txt
   ```

4. Salin `.env.example` menjadi `.env` dan isi `GEMINI_API_KEY`:
   ```powershell
   copy .env.example .env
   # Edit .env dan isi API key milik Anda
   ```

5. Jalankan aplikasi:
   ```powershell
   uvicorn app.main:app --reload
   ```

6. Akses API di: `http://localhost:8000/docs` atau `http://localhost:8000/ask`

Jalankan pengujian router dengan:
```powershell
python -m unittest discover -s tests -v
```

### B. Menggunakan Docker

1. Build image:
   ```powershell
   docker build -t helpdesk-agent .
   ```

2. Jalankan container (sertakan API key via environment variable):
   ```powershell
   docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key_here helpdesk-agent
   ```

3. Akses API dari luar container di: `http://localhost:8000/docs` atau `http://localhost:8000/ask`

File `.env` tidak disalin ke image Docker. Atur `GEMINI_API_KEY` pada environment container saat menjalankannya.

---

## 5. Endpoint API

### POST /ask

**Request body:**
```json
{
  "query": "Berapa jatah cuti tahunan karyawan tetap?"
}
```

**Response (faq):**
```json
{
  "status": "success",
  "intent": "faq",
  "data": {
    "answer": "Karyawan tetap mendapat jatah 12 hari cuti tahunan...",
    "sources": [
      {"faq_id": 1, "question": "Berapa jatah cuti tahunan karyawan tetap?"}
    ]
  }
}
```

**Response (ticket_status):**
```json
{
  "status": "success",
  "intent": "ticket_status",
  "data": {
    "ticket_id": "TICKET-0001",
    "employee_name": "Andi Pratama",
    "category": "Hardware",
    "subject": "Laptop tidak bisa menyala",
    "status": "Selesai",
    "last_update": "2026-08-20"
  }
}
```

**Response (ticket tidak ditemukan):**
```json
{
  "status": "not_found",
  "intent": "ticket_status",
  "data": "Tiket TICKET-9999 tidak ditemukan dalam database."
}
```

**Response (unknown):**
```json
{
  "status": "error",
  "intent": "unknown",
  "data": "Maaf, saya tidak dapat memahami pertanyaan Anda..."
}
```

### GET /health

Health check endpoint:
```json
{"status": "healthy", "service": "it-helpdesk-agent"}
```

---

## 6. Hasil Pengujian 5 Skenario

| # | Query | Intent yang Diperkirakan | Hasil Intent | Komponen | Observasi |
|---|-------|------------------------|--------------|----------|-----------|
| 1 | "Berapa jatah cuti tahunan karyawan tetap?" | faq | faq | RAG | ✅ Berdasarkan knowledge base |
| 2 | "Bagaimana cara reset password VPN perusahaan?" | faq | faq | RAG | ✅ Berdasarkan knowledge base |
| 3 | "Apa status tiket TICKET-0001 saya?" | ticket_status | ticket_status | Tool Call | ✅ Data tiket ditemukan |
| 4 | "Cek status tiket TICKET-9999" | ticket_status | ticket_status | Tool Call | ✅ Tidak ditemukan, graceful |
| 5 | "Halo, apa kabar?" | unknown | unknown | Tidak ada | ✅ Tidak menjalankan RAG untuk pesan di luar cakupan |

**Observasi:**
- Router mengarahkan pertanyaan tiket ke tool call, topik yang dikenal ke RAG, dan query di luar cakupan ke `unknown`.
- Tool call menangani `ticket_id` yang tidak ditemukan tanpa crash (mengembalikan status `not_found`).

---

## 7. Keterbatasan Sistem

1. **Intent detection berbasis keyword**: Tidak dapat menangani query yang sangat ambigu atau menggunakan kata-kata yang tidak ada dalam daftar keyword.
2. **Knowledge base terbatas**: Hanya 31 entri FAQ; pertanyaan di luar cakupan akan mendapatkan jawaban yang kurang relevan atau "tidak tersedia".
3. **Data tiket statis**: Hanya 15 tiket mock; tidak terhubung dengan sistem tiket nyata.
4. **Rate limit Gemini**: Free-tier memiliki batas 5 request/menit; retry otomatis telah ditambahkan tetapi masih terbatas.
5. **FAISS index dibangun saat startup**: Setiap kali aplikasi di-restart, index dibangun ulang dari CSV (belum disimpan ke file `.index`).

---

## 8. Catatan Penting

- File `.env` **jangan pernah di-commit** ke repository (sudah diatur di `.gitignore`).
- Gunakan `.env.example` sebagai template untuk menyisipkan API key Anda sendiri.
- Pastikan `GEMINI_API_KEY` diset sebelum menjalankan aplikasi (baik lokal maupun dalam Docker).