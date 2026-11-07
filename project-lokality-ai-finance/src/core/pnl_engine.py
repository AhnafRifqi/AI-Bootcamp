from typing import Dict, Any, Optional, List, Union
import pandas as pd
from .categorizer import apply_auto_categorization, ACCOUNT_TYPES


def format_rupiah(amount: float) -> str:
    """Formats float numbers into standard Indonesian Rupiah notation (e.g. Rp 46.875.000)."""
    sign = "-" if amount < 0 else ""
    return f"{sign}Rp {abs(amount):,.0f}".replace(",", ".")


def _serialize_date(val: Any) -> str:
    if pd.isna(val):
        return "-"
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


def calculate_pnl_metrics(
    sales_df: pd.DataFrame,
    expenses_df: pd.DataFrame,
    start_date: Optional[Union[pd.Timestamp, str]] = None,
    end_date: Optional[Union[pd.Timestamp, str]] = None,
) -> Dict[str, Any]:
    """
    100% deterministic calculation of Profit and Loss (PnL) metrics,
    including period filtering, data completeness flags, granular item breakdown,
    and transaction-level drill-down traceability.
    """
    sales = sales_df.copy() if sales_df is not None else pd.DataFrame()
    expenses = expenses_df.copy() if expenses_df is not None else pd.DataFrame()

    # Count unparseable dates before filtering so auditor knows if any rows were excluded
    unparsed_sales_dates = int(sales["tanggal"].isna().sum()) if ("tanggal" in sales.columns and not sales.empty) else 0
    unparsed_expense_dates = int(expenses["tanggal"].isna().sum()) if ("tanggal" in expenses.columns and not expenses.empty) else 0

    ts_start = pd.to_datetime(start_date).normalize() if start_date is not None else None
    ts_end = (pd.to_datetime(end_date).normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)) if end_date is not None else None

    # Apply date filters
    if ts_start is not None and "tanggal" in sales.columns and not sales.empty:
        sales = sales[sales["tanggal"] >= ts_start]
    if ts_end is not None and "tanggal" in sales.columns and not sales.empty:
        sales = sales[sales["tanggal"] <= ts_end]

    if ts_start is not None and "tanggal" in expenses.columns and not expenses.empty:
        expenses = expenses[expenses["tanggal"] >= ts_start]
    if ts_end is not None and "tanggal" in expenses.columns and not expenses.empty:
        expenses = expenses[expenses["tanggal"] <= ts_end]

    # Ensure expenses have standard tipe_akun & sumber_kategori
    expenses = apply_auto_categorization(expenses)

    # 1. Total Revenue (Pendapatan Kotor)
    total_revenue = float(sales["total_pendapatan"].sum()) if ("total_pendapatan" in sales.columns and not sales.empty) else 0.0
    total_sales_qty = int(sales["kuantitas"].sum()) if ("kuantitas" in sales.columns and not sales.empty) else 0
    total_transactions = len(sales)

    # 2. HPP / COGS Breakdown
    def _sum_account(code: str) -> float:
        if expenses.empty or "tipe_akun" not in expenses.columns or "total_biaya" not in expenses.columns:
            return 0.0
        return float(expenses[expenses["tipe_akun"] == code]["total_biaya"].sum())

    hpp_raw = _sum_account("HPP_Bahan_Baku")
    hpp_packaging = _sum_account("HPP_Kemasan")
    hpp_labor = _sum_account("HPP_Tenaga_Kerja")
    total_hpp = hpp_raw + hpp_packaging + hpp_labor

    # 3. Laba Kotor (Gross Profit)
    gross_profit = total_revenue - total_hpp
    gross_margin_pct = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

    # 4. Beban Operasional / OPEX Breakdown
    opex_utilities = _sum_account("OPEX_Utilitas")
    opex_logistics = _sum_account("OPEX_Logistik")
    opex_marketing = _sum_account("OPEX_Pemasaran")
    opex_admin = _sum_account("OPEX_Admin")
    total_opex = opex_utilities + opex_logistics + opex_marketing + opex_admin

    # 5. Laba Bersih Operasional (Net Operating Profit)
    net_profit = gross_profit - total_opex
    net_margin_pct = (net_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

    # 6. Aggregations by Product, Channel & Specific Expense Item
    sales_by_product = (
        sales.groupby("nama_produk")["total_pendapatan"].sum().to_dict()
        if "nama_produk" in sales.columns and not sales.empty else {}
    )
    sales_by_channel = (
        sales.groupby("saluran_penjualan")["total_pendapatan"].sum().to_dict()
        if "saluran_penjualan" in sales.columns and not sales.empty else {}
    )

    expense_items_detail: List[Dict[str, Any]] = []
    if not expenses.empty:
        for idx, row in expenses.iterrows():
            expense_items_detail.append({
                "row_id": f"EXP-{int(idx)+1:03d}" if isinstance(idx, (int,)) or str(idx).isdigit() else str(idx),
                "tanggal": _serialize_date(row.get("tanggal")),
                "kategori": str(row.get("kategori", "-")),
                "deskripsi": str(row.get("deskripsi", "-")),
                "jumlah": float(row.get("jumlah", 0)),
                "satuan": str(row.get("satuan", "-")),
                "harga_satuan": float(row.get("harga_satuan", 0)),
                "total_biaya": float(row.get("total_biaya", 0)),
                "tipe_akun": str(row.get("tipe_akun", "OPEX_Admin")),
                "sumber_kategori": str(row.get("sumber_kategori", "Otomatis (Rule)")),
            })

    sales_items_detail: List[Dict[str, Any]] = []
    if not sales.empty:
        for idx, row in sales.iterrows():
            sales_items_detail.append({
                "row_id": str(row.get("nomor_invoice", f"SLS-{int(idx)+1:03d}")),
                "tanggal": _serialize_date(row.get("tanggal")),
                "nama_pelanggan": str(row.get("nama_pelanggan", "-")),
                "saluran_penjualan": str(row.get("saluran_penjualan", "-")),
                "nama_produk": str(row.get("nama_produk", "-")),
                "kuantitas": int(row.get("kuantitas", 0)),
                "harga_satuan": float(row.get("harga_satuan", 0)),
                "total_pendapatan": float(row.get("total_pendapatan", 0)),
            })

    # 7. Traceability Map (Drill-down from PnL Line Item -> Underlying Source Rows)
    traceability_map: Dict[str, Dict[str, Any]] = {
        "PENDAPATAN_PENJUALAN": {
            "kode": "PENDAPATAN_PENJUALAN",
            "label": "1. Pendapatan Penjualan Mi Gluten-Free (Revenue)",
            "kelompok": "Pendapatan",
            "total": total_revenue,
            "jumlah_transaksi": len(sales_items_detail),
            "aturan_hitung": "Sum(total_pendapatan) dari seluruh invoice penjualan pada periode terpilih.",
            "records": sales_items_detail,
        }
    }
    for acc_code, acc_label in ACCOUNT_TYPES.items():
        matching = [item for item in expense_items_detail if item["tipe_akun"] == acc_code]
        acc_sum = sum(item["total_biaya"] for item in matching)
        traceability_map[acc_code] = {
            "kode": acc_code,
            "label": acc_label,
            "kelompok": "HPP (COGS)" if acc_code.startswith("HPP_") else "Beban Operasional (OPEX)",
            "total": acc_sum,
            "jumlah_transaksi": len(matching),
            "aturan_hitung": f"Sum(total_biaya) untuk seluruh pos pengeluaran dengan tipe_akun = '{acc_code}'.",
            "records": matching,
        }

    # 8. Data Completeness Verification (Flags insufficient data to compile full PnL)
    completeness_warnings: List[str] = []
    if total_revenue <= 0:
        completeness_warnings.append(
            "Data pendapatan (penjualan) kosong atau Rp 0 pada periode ini — draf PnL belum mencerminkan pemasukan usaha."
        )
    if total_revenue > 0 and hpp_raw <= 0:
        completeness_warnings.append(
            "Pos HPP Bahan Baku tercatat Rp 0 padahal terdapat transaksi penjualan — periksa apakah catatan belanja bahan baku (mocaf/tempe/beras) sudah diunggah."
        )
    if total_revenue > 0 and total_opex <= 0:
        completeness_warnings.append(
            "Pos Beban Operasional (OPEX) tercatat Rp 0 pada periode ini — laba bersih operasional mungkin tampak lebih tinggi dari kondisi riil karena biaya listrik/logistik/admin belum masuk."
        )
    if ts_start is not None or ts_end is not None:
        if unparsed_sales_dates > 0:
            completeness_warnings.append(
                f"{unparsed_sales_dates} baris penjualan memiliki tanggal kosong/tidak valid sehingga tidak ikut terfilter periode."
            )
        if unparsed_expense_dates > 0:
            completeness_warnings.append(
                f"{unparsed_expense_dates} baris pengeluaran memiliki tanggal kosong/tidak valid sehingga tidak ikut terfilter periode."
            )

    manual_overrides_count = sum(1 for x in expense_items_detail if x["sumber_kategori"] == "Koreksi Manual")

    period_label = "Seluruh Periode Data"
    if ts_start is not None and ts_end is not None:
        period_label = f"{ts_start.strftime('%Y-%m-%d')} s/d {ts_end.strftime('%Y-%m-%d')}"
    elif ts_start is not None:
        period_label = f"Sejak {ts_start.strftime('%Y-%m-%d')}"
    elif ts_end is not None:
        period_label = f"Hingga {ts_end.strftime('%Y-%m-%d')}"

    return {
        "period": {
            "start_date": ts_start.strftime("%Y-%m-%d") if ts_start is not None else None,
            "end_date": ts_end.strftime("%Y-%m-%d") if ts_end is not None else None,
            "label": period_label,
        },
        "summary": {
            "total_revenue": total_revenue,
            "total_sales_qty": total_sales_qty,
            "total_transactions": total_transactions,
            "total_hpp": total_hpp,
            "gross_profit": gross_profit,
            "gross_margin_pct": round(gross_margin_pct, 2),
            "total_opex": total_opex,
            "net_profit": net_profit,
            "net_margin_pct": round(net_margin_pct, 2),
            "manual_overrides_count": manual_overrides_count,
            "is_complete_for_pnl": len(completeness_warnings) == 0,
        },
        "completeness_warnings": completeness_warnings,
        "hpp_breakdown": {
            "Bahan Baku Utama (Mocaf, Beras, Tempe)": hpp_raw,
            "Bahan Kemasan & Packing": hpp_packaging,
            "Tenaga Kerja Langsung": hpp_labor,
        },
        "opex_breakdown": {
            "Utilitas & Pabrik (Listrik, Gas)": opex_utilities,
            "Logistik & Ekspedisi": opex_logistics,
            "Pemasaran & Iklan": opex_marketing,
            "Administrasi & Umum": opex_admin,
        },
        "sales_by_product": sales_by_product,
        "sales_by_channel": sales_by_channel,
        "expense_items_detail": expense_items_detail,
        "sales_items_detail": sales_items_detail,
        "traceability_map": traceability_map,
        "formulas": {
            "gross_profit": f"{format_rupiah(total_revenue)} (Revenue) - {format_rupiah(total_hpp)} (Total HPP) = {format_rupiah(gross_profit)}",
            "net_profit": f"{format_rupiah(gross_profit)} (Laba Kotor) - {format_rupiah(total_opex)} (Total OPEX) = {format_rupiah(net_profit)}",
        },
        "row_counts": {
            "sales_count": len(sales),
            "expenses_count": len(expenses),
        },
    }


def generate_pnl_summary_dataframe(metrics: Dict[str, Any]) -> pd.DataFrame:
    """Generates a standardized tabular PnL statement dataframe for reporting and CSV export."""
    s = metrics["summary"]
    hpp_b = metrics["hpp_breakdown"]
    opex_b = metrics["opex_breakdown"]
    rev = s["total_revenue"]

    def pct(val: float) -> str:
        return f"{(val / rev * 100):.2f}%" if rev > 0 else "0.00%"

    rows = [
        {
            "Kode Akun": "REV-00",
            "Komponen Laporan Keuangan": "1. PENDAPATAN PENJUALAN (REVENUE)",
            "Nominal (IDR)": s["total_revenue"],
            "Format Rupiah": format_rupiah(s["total_revenue"]),
            "% Terhadap Revenue": "100.00%" if rev > 0 else "0.00%",
        },
        {
            "Kode Akun": "PENDAPATAN_PENJUALAN",
            "Komponen Laporan Keuangan": "   - Penjualan Produk Mi Gluten-Free",
            "Nominal (IDR)": s["total_revenue"],
            "Format Rupiah": format_rupiah(s["total_revenue"]),
            "% Terhadap Revenue": "100.00%" if rev > 0 else "0.00%",
        },
        {"Kode Akun": "", "Komponen Laporan Keuangan": "", "Nominal (IDR)": 0.0, "Format Rupiah": "", "% Terhadap Revenue": ""},
        {
            "Kode Akun": "HPP-00",
            "Komponen Laporan Keuangan": "2. HARGA POKOK PENJUALAN (HPP / COGS)",
            "Nominal (IDR)": s["total_hpp"],
            "Format Rupiah": format_rupiah(s["total_hpp"]),
            "% Terhadap Revenue": pct(s["total_hpp"]),
        },
    ]

    hpp_codes = ["HPP_Bahan_Baku", "HPP_Kemasan", "HPP_Tenaga_Kerja"]
    for code, (name, val) in zip(hpp_codes, hpp_b.items()):
        rows.append({
            "Kode Akun": code,
            "Komponen Laporan Keuangan": f"   - {name}",
            "Nominal (IDR)": val,
            "Format Rupiah": format_rupiah(val),
            "% Terhadap Revenue": pct(val),
        })

    rows.extend([
        {"Kode Akun": "", "Komponen Laporan Keuangan": "", "Nominal (IDR)": 0.0, "Format Rupiah": "", "% Terhadap Revenue": ""},
        {
            "Kode Akun": "GP-00",
            "Komponen Laporan Keuangan": "3. LABA KOTOR (GROSS PROFIT)",
            "Nominal (IDR)": s["gross_profit"],
            "Format Rupiah": format_rupiah(s["gross_profit"]),
            "% Terhadap Revenue": f"{s['gross_margin_pct']:.2f}%",
        },
        {"Kode Akun": "", "Komponen Laporan Keuangan": "", "Nominal (IDR)": 0.0, "Format Rupiah": "", "% Terhadap Revenue": ""},
        {
            "Kode Akun": "OPEX-00",
            "Komponen Laporan Keuangan": "4. BEBAN OPERASIONAL (OPEX)",
            "Nominal (IDR)": s["total_opex"],
            "Format Rupiah": format_rupiah(s["total_opex"]),
            "% Terhadap Revenue": pct(s["total_opex"]),
        },
    ])

    opex_codes = ["OPEX_Utilitas", "OPEX_Logistik", "OPEX_Pemasaran", "OPEX_Admin"]
    for code, (name, val) in zip(opex_codes, opex_b.items()):
        rows.append({
            "Kode Akun": code,
            "Komponen Laporan Keuangan": f"   - {name}",
            "Nominal (IDR)": val,
            "Format Rupiah": format_rupiah(val),
            "% Terhadap Revenue": pct(val),
        })

    rows.extend([
        {"Kode Akun": "", "Komponen Laporan Keuangan": "", "Nominal (IDR)": 0.0, "Format Rupiah": "", "% Terhadap Revenue": ""},
        {
            "Kode Akun": "NP-00",
            "Komponen Laporan Keuangan": "5. LABA BERSIH OPERASIONAL (NET PROFIT)",
            "Nominal (IDR)": s["net_profit"],
            "Format Rupiah": format_rupiah(s["net_profit"]),
            "% Terhadap Revenue": f"{s['net_margin_pct']:.2f}%",
        },
    ])

    return pd.DataFrame(rows)
