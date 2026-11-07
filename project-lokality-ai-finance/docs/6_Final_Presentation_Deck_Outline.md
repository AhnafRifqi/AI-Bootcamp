# Final Presentation Deck Outline
## AI Solution for Enterprise - Capstone Presentation (Lokality)

---

### Slide 1: Judul & Informasi Proyek
- **Judul Proyek:** AI Financial Recap & PnL Copilot for Lokality
- **Subjudul:** Solusi Automasi Rekapitulasi Finansial dan Laporan Laba Rugi Cerdas untuk PT Lokal Komoditi Indonesia
- **Program:** AI Engineering Business Project - ReWork Academy Batch 1
- **Presenter / Tim:** Ahnaf Rifqi & Tim
- **Tanggal:** November 2026

---

### Slide 2: Latar Belakang Bisnis & Problem Statement
- **Konteks Mitra:** PT Lokal Komoditi Indonesia (Lokality) — produsen manufaktur mi sehat gluten-free (tepung mocaf, beras, jagung difortifikasi tempe).
- **Tantangan Operasional:**
  - Pencatatan transaksi belanja bahan baku dan penjualan masih terpisah-pisah.
  - Rekapitulasi manual memakan waktu berhari-hari setiap akhir bulan.
  - Laporan laba rugi (PnL) terlambat terbit, mengakibatkan manajemen lambat mengevaluasi harga jual dan kesehatan margin.
- **Tujuan Solusi:** Mengembangkan sistem otomasi yang mampu mengolah data belanja dan penjualan menjadi draf PnL seketika, serta menyediakan AI Copilot untuk analitik bisnis.

---

### Slide 3: Target Pengguna & Kebutuhan Utama
- **Persona 1: Pengelola Data (Admin Keuangan / Staf Operasional)**
  - *Need:* Ingestion data cepat, validasi anomali otomatis, auto-kategorisasi pos biaya HPP vs OPEX.
- **Persona 2: Peninjau Hasil (Pemilik / Direksi Manajemen)**
  - *Need:* Visibilitas real-time metrik laba rugi bulanan, ringkasan eksekutif instan, dan fitur interaktif tanya jawab finansial.

---

### Slide 4: Arsitektur Solusi & Pemilihan Teknologi
- **Prinsip Inti:** *Deterministic Financial Engine + Generative AI Narrative*.
  - **Kalkulasi Numerik:** 100% diproses oleh kode Python & Pandas secara deterministik (0% halusinasi matematika).
  - **Analitik Cerdas:** Google Gemini API (`gemini-2.5-flash`) bertindak sebagai Business Analyst untuk narasi dan dialog tanya jawab.
- **Stack Teknologi:**
  - Frontend: Streamlit (Dashboard interaktif, visualisasi grafik, chat panel).
  - Backend: Python 3.14 + Pandas (data transformation).
  - AI Engine: Google GenAI SDK (`google-genai`) + Custom Safety Guardrails.
  - Quality: Pytest unit test suite.

---

### Slide 5: Alur Pengguna & Fitur Utama Aplikasi
- **Fitur 1: Tab Data Transaksi & Rekap**
  - Ringkasan volume transaksi & kuantitas produk terjual.
  - Tabel data penjualan dan pengeluaran dengan filter pencarian & badge kategori.
- **Fitur 2: Tab Laporan Laba Rugi (PnL)**
  - Kartu KPI: Total Revenue, HPP, Gross Profit, OPEX, Net Profit.
  - Tabel resmi PnL dengan persentase margin terhadap revenue.
  - Ekspor laporan PnL format CSV sekali klik.
  - Visualisasi grafik batang distribusi biaya & performa saluran penjualan.
- **Fitur 3: Tab AI Financial Copilot**
  - Ringkasan eksekutif otomatis kondisi keuangan bulan berjalan.
  - Chatbot percakapan cerdas dengan tombol pertanyaan cepat.

---

### Slide 6: Hasil Pengujian & Evaluasi Kualitas
- **Unit Testing (Pytest):**
  - 10 dari 10 skenario pengujian dinyatakan **PASS (100% Berhasil)**.
  - Mencakup kalkulasi identitas matematika PnL, pembersihan format string Rupiah, auto-kategorisasi kata kunci, dan regex guardrails.
- **AI Output Evaluation:**
  - 100% query di luar konteks berhasil diblokir secara aman.
  - Jawaban Q&A finansial konsisten merujuk pada angka numerik terverifikasi.

---

### Slide 7: Keterbatasan & Rencana Pengembangan Lanjutan
- **Keterbatasan Saat Ini:**
  - Input berupa file spreadsheet digital (CSV/Excel).
  - Kuota API Gemini bergantung pada kuota akun pengembang (didukung fallback offline otomatis).
- **Rencana Pengembangan Selanjutnya:**
  - Penambahan modul Computer Vision (Gemini Vision) untuk membaca foto nota/struk belanja fisik pasar tradisional.
  - Integrasi konektor langsung ke Google Drive / Google Sheets perusahaan.

---

### Slide 8: Kontribusi Tim & Penutup
- **Rincian Kontribusi Anggota:**
  - Analisis Bisnis & Perumusan BRD: Merumuskan scope dan use cases.
  - Engineering & Deterministic PnL Engine: Membangun pipeline data dan kalkulasi akuntansi.
  - Integrasi AI & Guardrails: Menghubungkan Gemini API dan mendesain prompt teruji.
  - Testing & Dokumentasi: Menyusun skenario pengujian, user guide, dan dokumentasi teknis.
- **Sesi Tanya Jawab (Q&A):** Terima kasih.
