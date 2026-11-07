from typing import Dict, Any, List, Optional
from .client import get_gemini_client
from .guardrails import check_query_safety, sanitize_query_length
from .quota_manager import AIQuotaManager
from ..config import GEMINI_MODEL, COMPANY_NAME, BRAND_NAME
from ..core.pnl_engine import format_rupiah

SPECIFIC_EXPENSE_TOKENS = [
    "mocaf", "tempe", "beras", "jagung", "bumbu", "rempah",
    "pouch", "karton", "box", "upah", "operator",
    "listrik", "pln", "gas", "lpg", "ekspedisi", "iklan", "ads", "penyusutan",
]


def generate_offline_answer(query: str, metrics: Dict[str, Any], status_note: Optional[str] = None) -> str:
    """
    Answers financial questions using 100% deterministic item-level & aggregate calculations
    when LLM is offline, switched off, or quota-limited.
    """
    q = query.lower()
    s = metrics["summary"]
    hpp_b = metrics["hpp_breakdown"]
    opex_b = metrics["opex_breakdown"]
    period_label = metrics.get("period", {}).get("label", "Seluruh Periode Data")
    expense_items = metrics.get("expense_items_detail", [])
    prefix = f"*(Mode Deterministik — {status_note})*\n\n" if status_note else ""

    # 1. Granular item-level matching (e.g. "Berapa total belanja mocaf dan tempe?")
    matched_tokens = [tok for tok in SPECIFIC_EXPENSE_TOKENS if tok in q]
    if matched_tokens and expense_items:
        matched_rows = [
            it for it in expense_items
            if any(tok in f"{it['deskripsi']} {it['kategori']}".lower() for tok in matched_tokens)
        ]
        if matched_rows:
            subtotal = sum(it["total_biaya"] for it in matched_rows)
            bullet_lines = "\n".join(
                [
                    f"- **[{it['row_id']}] {it['deskripsi']}** ({it['tanggal']}): "
                    f"{it['jumlah']:g} {it['satuan']} × {format_rupiah(it['harga_satuan'])} = **{format_rupiah(it['total_biaya'])}** *({it['tipe_akun']})*"
                    for it in matched_rows
                ]
            )
            return (
                f"{prefix}Berdasarkan penelusuran transaksi sumber pada periode **{period_label}**, berikut rincian item terkait "
                f"({', '.join(matched_tokens)}):\n\n"
                f"{bullet_lines}\n\n"
                f"**Subtotal Terhitung:** **{format_rupiah(subtotal)}** "
                f"(dari Total HPP Bahan Baku **{format_rupiah(hpp_b['Bahan Baku Utama (Mocaf, Beras, Tempe)'])}** / Total HPP **{format_rupiah(s['total_hpp'])}**)."
            )

    # 2. Comparison of Gross Profit vs Net Profit
    if ("laba kotor" in q and "laba bersih" in q) or ("perbandingan" in q and "laba" in q):
        return (
            f"{prefix}Perbandingan laba **{BRAND_NAME}** pada periode **{period_label}**:\n"
            f"- **Pendapatan Kotor (Revenue):** **{format_rupiah(s['total_revenue'])}**\n"
            f"- **Total HPP (COGS):** **{format_rupiah(s['total_hpp'])}**\n"
            f"- **Laba Kotor (Gross Profit):** **{format_rupiah(s['gross_profit'])}** (*Gross Margin*: **{s['gross_margin_pct']}%**)\n"
            f"- **Total Beban Operasional (OPEX):** **{format_rupiah(s['total_opex'])}**\n"
            f"- **Laba Bersih Operasional (Net Profit):** **{format_rupiah(s['net_profit'])}** (*Net Margin*: **{s['net_margin_pct']}%**)\n\n"
            f"Selisih sebesar **{format_rupiah(s['total_opex'])}** berasal dari pemotongan beban operasional pabrik, logistik, pemasaran, dan administrasi."
        )

    # 3. Largest OPEX / Operational Expense query
    if ("opex" in q or "operasional" in q or "beban" in q) and ("terbesar" in q or "paling besar" in q or "rinci" in q or "apa" in q):
        sorted_opex = sorted(opex_b.items(), key=lambda x: x[1], reverse=True)
        top_name, top_val = sorted_opex[0] if sorted_opex else ("-", 0.0)
        lines = "\n".join([f"- **{k}:** **{format_rupiah(v)}**" for k, v in sorted_opex])
        return (
            f"{prefix}Pada periode **{period_label}**, pos beban operasional (OPEX) terbesar adalah **{top_name}** sebesar **{format_rupiah(top_val)}** "
            f"dari total OPEX **{format_rupiah(s['total_opex'])}**.\n\n**Rincian Lengkap OPEX:**\n{lines}"
        )

    # 4. Sales by Channel or Product
    if "saluran" in q or "shopee" in q or "tokopedia" in q or "reseller" in q or "b2b" in q:
        chan = metrics.get("sales_by_channel", {})
        lines = "\n".join([f"- **{k}:** **{format_rupiah(v)}**" for k, v in sorted(chan.items(), key=lambda x: x[1], reverse=True)])
        return f"{prefix}Rincian pendapatan per saluran penjualan ({period_label} — Total **{format_rupiah(s['total_revenue'])}**):\n{lines}"

    if "produk" in q:
        prod = metrics.get("sales_by_product", {})
        lines = "\n".join([f"- **{k}:** **{format_rupiah(v)}**" for k, v in sorted(prod.items(), key=lambda x: x[1], reverse=True)])
        return f"{prefix}Rincian pendapatan per varian produk mi gluten-free ({period_label}):\n{lines}"

    # 5. Individual Metric Queries
    if "laba bersih" in q or "net profit" in q:
        return (
            f"{prefix}Laba bersih operasional **{BRAND_NAME}** ({period_label}) adalah **{format_rupiah(s['net_profit'])}** "
            f"dengan *Net Profit Margin* **{s['net_margin_pct']}%** "
            f"(Rumus: `{metrics['formulas']['net_profit']}`)."
        )

    if "laba kotor" in q or "gross profit" in q:
        return (
            f"{prefix}Laba kotor (*Gross Profit*) pada periode **{period_label}** tercatat sebesar **{format_rupiah(s['gross_profit'])}** "
            f"dengan *Gross Margin* **{s['gross_margin_pct']}%** "
            f"(Rumus: `{metrics['formulas']['gross_profit']}`)."
        )

    if "omzet" in q or "pendapatan" in q or "revenue" in q or "penjualan" in q:
        return (
            f"{prefix}Total pendapatan penjualan pada periode **{period_label}** adalah **{format_rupiah(s['total_revenue'])}** "
            f"dari **{s['total_transactions']} transaksi** (**{s['total_sales_qty']} pack** mi gluten-free)."
        )

    if "hpp" in q or "cogs" in q or "bahan baku" in q:
        return (
            f"{prefix}Total HPP pada periode **{period_label}** adalah **{format_rupiah(s['total_hpp'])}**, terdiri dari:\n"
            f"- Bahan Baku Utama (Mocaf, Beras, Jagung, Tempe, Bumbu): **{format_rupiah(hpp_b['Bahan Baku Utama (Mocaf, Beras, Tempe)'])}**\n"
            f"- Bahan Kemasan & Packing: **{format_rupiah(hpp_b['Bahan Kemasan & Packing'])}**\n"
            f"- Tenaga Kerja Langsung: **{format_rupiah(hpp_b['Tenaga Kerja Langsung'])}**"
        )

    return (
        f"{prefix}Rekapitulasi keuangan **{BRAND_NAME}** ({period_label}):\n"
        f"- Pendapatan: **{format_rupiah(s['total_revenue'])}** ({s['total_transactions']} transaksi)\n"
        f"- Total HPP: **{format_rupiah(s['total_hpp'])}**\n"
        f"- Laba Kotor: **{format_rupiah(s['gross_profit'])}** ({s['gross_margin_pct']}%)\n"
        f"- Total OPEX: **{format_rupiah(s['total_opex'])}**\n"
        f"- Laba Bersih: **{format_rupiah(s['net_profit'])}** ({s['net_margin_pct']}%)\n\n"
        f"Silakan tanyakan rincian spesifik seperti belanja mocaf, tempe, kemasan, saluran penjualan, atau beban operasional!"
    )


def ask_financial_copilot(
    query: str,
    metrics: Dict[str, Any],
    chat_history: List[Dict[str, str]],
    quota_manager: Optional[AIQuotaManager] = None,
) -> str:
    """
    Answers financial questions using Gemini constrained to verified item-level & PnL metrics,
    protected by input length sanitization, regex guardrails, and session quota limits.
    """
    # 1. Input length sanitization
    sanitized_query, was_truncated = sanitize_query_length(query)

    # 2. Domain & injection guardrail check
    is_safe, message = check_query_safety(sanitized_query)
    if not is_safe:
        return message

    period_label = metrics.get("period", {}).get("label", "Seluruh Periode Data")
    cache_payload = {
        **metrics.get("summary", {}),
        "period": period_label,
        "hpp": metrics.get("hpp_breakdown", {}),
        "opex": metrics.get("opex_breakdown", {}),
    }
    cache_key = AIQuotaManager.build_cache_key("chat", sanitized_query, cache_payload)

    # 3. Quota, Cooldown, Kill Switch & Cache check
    if quota_manager is not None:
        cached = quota_manager.get_cached(cache_key)
        if cached:
            return cached
        allowed, reason = quota_manager.can_invoke_llm(cache_key)
        if not allowed:
            return generate_offline_answer(sanitized_query, metrics, status_note=reason)

    client = get_gemini_client()
    if not client:
        return generate_offline_answer(sanitized_query, metrics)

    s = metrics["summary"]
    sales_prod = "\n".join([f"  - {k}: {format_rupiah(v)}" for k, v in metrics.get("sales_by_product", {}).items()])
    sales_chan = "\n".join([f"  - {k}: {format_rupiah(v)}" for k, v in metrics.get("sales_by_channel", {}).items()])
    expense_rows_txt = "\n".join(
        [
            f"  - [{it['row_id']}] {it['tanggal']} | {it['deskripsi']} | {it['jumlah']:g} {it['satuan']} @ {format_rupiah(it['harga_satuan'])} = {format_rupiah(it['total_biaya'])} ({it['tipe_akun']})"
            for it in metrics.get("expense_items_detail", [])
        ]
    )

    recent_turns = ""
    if chat_history:
        filtered_hist = [m for m in chat_history[-6:] if m.get("content") != query]
        if filtered_hist:
            recent_turns = "\nRiwayat Percakapan Terakhir:\n" + "\n".join(
                [f"- {m['role'].upper()}: {m['content'][:250]}" for m in filtered_hist]
            )

    trunc_notice = "\n(Catatan: Pertanyaan pengguna dipotong ke 500 karakter untuk efisiensi token.)" if was_truncated else ""

    context = f"""
Konteks Terverifikasi {COMPANY_NAME} ({BRAND_NAME}) — Periode: {period_label}
- Total Pendapatan (Revenue): {format_rupiah(s['total_revenue'])} ({s['total_sales_qty']} pack, {s['total_transactions']} transaksi)
- Total HPP / COGS: {format_rupiah(s['total_hpp'])}
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

Rincian Penjualan per Produk:
{sales_prod}

Rincian Penjualan per Saluran:
{sales_chan}

Rincian Transaksi Belanja / Pengeluaran per Item (Sumber Keterlacakan):
{expense_rows_txt}
{recent_turns}
"""

    system_instruction = (
        f"Anda adalah AI Financial Analyst untuk {COMPANY_NAME} ({BRAND_NAME}), produsen mi gluten-free. "
        "Jawablah pertanyaan pengguna secara akurat, ringkas, dan sertakan kode referensi transaksi (misal [EXP-001]) bila merinci item belanja. "
        "ATURAN KETAT: Jangan pernah mengarang angka di luar konteks terverifikasi di atas. "
        "Jika menjumlahkan beberapa item spesifik, tunjukkan rincian nominal tiap item beserta totalnya secara presisi."
    )

    prompt = f"{system_instruction}{trunc_notice}\n{context}\nPertanyaan Pengguna: {sanitized_query}\nJawaban:"

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = response.text if response.text else generate_offline_answer(sanitized_query, metrics)
        if quota_manager is not None and response.text:
            quota_manager.record_call(cache_key, text)
        return text
    except Exception:
        return generate_offline_answer(sanitized_query, metrics)
