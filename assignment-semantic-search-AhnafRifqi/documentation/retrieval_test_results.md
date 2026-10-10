# Hasil Pengujian Relevansi Retrieval & Response AI

Notebook: `notebook/starter_notebook_semantic_search.ipynb` (Section 8)
Tanggal run: 10 Oktober 2026 — dijalankan end-to-end tanpa error.

## Konfigurasi uji

| Komponen | Nilai |
|---|---|
| Embedding model | `gemini-embedding-001` (dimensi 3072, vektor ternormalisasi L2) |
| Vector database | FAISS `IndexFlatL2` — 59 vektor = 59 entri FAQ |
| LLM | `gemini-flash-latest`, `temperature=0.3`, `thinking_budget=0` |
| `top_k` retrieval | 3 |
| Jumlah query uji | 6 (2 eksplisit + 3 parafrase + 1 di luar knowledge base) |

Skor: `distance` = squared L2 distance FAISS (makin kecil = makin mirip); `similarity` = cosine similarity hasil konversi `1 - distance/2` (makin besar = makin mirip).

## Ringkasan hasil

| # | Kategori | Query | Top-1 retrieval | Similarity | Jawaban LLM |
|---|---|---|---|---|---|
| 1 | Eksplisit | Bagaimana cara melacak paket yang sedang dikirim? | faq_id=10 ✔ | 0,8882 | ✅ Sesuai FAQ (nomor resi di menu 'Pesanan Saya' + website kurir) |
| 2 | Eksplisit | Berapa lama proses refund setelah pengembalian disetujui? | faq_id=25 ✔ | 0,9153 | ✅ Sesuai FAQ (3–7 hari kerja) |
| 3 | Parafrase | Uang saya sudah kepotong tapi kok status pesanan masih belum terbayar, kenapa ya? | faq_id=21 ✔ | 0,9114 | ✅ Sesuai FAQ (sinkronisasi 15–30 menit atau hubungi CS) |
| 4 | Parafrase | Barangku belum nyampe juga padahal udah lewat seminggu, harus saya lakukan apa? | faq_id=12 ✔ | 0,8494 | ✅ Sesuai FAQ (melebihi estimasi >3 hari → CS + sertakan no. resi) |
| 5 | Parafrase | Boleh nggak bayarnya dicicil per bulan? | faq_id=20 ✔ | 0,8545 | ✅ Sesuai FAQ (kartu kredit tertentu + nominal minimum) |
| 6 | Di luar KB | Apakah toko ini menerima pembayaran pakai mata uang kripto seperti Bitcoin? | faq_id=17 (konteks terdekat) | 0,7059 | ✅ Menolak dengan jujur + sarankan CS (tidak mengarang) |

**Top-1 accuracy pada query yang memiliki jawaban di KB: 5/5 (100%).** Query di luar KB mendapat skor top-1 terendah (0,71) — jarak ±0,14 dari query valid terlemah (0,85) — sehingga skor similarity menjadi sinyal kepercayaan yang berguna.

## Detail per query

### Query 1 — eksplisit ("Bagaimana cara melacak paket yang sedang dikirim?")
- Retrieval: **faq_id=10 (0,8882)** → faq_id=52 resi belum bisa dilacak (0,7901) → faq_id=12 paket melebihi estimasi (0,7751). Ketiga hasil satu kategori (Pengiriman) dan saling melengkapi.
- LLM: menjawab persis seperti FAQ 10 (cek nomor resi di menu 'Pesanan Saya', lacak di website kurir) dalam gaya chat.
- Analisis: retrieval **akurat**; kata "melacak" cocok langsung ke FAQ sumber.

### Query 2 — eksplisit ("Berapa lama proses refund setelah pengembalian disetujui?")
- Retrieval: **faq_id=25 (0,9153)** → faq_id=27 tujuan dana refund (0,7728) → faq_id=41 cashback promo (0,7345). Top-1 nyaris identik dengan FAQ; skornya lebih tinggi dari query 1 karena formulasi pertanyaan hampir persis.
- LLM: "3–7 hari kerja setelah barang diterima dan diverifikasi" — akurat.
- Analisis: retrieval **akurat**; peringkat 3 mulai keluar dari topik (cashback ≠ refund) tetapi tidak memengaruhi jawaban karena top-1 sudah tepat.

### Query 3 — parafrase ("Uang saya sudah kepotong tapi kok status pesanan masih belum terbayar, kenapa ya?")
- Retrieval: **faq_id=21 (0,9114)** → faq_id=8 pesanan otomatis dibatalkan (0,8034) → faq_id=19 batas waktu pembayaran (0,7798).
- LLM: menjelaskan keterlambatan sinkronisasi, menunggu 15–30 menit atau hubungi CS — sesuai FAQ 21.
- Analisis: **semantic search menangkap makna, bukan kata kunci**: "uang sudah kepotong" (sinonim "pembayaran berhasil dipotong") dan akhiran kasual "kenapa ya?" tidak mengganggu pencocokan. Retrieval **akurat**.

### Query 4 — parafrase ("Barangku belum nyampe juga padahal udah lewat seminggu…")
- Retrieval: **faq_id=12 (0,8494)** → faq_id=14 status pengiriman tidak berubah (0,7943) → faq_id=9 estimasi pengiriman (0,7703). Semua kategori Pengiriman.
- LLM: merekomendasikan hubungi CS dengan menyertakan nomor resi karena melebihi estimasi >3 hari — sesuai FAQ 12.
- Analisis: bahasa gaul "belum nyampe", "udah lewat seminggu" tidak ada dalam KB, tetapi retrieval tetap ke FAQ yang benar. **Akurat**; peringkat 2–3 juga relevan sebagai pendukung.

### Query 5 — parafrase ("Boleh nggak bayarnya dicicil per bulan?")
- Retrieval: **faq_id=20 (0,8545)** → faq_id=22 split payment (0,7135) → faq_id=17 metode pembayaran (0,7020).
- LLM: cicilan untuk kartu kredit tertentu dengan nominal minimal dari bank — sesuai FAQ 20.
- Analisis: **akurat di top-1**; peringkat 2–3 agak generik (topik pembayaran secara luas) — kualitas menurun tajam setelah peringkat 1, tetapi tidak merugikan karena prompt hanya butuh satu FAQ yang tepat.

### Query 6 — di luar knowledge base (mata uang kripto/Bitcoin)
- Retrieval: **faq_id=17 metode pembayaran (0,7059)** → faq_id=22 (0,6743) → faq_id=19 (0,6590). Tidak ada FAQ yang benar-benar menjawab.
- LLM: menyebutkan metode yang didukung (dari context), lalu dengan jujur menyatakan informasi pembayaran kripto **belum tersedia** dan menyarankan menghubungi customer service resmi — **tidak mengarang jawaban dari pengetahuan umum**.
- Analisis: perilaku yang diharapkan dari prompt Persona–Task–Context–Format terpenuhi. Skor top-1 terendah di seluruh uji (0,71) menunjukkan sistem "tahu" bahwa tidak ada konteks yang benar-benar cocok — potensi dasar untuk menambahkan cutoff similarity di pengembangan selanjutnya.

## Analisis kritis

1. **Retrieval konsisten pada makna, bukan kata kunci.** Ketiga query parafrase ("uang kepotong", "belum nyampe", "dicicil per bulan") tetap menemukan FAQ yang benar di peringkat-1 dengan similarity 0,85–0,91 — embedding semantic bekerja, bukan pencocokan string.
2. **Pola skor dapat dipercaya sebagai sinyal relevansi.** Query valid: 0,85–0,92; query tanpa jawaban: 0,71. Selisih ini konsisten dengan ekspektasi cosine similarity pada vektor ternormalisasi.
3. **Kualitas jawaban LLM tinggi pada semua kasus.** 6/6 jawaban sesuai FAQ atau (untuk query di luar KB) sesuai instruksi penolakan; tidak ditemukan halusinasi. Gaya bahasa natural dan tidak menyebut istilah teknis.
4. **Peringkat 2–3 kadang kurang relevan** (mis. faq 41 cashback untuk query refund, faq 22 split payment untuk query cicilan) — cukup sebagai konteks tambahan, tetapi menunjukkan batas top_k=3 pada knowledge base kecil; menaikkan top_k memperkaya context sekaligus menambah noise.
5. **Tidak ada mekanisme cutoff otomatis.** Sistem selalu mengirim top-k ke LLM berapa pun skornya; kejujuran jawaban pada query di luar KB bergantung pada kepatuhan LLM pada instruksi prompt. Menambahkan ambang similarity (mis. < 0,75 → langsung tolak) adalah peningkatan yang jelas.