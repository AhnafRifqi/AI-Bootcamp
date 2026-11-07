from typing import Dict, Any, Optional
from .client import get_gemini_client
from .quota_manager import AIQuotaManager
from ..config import GEMINI_MODEL, COMPANY_NAME, BRAND_NAME
from ..core.pnl_engine import format_rupiah


def generate_fallback_narrative(metrics: Dict[str, Any], status_note: Optional[str] = None) -> str:
    """Generates a deterministic, audit-grade executive financial summary when LLM is offline or quota-limited."""
    s = metrics["summary"]
    hpp_b = metrics["hpp_breakdown"]
    opex_b = metrics["opex_breakdown"]
    period_label = metrics.get("period", {}).get("label", "Seluruh Periode Data")
    warnings = metrics.get("completeness_warnings", [])

    status_usaha = "sehat dan menguntungkan (surplus)" if s["net_profit"] > 0 else "mengalami defisit operasional (rugi)"
    note_header = f"> *Catatan Mode Sistem: {status_note}*\n\n" if status_note else ""
    warning_block = ""
    if warnings:
        joined = "\n".join([f"- ⚠️ {w}" for w in warnings])
        warning_block = f"\n**Catatan Kelengkapan Data:**\n{joined}\n"

    # Identify top raw materials from granular detail
    raw_items = [
        item for item in metrics.get("expense_items_detail", [])
        if item.get("tipe_akun") == "HPP_Bahan_Baku"
    ]
    raw_lines = ", ".join(
        [f"{it['deskripsi']} ({format_rupiah(it['total_biaya'])})" for it in raw_items[:4]]
    ) or "Tidak ada rincian bahan baku pada periode ini"

    return f"""{note_header}### Ringkasan Eksekutif Keuangan — {BRAND_NAME} ({period_label})
{warning_block}
1. **Performa Pendapatan & Laba Bersih:**
   Pada periode **{period_label}**, {COMPANY_NAME} membukukan total pendapatan kotor sebesar **{format_rupiah(s['total_revenue'])}** dari **{s['total_transactions']} transaksi** (**{s['total_sales_qty']} pack** mi terjual). Setelah dikurangi HPP dan beban operasional, laba bersih operasional tercatat sebesar **{format_rupiah(s['net_profit'])}** (*Net Profit Margin* **{s['net_margin_pct']}%**), menunjukkan kondisi usaha **{status_usaha}**.

2. **Struktur Harga Pokok Penjualan (HPP):**
   Total HPP sebesar **{format_rupiah(s['total_hpp'])}**, menghasilkan Laba Kotor **{format_rupiah(s['gross_profit'])}** (*Gross Margin* **{s['gross_margin_pct']}%**).
   - **Bahan Baku Utama & Fortifikasi:** **{format_rupiah(hpp_b['Bahan Baku Utama (Mocaf, Beras, Tempe)'])}** — mencakup *{raw_lines}*.
   - **Bahan Kemasan & Packing:** **{format_rupiah(hpp_b['Bahan Kemasan & Packing'])}**
   - **Tenaga Kerja Langsung:** **{format_rupiah(hpp_b['Tenaga Kerja Langsung'])}**

3. **Beban Operasional (OPEX):**
   Total OPEX mencapai **{format_rupiah(s['total_opex'])}**, didominasi oleh **Utilitas Pabrik (Listrik & Gas Oven)** sebesar **{format_rupiah(opex_b['Utilitas & Pabrik (Listrik, Gas)'])}** dan **Pemasaran & Iklan** sebesar **{format_rupiah(opex_b['Pemasaran & Iklan'])}**.

4. **Rekomendasi Taktis Manajemen:**
   - Amankan kontrak harga grosir untuk komponen bahan baku terbesar (tepung mocaf & tepung beras) serta pemasok tempe fermentasi guna menjaga *Gross Margin* di atas 35%.
   - Optimalkan jadwal pemanggangan oven pengering mi secara *batch* penuh untuk menekan proporsi biaya listrik 3-phase dan LPG industri.
"""


def generate_pnl_narrative(
    metrics: Dict[str, Any],
    quota_manager: Optional[AIQuotaManager] = None,
) -> str:
    """Generates an executive narrative financial insight using Gemini LLM with quota & cache safeguards."""
    period_label = metrics.get("period", {}).get("label", "Seluruh Periode Data")
    cache_payload = {**metrics.get("summary", {}), "period": period_label}
    cache_key = AIQuotaManager.build_cache_key("narrative", period_label, cache_payload)

    if quota_manager is not None:
        cached = quota_manager.get_cached(cache_key)
        if cached:
            return cached
        allowed, reason = quota_manager.can_invoke_llm(cache_key)
        if not allowed:
            return generate_fallback_narrative(metrics, status_note=reason)

    client = get_gemini_client()
    if not client:
        return generate_fallback_narrative(metrics)

    s = metrics["summary"]
    item_lines = "\n".join(
        [
            f"  - [{it['row_id']}] {it['deskripsi']} ({it['jumlah']:g} {it['satuan']}): {format_rupiah(it['total_biaya'])} [{it['tipe_akun']}]"
            for it in metrics.get("expense_items_detail", [])
        ]
    )
    warnings_text = "; ".join(metrics.get("completeness_warnings", [])) or "Data lengkap & tervalidasi."

    prompt = f"""
Anda adalah Senior Financial & Business Analyst untuk {COMPANY_NAME} ({BRAND_NAME}), produsen mi gluten-free berbahan mocaf, beras, jagung, dan fortifikasi tempe.

Periode Laporan: {period_label}
Status Kelengkapan Data: {warnings_text}

Data aktual hasil perhitungan deterministik PnL:
- Total Pendapatan (Revenue): {format_rupiah(s['total_revenue'])} ({s['total_sales_qty']} pack dari {s['total_transactions']} transaksi)
- Total HPP (COGS): {format_rupiah(s['total_hpp'])}
  * Bahan Baku Utama: {format_rupiah(metrics['hpp_breakdown']['Bahan Baku Utama (Mocaf, Beras, Tempe)'])}
  * Bahan Kemasan: {format_rupiah(metrics['hpp_breakdown']['Bahan Kemasan & Packing'])}
  * Tenaga Kerja Langsung: {format_rupiah(metrics['hpp_breakdown']['Tenaga Kerja Langsung'])}
- Laba Kotor (Gross Profit): {format_rupiah(s['gross_profit'])} (Gross Margin: {s['gross_margin_pct']}%)
- Total Beban Operasional (OPEX): {format_rupiah(s['total_opex'])}
  * Utilitas Pabrik: {format_rupiah(metrics['opex_breakdown']['Utilitas & Pabrik (Listrik, Gas)'])}
  * Logistik & Ekspedisi: {format_rupiah(metrics['opex_breakdown']['Logistik & Ekspedisi'])}
  * Pemasaran & Iklan: {format_rupiah(metrics['opex_breakdown']['Pemasaran & Iklan'])}
  * Administrasi & Umum: {format_rupiah(metrics['opex_breakdown']['Administrasi & Umum'])}
- Laba Bersih Operasional (Net Profit): {format_rupiah(s['net_profit'])} (Net Margin: {s['net_margin_pct']}%)

Rincian Item Belanja Sumber:
{item_lines}

TUGAS ANDA:
Buat ringkasan eksekutif berbahasa Indonesia (ringkas, tajam, bernada bisnis) mencakup:
1. Performa Laba & Margin pada periode ini.
2. Evaluasi Efisiensi Bahan Baku (sebutkan komponen spesifik seperti mocaf & tempe) dan OPEX.
3. 2-3 Rekomendasi konkret untuk manajemen.

ATURAN KETAT:
- Gunakan angka persis sesuai data di atas. DILARANG mengarang atau membulatkan secara keliru.
- Jika ada peringatan kelengkapan data, cantumkan catatannya secara jujur.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = response.text if response.text else generate_fallback_narrative(metrics)
        if quota_manager is not None and response.text:
            quota_manager.record_call(cache_key, text)
        return text
    except Exception:
        return generate_fallback_narrative(metrics)
