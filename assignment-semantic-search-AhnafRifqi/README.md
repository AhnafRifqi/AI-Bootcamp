# Assignment Semantic Search & LLM Application

Prototype aplikasi **semantic search terintegrasi LLM** untuk customer service e-commerce: knowledge base FAQ diubah menjadi embedding, disimpan di vector database FAISS, di-retrieve berdasarkan semantic similarity, lalu hasilnya disisipkan sebagai context ke prompt sehingga LLM menghasilkan jawaban yang relevan. Ini adalah persiapan langsung menuju sistem RAG penuh pada sesi berikutnya.

## 1. Problem Statement

**Studi kasus:** tim customer service e-commerce menerima ratusan pertanyaan repetitif setiap hari seputar pemesanan, pengiriman, pembayaran, hingga pengembalian barang. Perlu prototype asisten AI yang menjawab otomatis berdasarkan knowledge base FAQ yang sudah ada — bahkan ketika pelanggan tidak menggunakan kata-kata persis seperti FAQ.

- **Objective:** membangun pipeline end-to-end **query → retrieval (semantic search) → prompt → jawaban LLM**, di mana pencarian berbasis makna (bukan keyword) menemukan entri FAQ paling relevan, dan LLM menyusun jawaban natural **hanya** dari entri tersebut.
- **Sumber knowledge base:** `data/ecommerce_faq_knowledge_base.csv` (dibagikan pada brief assignment; **tidak diubah sama sekali**).
- **Struktur knowledge base:** 59 entri FAQ, kolom `faq_id`, `category`, `question`, `answer`; 8 kategori — Pemesanan (9), Pengiriman (9), Pembayaran (8), Pengembalian (8), Akun (7), Produk (7), Promo (6), Customer Service (5); tanpa missing value dan tanpa duplikat pertanyaan.
- **Batasan / asumsi:**
  - Sistem **hanya menjawab berdasarkan FAQ yang tersedia**; jika tidak ada di knowledge base, LLM wajib menyatakan informasi tidak tersedia dan mengarahkan ke customer service.
  - Unit retrievable = 1 entri FAQ (question + answer digabung) — **tanpa chunking**, sesuai lingkup sesi ini.
  - Evaluasi menggunakan 6 query uji subjektif, bukan benchmark kuantitatif.
  - Berjalan di atas API free-tier Gemini (ada rate limit; ditangani dengan retry otomatis).

## 2. Struktur Project

```
assignment-semantic-search-AhnafRifqi/
├── data/
│   ├── ecommerce_faq_knowledge_base.csv   # knowledge base asli (read-only, tidak diubah)
│   ├── faiss_index.index                  # vector database FAISS (59 vektor x 3072 dim)
│   └── faq_metadata.json                  # metadata FAQ sebaris dengan urutan vektor
├── notebook/
│   └── starter_notebook_semantic_search.ipynb   # notebook lengkap 8 section + output run
├── documentation/
│   ├── retrieval_test_results.md          # hasil uji 6 query + analisis relevansi
│   └── _analysis_cell.md                  # sumber teks cell analisis di notebook
├── src/
│   └── build_index.py                     # script pembuat FAISS index (ingest→embed→store)
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## 3. Alur Sistem

| Tahap | Proses | Implementasi |
|---|---|---|
| **Ingest** | Muat knowledge base & siapkan unit retrievable | Pandas membaca CSV (read-only); `content = 'Q: ' + question + '\nA: ' + answer` per entri → 59 dokumen |
| **Embed** | Ubah tiap unit menjadi vektor | Gemini Embeddings API `gemini-embedding-001`, 1 request batch untuk 59 teks → shape `(59, 3072)`, `float32`, dinormalisasi L2 |
| **Store** | Simpan ke vector database | FAISS `IndexFlatL2(3072)` → `index.add()` → verifikasi `ntotal == 59` → disimpan ke `data/faiss_index.index` + `data/faq_metadata.json` |
| **Retrieve** | Semantic search untuk query pengguna | `semantic_search(query, top_k=3)`: embed query → `index.search()` → tampilkan distance (squared L2) & similarity (cosine = `1 - distance/2`) |
| **Generate** | Sisipkan hasil retrieval sebagai context → jawaban LLM | Prompt terstruktur **Persona–Task–Context–Format** → Gemini AI API (`gemini-flash-latest`, `temperature=0.3`) → jawaban natural |

Model yang dipakai (disesuaikan dengan ketersediaan API saat pengerjaan):

| Komponen | Model | Catatan |
|---|---|---|
| Embeddings | `gemini-embedding-001` | `text-embedding-004` sudah 404; dimensi default 3072 |
| LLM generation | `gemini-flash-latest` | `gemini-2.0-flash` & `gemini-2.5-flash` mengembalikan 404 "no longer available to new users" |
| Vector DB | FAISS `IndexFlatL2` | vektor dinormalisasi agar L2 setara cosine similarity |

## 4. Prompt Design

Prompt disusun dari 4 blok (lihat section 6 notebook):

- **[PERSONA]** — asisten customer service e-commerce yang ramah, menjawab dalam bahasa Indonesia.
- **[TASK]** — jawab **HANYA** dari `[CONTEXT]`; dilarang memakai pengetahuan umum; jika informasi tidak ada, katakan jujur dan sarankan menghubungi customer service.
- **[CONTEXT]** — hasil semantic search disisipkan sebagai daftar FAQ (`[FAQ n] Pertanyaan/Jawaban`) beserta kategorinya.
- **[FORMAT]** — maksimal 3 kalimat, gaya chat natural, tanpa istilah teknis ("FAQ", "context", "knowledge base").

## 5. Hasil Pengujian & Analisis Relevansi

Uji lengkap 6 query (memenuhi syarat minimal 5) — detail per query ada di `documentation/retrieval_test_results.md`:

| # | Kategori | Query | Top-1 | Similarity | Hasil |
|---|---|---|---|---|---|
| 1 | Eksplisit | cara melacak paket yang sedang dikirim | faq 10 ✔ | 0,89 | Jawaban sesuai FAQ |
| 2 | Eksplisit | berapa lama proses refund disetujui | faq 25 ✔ | 0,92 | Jawaban sesuai FAQ |
| 3 | Parafrase | "uang sudah kepotong tapi status belum terbayar" | faq 21 ✔ | 0,91 | Jawaban sesuai FAQ |
| 4 | Parafrase | "barangku belum nyampe, udah lewat seminggu" | faq 12 ✔ | 0,85 | Jawaban sesuai FAQ |
| 5 | Parafrase | "boleh nggak dicicil per bulan?" | faq 20 ✔ | 0,85 | Jawaban sesuai FAQ |
| 6 | Di luar KB | pembayaran mata uang kripto/Bitcoin | faq 17 (0,71) | 0,71 | LLM menolak dengan jujur + sarankan CS |

**Analisis singkat:**

- **Top-1 accuracy 5/5 (100%)** pada query yang punya jawaban di KB — termasuk ketiga parafrase dengan sinonim/bahasa gaul yang kata-katanya tidak ada di FAQ ("uang kepotong", "belum nyampe", "dicicil per bulan"). Semantic search menangkap **makna, bukan kata kunci**.
- **Skor menjadi sinyal kepercayaan:** query valid 0,85–0,92 vs query di luar KB 0,71 (selisih ±0,14). Peringkat 2–3 kadang kurang relevan (mis. faq cashback untuk query refund) tetapi tidak merugikan karena top-1 sudah tepat.
- **LLM tidak mengarang:** pada query kripto (di luar KB), jawaban menyebut metode yang didukung lalu menyatakan informasi tidak tersedia dan mengarahkan ke customer service — sesuai instruksi `[TASK]`. 6/6 jawaban relevan tanpa halusinasi.

## 6. Keterbatasan Sistem

- **Belum ada cutoff similarity otomatis** — top-k selalu dikirim ke LLM berapa pun skornya; penolakan pada query di luar KB bergantung pada kepatuhan LLM pada prompt. Ambang similarity (mis. < 0,75 → tolak) adalah peningkatan jelas menuju RAG.
- **Knowledge base kecil & pendek** (59 entri, rata-rata 190 karakter) tanpa chunking — hasil belum mewakili dokumen panjang nyata.
- **Evaluasi 6 query subjektif**, belum ada metrik kuantitatif (precision@k, dst.) pada kumpulan query yang lebih besar.
- **Tergantung API online & kuota free-tier** (rate limit ±5 request/menit per model; ditangani retry otomatis dengan backoff pada notebook dan script).
- **Peringkat 2–3 bisa menambah noise** jika `top_k` dinaikkan pada knowledge base sekecil ini.

## 7. Cara Menjalankan

### Prasyarat

- Python 3.10+ (dikembangkan & diuji pada Python 3.14.3, Windows)
- API key Gemini dari [Google AI Studio](https://aistudio.google.com/apikey)

### Langkah

```bash
# 1. Masuk ke folder project & buat virtual environment
cd assignment-semantic-search-AhnafRifqi
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Install dependency
pip install -r requirements.txt

# 3. Salin .env.example menjadi .env lalu isi GEMINI_API_KEY
copy .env.example .env          # Windows (edit isinya)

# 4a. Jalankan notebook (dari root project) — Run All dari awal sampai akhir
python -m jupyter notebook notebook/starter_notebook_semantic_search.ipynb

# 4b. ATAU bangun ulang FAISS index tanpa notebook
python src/build_index.py
```

Catatan:

- Notebook **dapat dijalankan dari root project maupun dari folder `notebook/`** (path `.env` & CSV menyesuaikan otomatis).
- Notebook memuat **output run asli** (shape embedding, jumlah vektor, skor retrieval, jawaban LLM) sehingga hasil dapat diperiksa tanpa menjalankan ulang.
- Proses embed knowledge base hanya **1 request batch**; seluruh alur uji (6 query + demo) membutuhkan ±17 request API — muat dalam kuota free-tier dengan retry otomatis bila kena rate limit.
- Membangun ulang index via `src/build_index.py` akan menimpa `data/faiss_index.index` dengan embedding baru (isinya setara, karena dihitung dari CSV yang sama).

### catatan Cline
Assignment selesai dan tervalidasi penuh. Ringkasan akhir:

## ✅ Yang dikerjakan

**Lokasi:** `d:\Rework Academy\Praktek\AI-Bootcamp\assignment-semantic-search-AhnafRifqi\` (subfolder, belum di-commit/push sesuai permintaan)

| Komponen | Status |
|---|---|
| `data/ecommerce_faq_knowledge_base.csv` | ✅ Diunduh dari link Drive di brief (59 entri, 8 kategori), **tidak diubah** (sha256 diverifikasi) |
| `data/faiss_index.index` + `faq_metadata.json` | ✅ 59 vektor × 3072 dimensi (`IndexFlatL2`, ternormalisasi L2), `ntotal == 59` |
| `notebook/starter_notebook_semantic_search.ipynb` | ✅ Struktur 8 section starter dipertahankan; **di-run end-to-end, 0 error, semua output tersimpan** |
| `src/build_index.py` | ✅ Script pembuat index (ingest→embed→store) — diuji jalan, EXIT=0 |
| `documentation/retrieval_test_results.md` | ✅ 6 query + detail skor + analisis kritis |
| `README.md` | ✅ Problem statement, alur sistem, hasil uji, keterbatasan, cara menjalankan |
| `requirements.txt`, `.env.example`, `.gitignore` | ✅ `.env` terverifikasi ter-ignore Git |

## ⚠️ Temuan penting soal model (sesuai permintaan Anda)

- **`gemini-2.5-flash` mengembalikan 404** "no longer available to new users" untuk API key ini → sesuai pilihan Anda, dipakai **`gemini-flash-latest`** (juga `gemini-2.0-flash` dan `gemini-2.5-flash-lite` 404).
- Embedding `text-embedding-004` juga sudah 404 → dipakai **`gemini-embedding-001`** (3072 dimensi).
- Free-tier hanya **5 request/menit/model** → ditambahkan helper `with_quota_retry` (retry 429/timeout/5xx dengan backoff) di notebook & script.

## 📊 Hasil uji (6 query)

- **Top-1 accuracy 5/5 (100%)** pada query yang ada jawabannya di FAQ — termasuk 3 parafrase: *"uang sudah kepotong"* → faq 21 (sim 0,91), *"belum nyampe lewat seminggu"* → faq 12 (0,85), *"dicicil per bulan"* → faq 20 (0,85).
- **Query di luar KB** (kripto): skor top-1 terendah (0,71) dan LLM **menolak dengan jujur** + sarankan CS — tidak mengarang.
- 6/6 jawaban LLM sesuai konteks, tanpa halusinasi.

**Validasi akhir:** 0 error output · semua code cell ter-eksekusi · `nbformat` valid · `.env` di-ignore · folder hanya `??` untracked di Git (belum di-commit sesuai instruksi). Kalau nanti mau submit, tinggal bilang — saya bisa bantu commit & push dengan nama repo `assignment-semantic-search-AhnafRifqi`.