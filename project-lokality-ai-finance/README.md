# Lokality AI Financial Recap & PnL Copilot (`v1.1.0`)

Aplikasi otomasi rekapitulasi keuangan dan penyusunan draf Laporan Laba Rugi (*Profit & Loss* / PnL) untuk **PT Lokal Komoditi Indonesia (Lokality)** — produsen manufaktur mi *gluten-free* berbasis tepung mocaf, tepung beras, dan tepung jagung dengan fortifikasi tempe (Studi Kasus ID: `LKI-01`). Sistem ini memadukan **mesin akuntansi deterministik Python** (akurasi perhitungan 100%, bebas halusinasi angka, dengan *drill-down* keterlacakan per transaksi) dan **AI Financial Copilot berbasis Google Gemini** yang dilengkapi *Human-in-the-Loop* editor, *Safety Guardrails*, serta pembatas kuota sesi.

## Fitur Utama (`v1.1.0`)

1. **Ingestion Fleksibel & Filter Periode:** Mendukung data sampel bawaan maupun unggah berkas `.csv` / `.xlsx`, dilengkapi filter **Semua Periode**, **Per Bulan**, atau **Rentang Tanggal Kustom** di sidebar.
2. **Auto-Kategorisasi + *Human-in-the-Loop* Override:** Mengelompokkan belanja ke pos HPP (`HPP_Bahan_Baku`, `HPP_Kemasan`, `HPP_Tenaga_Kerja`) dan OPEX (`OPEX_Utilitas`, `OPEX_Pemasaran`, `OPEX_Logistik`, `OPEX_Admin`) secara otomatis, disertai tabel editor interaktif agar pengguna dapat meninjau/mengoreksi kategori akun sebelum draf PnL dipakai.
3. **Laporan PnL Deterministik & *Drill-Down Audit Trail*:** Menampilkan banner kelengkapan data, kartu KPI, rumus eksplisit, ekspor `.csv`, serta panel *drill-down* untuk menelusuri setiap nominal akun PnL kembali ke baris transaksi aslinya (`[EXP-001]` s/d `[EXP-014]`).
4. **AI Financial Copilot Rincian Item:** Menyajikan ringkasan eksekutif bulanan dan chatbot tanya-jawab terikat data hingga level item spesifik (mis. rincian belanja mocaf `Rp 7.000.000` + tempe `Rp 2.400.000` = `Rp 9.400.000`).
5. **Safety Guardrails & Pengendali Kuota AI (`AIQuotaManager`):** Memblokir *prompt injection* (ID/EN) dan kueri luar domain, membatasi panjang input (500 karakter), menerapkan cache `SHA-256`, batas kuota per sesi (15 panggilan), *cooldown* (2 detik), saklar on/off AI, serta *fallback* deterministik lokal otomatis.

## Mengatur Lingkungan & API Key

1. Salin `.env.example` menjadi `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Sesuaikan konfigurasi pada `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   APP_PORT=8501
   MAX_AI_CALLS_PER_SESSION=15
   MIN_AI_COOLDOWN_SECONDS=2.0
   MAX_QUERY_CHARS=500
   ```
> **Catatan:** Apabila `GEMINI_API_KEY` dikosongkan atau saklar AI dimatikan di sidebar, seluruh fitur dashboard, PnL, dan tanya-jawab rincian item tetap berjalan normal menggunakan mesin deterministik lokal. Jangan pernah meng-commit berkas `.env` ke repository.

## Cara Menjalankan secara Lokal

```powershell
# 1. Masuk ke folder proyek
cd "d:\Rework Academy\Praktek\AI-Bootcamp\project-lokality-ai-finance"

# 2. Aktifkan virtual environment workspace
& "d:\Rework Academy\Praktek\AI-Bootcamp\.venv\Scripts\Activate.ps1"

# 3. Pasang pustaka dependensi
pip install -r requirements.txt

# 4. Jalankan seluruh unit test otomatis (18 skenario)
pytest tests/ -v

# 5. Jalankan aplikasi web Streamlit
streamlit run src/ui/app.py
```
Buka peramban di `http://localhost:8501`.

## Struktur Repository

```text
project-lokality-ai-finance/
├── .env.example                     # Template konfigurasi environment & kuota AI
├── .gitignore                       # Proteksi file sensitif (.env) dan cache
├── README.md                        # Panduan utama proyek
├── requirements.txt                 # Daftar dependensi Python
├── data/
│   ├── raw/                         # Folder data mentah lokal
│   ├── processed/                   # Folder hasil olahan
│   └── mock/                        # Dataset simulasi Lokality (sample_sales.csv, sample_expenses.csv)
├── docs/                            # Paket dokumen resmi Capstone & diagram arsitektur
│   ├── 1_Business_Requirement_Document_BRD.md
│   ├── 2_AI_Solution_Blueprint_Architecture.md
│   ├── 3_Testing_Evaluation_Report.md
│   ├── 4_Technical_Documentation.md
│   ├── 5_User_Guide.md
│   ├── 6_Final_Presentation_Deck_Outline.md
│   ├── Dokumen_Resmi_Lokality_dan_AI_Bootcamp.pdf
│   ├── diagrams/                    # Diagram User Flow, Arsitektur & Visual PnL (.png & .mmd)
│   └── official_docx/               # Dokumen resmi terisi format Word (.docx) Deliverable 1-5
├── src/
│   ├── config.py                    # Konfigurasi path, model, dan batas kuota AI
│   ├── ingestion/
│   │   ├── loader.py                # Pembaca CSV/Excel & pembersih format Rupiah
│   │   └── validator.py             # Validasi kolom wajib & anomali transaksi
│   ├── core/
│   │   ├── categorizer.py           # Auto-kategorisasi HPP/OPEX & pelacak koreksi manual
│   │   └── pnl_engine.py            # Kalkulasi PnL, filter periode, kelengkapan & traceability_map
│   ├── ai/
│   │   ├── client.py                # Klien Google GenAI SDK dengan deteksi fallback
│   │   ├── guardrails.py            # Sanitasi panjang kueri & proteksi prompt injection
│   │   ├── quota_manager.py         # Pembatas kuota sesi, cooldown, saklar AI & SHA-256 cache
│   │   ├── narrative_generator.py   # Generator ringkasan eksekutif bulanan
│   │   └── chatbot.py               # Chatbot keuangan rincian item multi-turn
│   └── ui/
│       └── app.py                   # Aplikasi web Streamlit 3-Tab + Sidebar Kontrol
└── tests/                           # 18 Unit & Integration Tests (Pytest)
    ├── test_pnl_engine.py
    ├── test_categorizer.py
    └── test_ai_guardrails.py
```

## Catatan Data & Keterbatasan
- Dataset di `data/mock/` merupakan data simulasi representatif operasional manufaktur mi *gluten-free* Lokality (Pendapatan `Rp 46.875.000`, HPP `Rp 29.800.000`, OPEX `Rp 8.500.000`, Laba Bersih `Rp 8.575.000`).
- Masukan saat ini berfokus pada berkas tabel terstruktur (`.csv` dan `.xlsx`); pencatatan struk kertas fisik direkap terlebih dahulu ke tabel sebelum diunggah.
