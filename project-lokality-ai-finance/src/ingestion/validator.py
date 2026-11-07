from typing import List, Dict, Any
import pandas as pd

REQUIRED_SALES_COLS = ["tanggal", "total_pendapatan"]
REQUIRED_EXPENSES_COLS = ["tanggal", "deskripsi", "total_biaya"]

def validate_sales_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validates sales dataframe against requirements and checks anomalies."""
    issues: List[str] = []
    missing_cols = [c for c in REQUIRED_SALES_COLS if c not in df.columns]
    if missing_cols:
        return {
            "is_valid": False,
            "errors": [f"Kolom wajib tidak ditemukan: {', '.join(missing_cols)}"],
            "warnings": [],
            "row_count": len(df)
        }

    warnings: List[str] = []
    
    # Check null dates
    null_dates = df["tanggal"].isna().sum()
    if null_dates > 0:
        warnings.append(f"Terdapat {null_dates} baris dengan format tanggal tidak valid atau kosong.")

    # Check negative or zero revenue
    invalid_rev = (df["total_pendapatan"] <= 0).sum()
    if invalid_rev > 0:
        warnings.append(f"Terdapat {invalid_rev} baris transaksi dengan nilai pendapatan <= 0.")

    return {
        "is_valid": True,
        "errors": [],
        "warnings": warnings,
        "row_count": len(df)
    }

def validate_expenses_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validates expenses dataframe against requirements and checks anomalies."""
    missing_cols = [c for c in REQUIRED_EXPENSES_COLS if c not in df.columns]
    if missing_cols:
        return {
            "is_valid": False,
            "errors": [f"Kolom wajib tidak ditemukan: {', '.join(missing_cols)}"],
            "warnings": [],
            "row_count": len(df)
        }

    warnings: List[str] = []

    null_dates = df["tanggal"].isna().sum()
    if null_dates > 0:
        warnings.append(f"Terdapat {null_dates} baris dengan format tanggal tidak valid atau kosong.")

    invalid_cost = (df["total_biaya"] <= 0).sum()
    if invalid_cost > 0:
        warnings.append(f"Terdapat {invalid_cost} baris belanja dengan nilai biaya <= 0.")

    return {
        "is_valid": True,
        "errors": [],
        "warnings": warnings,
        "row_count": len(df)
    }
