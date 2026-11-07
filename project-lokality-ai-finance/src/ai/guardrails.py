import re
from typing import Tuple
from ..config import MAX_QUERY_CHARS

DISALLOWED_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"abaikan (semua )?instruksi",
    r"lupakan (semua )?instruksi",
    r"tampilkan (seluruh )?prompt",
    r"system prompt",
    r"prompt sistem",
    r"api[ _]?key",
    r"secret key",
    r"bypass",
    r"jailbreak",
    r"password",
    r"token",
    r"who created you",
    r"what is your prompt",
]

RELEVANT_KEYWORDS = [
    "pnl", "laba", "rugi", "profit", "margin", "penjualan", "revenue",
    "omzet", "belanja", "biaya", "pengeluaran", "cash out", "income",
    "mocaf", "tempe", "beras", "jagung", "bumbu", "bahan baku", "kemasan",
    "pouch", "karton", "upah", "tenaga kerja", "operator", "hpp", "cogs",
    "opex", "operasional", "listrik", "pln", "gas", "lpg", "utilitas",
    "logistik", "ekspedisi", "ongkir", "iklan", "ads", "pemasaran", "admin",
    "shopee", "tokopedia", "reseller", "komunitas", "b2b", "produk", "mi",
    "harga", "keuangan", "rekap", "kuantitas", "transaksi", "invoice",
    "performa", "analisis", "rincian", "rincikan", "total", "terbesar",
    "terkecil", "periode", "bulan", "rekomendasi", "efisiensi",
]


def sanitize_query_length(user_query: str, max_chars: int = MAX_QUERY_CHARS) -> Tuple[str, bool]:
    """Truncates overly long user input to prevent token exhaustion attacks."""
    text = (user_query or "").strip()
    if len(text) > max_chars:
        return text[:max_chars], True
    return text, False


def check_query_safety(user_query: str) -> Tuple[bool, str]:
    """
    Checks if query meets guardrail safety standards and is within Lokality's financial domain.
    Returns (is_safe, explanation_or_warning).
    """
    cleaned = (user_query or "").strip().lower()

    if not cleaned:
        return False, "Pertanyaan kosong. Silakan ajukan pertanyaan seputar keuangan, belanja bahan baku, atau penjualan Lokality."

    # 1. Check for adversarial / prompt injection patterns (English & Indonesian)
    for pat in DISALLOWED_PATTERNS:
        if re.search(pat, cleaned):
            return (
                False,
                "Permintaan tidak diizinkan oleh Safety Guardrail. Sistem dirancang khusus untuk menganalisis data keuangan PT Lokal Komoditi Indonesia.",
            )

    # 2. Check domain relevance
    is_relevant = any(kw in cleaned for kw in RELEVANT_KEYWORDS)
    if not is_relevant:
        return (
            False,
            "Pertanyaan berada di luar konteks keuangan Lokality. "
            "Anda dapat menanyakan hal seperti: 'Rincikan total belanja mocaf dan tempe', "
            "'Bagaimana perbandingan laba kotor dan laba bersih?', atau 'Apa pos beban operasional terbesar?'",
        )

    return True, "OK"
