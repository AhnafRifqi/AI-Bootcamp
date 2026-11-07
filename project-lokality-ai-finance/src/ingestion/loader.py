import pandas as pd
from pathlib import Path
from typing import Union, BinaryIO

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names into lowercase without leading/trailing whitespace."""
    df = df.copy()
    df.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "")
        for col in df.columns
    ]
    return df

def clean_currency_series(series: pd.Series) -> pd.Series:
    """Converts Indonesian Rupiah string formats (e.g., 'Rp 14.000', '14,000') into float numbers."""
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0.0).astype(float)
    
    cleaned = (
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace("rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)

def load_sales_data(filepath_or_buffer: Union[str, Path, BinaryIO]) -> pd.DataFrame:
    """Loads sales data from CSV or Excel and standardizes fields."""
    if isinstance(filepath_or_buffer, (str, Path)):
        path = Path(filepath_or_buffer)
        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
    else:
        # Buffer from Streamlit file_uploader
        try:
            df = pd.read_csv(filepath_or_buffer)
        except Exception:
            filepath_or_buffer.seek(0)
            df = pd.read_excel(filepath_or_buffer)

    df = clean_column_names(df)

    # Standardize column mapping if slightly different
    col_map = {
        "date": "tanggal",
        "invoice": "nomor_invoice",
        "customer": "nama_pelanggan",
        "channel": "saluran_penjualan",
        "product": "nama_produk",
        "qty": "kuantitas",
        "quantity": "kuantitas",
        "price": "harga_satuan",
        "unit_price": "harga_satuan",
        "revenue": "total_pendapatan",
        "total": "total_pendapatan"
    }
    df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})

    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    if "kuantitas" in df.columns:
        df["kuantitas"] = pd.to_numeric(df["kuantitas"], errors="coerce").fillna(0)

    if "harga_satuan" in df.columns:
        df["harga_satuan"] = clean_currency_series(df["harga_satuan"])

    if "total_pendapatan" in df.columns:
        df["total_pendapatan"] = clean_currency_series(df["total_pendapatan"])
    elif "kuantitas" in df.columns and "harga_satuan" in df.columns:
        df["total_pendapatan"] = df["kuantitas"] * df["harga_satuan"]

    return df

def load_expenses_data(filepath_or_buffer: Union[str, Path, BinaryIO]) -> pd.DataFrame:
    """Loads expenses/spending data from CSV or Excel and standardizes fields."""
    if isinstance(filepath_or_buffer, (str, Path)):
        path = Path(filepath_or_buffer)
        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
    else:
        try:
            df = pd.read_csv(filepath_or_buffer)
        except Exception:
            filepath_or_buffer.seek(0)
            df = pd.read_excel(filepath_or_buffer)

    df = clean_column_names(df)

    col_map = {
        "date": "tanggal",
        "category": "kategori",
        "item": "deskripsi",
        "keterangan": "deskripsi",
        "description": "deskripsi",
        "qty": "jumlah",
        "quantity": "jumlah",
        "unit": "satuan",
        "price": "harga_satuan",
        "unit_price": "harga_satuan",
        "total": "total_biaya",
        "amount": "total_biaya",
        "account_type": "tipe_akun"
    }
    df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})

    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    if "jumlah" in df.columns:
        df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce").fillna(0)

    if "harga_satuan" in df.columns:
        df["harga_satuan"] = clean_currency_series(df["harga_satuan"])

    if "total_biaya" in df.columns:
        df["total_biaya"] = clean_currency_series(df["total_biaya"])
    elif "jumlah" in df.columns and "harga_satuan" in df.columns:
        df["total_biaya"] = df["jumlah"] * df["harga_satuan"]

    return df
