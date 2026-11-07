# Business Requirement Document (BRD)
## AI Solution for Enterprise — Capstone Business Project

---

### Informasi Project

| Informasi | Isian Kelompok |
| :--- | :--- |
| **Nama Project** | Lokality AI Financial Recap & PnL Copilot |
| **Studi Kasus Mitra** | PT Lokal Komoditi Indonesia (Lokality) — Kasus ID: LKI-01 |
| **Nama Kelompok** | Tim AI Engineering Batch 1 |
| **Anggota Kelompok** | Ahnaf Rifqi |
| **Tanggal / Versi Dokumen** | 08 November 2026 / Versi 1.1 |

---

### 1. Problem Statement

| Komponen | Uraian Fakta & Analisis Kasus |
| :--- | :--- |
| **Kondisi Saat Ini (As-Is)** | PT Lokal Komoditi Indonesia (Lokality) memproduksi mi *gluten-free* berbahan tepung mocaf, tepung beras, dan tepung jagung dengan fortifikasi tempe. Aktivitas operasional mencakup produksi, pencatatan penjualan (*income*), dan pembelian bahan baku (*cash out*). Tim internal sudah familiar menggunakan ChatGPT untuk kebutuhan perencanaan umum, namun pencatatan keuangan bulanan masih dilakukan secara terpisah dan direkap manual. |
| **Masalah Utama** | Rekapitulasi data penjualan, belanja bahan baku, dan pengeluaran operasional memakan waktu lama, belum terstandarisasi pos akunnya (HPP vs OPEX), serta menyulitkan penyusunan Laporan Laba Rugi (PnL) bulanan secara tepat waktu. |
| **Dampak Masalah** | Manajemen harus menunggu proses rekap manual yang lambat untuk mengetahui posisi laba kotor, laba bersih, dan proporsi biaya bahan baku (mocaf, tempe, beras, kemasan) setiap bulan, sehingga menghambat evaluasi harga dan efisiensi pengadaan. |
| **Informasi yang Perlu Diklarifikasi** | 1. Format asli berkas rekap penjualan & belanja dari PIC Lokality (apakah murni spreadsheet CSV/Excel atau disertai foto nota/struk fisik).<br>2. Aturan cut-off tanggal pembukuan bulanan serta perlakuan pajak/penyusutan alat produksi yang disepakati perusahaan. |

---

### 2. Target User

| Peran Pengguna | Tanggung Jawab / Konteks | Kebutuhan Terkait |
| :--- | :--- | :--- |
| **Pengelola Data (Admin Keuangan / Staf Operasional)** | Mengunggah, memeriksa, memvalidasi, dan merekap data penjualan serta pengeluaran operasional perusahaan. | Unggah CSV/Excel yang toleran variasi format Rupiah, filter periode tanggal/bulan, auto-kategorisasi pos biaya, dan tabel interaktif *Human-in-the-Loop* untuk mengoreksi kategori akun sebelum draf PnL disahkan. |
| **Peninjau Hasil (Pemilik / Manajemen Lokality)** | Meninjau laporan ringkasan keuangan bulanan untuk memahami kesehatan usaha dan mengambil keputusan bisnis. | Draf Laporan Laba Rugi (PnL) yang presisi, penanda kelengkapan data, *drill-down* keterlacakan angka ke transaksi sumber, ringkasan eksekutif AI, dan chatbot tanya-jawab keuangan terinci per item. |

---

### 3. User Needs

| ID | Kebutuhan Pengguna | Alasan / Konteks | Target Keberhasilan |
| :--- | :--- | :--- | :--- |
| **UN-01** | Merekap dan memfilter data *income* serta *cash out* berdasarkan periode bulan atau rentang tanggal. | Manajemen memerlukan evaluasi kinerja spesifik per bulan maupun per paruh bulan. | Filter periode memperbarui seluruh tabel rekap, metrik PnL, dan konteks AI secara seketika (< 2 detik). |
| **UN-02** | Mengelompokkan pos belanja ke akun HPP & OPEX secara otomatis sekaligus menyediakan koreksi manual (*Human-in-the-Loop*). | Mencegah salah klasifikasi akun biaya dan memenuhi prinsip peninjauan pengguna sebelum draf PnL dipakai. | Seluruh item belanja terpetakan otomatis dan setiap koreksi manual langsung menghitung ulang HPP/OPEX. |
| **UN-03** | Menyusun draf PnL deterministik beserta penanda kelengkapan data dan *drill-down* transaksi sumber. | Angka keuangan tidak boleh berasal dari halusinasi AI dan wajib dapat ditelusuri ke baris transaksi aslinya. | 100% angka PnL cocok dengan penjumlahan baris sumber (`traceability_map`) dan memberi peringatan bila ada komponen Rp 0/kosong. |
| **UN-04** | Memperoleh ringkasan naratif eksekutif dan tanya-jawab rincian item belanja (mis. mocaf & tempe) dalam bahasa alami. | Memanfaatkan kebiasaan tim menggunakan ChatGPT namun dengan rujukan angka terverifikasi dan kode transaksi (`[EXP-xxx]`). | Chatbot menjawab nominal spesifik per bahan baku beserta subtotal presisi dan menolak kueri di luar lingkup. |
| **UN-05** | Mengendalikan pemakaian layanan AI melalui pembatas kuota sesi, cache jawaban, dan saklar on/off AI. | Melindungi kuota API perusahaan dan memastikan aplikasi tetap berjalan normal walaupun AI dimatikan. | Saklar AI, batas kuota per sesi, jeda rate-limit, dan fallback deterministik lokal bekerja tanpa gangguan. |

---

### 4. Project Scope

| Termasuk dalam Ruang Lingkup (In-Scope) | Di Luar Ruang Lingkup (Out-of-Scope) | Batasan & Dependensi |
| :--- | :--- | :--- |
| • Ingestion & normalisasi CSV/Excel penjualan dan pengeluaran.<br>• Filter periode (Seluruh Data, Per Bulan, Rentang Tanggal).<br>• Auto-kategorisasi HPP/OPEX + editor *Human-in-the-Loop*.<br>• Mesin PnL deterministik Python, indikator kelengkapan data, ekspor CSV, & *drill-down audit trail*.<br>• AI Financial Copilot (narasi eksekutif + chatbot rincian item) dengan Guardrails & Quota Manager. | • Integrasi mutasi rekening bank otomatis (*Open Banking API*).<br>• Pelaporan perpajakan korporat (SPT PPh Badan / e-Faktur).<br>• Sistem kasir *Point-of-Sale* (POS) dan manajemen stok gudang fisik.<br>• OCR foto nota kertas (ditangguhkan hingga ada konfirmasi ketersediaan berkas nota fisik dari PIC). | • Kredensial `GEMINI_API_KEY` wajib disimpan di `.env` di luar repository.<br>• Pengujian saat ini menggunakan dataset simulasi operasional Lokality sambil menunggu serah-terima data riil resmi dari PIC perusahaan. |

---

### 5. Main Use Cases

| ID / Nama Use Case | Aktor | Tujuan | Langkah Utama | Hasil yang Diharapkan |
| :--- | :--- | :--- | :--- | :--- |
| **UC-01: Rekap Periode & Koreksi Kategori (*Human-in-the-Loop*)** | Pengelola Data | Memvalidasi transaksi dan memastikan klasifikasi akun HPP/OPEX tepat. | 1. Memilih sumber data & filter periode di sidebar.<br>2. Memeriksa peringatan validasi di Tab 1.<br>3. Mengubah `tipe_akun` pada `st.data_editor` bila diperlukan. | Baris berubah status menjadi `"Koreksi Manual"` dan seluruh perhitungan PnL langsung diperbarui. |
| **UC-02: Peninjauan Draf PnL & Drill-Down Audit** | Peninjau Hasil | Memahami laba rugi bulanan dan menelusuri asal-usul tiap nominal biaya. | 1. Membuka Tab 2 Laporan PnL.<br>2. Memeriksa status kelengkapan data & kartu KPI.<br>3. Memilih akun pada panel *Drill-Down* untuk melihat baris sumber.<br>4. Mengunduh draf PnL `.csv`. | Tabel PnL standar, rumus eksplisit, dan rincian baris transaksi sumber tampil konsisten 100%. |
| **UC-03: Konsultasi Analitik Rincian Item via AI Copilot** | Peninjau Hasil | Menanyakan rincian biaya bahan baku atau performa laba dengan bahasa sehari-hari. | 1. Membuka Tab 3 AI Financial Copilot.<br>2. Membaca ringkasan eksekutif.<br>3. Mengajukan pertanyaan (mis. *"Berapa total belanja mocaf dan tempe?"*). | Sistem merinci `[EXP-001]` Mocaf `Rp 7.000.000` + `[EXP-004]` Tempe `Rp 2.400.000` = `Rp 9.400.000` secara akurat. |
| **UC-04: Pengendalian Kuota & Saklar AI** | Pengelola Data / Admin | Membatasi pemakaian token API atau mengoperasikan aplikasi secara lokal murni. | 1. Memantau bar kuota sesi di sidebar.<br>2. Mematikan toggle *Aktifkan AI Generatif* bila diperlukan. | Sistem beralih mulus ke mode deterministik lokal tanpa menghentikan fungsi rekap maupun PnL. |

---

### 6. Success Criteria

| ID | Kriteria Keberhasilan | Cara Memeriksa / Mengukur | Target |
| :--- | :--- | :--- | :--- |
| **SC-01** | Akurasi Perhitungan PnL & Filter Periode | Unit test `pytest` memverifikasi identitas `Revenue - HPP = Gross Profit`, `Gross Profit - OPEX = Net Profit`, dan hasil filter tanggal. | Deviasi Rp 0 (100% presisi deterministik). |
| **SC-02** | Konsistensi Keterlacakan (*Traceability*) | Pengujian otomatis memastikan jumlah baris pada `traceability_map` sama persis dengan nominal pada tabel PnL untuk seluruh 8 kode akun. | 100% rekonsiliasi cocok pada seluruh akun. |
| **SC-03** | Penanda Ketidaklengkapan Data | Uji skenario saat komponen penjualan, HPP bahan baku, atau OPEX bernilai kosong/Rp 0. | 100% memunculkan `completeness_warnings` (`is_complete_for_pnl = False`). |
| **SC-04** | Ketepatan Rincian Item & Guardrail AI | Uji kueri rincian bahan baku (`mocaf` + `tempe`), kueri luar topik, *prompt injection*, dan input > 500 karakter. | Rincian item akurat 100%; kueri luar topik & injeksi ditolak 100%. |
| **SC-05** | Kepatuhan Pembatas Kuota & Saklar AI | Uji `AIQuotaManager` pada kondisi *cache hit*, kuota habis, dan saklar AI dimatikan. | *Cache hit* tidak memotong kuota; kuota habis & saklar mati otomatis fallback tanpa error. |
