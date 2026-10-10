# Assignment AI Model Experiment & Evaluation

Individual assignment: membandingkan **model klasik Machine Learning (Scikit-learn)** dengan **LLM API (Gemini AI)** untuk task **sentiment analysis** ulasan pelanggan e-commerce, lalu menyusun rekomendasi teknis berbasis data eksperimen.

## 1. Problem Statement

**Studi kasus:** Tim produk e-commerce ingin membangun fitur otomatis untuk mengklasifikasikan sentimen ulasan pelanggan (`positif`/`negatif`) pada halaman produk.

- **Objective:** Mengklasifikasikan sentimen ulasan produk secara otomatis agar tim produk dapat memahami pengalaman pelanggan dan menindaklanjuti ulasan negatif.
- **Target/Label:** kolom `sentiment` pada dataset → nilai `positif` atau `negatif`.
- **Batasan/Asumsi:** hanya dua kelas; teks berbahasa Indonesia; label dataset dianggap ground truth. Dataset berisi 200 baris tetapi hanya 40 teks unik, sehingga split dikelompokkan menurut `review_text` agar teks identik tidak bocor dari train ke test. Test set terdiri dari 40 baris (8 teks unik) dan dipakai sama untuk kedua pendekatan. Ukurannya kecil dan hasilnya bukan estimasi kesiapan produksi.

## 2. Dataset

- Sumber: `data/customer_reviews_sentiment.csv` (200 baris, kolom `review_id`, `product_name`, `review_text`, `sentiment`).
- Distribusi label: `positif` 110, `negatif` 90.
- Dataset asli **tidak diubah**. Pembagian train/test dilakukan di notebook dengan `StratifiedGroupKFold` (5 fold, shuffle, `random_state=42`, grup `review_text`), dan **test set yang sama** dipakai untuk kedua pendekatan. Tidak ada teks unik yang tumpang tindih antara train dan test.
- Split acak per baris sebelumnya menempatkan teks yang sama di kedua sisi (39/40 baris test juga ada di train) dan memberi skor klasik 100%; skor itu tidak dipakai karena mengalami kebocoran data.

## 3. Struktur Project

```
assignment-AI-Model-Experiment-AhnafRifqi/
├── data/
│   ├── customer_reviews_sentiment.csv   # dataset asli (tidak diubah)
│   ├── predictions_classic.csv          # output prediksi model klasik
│   ├── predictions_llm.csv              # output prediksi LLM (dibuat saat Run All)
│   └── llm_predictions.csv              # cache prediksi Gemini per teks unik (resume otomatis)
├── notebook/
│   └── experiment_notebook.ipynb
├── documentation/                       # dihasilkan otomatis oleh notebook (Run All)
│   ├── model_comparison_summary.png     # confusion matrix kedua pendekatan
│   └── comparison_summary.csv           # tabel ringkasan metrik
├── _tmp_batch_llm.py                    # helper opsional: lengkapi cache LLM di luar notebook
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## 4. Setup & Cara Menjalankan

1. Masuk ke folder project dan buat virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Linux/macOS
   ```
2. Install dependency:
   ```
   pip install -r requirements.txt
   ```
3. Salin `.env.example` menjadi `.env`, lalu isi `GEMINI_API_KEY` dari [Google AI Studio](https://aistudio.google.com/apikey).
4. Jalankan notebook dari root project dan **Run All**:
   ```
   jupyter notebook notebook/experiment_notebook.ipynb
   ```
   Notebook dapat dijalankan dari root project maupun dari dalam folder `notebook/` (path sudah menyesuaikan otomatis).

> **Catatan kuota & cache LLM.** Inference Gemini memanggil API **sekali per teks unik** (test set berisi 40 baris tetapi hanya 8 teks unik), sehingga total yang dibutuhkan hanya 8 permintaan — muat dalam kuota free-tier harian (20 request/model/hari). Hasil disimpan di `data/llm_predictions.csv` dan bersifat *resume*: jika kuota habis di tengah jalan, cukup jalankan ulang — teks yang sudah terprediksi tidak dipanggil lagi. Alternatif: jalankan helper `python _tmp_batch_llm.py` dari root project untuk melengkapi cache tanpa membuka notebook.

## 5. Ringkasan Eksperimen

### 5.1 Model Klasik (Scikit-learn)
- Preprocessing: TF-IDF (`TfidfVectorizer`).
- Model: `LogisticRegression` (max_iter=1000).
- Split grup menghasilkan 160 baris training dan 40 baris test. TF-IDF dan Logistic Regression (`max_iter=1000`) dilatih hanya pada training set. Pada test set tanpa teks duplikat lintas split, hasilnya accuracy 0,625 dan macro-F1 0,6248; model salah pada 15 dari 40 baris.

### 5.2 LLM API (Gemini)
- Pendekatan prompting: **zero-shot**, prompt meminta jawaban satu kata (`positif`/`negatif`).
- Model: `gemini-3.8-flash`, parameter `temperature=0.2` (dipilih agar output konsisten untuk tugas klasifikasi).
- Output dinormalisasi agar sesuai label dataset; ada cache lokal agar menjalankan ulang tidak memanggil API berulang.
- Inference dijalankan **per teks unik** (8 teks) lalu dipetakan ke 40 baris test, bukan per baris — hemat kuota & biaya ~5x. Notebook memakai cache berdasarkan ID dan teks ulasan yang cocok, menyimpan hasil yang berhasil, dan otomatis melanjutkan teks yang belum selesai (resume). Status: 3 dari 8 teks unik sudah terprediksi (tersimpan di cache); 5 teks sisanya menunggu kuota harian free-tier reset (HTTP 429, limit 20 request/model/hari). Metrik LLM tidak disimpulkan dari cache parsial.

## 6. Hasil Evaluasi

| Metrik | Model Klasik (Scikit-learn) | LLM API (Gemini) |
|---|---|---|
| Accuracy | 0,6250 | Belum tersedia (3/8 teks unik, menunggu kuota reset) |
| Precision (macro) | 0,6278 | Belum tersedia (3/8 teks unik, menunggu kuota reset) |
| Recall (macro) | 0,6288 | Belum tersedia (3/8 teks unik, menunggu kuota reset) |
| F1-Score (macro) | 0,6248 | Belum tersedia (3/8 teks unik, menunggu kuota reset) |

Interpretasi: accuracy berarti 25 dari 40 prediksi klasik benar. Precision dan recall macro merata-ratakan kedua kelas, masing-masing sekitar 0,63. Confusion matrix (baris aktual, kolom prediksi; urutan `negatif`, `positif`) adalah `[[12, 6], [9, 13]]`: 6 ulasan negatif salah menjadi positif dan 9 ulasan positif salah menjadi negatif. Metrik Gemini dihitung oleh notebook **setelah 8/8 teks unik terprediksi** — cukup jalankan ulang `experiment_notebook.ipynb` (atau `python _tmp_batch_llm.py` lalu Run All) setelah kuota harian reset; notebook otomatis mengisi sel evaluasi, tabel perbandingan, dan confusion matrix.

Detail lain: confusion matrix di `documentation/model_comparison_summary.png`, prediksi per-ulasan di `data/predictions_classic.csv` dan `data/predictions_llm.csv`.

## 7. Analisis Trade-off dan Limitation

Belum dapat dinyatakan pendekatan mana yang unggul dari sisi performa karena metrik Gemini belum tersedia (teks unik baru 3/8 tercache, 5 permintaan menunggu kuota reset). Model klasik perlu preprocessing dan training, tetapi prediksi berjalan lokal tanpa biaya per-request serta latensinya dapat dikendalikan. Gemini dapat dicoba tanpa training khusus dan cepat disiapkan, tetapi inference bergantung pada layanan jaringan, menambah latensi, serta memiliki potensi biaya dan batas kuota.

Keterbatasan utama adalah dataset yang kecil dan repetitif: 200 baris hanya mewakili 40 teks unik. Split acak per baris menghasilkan kebocoran data; grouped split mencegahnya tetapi test hanya berisi 8 teks unik. Model klasik salah mengklasifikasikan contoh dari kedua kelas (6 negatif sebagai positif, 9 positif sebagai negatif). Kualitas label diasumsikan benar dan data belum tentu mewakili ulasan produksi. Gemini belum dapat dianalisis karena kuota free-tier habis saat menyisakan 5 teks unik; cache parsial tidak dipakai sebagai evaluasi.

## 8. Rekomendasi Technical Approach

Gunakan TF-IDF + Logistic Regression sebagai baseline lokal untuk iterasi lanjutan karena mudah dioperasikan dan tidak bergantung pada kuota API, tetapi **jangan deploy ke produksi berdasarkan hasil ini**: macro-F1 0,6248 masih terbatas. Belum ada dasar yang cukup untuk memilihnya dibanding Gemini sebelum inference Gemini selesai pada test set identik. Setelah kuota harian reset, lengkapi 5 permintaan tersisa (jalankan ulang notebook atau `python _tmp_batch_llm.py`, keduanya *resume* dari cache) lalu Run All untuk menghasilkan metrik LLM dan tabel perbandingan; kumpulkan lebih banyak teks unik dan validasi pada test set representatif yang lebih besar sebelum keputusan produksi.