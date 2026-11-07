import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    COMPANY_NAME,
    BRAND_NAME,
    PRODUCT_FOCUS,
    MOCK_DATA_DIR,
    GEMINI_MODEL,
    MAX_AI_CALLS_PER_SESSION,
    MIN_AI_COOLDOWN_SECONDS,
)
from src.ingestion.loader import load_sales_data, load_expenses_data
from src.ingestion.validator import validate_sales_dataframe, validate_expenses_dataframe
from src.core.categorizer import (
    apply_auto_categorization,
    VALID_ACCOUNT_CODES,
    ACCOUNT_TYPES,
)
from src.core.pnl_engine import (
    calculate_pnl_metrics,
    generate_pnl_summary_dataframe,
    format_rupiah,
)
from src.ai.client import is_gemini_available
from src.ai.quota_manager import AIQuotaManager
from src.ai.narrative_generator import generate_pnl_narrative
from src.ai.chatbot import ask_financial_copilot

# Page Config
st.set_page_config(
    page_title=f"{BRAND_NAME} — AI Financial Engine & PnL Copilot",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .audit-box {
        background-color: #f8fafc;
        border-left: 4px solid #0f766e;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 14px;
        font-size: 0.92rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Quota Manager in Session State
if "quota_manager" not in st.session_state:
    st.session_state.quota_manager = AIQuotaManager(
        max_calls=MAX_AI_CALLS_PER_SESSION,
        cooldown_seconds=MIN_AI_COOLDOWN_SECONDS,
        ai_enabled=True,
    )
quota_mgr: AIQuotaManager = st.session_state.quota_manager


@st.cache_data
def get_sample_data():
    sales_path = MOCK_DATA_DIR / "sample_sales.csv"
    expenses_path = MOCK_DATA_DIR / "sample_expenses.csv"
    return load_sales_data(sales_path), load_expenses_data(expenses_path)


# ----------------- SIDEBAR -----------------
st.sidebar.title(f"🍜 {BRAND_NAME}")
st.sidebar.caption(f"**{COMPANY_NAME}**\n\n*{PRODUCT_FOCUS}*")
st.sidebar.divider()

st.sidebar.subheader("1. Sumber Data")
data_source = st.sidebar.radio(
    "Pilih Sumber Data:",
    ["Gunakan Data Sampel Lokality", "Unggah Berkas Baru (CSV/Excel)"],
    index=0,
)

sales_file = None
expenses_file = None
if data_source == "Unggah Berkas Baru (CSV/Excel)":
    sales_file = st.sidebar.file_uploader("Data Penjualan (Sales):", type=["csv", "xlsx"])
    expenses_file = st.sidebar.file_uploader("Data Belanja & Pengeluaran:", type=["csv", "xlsx"])

# Load Raw Base Data
if data_source == "Gunakan Data Sampel Lokality":
    raw_sales_df, raw_expenses_df = get_sample_data()
    dataset_key = "sample_lokality_v1"
else:
    raw_sales_df = load_sales_data(sales_file) if sales_file is not None else pd.DataFrame()
    raw_expenses_df = load_expenses_data(expenses_file) if expenses_file is not None else pd.DataFrame()
    dataset_key = f"upload_{getattr(sales_file, 'name', 'none')}_{getattr(expenses_file, 'name', 'none')}"

# Initialize or refresh editable expenses dataframe for Human-in-the-Loop review
if st.session_state.get("active_dataset_key") != dataset_key:
    st.session_state.active_dataset_key = dataset_key
    st.session_state.working_expenses_df = apply_auto_categorization(raw_expenses_df) if not raw_expenses_df.empty else pd.DataFrame()

working_expenses_df: pd.DataFrame = st.session_state.working_expenses_df
sales_df: pd.DataFrame = raw_sales_df

# ----------------- SIDEBAR: PERIOD FILTER -----------------
st.sidebar.divider()
st.sidebar.subheader("2. Filter Periode Laporan")

start_date_filter = None
end_date_filter = None

all_dates = []
if not sales_df.empty and "tanggal" in sales_df.columns:
    all_dates.extend(sales_df["tanggal"].dropna().tolist())
if not working_expenses_df.empty and "tanggal" in working_expenses_df.columns:
    all_dates.extend(working_expenses_df["tanggal"].dropna().tolist())

period_mode = st.sidebar.selectbox(
    "Mode Periode:",
    ["Seluruh Periode Data", "Filter per Bulan", "Rentang Tanggal Kustom"],
    index=0,
)

if all_dates:
    min_dt = min(all_dates).date()
    max_dt = max(all_dates).date()

    if period_mode == "Filter per Bulan":
        months_available = sorted(list({d.strftime("%Y-%m") for d in all_dates}))
        selected_month = st.sidebar.selectbox("Pilih Bulan (YYYY-MM):", months_available, index=len(months_available) - 1)
        m_start = pd.to_datetime(f"{selected_month}-01")
        m_end = m_start + pd.offsets.MonthEnd(1)
        start_date_filter = m_start
        end_date_filter = m_end
    elif period_mode == "Rentang Tanggal Kustom":
        date_range = st.sidebar.date_input(
            "Pilih Rentang Tanggal:",
            value=(min_dt, max_dt),
            min_value=min_dt,
            max_value=max_dt,
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_date_filter = pd.to_datetime(date_range[0])
            end_date_filter = pd.to_datetime(date_range[1])

# ----------------- SIDEBAR: AI QUOTA & KILL SWITCH -----------------
st.sidebar.divider()
st.sidebar.subheader("3. Kontrol & Kuota AI")

ai_toggle = st.sidebar.toggle(
    "Aktifkan AI Generatif (Gemini)",
    value=quota_mgr.ai_enabled,
    help="Saklar utama (Kill Switch) untuk mengizinkan atau mematikan pemanggilan API eksternal.",
)
quota_mgr.ai_enabled = ai_toggle

gemini_configured = is_gemini_available()
q_status = quota_mgr.status_dict()

if not ai_toggle:
    st.sidebar.warning("Saklar AI Nonaktif — Mode Deterministik Lokal")
elif gemini_configured:
    st.sidebar.success(f"Gemini API Siap ({GEMINI_MODEL})")
else:
    st.sidebar.info("Tanpa API Key — Mode Deterministik Lokal")

quota_ratio = min(1.0, q_status["calls_made"] / q_status["max_calls"])
st.sidebar.progress(quota_ratio, text=f"Kuota Sesi AI: {q_status['calls_made']} / {q_status['max_calls']} panggilan")
st.sidebar.caption(f"Sisa Kuota: **{q_status['remaining_calls']}** | Cache Hit: **{q_status['cache_hits']}**")

# Validation & Deterministic PnL Calculation
sales_val = validate_sales_dataframe(sales_df) if not sales_df.empty else {"is_valid": False, "warnings": ["Belum ada data penjualan."]}
expenses_val = validate_expenses_dataframe(working_expenses_df) if not working_expenses_df.empty else {"is_valid": False, "warnings": ["Belum ada data pengeluaran."]}

has_valid_data = (not sales_df.empty or not working_expenses_df.empty) and (sales_val.get("is_valid") or expenses_val.get("is_valid"))

if has_valid_data:
    metrics = calculate_pnl_metrics(
        sales_df,
        working_expenses_df,
        start_date=start_date_filter,
        end_date=end_date_filter,
    )
    pnl_df = generate_pnl_summary_dataframe(metrics)
else:
    metrics = None
    pnl_df = pd.DataFrame()

# ----------------- MAIN HEADER -----------------
st.title("🍜 Lokality AI Financial Recap & PnL Copilot")
if metrics is not None:
    st.markdown(
        f"Sistem Rekapitulasi Keuangan & Laporan Laba Rugi Deterministik **{COMPANY_NAME}** "
        f"| **Periode Aktif:** `{metrics['period']['label']}`"
    )
else:
    st.markdown(f"Sistem Rekapitulasi Keuangan & Laporan Laba Rugi Deterministik **{COMPANY_NAME}**")

tab1, tab2, tab3 = st.tabs([
    "📋 1. Data & Koreksi Kategori (Human-in-the-Loop)",
    "📊 2. Laporan PnL & Drill-Down Keterlacakan",
    "🤖 3. AI Financial Copilot",
])

# ----------------- TAB 1: DATA & HUMAN-IN-THE-LOOP -----------------
with tab1:
    st.subheader("Rekapitulasi Transaksi & Peninjauan Kategori Akun")

    if metrics is not None:
        s = metrics["summary"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Transaksi Penjualan (Terfilter)", f"{metrics['row_counts']['sales_count']} Invoice")
        c2.metric("Volume Produk Terjual", f"{s['total_sales_qty']:,} Pack".replace(",", "."))
        c3.metric("Pos Pengeluaran (Terfilter)", f"{metrics['row_counts']['expenses_count']} Baris")
        c4.metric("Koreksi Kategori Manual", f"{s['manual_overrides_count']} Baris")

        for w in sales_val.get("warnings", []):
            st.warning(f"Validasi Penjualan: {w}")
        for w in expenses_val.get("warnings", []):
            st.warning(f"Validasi Pengeluaran: {w}")

        st.divider()
        col_head, col_reset = st.columns([4, 1])
        with col_head:
            st.markdown("#### 💸 Tabel Belanja & Koreksi Kategori (*Human-in-the-Loop Review*)")
            st.caption(
                "Pengelola data dapat memeriksa dan mengubah kolom **Tipe Akun PnL (`tipe_akun`)** secara langsung sebelum draf PnL disahkan. "
                "Setiap perubahan otomatis memperbarui perhitungan HPP, OPEX, dan Laba Bersih secara deterministik."
            )
        with col_reset:
            if st.button("🔄 Reset Kategori Default", width="stretch"):
                st.session_state.working_expenses_df = apply_auto_categorization(raw_expenses_df)
                st.rerun()

        edited_df = st.data_editor(
            working_expenses_df,
            column_config={
                "tipe_akun": st.column_config.SelectboxColumn(
                    "Tipe Akun PnL (Dapat Dikoreksi)",
                    help="Pilih kategori akun HPP atau OPEX yang sesuai",
                    options=VALID_ACCOUNT_CODES,
                    required=True,
                ),
                "sumber_kategori": st.column_config.TextColumn(
                    "Status Verifikasi",
                    disabled=True,
                ),
                "total_biaya": st.column_config.NumberColumn(
                    "Total Biaya (Rp)",
                    format="Rp %d",
                    disabled=True,
                ),
                "harga_satuan": st.column_config.NumberColumn(
                    "Harga Satuan (Rp)",
                    format="Rp %d",
                    disabled=True,
                ),
            },
            disabled=[c for c in working_expenses_df.columns if c != "tipe_akun"],
            width="stretch",
            key="expense_category_editor",
        )

        # Detect manual edits & update state immediately (dtype-safe string list check)
        if edited_df["tipe_akun"].astype(str).tolist() != working_expenses_df["tipe_akun"].astype(str).tolist():
            updated = edited_df.copy()
            changed_mask = updated["tipe_akun"].astype(str) != working_expenses_df["tipe_akun"].astype(str)
            updated.loc[changed_mask, "sumber_kategori"] = "Koreksi Manual"
            st.session_state.working_expenses_df = updated
            st.rerun()

        with st.expander("📖 Keterangan Kamus Kode Akun PnL"):
            acc_ref = pd.DataFrame(
                [{"Kode Akun": k, "Deskripsi Komponen Laporan": v} for k, v in ACCOUNT_TYPES.items()]
            )
            st.dataframe(acc_ref, width="stretch", hide_index=True)

        st.divider()
        st.markdown("#### 🛒 Tabel Rekap Penjualan (*Income*)")
        if start_date_filter is not None or end_date_filter is not None:
            st.dataframe(pd.DataFrame(metrics["sales_items_detail"]), width="stretch", hide_index=True)
        else:
            st.dataframe(sales_df, width="stretch", hide_index=True)
    else:
        st.warning("Silakan muat berkas data penjualan dan pengeluaran terlebih dahulu melalui bilah sisi kiri.")

# ----------------- TAB 2: LAPORAN PNL & DRILL-DOWN TRACEABILITY -----------------
with tab2:
    st.subheader("Draf Laporan Laba Rugi (PnL) & Keterlacakan Transaksi")

    if metrics is not None:
        s = metrics["summary"]

        # Completeness Status Banner
        if s["is_complete_for_pnl"]:
            st.success(
                f"✅ **Kelengkapan Data Memadai ({metrics['period']['label']}):** "
                "Komponen Pendapatan, HPP Bahan Baku, dan Beban Operasional lengkap dan siap ditinjau manajemen."
            )
        else:
            warn_items = "\n".join([f"- {w}" for w in metrics["completeness_warnings"]])
            st.warning(
                f"⚠️ **Penanda Data Belum Memadai untuk Laporan PnL Lengkap ({metrics['period']['label']}):**\n{warn_items}"
            )

        # KPI Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Pendapatan (Revenue)", format_rupiah(s["total_revenue"]))
        hpp_pct_str = f"-{(s['total_hpp'] / s['total_revenue'] * 100):.2f}% dr Revenue" if s["total_revenue"] > 0 else "0%"
        kpi2.metric("Total HPP (COGS)", format_rupiah(s["total_hpp"]), hpp_pct_str, delta_color="inverse")
        kpi3.metric("Laba Kotor (Gross Profit)", format_rupiah(s["gross_profit"]), f"Gross Margin: {s['gross_margin_pct']}%")
        kpi4.metric("Laba Bersih Operasional", format_rupiah(s["net_profit"]), f"Net Margin: {s['net_margin_pct']}%")

        st.markdown(
            f"""<div class="audit-box">
            <strong>Rumus Verifikasi Deterministik:</strong><br/>
            • <strong>Laba Kotor:</strong> <code>{metrics['formulas']['gross_profit']}</code><br/>
            • <strong>Laba Bersih Operasional:</strong> <code>{metrics['formulas']['net_profit']}</code>
            </div>""",
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("#### 📑 Tabel Draf Laporan Laba Rugi (PnL)")
            st.dataframe(
                pnl_df[["Kode Akun", "Komponen Laporan Keuangan", "Format Rupiah", "% Terhadap Revenue"]],
                width="stretch",
                hide_index=True,
            )

            csv_export = pnl_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Unduh Draf Laporan PnL (.CSV)",
                data=csv_export,
                file_name=f"pnl_lokality_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col_right:
            st.markdown("#### 📈 Proporsi Komponen Biaya (HPP & OPEX)")
            cost_items = {**metrics["hpp_breakdown"], **metrics["opex_breakdown"]}
            cost_df = pd.DataFrame(
                [{"Kategori Biaya": k, "Nominal": v} for k, v in cost_items.items() if v > 0]
            )
            if not cost_df.empty:
                cost_df = cost_df.sort_values("Nominal", ascending=False)
                st.bar_chart(cost_df.set_index("Kategori Biaya"))
            else:
                st.info("Tidak ada biaya tercatat pada periode ini.")

            st.markdown("#### 🎯 Pendapatan per Saluran Penjualan")
            channel_df = pd.DataFrame(
                [
                    {"Saluran Penjualan": k, "Pendapatan": format_rupiah(v)}
                    for k, v in sorted(metrics["sales_by_channel"].items(), key=lambda x: x[1], reverse=True)
                ]
            )
            if not channel_df.empty:
                st.dataframe(channel_df, width="stretch", hide_index=True)

        st.divider()
        st.markdown("#### 🔍 Drill-Down Keterlacakan Angka PnL ke Transaksi Sumber (*Audit Trail*)")
        st.caption("Pilih komponen laporan untuk memeriksa daftar transaksi asli pembentuk nominal pada laporan PnL.")

        trace_map = metrics["traceability_map"]
        trace_options = list(trace_map.keys())
        selected_trace_key = st.selectbox(
            "Pilih Komponen Akun PnL untuk Ditelusuri:",
            options=trace_options,
            format_func=lambda k: f"{trace_map[k]['label']} — {format_rupiah(trace_map[k]['total'])} ({trace_map[k]['jumlah_transaksi']} transaksi)",
        )

        trace_detail = trace_map[selected_trace_key]
        st.info(
            f"**Aturan Perhitungan:** {trace_detail['aturan_hitung']}  \n"
            f"**Subtotal Terverifikasi:** **{format_rupiah(trace_detail['total'])}** dari **{trace_detail['jumlah_transaksi']} baris transaksi sumber**."
        )
        if trace_detail["records"]:
            st.dataframe(pd.DataFrame(trace_detail["records"]), width="stretch", hide_index=True)
        else:
            st.caption("Tidak ada baris transaksi untuk akun ini pada periode yang dipilih.")
    else:
        st.info("Laporan laba rugi akan tampil setelah data transaksi dimuat.")

# ----------------- TAB 3: AI FINANCIAL COPILOT -----------------
with tab3:
    st.subheader("🤖 AI Financial Copilot & Analitik Percakapan")

    if metrics is not None:
        narrative_sig = f"{metrics['period']['label']}_{metrics['summary']['net_profit']}_{quota_mgr.ai_enabled}"
        if st.session_state.get("narrative_sig") != narrative_sig:
            st.session_state.narrative_sig = narrative_sig
            st.session_state.narrative = generate_pnl_narrative(metrics, quota_manager=quota_mgr)

        with st.expander("📄 Ringkasan Eksekutif Finansial (AI Insight)", expanded=True):
            st.markdown(st.session_state.narrative)
            if st.button("🔄 Segarkan Ringkasan Eksekutif"):
                with st.spinner("Menyusun ulang analisis keuangan..."):
                    st.session_state.narrative = generate_pnl_narrative(metrics, quota_manager=quota_mgr)
                    st.rerun()

        st.divider()
        st.markdown("#### 💬 Tanya Jawab Analitik Data Keuangan")
        st.caption(
            "Tanyakan rincian biaya bahan baku spesifik (mocaf, tempe, beras), perbandingan margin, atau saluran penjualan. "
            "Seluruh angka merujuk langsung pada data terverifikasi beserta kode transaksi sumber."
        )

        st.markdown("**Pertanyaan Cepat:**")
        q_cols = st.columns(3)
        sample_questions = [
            "Berapa total belanja mocaf dan tempe?",
            "Bagaimana perbandingan laba kotor dan laba bersih?",
            "Apa pos beban operasional yang paling besar?",
        ]

        clicked_prompt = None
        for i, sq in enumerate(sample_questions):
            if q_cols[i].button(sq, key=f"q_btn_{i}", width="stretch"):
                clicked_prompt = sq

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        f"Halo! Saya **Financial Copilot {BRAND_NAME}**. "
                        "Silakan ajukan pertanyaan mengenai rincian belanja bahan baku mi gluten-free, "
                        "performa saluran penjualan, atau laporan PnL pada periode aktif."
                    ),
                }
            ]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ketik pertanyaan seputar keuangan Lokality...")
        query_to_process = clicked_prompt if clicked_prompt else user_input

        if query_to_process:
            st.session_state.messages.append({"role": "user", "content": query_to_process})
            with st.chat_message("user"):
                st.markdown(query_to_process)

            with st.chat_message("assistant"):
                with st.spinner("Menelusuri data transaksi & metrik PnL..."):
                    response_text = ask_financial_copilot(
                        query_to_process,
                        metrics,
                        st.session_state.messages,
                        quota_manager=quota_mgr,
                    )
                    st.markdown(response_text)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
    else:
        st.info("Silakan muat data terlebih dahulu untuk mengaktifkan AI Financial Copilot.")
