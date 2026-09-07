"""
pipeline.py
===========
ETL pipeline sederhana untuk membersihkan dan mentransformasi dataset
otomotif (automobileEDA_dirty_training.csv) menjadi dataset yang siap
digunakan untuk tahap analisis atau pemodelan berikutnya.

Alur ETL:
    Extract  -> load_data()
    Transform-> inspect_data(), clean_data(), transform_data()
    Load     -> save_data()

Tahapan dalam assignment:
    Extract   : membaca dataset CSV dari folder data/raw/
    Transform : pemeriksa, membersihkan, dan mentransformasi data
    Load      : menyimpan processed dataset ke folder data/processed/

Jalankan dengan (dari root folder project):
    python src/pipeline.py
"""

import os
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Konfigurasi path
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "automobileEDA_dirty_training.csv")
PROCESSED_PATH = os.path.join(
    BASE_DIR, "data", "processed", "automobileEDA_processed.csv"
)

# Beberapa format tanggal yang dicampur pada kolom transaction_date.
# Urutan dicoba satu per satu sampai berhasil di-parse.
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y"]

# ----------------------------------------------------------------------
# 1. EXTRACT - Membaca dataset
# ----------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    """Membaca dataset mentah dari file CSV di folder data/raw/."""
    df = pd.read_csv(path)
    print(f"[EXTRACT] Dataset berhasil dimuat dari: {path}")
    print(f"[EXTRACT] Ukuran dataset: {df.shape[0]} baris, {df.shape[1]} kolom\n")
    return df


# ----------------------------------------------------------------------
# 2. TRANSFORM (tahap 1) - Pemeriksaan awal dataset
# ----------------------------------------------------------------------
def inspect_data(df: pd.DataFrame) -> None:
    """Menampilkan pemeriksaan awal kondisi dataset ke terminal."""
    print("=" * 70)
    print("DATA INSPECTION")
    print("=" * 70)

    print("\n-- 5 baris pertama --")
    print(df.head())

    print(f"\n-- Jumlah baris & kolom --\n{df.shape[0]} baris, {df.shape[1]} kolom")

    print("\n-- Nama kolom --")
    print(list(df.columns))

    print("\n-- Tipe data tiap kolom --")
    print(df.dtypes)

    print("\n-- Jumlah missing values per kolom --")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    print(f"\n-- Jumlah duplicate records --\n{df.duplicated().sum()}")

    print("\n-- Nilai unik pada kolom kategorikal relevan --")
    cat_cols = ["make", "body-style", "drive-wheels", "fuel-system", "num-of-doors"]
    for col in cat_cols:
        print(f"{col}: {sorted(df[col].dropna().unique().tolist())}")

    print("=" * 70 + "\n")


# ----------------------------------------------------------------------
# Helper: standarisasi format tanggal multi-format
# ----------------------------------------------------------------------
def _standardize_date(value):
    """Mencoba mem-parsing satu nilai tanggal dengan beberapa format yang mungkin."""
    if pd.isna(value):
        return pd.NaT
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT  # tidak ada format yang cocok


# ----------------------------------------------------------------------
# 3. TRANSFORM (tahap 2) - Data Cleaning
# ----------------------------------------------------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan dataset berdasarkan masalah yang ditemukan pada tahap
    inspeksi:
      - Baris duplikat
      - Kategori teks yang tidak konsisten (huruf besar/kecil, spasi)
      - Kategori 'awd' vs '4wd' yang merepresentasikan konsep sama
      - Format tanggal yang tidak konsisten
      - Missing values (numerik & kategorikal)
      - Kolom turunan (horsepower-binned) yang perlu dihitung ulang
    """
    df = df.copy()
    n_before = len(df)
    missing_before = df.isnull().sum().sum()

    print("=" * 70)
    print("DATA CLEANING")
    print("=" * 70)

    # 1) Hapus baris duplikat ---------------------------------------------
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[CLEANING] Baris duplikat dihapus: {n_dup}")

    # 2) Standarisasi kolom kategorikal teks (strip spasi + lowercase) ----
    text_cols = [
        "make", "body-style", "drive-wheels", "fuel-system", "aspiration",
        "engine-type", "num-of-cylinders", "engine-location", "num-of-doors",
        "horsepower-binned",
    ]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].replace({"nan": np.nan})  # kembalikan NaN yang sempat jadi teks
    print(f"[CLEANING] Kolom kategorikal dirapikan (strip + lowercase): {text_cols}")

    # 'awd' dan '4wd' merepresentasikan konsep yang sama (all/four-wheel
    # drive) tetapi ditulis berbeda -> disatukan menjadi satu kategori '4wd'.
    df["drive-wheels"] = df["drive-wheels"].replace({"awd": "4wd"})
    print("[CLEANING] Kategori 'awd' pada drive-wheels disatukan menjadi '4wd'")

    # 3) Standarisasi format tanggal --------------------------------------
    df["transaction_date"] = df["transaction_date"].apply(_standardize_date)
    n_unparsed = df["transaction_date"].isna().sum()
    print(f"[CLEANING] Kolom transaction_date distandarisasi ke format YYYY-MM-DD "
          f"(tidak dapat di-parse/kosong: {n_unparsed} baris, dipertahankan sebagai NaT "
          f"karena kolom ini tidak dipakai untuk analisis numerik)")

    # 4) Tangani missing values --------------------------------------------
    # a. Kolom identitas 'make' tidak bisa diisi otomatis (nama merek tidak
    #    bisa ditebak dari kolom lain) -> baris dengan make kosong dihapus.
    before_make_drop = len(df)
    df = df.dropna(subset=["make"]).reset_index(drop=True)
    print(f"[CLEANING] Baris dengan 'make' kosong dihapus: {before_make_drop - len(df)}")

    # b. num-of-doors: diisi dengan modus (nilai paling sering muncul)
    mode_doors = df["num-of-doors"].mode()[0]
    n_fill = df["num-of-doors"].isna().sum()
    df["num-of-doors"] = df["num-of-doors"].fillna(mode_doors)
    print(f"[CLEANING] 'num-of-doors' kosong ({n_fill} baris) diisi modus: '{mode_doors}'")

    # c. Kolom numerik (stroke, horsepower, price): diisi dengan median,
    #    karena median tahan terhadap outlier dan jumlah data kosong kecil.
    numeric_fill_cols = ["stroke", "horsepower", "price"]
    for col in numeric_fill_cols:
        n_fill = df[col].isna().sum()
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"[CLEANING] '{col}' kosong ({n_fill} baris) diisi median: {median_val:.2f}")

    # d. horsepower-binned adalah kolom turunan dari horsepower.
    #    Dihitung ulang dari horsepower yang sudah bersih agar konsisten
    #    dan sekaligus menutup nilai yang sebelumnya kosong.
    bins = np.linspace(df["horsepower"].min(), df["horsepower"].max(), 4)
    df["horsepower-binned"] = pd.cut(
        df["horsepower"], bins=bins,
        labels=["low", "medium", "high"], include_lowest=True,
    ).astype(str)
    print("[CLEANING] 'horsepower-binned' dihitung ulang dari horsepower yang sudah bersih")

    # e. transaction_date yang masih kosong (tidak bisa di-parse dari format
    #    manapun) sengaja DIPERTAHANKAN sebagai NaT, bukan dihapus/diisi,
    #    karena kolom ini hanya metadata dan tidak memengaruhi analisis
    #    spesifikasi kendaraan.

    missing_after = df.isnull().sum().sum()
    print(f"\n[CLEANING] Jumlah baris  : sebelum={n_before} -> sesudah={len(df)}")
    print(f"[CLEANING] Total missing : sebelum={missing_before} -> sesudah={missing_after}")
    print("=" * 70 + "\n")

    return df


# ----------------------------------------------------------------------
# 4. TRANSFORM (tahap 3) - Data Transformation
# ----------------------------------------------------------------------
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan transformasi wajib:
      - Min-Max Scaling pada kolom numerik 'horsepower'
      - One-Hot Encoding pada kolom kategorikal 'body-style'
    """
    df = df.copy()

    print("=" * 70)
    print("DATA TRANSFORMATION")
    print("=" * 70)

    # 1) Min-Max Scaling pada 'horsepower' ---------------------------------
    hp_min, hp_max = df["horsepower"].min(), df["horsepower"].max()
    df["horsepower-normalized"] = (df["horsepower"] - hp_min) / (hp_max - hp_min)
    print("[TRANSFORM] Min-Max Scaling diterapkan pada 'horsepower' -> "
          "kolom baru 'horsepower-normalized' (rentang 0-1)")
    print(df[["horsepower", "horsepower-normalized"]].head(5).to_string(index=False))

    # 2) One-Hot Encoding pada 'body-style' ---------------------------------
    before_cols = set(df.columns)
    body_dummies = pd.get_dummies(df["body-style"], prefix="body-style").astype(int)
    df = pd.concat([df, body_dummies], axis=1)
    new_cols = list(set(df.columns) - before_cols)
    print(f"\n[TRANSFORM] One-Hot Encoding diterapkan pada 'body-style' -> "
          f"kolom baru: {sorted(new_cols)}")

    print("=" * 70 + "\n")
    return df


# ----------------------------------------------------------------------
# 5. LOAD - Menyimpan hasil
# ----------------------------------------------------------------------
def save_data(df: pd.DataFrame, path: str) -> None:
    """Menyimpan dataset hasil pengolahan ke file CSV baru di data/processed/."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[LOAD] Processed dataset disimpan di: {path}")
    print(f"[LOAD] Ukuran akhir dataset: {df.shape[0]} baris, {df.shape[1]} kolom\n")


# ----------------------------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------------------------
def main():
    print("\n" + "#" * 70)
    print("# MENJALANKAN DATA PIPELINE: automobileEDA_dirty_training.csv")
    print("#" * 70 + "\n")

    df_raw = load_data(RAW_PATH)
    inspect_data(df_raw)
    df_clean = clean_data(df_raw)
    df_final = transform_data(df_clean)
    save_data(df_final, PROCESSED_PATH)

    print("#" * 70)
    print("# PIPELINE SELESAI DIJALANKAN")
    print("#" * 70 + "\n")


if __name__ == "__main__":
    main()