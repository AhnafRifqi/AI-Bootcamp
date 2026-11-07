import pandas as pd
from src.core.pnl_engine import calculate_pnl_metrics, generate_pnl_summary_dataframe
from src.ingestion.loader import load_sales_data, load_expenses_data
from src.config import MOCK_DATA_DIR


def test_pnl_engine_deterministic_calculation():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    expenses_df = load_expenses_data(MOCK_DATA_DIR / "sample_expenses.csv")

    metrics = calculate_pnl_metrics(sales_df, expenses_df)
    s = metrics["summary"]

    # Exact reference numbers from Lokality sample dataset
    assert s["total_revenue"] == 46_875_000.0
    assert s["total_sales_qty"] == 2520
    assert s["total_transactions"] == 11
    assert s["total_hpp"] == 29_800_000.0
    assert s["gross_profit"] == 17_075_000.0
    assert s["gross_margin_pct"] == 36.43
    assert s["total_opex"] == 8_500_000.0
    assert s["net_profit"] == 8_575_000.0
    assert s["net_margin_pct"] == 18.29
    assert s["is_complete_for_pnl"] is True


def test_pnl_period_filtering():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    expenses_df = load_expenses_data(MOCK_DATA_DIR / "sample_expenses.csv")

    # Filter first half of October (2026-10-01 to 2026-10-15)
    m_half = calculate_pnl_metrics(
        sales_df,
        expenses_df,
        start_date="2026-10-01",
        end_date="2026-10-15",
    )
    assert m_half["row_counts"]["sales_count"] == 6
    assert m_half["summary"]["total_revenue"] == 27_115_000.0
    assert m_half["period"]["label"] == "2026-10-01 s/d 2026-10-15"


def test_human_in_the_loop_manual_category_override():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    expenses_df = load_expenses_data(MOCK_DATA_DIR / "sample_expenses.csv")

    # Simulate user reclassifying EXP-011 (Rp 1.250.000 Ekspedisi) from OPEX_Logistik -> HPP_Bahan_Baku
    edited = expenses_df.copy()
    edited["sumber_kategori"] = "Bawaan Data"
    mask = edited["tipe_akun"] == "OPEX_Logistik"
    edited.loc[mask, "tipe_akun"] = "HPP_Bahan_Baku"
    edited.loc[mask, "sumber_kategori"] = "Koreksi Manual"

    metrics = calculate_pnl_metrics(sales_df, edited)
    s = metrics["summary"]

    assert s["manual_overrides_count"] == 1
    assert s["total_hpp"] == 29_800_000.0 + 1_250_000.0
    assert s["total_opex"] == 8_500_000.0 - 1_250_000.0
    # Net profit remains invariant under HPP <-> OPEX reclassification
    assert s["net_profit"] == 8_575_000.0


def test_traceability_drilldown_reconciles_with_pnl():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    expenses_df = load_expenses_data(MOCK_DATA_DIR / "sample_expenses.csv")
    metrics = calculate_pnl_metrics(sales_df, expenses_df)

    tmap = metrics["traceability_map"]
    assert tmap["PENDAPATAN_PENJUALAN"]["total"] == 46_875_000.0
    assert sum(r["total_pendapatan"] for r in tmap["PENDAPATAN_PENJUALAN"]["records"]) == 46_875_000.0

    for code in ["HPP_Bahan_Baku", "HPP_Kemasan", "HPP_Tenaga_Kerja", "OPEX_Utilitas", "OPEX_Logistik", "OPEX_Pemasaran", "OPEX_Admin"]:
        records_sum = sum(r["total_biaya"] for r in tmap[code]["records"])
        assert records_sum == tmap[code]["total"]


def test_incomplete_data_flags_warning():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    empty_expenses = pd.DataFrame(columns=["tanggal", "deskripsi", "total_biaya"])

    metrics = calculate_pnl_metrics(sales_df, empty_expenses)
    assert metrics["summary"]["is_complete_for_pnl"] is False
    assert len(metrics["completeness_warnings"]) >= 2


def test_pnl_summary_dataframe_structure():
    sales_df = load_sales_data(MOCK_DATA_DIR / "sample_sales.csv")
    expenses_df = load_expenses_data(MOCK_DATA_DIR / "sample_expenses.csv")

    metrics = calculate_pnl_metrics(sales_df, expenses_df)
    df_pnl = generate_pnl_summary_dataframe(metrics)

    assert not df_pnl.empty
    assert "Kode Akun" in df_pnl.columns
    assert "Komponen Laporan Keuangan" in df_pnl.columns
    assert "Nominal (IDR)" in df_pnl.columns
    assert "Format Rupiah" in df_pnl.columns
