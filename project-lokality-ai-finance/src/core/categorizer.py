import pandas as pd
from typing import Optional, Dict, List

ACCOUNT_TYPES: Dict[str, str] = {
    "HPP_Bahan_Baku": "HPP - Bahan Baku Utama & Fortifikasi",
    "HPP_Kemasan": "HPP - Bahan Kemasan & Packing",
    "HPP_Tenaga_Kerja": "HPP - Upah Tenaga Kerja Langsung",
    "OPEX_Utilitas": "OPEX - Utilitas & Pabrik (Listrik, Gas, Air)",
    "OPEX_Logistik": "OPEX - Pengiriman & Logistik",
    "OPEX_Pemasaran": "OPEX - Pemasaran & Iklan",
    "OPEX_Admin": "OPEX - Administrasi, Kantor & Umum",
}

VALID_ACCOUNT_CODES: List[str] = list(ACCOUNT_TYPES.keys())

KEYWORDS_MAPPING: Dict[str, List[str]] = {
    "HPP_Bahan_Baku": [
        "mocaf", "tepung", "beras", "jagung", "tempe", "kedelai",
        "bumbu", "rempah", "garam", "fortifikasi", "bahan baku", "ekstrak",
    ],
    "HPP_Kemasan": [
        "kemasan", "pouch", "standing pouch", "karton", "box",
        "kardus", "plastik", "silica", "label", "stiker", "sealer",
    ],
    "HPP_Tenaga_Kerja": [
        "upah", "gaji operator", "ongkos kerja", "tukang giling",
        "pekerja", "tenaga kerja", "harian produksi", "operator",
    ],
    "OPEX_Utilitas": [
        "listrik", "pln", "gas", "lpg", "air", "pdam", "token",
    ],
    "OPEX_Logistik": [
        "ongkir", "ongkos kirim", "ekspedisi", "kargo", "jne",
        "j&t", "sicepat", "kurir", "bahan bakar", "bensin", "solar", "distribusi",
    ],
    "OPEX_Pemasaran": [
        "iklan", "ads", "meta", "facebook ads", "instagram", "tiktok",
        "shopee ads", "endorse", "promosi", "brosur", "bazar", "pameran",
    ],
    "OPEX_Admin": [
        "sewa", "kantor", "internet", "wifi", "atk", "kertas",
        "perlengkapan", "konsumsi", "penyusutan", "admin", "pembukuan",
    ],
}


def categorize_expense_item(description: str, existing_category: Optional[str] = None) -> str:
    """Categorizes an expense item into a standard PnL account code using deterministic keyword rules."""
    text = f"{description or ''} {existing_category or ''}".lower()

    for account_type, keywords in KEYWORDS_MAPPING.items():
        if any(kw in text for kw in keywords):
            return account_type

    return "OPEX_Admin"


def apply_auto_categorization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures every expense row has a valid standard 'tipe_akun' and tracks 'sumber_kategori'
    to support Human-in-the-Loop auditing and manual category overrides.
    """
    df = df.copy()
    if df.empty:
        if "tipe_akun" not in df.columns:
            df["tipe_akun"] = pd.Series(dtype="object")
        if "sumber_kategori" not in df.columns:
            df["sumber_kategori"] = pd.Series(dtype="object")
        return df

    if "tipe_akun" not in df.columns:
        df["tipe_akun"] = None
    if "sumber_kategori" not in df.columns:
        df["sumber_kategori"] = None

    for idx, row in df.iterrows():
        current = row["tipe_akun"]
        source = row["sumber_kategori"]
        if pd.notna(current) and str(current) in ACCOUNT_TYPES:
            if pd.isna(source) or not str(source).strip():
                df.at[idx, "sumber_kategori"] = "Bawaan Data"
        else:
            desc = str(row.get("deskripsi", ""))
            cat = str(row.get("kategori", ""))
            df.at[idx, "tipe_akun"] = categorize_expense_item(desc, cat)
            df.at[idx, "sumber_kategori"] = "Otomatis (Rule)"

    return df
