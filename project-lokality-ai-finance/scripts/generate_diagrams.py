"""Generator diagram teknis resolusi tinggi untuk Lokality AI Financial Recap & PnL Copilot."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
DIAGRAMS_DIR = ROOT_DIR / "docs" / "diagrams"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)


def _draw_box(
    ax,
    x,
    y,
    w,
    h,
    title,
    subtitle="",
    bg="#FFFFFF",
    edge="#2B3A4A",
    title_color="#111827",
    sub_color="#4B5563",
    lw=1.35,
    fontsize=9.2,
    subsize=7.7,
):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.003,rounding_size=0.014",
        facecolor=bg,
        edgecolor=edge,
        linewidth=lw,
        zorder=3,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(
            x + w / 2,
            y + h * 0.68,
            title,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color=title_color,
            family="sans-serif",
            zorder=4,
        )
        ax.text(
            x + w / 2,
            y + h * 0.30,
            subtitle,
            ha="center",
            va="center",
            fontsize=subsize,
            color=sub_color,
            family="sans-serif",
            linespacing=1.25,
            zorder=4,
        )
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            title,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color=title_color,
            family="sans-serif",
            zorder=4,
        )


def _draw_arrow(ax, x1, y1, x2, y2, label="", color="#334155", lx_offset=0.0, ly_offset=0.0, zorder=2.2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>,head_width=0.42,head_length=0.55", color=color, lw=1.35, shrinkA=0, shrinkB=0),
        zorder=zorder,
    )
    if label:
        mx = (x1 + x2) / 2 + lx_offset
        my = (y1 + y2) / 2 + ly_offset
        ax.text(
            mx,
            my,
            label,
            ha="center",
            va="center",
            fontsize=7.3,
            color="#1F2937",
            bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=0.7),
            zorder=6,
        )


def generate_user_flow():
    fig, ax = plt.subplots(figsize=(11.8, 7.8), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(
        0.5,
        0.968,
        "User Flow Diagram — Lokality AI Financial Recap & PnL Copilot (v1.1)",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color="#111827",
    )
    ax.text(
        0.5,
        0.935,
        "Alur Interaksi Pengelola Data (Admin/Operasional) & Peninjau Hasil (Pemilik/Manajemen Lokality)",
        ha="center",
        va="center",
        fontsize=9.0,
        color="#4B5563",
    )

    # Row 1: Entry & Ingestion
    _draw_box(ax, 0.03, 0.79, 0.27, 0.10, "1. Mulai & Kontrol Sidebar", "Pilih Sumber Data, Filter Periode\n& Saklar On/Off AI", bg="#EFF6FF", edge="#1D4ED8")
    _draw_box(ax, 0.365, 0.79, 0.27, 0.10, "2. Ingestion & Validasi Skema", "Periksa Kolom Wajib CSV/Excel\n& Anomali Format Tanggal", bg="#EFF6FF", edge="#1D4ED8")
    _draw_box(ax, 0.70, 0.79, 0.27, 0.10, "3. Normalisasi & Auto-Kategori", "Bersihkan String Rupiah &\nPetakan 7 Sub-Akun HPP/OPEX", bg="#EFF6FF", edge="#1D4ED8")

    _draw_arrow(ax, 0.303, 0.84, 0.362, 0.84)
    _draw_arrow(ax, 0.638, 0.84, 0.697, 0.84, label="Valid", ly_offset=0.028)

    # Row 2: HITL, Period, Deterministic PnL
    _draw_box(ax, 0.70, 0.60, 0.27, 0.105, "4. Review Human-in-the-Loop", "Tab 1: st.data_editor Koreksi\nManual Kolom tipe_akun", bg="#FEF3C7", edge="#B45309")
    _draw_box(ax, 0.365, 0.60, 0.27, 0.105, "5. Filter Periode Aktif", "Semua Periode / Per Bulan /\nRentang Tanggal Kustom", bg="#F3F4F6", edge="#374151")
    _draw_box(ax, 0.03, 0.60, 0.27, 0.105, "6. Mesin PnL Deterministik", "Hitung Revenue, HPP, Laba Kotor,\nOPEX, Laba Bersih & Kelengkapan", bg="#ECFDF5", edge="#047857")

    _draw_arrow(ax, 0.835, 0.787, 0.835, 0.708)
    _draw_arrow(ax, 0.697, 0.652, 0.638, 0.652, label="Update", ly_offset=0.03)
    _draw_arrow(ax, 0.362, 0.652, 0.303, 0.652)

    # Row 3: Output branches (Tab 2 Audit & Tab 3 Copilot)
    _draw_box(
        ax, 0.03, 0.38, 0.42, 0.125,
        "7A. Tab 2 — Laporan Laba Rugi (PnL) & Audit Trail",
        "Banner Kelengkapan Data + Kartu KPI + Rumus Eksplisit\nDrill-Down Baris Sumber [EXP-001..014] + Unduh CSV",
        bg="#ECFDF5", edge="#047857"
    )
    _draw_box(
        ax, 0.51, 0.38, 0.46, 0.125,
        "7B. Tab 3 — AI Financial Copilot & Tanya-Jawab",
        "Ringkasan Eksekutif Bulanan + Pertanyaan Cepat / Kustom\nSanitasi Panjang Kueri Maks. 500 Karakter",
        bg="#F5F3FF", edge="#6D28D9"
    )

    _draw_arrow(ax, 0.165, 0.597, 0.165, 0.508)
    _draw_arrow(ax, 0.25, 0.597, 0.65, 0.508, label="Snapshot PnL & Rincian Item", ly_offset=0.022)

    # Row 4: Guardrails & Quota Manager (well-separated)
    _draw_box(ax, 0.51, 0.20, 0.21, 0.105, "8. Safety Guardrails", "Filter Domain Keuangan &\nBlokir Prompt Injection", bg="#FEF2F2", edge="#B91C1C")
    _draw_box(ax, 0.76, 0.20, 0.21, 0.105, "9. AI Quota Manager", "SHA-256 Cache, Saklar AI,\nKuota 15/Sesi & Cooldown 2s", bg="#FFFBEB", edge="#B45309")

    _draw_arrow(ax, 0.615, 0.377, 0.615, 0.308)
    _draw_arrow(ax, 0.723, 0.252, 0.757, 0.252, label="Lolos", ly_offset=0.03)

    # Row 5: Final Responses
    _draw_box(ax, 0.03, 0.035, 0.29, 0.095, "Penolakan Santun (0 Token)", "Tolak Topik Luar / Injeksi\nArahkan ke Topik Bisnis Lokality", bg="#FEF2F2", edge="#DC2626")
    _draw_box(ax, 0.355, 0.035, 0.29, 0.095, "Fallback Deterministik / Cache", "Jawab Akurat Tanpa Kuota API\n(Saat Offline / Saklar AI Mati)", bg="#F3F4F6", edge="#4B5563")
    _draw_box(ax, 0.68, 0.035, 0.29, 0.095, "Respons Gemini 2.5 Flash", "Jawaban Kontekstual Terikat Angka\nPnL & Kode Transaksi [EXP-xxx]", bg="#EEF2FF", edge="#4338CA")

    _draw_arrow(ax, 0.55, 0.197, 0.23, 0.133, label="Ditolak", ly_offset=0.016)
    _draw_arrow(ax, 0.81, 0.197, 0.52, 0.133, label="Cache / Lokal", ly_offset=0.016)
    _draw_arrow(ax, 0.88, 0.197, 0.84, 0.133, label="Online", lx_offset=0.04)

    out_path = DIAGRAMS_DIR / "user_flow_diagram.png"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_architecture():
    fig, ax = plt.subplots(figsize=(11.8, 8.2), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(
        0.5,
        0.972,
        "AI Solution Architecture — Lokality AI Financial Recap & PnL Copilot (v1.1)",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color="#111827",
    )
    ax.text(
        0.5,
        0.942,
        "Pemisahan Tegas Deterministic Accounting Layer (100% Presisi Angka) dan Grounded Generative AI Layer",
        ha="center",
        va="center",
        fontsize=9.0,
        color="#4B5563",
    )

    layers = [
        (0.025, 0.735, 0.95, 0.175, "1. PRESENTATION LAYER — Streamlit Web UI (src/ui/app.py)", "#F8FAFC", "#94A3B8"),
        (0.025, 0.495, 0.95, 0.185, "2. DETERMINISTIC ACCOUNTING & BUSINESS LOGIC LAYER (Python + Pandas)", "#F0FDF4", "#86EFAC"),
        (0.025, 0.245, 0.95, 0.195, "3. GROUNDED AI, GUARDRAILS & QUOTA LAYER (src/ai/)", "#FAF5FF", "#C4B5FD"),
        (0.025, 0.025, 0.95, 0.165, "4. DATA, CONFIGURATION & EXTERNAL MODEL SERVICES", "#FFFBEB", "#FCD34D"),
    ]
    for x, y, w, h, label, bg, edge in layers:
        rect = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.003,rounding_size=0.014",
            facecolor=bg, edgecolor=edge, linewidth=1.2, zorder=1
        )
        ax.add_patch(rect)
        ax.text(x + 0.016, y + h - 0.022, label, ha="left", va="center", fontsize=8.4, fontweight="bold", color="#1E293B", zorder=2)

    # Layer 1 boxes (width 0.215, gaps 0.02)
    _draw_box(ax, 0.04, 0.752, 0.215, 0.115, "Sidebar Controls", "Sumber Data, Filter Periode,\nSaklar & Bar Kuota AI", bg="#FFFFFF", edge="#2563EB", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.275, 0.752, 0.215, 0.115, "Tab 1: Data & Override", "Validasi Skema & Tabel\nst.data_editor (HITL)", bg="#FFFFFF", edge="#2563EB", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.51, 0.752, 0.215, 0.115, "Tab 2: PnL & Audit", "KPI, Tabel PnL, Rumus,\nDrill-Down & CSV Export", bg="#FFFFFF", edge="#2563EB", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.745, 0.752, 0.215, 0.115, "Tab 3: AI Copilot", "Ringkasan Eksekutif &\nChat Rincian Item", bg="#FFFFFF", edge="#2563EB", fontsize=8.7, subsize=7.4)

    # Layer 2 boxes
    _draw_box(ax, 0.04, 0.512, 0.215, 0.122, "Data Loader", "src/ingestion/loader.py\nCSV/Excel & Clean Rupiah", bg="#FFFFFF", edge="#059669", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.275, 0.512, 0.215, 0.122, "Schema Validator", "src/ingestion/validator.py\nKolom Wajib & Anomali", bg="#FFFFFF", edge="#059669", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.51, 0.512, 0.215, 0.122, "Expense Categorizer", "src/core/categorizer.py\n7 Sub-Akun & Override Flag", bg="#FFFFFF", edge="#059669", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.745, 0.512, 0.215, 0.122, "Deterministic PnL Engine", "src/core/pnl_engine.py\nPnL, Periode & Traceability", bg="#FFFFFF", edge="#059669", fontsize=8.7, subsize=7.4)

    # Layer 3 boxes
    _draw_box(ax, 0.04, 0.262, 0.215, 0.132, "Safety Guardrails", "src/ai/guardrails.py\n500-Char Limit, Domain &\nAnti-Injection (ID/EN)", bg="#FFFFFF", edge="#7C3AED", fontsize=8.7, subsize=7.3)
    _draw_box(ax, 0.275, 0.262, 0.215, 0.132, "AI Quota Manager", "src/ai/quota_manager.py\nKill-Switch, 15 Calls/Sesi,\nCooldown 2s & SHA-256 Cache", bg="#FFFFFF", edge="#7C3AED", fontsize=8.7, subsize=7.3)
    _draw_box(ax, 0.51, 0.262, 0.215, 0.132, "Narrative Generator", "src/ai/narrative_generator.py\nRingkasan Eksekutif +\nOffline Rule Fallback", bg="#FFFFFF", edge="#7C3AED", fontsize=8.7, subsize=7.3)
    _draw_box(ax, 0.745, 0.262, 0.215, 0.132, "Financial Q&A Chatbot", "src/ai/chatbot.py\nKonteks [EXP-001..014] +\nKalkulator Item Lokal", bg="#FFFFFF", edge="#7C3AED", fontsize=8.7, subsize=7.3)

    # Layer 4 boxes (well below Layer 4 header at 0.168)
    _draw_box(ax, 0.04, 0.042, 0.29, 0.098, "Spreadsheet Files", "data/mock/*.csv & User .csv/.xlsx", bg="#FFFFFF", edge="#D97706", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.355, 0.042, 0.29, 0.098, "Config & Session State", "src/config.py (.env) & st.session_state", bg="#FFFFFF", edge="#D97706", fontsize=8.7, subsize=7.4)
    _draw_box(ax, 0.67, 0.042, 0.29, 0.098, "Google Gemini API", "src/ai/client.py -> gemini-2.5-flash", bg="#FFFFFF", edge="#D97706", fontsize=8.7, subsize=7.4)

    # Clean vertical & horizontal connectors between adjacent modules
    _draw_arrow(ax, 0.147, 0.749, 0.147, 0.637)
    _draw_arrow(ax, 0.258, 0.573, 0.272, 0.573)
    _draw_arrow(ax, 0.493, 0.573, 0.507, 0.573)
    _draw_arrow(ax, 0.728, 0.573, 0.742, 0.573)

    # HITL Tab 1 -> Categorizer & PnL Engine -> Tab 2
    _draw_arrow(ax, 0.382, 0.749, 0.58, 0.637, label="HITL Edit", ly_offset=0.012)
    _draw_arrow(ax, 0.81, 0.637, 0.63, 0.749, label="PnL & Audit", ly_offset=0.012)

    # PnL Engine -> Narrative & Chatbot; Tab 3 -> Chatbot
    _draw_arrow(ax, 0.80, 0.509, 0.64, 0.397)
    _draw_arrow(ax, 0.83, 0.509, 0.83, 0.397)
    _draw_arrow(ax, 0.87, 0.749, 0.87, 0.397)

    # Horizontal pipeline inside Layer 3
    _draw_arrow(ax, 0.258, 0.328, 0.272, 0.328)
    _draw_arrow(ax, 0.493, 0.328, 0.507, 0.328)
    _draw_arrow(ax, 0.728, 0.328, 0.742, 0.328)

    # Layer 4 connections
    _draw_arrow(ax, 0.12, 0.143, 0.12, 0.509)
    _draw_arrow(ax, 0.50, 0.259, 0.50, 0.143)
    _draw_arrow(ax, 0.64, 0.259, 0.77, 0.143)
    _draw_arrow(ax, 0.85, 0.259, 0.85, 0.143)

    out_path = DIAGRAMS_DIR / "architecture_diagram.png"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_pnl_visual_summary():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6), dpi=220)
    fig.patch.set_facecolor("#FFFFFF")

    categories = ["Pendapatan\n(Revenue)", "Total HPP\n(COGS)", "Laba Kotor\n(36,43%)", "Total OPEX\n(18,13%)", "Laba Bersih\n(18,29%)"]
    values_mio = [46.875, 29.800, 17.075, 8.500, 8.575]
    colors = ["#1D4ED8", "#DC2626", "#059669", "#D97706", "#047857"]

    bars = ax1.bar(categories, values_mio, color=colors, width=0.56, edgecolor="#1F2937", linewidth=0.8)
    ax1.set_title("Ringkasan Laba Rugi (PnL) Lokality — Okt 2026", fontsize=10.5, fontweight="bold", pad=12, color="#111827")
    ax1.set_ylabel("Nominal (Juta Rupiah)", fontsize=9, color="#374151")
    ax1.set_ylim(0, 55)
    ax1.grid(axis="y", linestyle="--", alpha=0.45)
    ax1.tick_params(axis="x", labelsize=8.2)
    ax1.tick_params(axis="y", labelsize=8.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    for bar, val in zip(bars, values_mio):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.1,
            f"Rp {val:,.3f} jt".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=8.0,
            fontweight="bold",
            color="#111827",
        )

    sub_labels = [
        "HPP Bahan Baku (Mocaf, Tempe, dll.)",
        "HPP Tenaga Kerja Produksi",
        "HPP Kemasan Produk",
        "OPEX Utilitas (Listrik & Gas)",
        "OPEX Pemasaran & Iklan",
        "OPEX Administrasi & Umum",
        "OPEX Logistik & Pengiriman",
    ][::-1]
    sub_vals = [17.150, 7.000, 5.650, 3.750, 2.000, 1.500, 1.250][::-1]
    sub_colors = ["#B91C1C", "#DC2626", "#EF4444", "#D97706", "#F59E0B", "#6B7280", "#9CA3AF"][::-1]

    hbars = ax2.barh(sub_labels, sub_vals, color=sub_colors, height=0.58, edgecolor="#1F2937", linewidth=0.7)
    ax2.set_title("Rincian Struktur Biaya HPP & OPEX per Akun", fontsize=10.5, fontweight="bold", pad=12, color="#111827")
    ax2.set_xlabel("Nominal (Juta Rupiah)", fontsize=9, color="#374151")
    ax2.set_xlim(0, 21.5)
    ax2.grid(axis="x", linestyle="--", alpha=0.45)
    ax2.tick_params(axis="y", labelsize=8.2)
    ax2.tick_params(axis="x", labelsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    for bar, val in zip(hbars, sub_vals):
        ax2.text(
            bar.get_width() + 0.35,
            bar.get_y() + bar.get_height() / 2,
            f"Rp {val:,.3f} jt".replace(",", "."),
            ha="left",
            va="center",
            fontsize=8.0,
            fontweight="bold",
            color="#111827",
        )

    plt.tight_layout(pad=1.8)
    out_path = DIAGRAMS_DIR / "pnl_visual_summary.png"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    generate_user_flow()
    generate_architecture()
    generate_pnl_visual_summary()
