### Catatan Analisis Relevansi

Diuji **6 query** (2 eksplisit, 3 parafrase, 1 di luar knowledge base). Detail lengkap: `documentation/retrieval_test_results.md`.

**Temuan utama:**

1. **Retrieval akurat pada semua query yang punya jawaban di KB (5/5 top-1 benar).** Query eksplisit mendapat similarity 0,89–0,92 (faq 10 & 25); ketiga query parafrase juga menemukan FAQ yang tepat di peringkat-1 (0,85–0,91): "uang sudah kepotong" → faq 21, "belum nyampe lewat seminggu" → faq 12, "dicicil per bulan" → faq 20. Ini membuktikan semantic search menangkap **makna, bukan kata kunci** — kata gaul/sinonim yang tidak ada di KB tidak menggagalkan pencocokan.
2. **Query di luar KB menghasilkan skor terendah (0,71 vs 0,85–0,92)** — faq 17 (metode pembayaran) tetap terambil sebagai konteks terdekat, dan LLM **menolak dengan jujur**: menyebut metode yang didukung, menyatakan informasi kripto belum tersedia, lalu menyarankan customer service. Tidak ada halusinasi dari pengetahuan umum — instruksi `[TASK]` pada prompt terpenuhi.
3. **Peringkat 2–3 kadang kurang relevan** (faq 41 cashback untuk query refund; faq 22 split payment untuk query cicilan) — tidak merugikan karena top-1 sudah tepat, tetapi menunjukkan batas `top_k=3` pada knowledge base kecil.
4. **Kualitas jawaban LLM konsisten**: 6/6 sesuai isi FAQ atau sesuai instruksi penolakan, gaya chat natural, maksimal 3 kalimat, tanpa istilah teknis.

**Keterbatasan yang teramati:** belum ada ambang similarity otomatis (sistem selalu mengirim top-k berapa pun skornya; kejujuran penolakan bergantung pada kepatuhan LLM pada prompt), evaluasi hanya 6 query subjektif (bukan benchmark kuantitatif), dan knowledge base hanya 59 entri FAQ pendek tanpa chunking (sesuai lingkup sesi ini).