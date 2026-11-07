import pandas as pd
from src.core.categorizer import categorize_expense_item, apply_auto_categorization


def test_categorize_raw_materials():
    assert categorize_expense_item("Tepung Mocaf Organik") == "HPP_Bahan_Baku"
    assert categorize_expense_item("Tempe Kedelai Fortifikasi") == "HPP_Bahan_Baku"
    assert categorize_expense_item("Tepung Jagung Manis") == "HPP_Bahan_Baku"


def test_categorize_packaging():
    assert categorize_expense_item("Standing pouch kemasan mi") == "HPP_Kemasan"
    assert categorize_expense_item("Karton box master") == "HPP_Kemasan"


def test_categorize_labor():
    assert categorize_expense_item("Upah operator mesin") == "HPP_Tenaga_Kerja"


def test_categorize_utilities():
    assert categorize_expense_item("Token Listrik PLN") == "OPEX_Utilitas"
    assert categorize_expense_item("Tabung gas LPG oven") == "OPEX_Utilitas"


def test_categorize_logistics():
    assert categorize_expense_item("Ongkos kirim ekspedisi JNE") == "OPEX_Logistik"


def test_apply_auto_categorization_tracks_source():
    df = pd.DataFrame([
        {"deskripsi": "Tepung Mocaf 100kg", "kategori": "Bahan", "total_biaya": 1400000, "tipe_akun": None},
        {"deskripsi": "Biaya Iklan", "kategori": "Ads", "total_biaya": 500000, "tipe_akun": "OPEX_Pemasaran"},
    ])
    res = apply_auto_categorization(df)
    assert res.loc[0, "tipe_akun"] == "HPP_Bahan_Baku"
    assert res.loc[0, "sumber_kategori"] == "Otomatis (Rule)"
    assert res.loc[1, "tipe_akun"] == "OPEX_Pemasaran"
    assert res.loc[1, "sumber_kategori"] == "Bawaan Data"
