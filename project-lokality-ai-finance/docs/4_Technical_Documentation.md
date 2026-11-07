# Technical Documentation
## AI Solution for Enterprise — Capstone Business Project

---

### 1. Project Information

| Informasi | Isian Kelompok |
| :--- | :--- |
| **Nama Project** | Lokality AI Financial Recap & PnL Copilot |
| **Studi Kasus Mitra** | PT Lokal Komoditi Indonesia (Lokality) — Kasus ID: `LKI-01` |
| **Nama Kelompok** | Tim AI Engineering Batch 1 (Ahnaf Rifqi) |
| **Versi Aplikasi** | `v1.1.0` |
| **Lokasi Repository** | `d:\Rework Academy\Praktek\AI-Bootcamp\project-lokality-ai-finance` |
| **Tanggal Pembaruan** | 08 November 2026 |

---

### 2. Technology Stack

| Teknologi / Pustaka | Versi Teruji | Peran dalam Sistem |
| :--- | :--- | :--- |
| **Python** | `3.14.3` | Bahasa pemrograman utama untuk pemrosesan data, mesin akuntansi deterministik, dan layanan AI. |
| **Streamlit** | `1.67.0` | Kerangka antarmuka web interaktif (3 tab utama, `st.data_editor`, kontrol filter & kuota). |
| **Pandas** | `3.1.1` | Manipulasi tabel transaksi, pembersihan mata uang, pemfilteran tanggal, dan agregasi PnL. |
| **OpenPyXL** | `3.1.5` | Mesin pembacaan berkas spreadsheet Microsoft Excel (`.xlsx` / `.xls`). |
| **Google GenAI SDK (`google-genai`)** | `3.0.0` | Klien resmi untuk pemanggilan model generatif `gemini-2.5-flash`. |
| **Pydantic** | `2.14.3` | Validasi tipe data dan struktur konfigurasi. |
| **Pytest** | `9.2.0` | Kerangka pengujian otomatis (18 unit test logika akuntansi, keterlacakan, guardrails, dan kuota). |

---

### 3. System Components & Implementation

| Komponen | Tanggung Jawab Teknis | Lokasi Kode Aktual |
| :--- | :--- | :--- |
| **Configuration Manager** | Memuat variabel `.env`, path direktori data, parameter model, serta konstanta batas kuota & sanitasi input. | `src/config.py` |
| **Data Loader & Normalizer** | Membaca CSV/Excel, menormalisasi nama kolom (`snake_case`), dan mengonversi format Rupiah (`"Rp 14.000"`) menjadi `float`. | `src/ingestion/loader.py` |
| **Schema & Anomaly Validator** | Memeriksa ketersediaan kolom wajib (`tanggal`, nominal pendapatan/pengeluaran) dan mendeteksi nilai negatif atau tanggal rusak. | `src/ingestion/validator.py` |
| **Rule-Based Expense Categorizer** | Memetakan item belanja ke 7 sub-akun HPP/OPEX berbasis kata kunci serta melacak `sumber_kategori` (`Bawaan Data`, `Otomatis (Rule)`, `Koreksi Manual`). | `src/core/categorizer.py` |
| **Deterministic PnL & Audit Engine** | Memfilter rentang tanggal (`start_date`, `end_date`), menghitung metrik PnL, memvalidasi kelengkapan data (`completeness_warnings`), dan menyusun `traceability_map` per baris transaksi. | `src/core/pnl_engine.py` |
| **Gemini Client Wrapper** | Menginisialisasi klien `genai.Client` secara aman dan menyediakan deteksi status kesiapan API key. | `src/ai/client.py` |
| **Safety & Domain Guardrails** | Memotong input > 500 karakter (`sanitize_query_length`), memblokir *prompt injection* Bahasa Indonesia & Inggris, dan menyaring topik luar domain. | `src/ai/guardrails.py` |
| **AI Quota & Cache Manager** | Mengelola saklar on/off AI (`ai_enabled`), batas panggilan per sesi (`15`), jeda *cooldown* (`2.0s`), dan cache respons berbasis hash `SHA-256`. | `src/ai/quota_manager.py` |
| **Executive Narrative Generator** | Menghasilkan ringkasan eksekutif bulanan berbasis fakta PnL dengan fallback deterministik lokal. | `src/ai/narrative_generator.py` |
| **Item-Level Financial Chatbot** | Menjawab kueri keuangan multi-giliran (termasuk rincian per item `[EXP-xxx]`) menggunakan konteks terverifikasi atau mesin kalkulasi lokal. | `src/ai/chatbot.py` |
| **Streamlit Web Application** | Menyajikan Sidebar kontrol, Tab 1 Rekap & Editor *Human-in-the-Loop*, Tab 2 Laporan PnL & *Drill-Down*, serta Tab 3 AI Copilot. | `src/ui/app.py` |

---

### 4. Data Processing & AI Workflow

#### 4.1 Sumber Data, Normalisasi, dan Filter Periode
- **Format Masukan:** Berkas `.csv` atau `.xlsx` untuk transaksi penjualan (`tanggal`, `produk`, `channel`, `qty_pack`, `harga_satuan`, `total_pendapatan`) dan pengeluaran (`tanggal`, `kategori_biaya`, `deskripsi_item`, `total_pengeluaran`, opsional `tipe_akun`).
- **Normalisasi:** Fungsi `clean_currency_series` menghapus simbol `Rp`, pemisah ribuan titik/koma, dan spasi sehingga siap dijumlahkan tanpa galat tipe data.
- **Filter Periode:** Parameter `start_date` dan `end_date` dinormalisasi ke batas hari (`00:00:00` hingga `23:59:59`) pada kolom `_parsed_date` sebelum seluruh agregasi dieksekusi.

#### 4.2 Rumus Akuntansi Deterministik & Keterlacakan (*Traceability*)
Seluruh perhitungan PnL dieksekusi murni di Python (`calculate_pnl_metrics`):
$$\text{Total HPP} = \text{HPP Bahan Baku} + \text{HPP Kemasan} + \text{HPP Tenaga Kerja}$$
$$\text{Gross Profit (Laba Kotor)} = \text{Total Revenue} - \text{Total HPP}$$
$$\text{Net Operating Profit (Laba Bersih)} = \text{Gross Profit} - \text{Total OPEX}$$
Setiap kode akun pada tabel PnL (`REV_TOTAL`, `HPP_Bahan_Baku`, `HPP_Kemasan`, `HPP_Tenaga_Kerja`, `OPEX_Utilitas`, `OPEX_Pemasaran`, `OPEX_Logistik`, `OPEX_Admin`) dipetakan di dalam `traceability_map` langsung ke daftar baris sumber beserta kolom `sumber_kategori`-nya. Selain itu, fungsi memeriksa `completeness_warnings` apabila pendapatan, HPP bahan baku, atau OPEX bernilai `Rp 0` sehingga pengguna mendapat peringatan bahwa draf PnL belum lengkap.

#### 4.3 Strategi Grounded Prompting & Konteks Rincian Item
Modul `narrative_generator.py` dan `chatbot.py` menyuntikkan:
1. Ringkasan metrik PnL terverifikasi pada periode aktif.
2. Daftar rincian seluruh baris pengeluaran (`[EXP-001]` s/d `[EXP-014]`) dan agregasi produk/saluran penjualan.
3. Riwayat percakapan terakhir (maksimal 6 pesan) untuk menjaga koherensi tanya-jawab lanjutan.
4. Instruksi sistem ketat yang melarang model mengarang angka di luar konteks yang disuntikkan.

#### 4.4 Safety Guardrails & Pembatas Pemakaian (`AIQuotaManager`)
1. **Sanitasi Panjang Input:** `sanitize_query_length` memotong input pengguna maksimal `MAX_QUERY_CHARS = 500` karakter.
2. **Anti-Prompt Injection & Domain Filter:** Regex berlapis memblokir pola manipulasi instruksi (*"ignore previous instructions"*, *"abaikan semua instruksi"*, *"tampilkan prompt sistem"*, eksfiltrasi `api_key`) serta menolak pertanyaan non-keuangan sebelum menyentuh kuota API.
3. **Manajemen Kuota & Cache Sesi:**
   - Kueri identik pada konteks data yang sama dilayani langsung dari cache `SHA-256` (0 token API).
   - Batas default `MAX_AI_CALLS_PER_SESSION = 15` panggilan dan jeda `MIN_AI_COOLDOWN_SECONDS = 2.0` detik mencegah lonjakan biaya atau *rate-limit* `429`.
   - Saklar *Kill-Switch* di sidebar memungkinkan admin mematikan pemanggilan LLM kapan saja dan beralih ke penjawab deterministik lokal.

---

### 5. Configuration & Environment Variables

Salin berkas `.env.example` menjadi `.env` di root proyek (`project-lokality-ai-finance/.env`):

| Variabel Lingkungan | Nilai Default | Keterangan |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | *(kosong)* | Kunci API dari Google AI Studio. Jika dikosongkan, aplikasi otomatis berjalan pada mode deterministik lokal. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Nama model Gemini untuk narasi eksekutif dan chatbot keuangan. |
| `APP_ENV` | `development` | Penanda mode lingkungan aplikasi. |
| `APP_PORT` | `8501` | Port HTTP lokal untuk server Streamlit. |
| `MAX_AI_CALLS_PER_SESSION` | `15` | Batas maksimum pemanggilan API Gemini per sesi pengguna. |
| `MIN_AI_COOLDOWN_SECONDS` | `2.0` | Jeda minimum antar-pemanggilan API Gemini (detik). |
| `MAX_QUERY_CHARS` | `500` | Batas maksimum panjang karakter pertanyaan di chatbot. |

> **Keamanan Kredensial:** Berkas `.env` telah didaftarkan di `.gitignore` dan dilarang keras di-commit ke dalam repository Git.

---

### 6. Deployment & Execution Guide

#### 6.1 Menjalankan Aplikasi Secara Lokal
```powershell
# 1. Masuk ke direktori proyek
cd "d:\Rework Academy\Praktek\AI-Bootcamp\project-lokality-ai-finance"

# 2. Aktifkan virtual environment workspace
& "d:\Rework Academy\Praktek\AI-Bootcamp\.venv\Scripts\Activate.ps1"

# 3. Pasang pustaka dependensi (bila diperlukan)
pip install -r requirements.txt

# 4. Jalankan server aplikasi Streamlit
streamlit run src/ui/app.py
```
Aplikasi dapat diakses melalui peramban di `http://localhost:8501`.

#### 6.2 Menjalankan Pengujian Otomatis (`pytest`)
```powershell
& "d:\Rework Academy\Praktek\AI-Bootcamp\.venv\Scripts\python.exe" -m pytest tests/ -v
```
Seluruh **18 pengujian unit & integrasi** memverifikasi perhitungan PnL, filter tanggal, *Human-in-the-Loop override*, rekonsiliasi `traceability_map`, *guardrails*, rincian item chatbot, dan manajer kuota AI.

---

### 7. Technical Limitations & Notes
1. **Fokus Masukan Terstruktur:** Versi `v1.1.0` mengolah berkas tabel `.csv` dan `.xlsx`. Pencatatan nota fisik kertas perlu direkap ke spreadsheet terlebih dahulu (modul ekstraksi OCR disiapkan sebagai kandidat pengembangan fase berikutnya setelah konfirmasi bentuk nota dari PIC Lokality).
2. **Penyimpanan Berbasis Sesi:** Koreksi manual kategori pada `st.data_editor` berlaku selama sesi aktif dan langsung tercermin pada berkas `.csv` PnL yang diunduh; penyimpanan permanen lintas-sesi ke basis data relasional (PostgreSQL/SQLite) dapat ditambahkan saat deployment multi-user produksi.
