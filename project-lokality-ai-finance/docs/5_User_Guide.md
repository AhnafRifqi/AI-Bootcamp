# User Guide: Panduan Pengguna
## Lokality AI Financial Recap & PnL Copilot (`v1.1.0`)

---

### 1. Application Overview

| Informasi | Uraian |
| :--- | :--- |
| **Nama Aplikasi** | Lokality AI Financial Recap & PnL Copilot |
| **Tujuan Aplikasi** | Membantu PT Lokal Komoditi Indonesia (Lokality) mengotomatisasi rekapitulasi penjualan (*income*) serta belanja bahan baku & operasional (*cash out*), menyusun draf Laporan Laba Rugi (PnL) yang dapat ditelusuri ke transaksi sumber, dan menyediakan asisten AI untuk konsultasi finansial harian/bulanan. |
| **Target Pengguna** | 1. **Pengelola Data** (Admin Keuangan / Staf Operasional Pabrik)<br>2. **Peninjau Hasil** (Pemilik Usaha / Manajemen Lokality) |
| **Fitur Utama** | 1. Muat Data Sampel Lokality atau Unggah CSV/Excel Mandiri<br>2. Filter Periode Fleksibel (Semua Periode, Per Bulan, atau Rentang Tanggal)<br>3. Auto-Kategorisasi HPP/OPEX + Koreksi Manual Interaktif (*Human-in-the-Loop*)<br>4. Laporan Laba Rugi (PnL) Deterministik, Indikator Kelengkapan Data, *Drill-Down* Audit Transaksi, & Unduh CSV<br>5. AI Financial Copilot (Narasi Eksekutif + Tanya-Jawab Rincian Item dengan *Guardrails* & Kontrol Kuota AI) |

---

### 2. Access Requirements

| Kebutuhan Akses | Spesifikasi |
| :--- | :--- |
| **Alamat Aplikasi** | Lokal: `http://localhost:8501` |
| **Autentikasi** | Dashboard internal lokal (tanpa login eksternal pada mode pengembangan/evaluasi). |
| **Perangkat & Peramban** | Laptop/PC dengan Google Chrome, Microsoft Edge, atau Mozilla Firefox terbaru. |
| **Format Berkas Masukan** | Berkas `.csv` atau Microsoft Excel `.xlsx` untuk data Penjualan dan Pengeluaran. |

---

### 3. Getting Started (Memulai Aplikasi)

1. Jalankan perintah berikut pada terminal PowerShell di folder proyek:
   ```powershell
   & "d:\Rework Academy\Praktek\AI-Bootcamp\.venv\Scripts\streamlit.exe" run src/ui/app.py
   ```
2. Buka peramban web dan akses `http://localhost:8501`.
3. Pada **Sidebar (Panel Kiri)**:
   - **Sumber Data:** Pilih **"Gunakan Data Sampel Lokality"** untuk mencoba simulasi lengkap bulan Oktober 2026, atau pilih **"Unggah Berkas Baru (CSV/Excel)"** untuk mengunggah berkas penjualan dan belanja perusahaan.
   - **Filter Periode Laporan:** Pilih **Semua Periode**, **Per Bulan** (mis. `2026-10`), atau **Rentang Tanggal Kustom** (mis. `01/10/2026` s/d `15/10/2026`).
   - **Kontrol & Kuota AI:** Pantau sisa kuota panggilan sesi atau matikan saklar **"Aktifkan AI Generatif (Gemini)"** bila ingin bekerja 100% dalam mode perhitungan lokal tanpa koneksi API.

---

### 4. Panduan Penggunaan Fitur Langkah demi Langkah

#### Fitur 1: Rekap Transaksi & Koreksi Kategori (*Human-in-the-Loop*)
- **Lokasi:** Tab **"📋 1. Data Transaksi & Koreksi Kategori"**
- **Langkah Penggunaan:**
  1. Periksa 4 kartu ringkasan di bagian atas (Transaksi Penjualan, Volume Terjual dalam Pack, Pos Pengeluaran, dan jumlah Koreksi Manual Kategori).
  2. Tinjau kotak status validasi untuk memastikan tidak ada kolom wajib yang terlewat atau format tanggal yang rusak.
  3. Pada bagian **"Tabel Pengeluaran Interaktif (Human-in-the-Loop)"**, klik sel pada kolom **`Tipe Akun PnL`** jika Anda ingin mengubah klasifikasi suatu pos belanja (misalnya memindahkan biaya pengiriman bahan baku dari `OPEX_Logistik` ke `HPP_Bahan_Baku`).
  4. Begitu pilihan diubah, kolom `Sumber Kategori` otomatis berubah menjadi **`Koreksi Manual`** dan seluruh perhitungan pada Tab PnL serta AI Copilot langsung diperbarui.

#### Fitur 2: Laporan Laba Rugi (PnL) & *Drill-Down* Keterlacakan Audit
- **Lokasi:** Tab **"📊 2. Laporan Laba Rugi (PnL) & Audit"**
- **Langkah Penggunaan:**
  1. Perhatikan **Banner Kelengkapan Data** di bagian paling atas tab: warna hijau menandakan seluruh komponen utama PnL (Pendapatan, HPP Bahan Baku, dan OPEX) telah terisi; warna kuning akan memberi peringatan spesifik jika ada komponen yang masih kosong (`Rp 0`).
  2. Amati 4 Kartu KPI Utama (**Total Pendapatan**, **Total HPP (COGS)**, **Laba Kotor**, dan **Laba Bersih Operasional**) beserta persentase marginnya.
  3. Tinjau tabel **Laporan Laba Rugi (PnL)** di sisi kiri, atau buka kotak **"Rumus Perhitungan Deterministik"** untuk memeriksa formula matematis yang digunakan sistem.
  4. Klik **"📥 Unduh Laporan PnL (.CSV)"** untuk menyimpan laporan ke komputer.
  5. Gulir ke bagian **"🔍 Drill-Down Keterlacakan Angka PnL (Audit Trail)"**, lalu pilih salah satu kode akun pada menu *dropdown* (misal `HPP_Bahan_Baku`). Sistem akan menampilkan seluruh baris transaksi asli beserta ID item (`EXP-001`, dst.) yang membentuk angka tersebut.

#### Fitur 3: AI Financial Copilot & Tanya-Jawab Rincian Item
- **Lokasi:** Tab **"🤖 3. AI Financial Copilot"**
- **Langkah Penggunaan:**
  1. Baca **Ringkasan Eksekutif Finansial** di panel atas untuk memahami evaluasi margin, struktur biaya, dan rekomendasi efisiensi pada periode aktif.
  2. Klik **"🔄 Perbarui Analisis AI"** jika Anda ingin menyegarkan ringkasan setelah mengubah filter atau kategori.
  3. Gunakan salah satu dari 4 tombol pertanyaan cepat atau ketik pertanyaan spesifik di kolom chat bawah (maksimal 500 karakter), misalnya menanyakan total belanja bahan baku tertentu, saluran penjualan tertinggi, atau perbandingan laba.

---

### 5. Contoh Penggunaan Nyata (Data Sampel Lokality — Oktober 2026)

| Tindakan / Pertanyaan Pengguna | Respons Aktual Aplikasi | Penjelasan |
| :--- | :--- | :--- |
| Memuat Data Sampel Penuh (`Semua Periode`) di **Tab 2** | **Pendapatan:** `Rp 46.875.000` (`2.520 pack`, `11 transaksi`)<br>**Total HPP:** `Rp 29.800.000` (`63,57%`)<br>**Laba Kotor:** `Rp 17.075.000` (`36,43%`)<br>**Total OPEX:** `Rp 8.500.000` (`18,13%`)<br>**Laba Bersih:** `Rp 8.575.000` (`18,29%`) | Dihitung deterministik dari 11 faktur penjualan dan 14 baris pengeluaran pabrik. |
| Mengatur Filter Rentang Tanggal `2026-10-01` s/d `2026-10-15` | **Pendapatan:** `Rp 27.115.000` (`6 transaksi` paruh pertama Oktober) | Seluruh tabel, grafik, dan konteks AI otomatis menyesuaikan ke rentang tanggal aktif. |
| Klik tombol cepat: *"Berapa total belanja mocaf dan tempe?"* | Merinci **`[EXP-001]` Tepung Mocaf = `Rp 7.000.000`** (`500 kg`) + **`[EXP-004]` Tempe Fermentasi = `Rp 2.400.000`** (`150 kg`), sehingga **Subtotal Mocaf & Tempe = `Rp 9.400.000`** (dari total bahan baku `Rp 17.150.000`). | Chatbot membaca rincian per baris transaksi dan menyertakan kode item sumber. |
| Klik tombol cepat: *"Apa pos beban operasional yang paling besar?"* | Menyebutkan **Utilitas & Pabrik (Listrik PLN & Gas LPG)** sebesar **`Rp 3.750.000`**, diikuti **Pemasaran & Iklan (`Rp 2.000.000`)**. | Membantu manajemen memprioritaskan efisiensi energi oven pengering & produksi. |

---

### 6. Troubleshooting & Penanganan Kendala

| Gejala / Pesan pada Layar | Penyebab | Solusi yang Disarankan |
| :--- | :--- | :--- |
| **Mode Lokal Deterministik Aktif** di Sidebar | `GEMINI_API_KEY` belum diisi di `.env`, kuota sesi (15 panggilan) habis, atau saklar AI dimatikan. | Aplikasi **tetap berfungsi penuh** menggunakan mesin analitik lokal. Jika ingin memakai narasi LLM Gemini, isi `GEMINI_API_KEY` di `.env` atau klik **Reset Kuota Sesi**. |
| **Banner Kuning: Data Belum Lengkap untuk PnL Utuh** | Pada rentang tanggal terpilih, nilai Pendapatan, HPP Bahan Baku, atau OPEX bernilai `Rp 0`. | Perluas filter periode tanggal atau periksa apakah berkas pengeluaran/penjualan bulan tersebut sudah lengkap diunggah. |
| **Peringatan Kolom Wajib Tidak Ditemukan** | Judul kolom berkas CSV/Excel tidak memuat kata kunci tanggal atau nominal rupiah. | Pastikan berkas penjualan memiliki kolom `tanggal` & `total_pendapatan`, dan berkas pengeluaran memiliki `tanggal` & `total_pengeluaran`. |
| **Chatbot Menolak Pertanyaan** | Pertanyaan berada di luar topik keuangan/operasional Lokality atau terdeteksi sebagai instruksi manipulatif. | Ajukan pertanyaan seputar pendapatan, HPP, bahan baku (mocaf, tempe, beras, jagung, kemasan), OPEX, margin laba, atau saluran penjualan. |
