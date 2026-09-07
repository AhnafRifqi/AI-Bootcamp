# Data Pipeline Assignment - Automobile Dataset

## Deskripsi Singkat
Project ini membangun pipeline ETL (Extract, Transform, Load) sederhana menggunakan Python dan Pandas untuk membersihkan dan mentransformasi dataset otomotif mentah (`automobileEDA_dirty_training.csv`) menjadi dataset yang siap digunakan untuk tahap analisis atau pemodelan berikutnya.

## Sumber Dataset
Dataset diambil dari paket `Dataset_Sesi_3.zip` yang disediakan pada sesi Data Engineering (AI Engineering Bootcamp). File yang digunakan sebagai input pipeline adalah `automobileEDA_dirty_training.csv` (versi "kotor" dari dataset otomotif untuk keperluan latihan data cleaning). Dataset mentah tidak ditimpa dan tetap tersedia di folder `data/raw/`.

## Struktur Folder Project
```
assignment-data-pipeline-AhnafRifqi/
├── data/
│   ├── raw/
│   │   └── automobileEDA_dirty_training.csv     # dataset mentah (tidak diubah)
│   └── processed/
│       └── automobileEDA_processed.csv          # hasil pipeline
├── src/
│   └── pipeline.py                              # seluruh proses ETL
├── documentation/
│   └── data-flow-diagram.png                    # diagram alur data
├── README.md
└── requirements.txt
```

## Kondisi Awal Dataset
- Ukuran awal: **205 baris, 30 kolom**
- Total missing values: **17 sel**, tersebar di kolom:
  - `transaction_date` (2), `make` (2), `num-of-doors` (2), `stroke` (4), `horsepower` (3), `price` (3), `horsepower-binned` (1)
- Jumlah baris terduplikasi (exact duplicate): **4 baris**
- Kolom dengan tipe data belum sesuai:
  - `transaction_date` bertipe teks dengan **4 format tanggal berbeda** tercampur dalam satu kolom: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, dan `DD-Mon-YYYY` (contoh: `2025-01-01`, `02/01/2025`, `01-03-2025`, `04-Jan-2025`).
- Penulisan kategori yang belum konsisten:
  - `make`: campuran huruf besar/kecil dan ada spasi berlebih, contoh `ALFA-ROMERO`, `Audi`, `BMW`, `"dodge  "`, `"mercury  "`, `"porsche  "`.
  - `body-style`: `SEDAN`, `Sedan`, `sedan` merujuk pada kategori yang sama.
  - `drive-wheels`: `AWD`/`RWD` (huruf besar) bercampur dengan `awd`/`rwd`/`fwd`/`4wd` (huruf kecil). `AWD` merepresentasikan konsep sama dengan `4wd` (all/four-wheel drive) hanya ditulis berbeda.
  - `fuel-system`: `MPFI`, `Mpfi`, `mpfi` merujuk pada kategori yang sama.
- Permasalahan lain:
  - `horsepower-binned` adalah kolom turunan dari `horsepower`, sehingga nilai kosongnya perlu dihitung ulang, bukan sekadar diisi nilai acak.

## Cleaning yang Dilakukan & Alasannya

| Masalah | Kolom | Metode | Alasan |
|---|---|---|---|
| Baris duplikat | seluruh baris | `drop_duplicates()` | Baris identik 100% tidak menambah informasi, hanya membuat data bias/ganda. |
| Kategori tidak konsisten (huruf besar/kecil, spasi) | `make`, `body-style`, `drive-wheels`, `fuel-system`, dll. | `.str.strip().str.lower()` | Menyamakan penulisan agar setiap kategori terhitung sebagai satu nilai unik, bukan beberapa kategori berbeda. |
| Kategori `awd` vs `4wd` | `drive-wheels` | Mapping manual `awd -> 4wd` | Keduanya secara semantik menunjuk konsep yang sama (penggerak 4 roda), hanya penulisan berbeda. |
| Format tanggal tidak konsisten | `transaction_date` | Parsing multi-format ke `YYYY-MM-DD` | Kolom perlu format tunggal yang konsisten agar bisa diproses/diurutkan sebagai tanggal. |
| Missing value pada identitas kategorikal (`make`) | `make` | Hapus baris (2 baris sebelum dedup, tersisa 1 baris unik) | Nama merek mobil tidak bisa ditebak dari kolom lain; jumlah baris yang hilang sangat kecil sehingga aman dihapus. |
| Missing value kategorikal (`num-of-doors`) | `num-of-doors` | Isi dengan **modus** (`"four"`) | Nilai paling sering muncul adalah representasi yang wajar untuk data kategorikal dengan sedikit missing value. |

| Missing value numerik (`stroke`, `horsepower`, `price`) | `stroke`, `horsepower`, `price` | Isi dengan **median** | Median tahan terhadap outlier dan jumlah data kosong per kolom kecil (<5 baris) sehingga tidak mengubah distribusi data secara signifikan. |
| Missing value pada kolom turunan (`horsepower-binned`) | `horsepower-binned` | Hitung ulang dengan `pd.cut()` dari `horsepower` yang sudah bersih (3 bin: low/medium/high) | Kolom ini adalah hasil binning dari `horsepower`, sehingga cara paling konsisten adalah menghitung ulang, bukan menebak nilainya. |
| Missing value pada metadata (`transaction_date`, 2 baris tersisa) | `transaction_date` | **Dipertahankan** sebagai `NaT` | Kolom ini hanya metadata transaksi dan tidak digunakan pada analisis spesifikasi kendaraan, sehingga tidak perlu menghapus baris yang datanya (fitur mobil) sebenarnya masih valid. |

**Jumlah data sebelum dan sesudah cleaning:** 205 baris → 200 baris (5 baris dihapus: 4 duplikat + 1 baris dengan `make` kosong).
**Jumlah missing values sebelum dan sesudah cleaning:** 17 sel → 2 sel (sisa missing hanya pada `transaction_date`, yang sengaja dipertahankan).

## Transformasi yang Dilakukan

| Kolom Asal | Metode | Kolom Baru | Alasan Pemilihan |
|---|---|---|---|
| `horsepower` | Min-Max Scaling | `horsepower-normalized` | `horsepower` memiliki rentang nilai yang lebar dan berbeda skala dengan kolom numerik lain, sehingga perlu dinormalisasi ke rentang 0-1 agar setara jika digunakan dalam pemodelan. |
| `body-style` | One-Hot Encoding | `body-style_convertible`, `body-style_hardtop`, `body-style_hatchback`, `body-style_sedan`, `body-style_wagon` | `body-style` adalah data kategorikal nominal (tidak ada urutan/tingkatan) dengan jumlah kategori sedikit (5), sehingga one-hot encoding adalah metode yang tepat agar bisa digunakan model machine learning. |

### Contoh Nilai Sebelum dan Sesudah Transformasi

**Min-Max Scaling (`horsepower`):**

| horsepower (asli) | horsepower-normalized |
|---|---|
| 111.0 | 0.294 |
| 154.0 | 0.495 |
| 102.0 | 0.252 |
| 115.0 | 0.313 |

**One-Hot Encoding (`body-style`):**

| body-style (asli) | body-style_convertible | body-style_hardtop | body-style_hatchback | body-style_sedan | body-style_wagon |
|---|---|---|---|---|---|
| convertible | 1 | 0 | 0 | 0 | 0 |
| hatchback | 0 | 0 | 1 | 0 | 0 |
| sedan | 0 | 0 | 0 | 1 | 0 |
| wagon | 0 | 0 | 0 | 0 | 1 |

## Jumlah Data Sebelum dan Sesudah Diproses
- Sebelum: 205 baris, 30 kolom
- Sesudah: 200 baris, 36 kolom (bertambah 6 kolom hasil transformasi: 1 kolom normalisasi + 5 kolom one-hot encoding)

## Cara Menginstal Dependency
Instal semua library yang dibutuhkan (Pandas dan NumPy):
```bash
pip install -r requirements.txt
```

## Cara Menjalankan Pipeline
Jalankan dari root folder project:
```bash
python src/pipeline.py
```
Script akan menampilkan hasil inspeksi data dan proses cleaning/transformasi di terminal, lalu otomatis menyimpan dataset hasil ke `data/processed/automobileEDA_processed.csv`. Script dapat dijalankan ulang mana-mana kali dan selalu menghasilkan output yang konsisten.

## Penjelasan Singkat Alur ETL
1. **Extract** – `load_data()` membaca dataset mentah dari `data/raw/automobileEDA_dirty_training.csv`.
2. **Transform** – terdiri dari tiga tahap:
   - `inspect_data()`: memeriksa struktur, tipe data, missing values, duplikat, dan nilai unik kategori.
   - `clean_data()`: menangani duplikat, missing values, kategori tidak konsisten, dan format tanggal.
   - `transform_data()`: melakukan Min-Max Scaling dan One-Hot Encoding.
3. **Load** – `save_data()` menyimpan dataset hasil akhir sebagai file CSV baru di `data/processed/`, tanpa mengubah dataset mentah sedikit pun.

Seluruh tahapan digabung dalam function `main()` sehingga pipeline dapat dijalankan dari awal sampai akhir dalam satu kali eksekusi.

## Lokasi Processed Dataset
```
data/processed/automobileEDA_processed.csv
```