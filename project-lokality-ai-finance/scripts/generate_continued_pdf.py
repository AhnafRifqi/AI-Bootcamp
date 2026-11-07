"""Generator PDF Lanjutan Resmi: Menggabungkan Halaman 1-10 asli (IT Helpdesk Agent)
dengan seluruh folder modul di workspace AI-Bootcamp serta 5 Dokumen Resmi Capstone
PT Lokal Komoditi Indonesia (Lokality: BRD, Blueprint, Testing Report, Technical Docs, User Guide).
"""

import io
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import pypdf
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(r"d:\Rework Academy\Praktek\AI-Bootcamp")
PROJECT_DIR = WORKSPACE_DIR / "project-lokality-ai-finance"
DIAGRAMS_DIR = PROJECT_DIR / "docs" / "diagrams"
PIPELINE_DIAGRAM = WORKSPACE_DIR / "assignment-data-pipeline-AhnafRifqi" / "documentation" / "data-flow-diagram.png"

SOURCE_PDF = Path(
    r"C:\Users\USER\.gemini\antigravity\brain\e7425277-7c43-45bf-9724-82464a72d1ea\.user_uploaded\media_1794076640814_1dcda86f.pdf"
)
ARTIFACT_PDF_OUT = Path(
    r"C:\Users\USER\.gemini\antigravity\brain\e7425277-7c43-45bf-9724-82464a72d1ea\ai-bootcamp-dokumentasi-lengkap.pdf"
)
WORKSPACE_PDF_OUT = WORKSPACE_DIR / "ai-bootcamp-dokumentasi-lengkap.pdf"
PROJECT_PDF_OUT = PROJECT_DIR / "docs" / "Dokumen_Resmi_Lokality_dan_AI_Bootcamp.pdf"

PAGE_W, PAGE_H = A4  # 595.2756 x 841.8898 pt
MARGIN = 62.36       # 2.2 cm — persis sama dengan halaman 1-10
CONTENT_W = PAGE_W - 2 * MARGIN  # ~470.55 pt


def build_styles():
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=15.0,
            leading=19.0,
            textColor=colors.HexColor("#111111"),
            spaceAfter=3,
        ),
        "doc_subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=14.0,
            textColor=colors.HexColor("#444444"),
            spaceAfter=8,
        ),
        "meta_key": ParagraphStyle(
            "MetaKey",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=9.5,
            leading=13.0,
            textColor=colors.HexColor("#111111"),
        ),
        "meta_val": ParagraphStyle(
            "MetaVal",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=13.0,
            textColor=colors.HexColor("#222222"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=12.5,
            leading=16.5,
            textColor=colors.HexColor("#111111"),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=10.8,
            leading=14.5,
            textColor=colors.HexColor("#111111"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10.3,
            leading=14.6,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1A1A1A"),
            spaceAfter=6,
        ),
        "query_line": ParagraphStyle(
            "QueryLine",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=13.2,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#333333"),
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.2,
            leading=11.4,
            textColor=colors.HexColor("#1F2937"),
        ),
        "result_italic": ParagraphStyle(
            "ResultItalic",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=9.4,
            leading=13.0,
            textColor=colors.HexColor("#4B5563"),
            spaceBefore=4,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9.0,
            leading=12.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceBefore=5,
            spaceAfter=10,
        ),
        "tbl_hdr": ParagraphStyle(
            "TblHdr",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=9.2,
            leading=12.4,
            textColor=colors.white,
        ),
        "tbl_cell": ParagraphStyle(
            "TblCell",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9.0,
            leading=12.4,
            textColor=colors.HexColor("#1A1A1A"),
        ),
        "tbl_cell_bold": ParagraphStyle(
            "TblCellBold",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=9.0,
            leading=12.4,
            textColor=colors.HexColor("#111111"),
        ),
        "footer_note": ParagraphStyle(
            "FooterNote",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=8.6,
            leading=12.0,
            textColor=colors.HexColor("#666666"),
            spaceBefore=6,
        ),
    }


ST = build_styles()


def add_header_block(story, title: str, subtitle: str, meta_rows: list[tuple[str, str]]):
    story.append(Paragraph(title, ST["doc_title"]))
    story.append(Paragraph(subtitle, ST["doc_subtitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#BBBBBB"), spaceBefore=2, spaceAfter=8))

    tbl_data = [
        [Paragraph(escape(k), ST["meta_key"]), Paragraph(escape(v), ST["meta_val"])]
        for k, v in meta_rows
    ]
    tbl = Table(tbl_data, colWidths=[132, CONTENT_W - 132])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E0E0E0")),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 10))


def add_code_box(story, raw_text: str, result_note: str = ""):
    wrapped_lines = []
    for line in raw_text.strip("\n").splitlines():
        if len(line) <= 84:
            wrapped_lines.append(line)
        else:
            sub = textwrap.wrap(line, width=84, subsequent_indent="    ")
            wrapped_lines.extend(sub if sub else [""])
    formatted = "\n".join(wrapped_lines)
    pre = Preformatted(formatted, ST["code"])
    box = Table([[pre]], colWidths=[CONTENT_W])
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F6F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    items = [box]
    if result_note:
        items.append(Paragraph(escape(result_note), ST["result_italic"]))
    else:
        items.append(Spacer(1, 6))
    story.append(KeepTogether(items))


def add_matrix_table(story, headers: list[str], rows: list[list[str]], col_widths: list[float], bold_first_col: bool = True):
    data = [[Paragraph(escape(h), ST["tbl_hdr"]) for h in headers]]
    for r in rows:
        row_cells = []
        for idx, cell_text in enumerate(r):
            style = ST["tbl_cell_bold"] if (idx == 0 and bold_first_col) else ST["tbl_cell"]
            html_text = escape(cell_text).replace("\n", "<br/>")
            row_cells.append(Paragraph(html_text, style))
        data.append(row_cells)

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B2B2B")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D2D2D2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5.5),
        ("TOPPADDING", (0, 0), (-1, -1), 5.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.0),
    ]
    for r_i in range(1, len(data)):
        bg = colors.white if r_i % 2 == 1 else colors.HexColor("#F9F9F9")
        cmds.append(("BACKGROUND", (0, r_i), (-1, r_i), bg))
    tbl.setStyle(TableStyle(cmds))
    story.append(tbl)
    story.append(Spacer(1, 9))


def add_figure(story, img_path: Path, caption: str, max_w: float = CONTENT_W, max_h: float = 290.0):
    if not img_path.exists():
        return
    with PILImage.open(img_path) as im:
        w_px, h_px = im.size
    scale = min(max_w / w_px, max_h / h_px)
    draw_w = w_px * scale
    draw_h = h_px * scale

    img_flow = Image(str(img_path), width=draw_w, height=draw_h)
    framed = Table([[img_flow]], colWidths=[draw_w + 8])
    framed.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    framed.hAlign = "CENTER"
    story.append(KeepTogether([Spacer(1, 4), framed, Paragraph(escape(caption), ST["caption"])]))


def add_section_footer(story, text: str):
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceBefore=2, spaceAfter=4))
    story.append(Paragraph(escape(text), ST["footer_note"]))


def build_continuation_story() -> list:
    story = []

    # =========================================================================
    # BAGIAN LANJUTAN I: PETA EKOSISTEM WORKSPACE AI-BOOTCAMP & MODUL 1, 2, 3, 5
    # =========================================================================
    add_header_block(
        story,
        "Dokumentasi Terpadu Ekosistem Proyek AI Engineering Bootcamp",
        "Lanjutan Dokumentasi Resmi — Mencakup Seluruh Folder Modul Pembelajaran & Capstone Studi Kasus Industri",
        [
            ("Ruang kerja utama", r"d:\Rework Academy\Praktek\AI-Bootcamp (6 Folder Proyek Terintegrasi)"),
            ("Halaman 1 s/d 10", "assignment-helpdesk-agent-AhnafRifqi — IT Helpdesk Assistant AI System (Telah Terdokumentasi)"),
            ("Halaman Lanjutan", "Modul Data Pipeline, Model Experiment, Semantic Search, AI Evaluation & Capstone Lokality (LKI-01)"),
            ("Penyusun", "Ahnaf Rifqi — Program AI Engineering Bootcamp"),
            ("Status verifikasi", "Seluruh modul lulus verifikasi otomatis & sinkron dengan kode aktual repository"),
        ],
    )

    story.append(Paragraph("1. Peta Keseluruhan Folder Proyek dalam Workspace AI-Bootcamp", ST["h1"]))
    story.append(
        Paragraph(
            "Dokumen induk ini mengonsolidasikan bukti rekayasa, arsitektur, pengujian, dan panduan operasional dari seluruh "
            "enam folder proyek di dalam ruang kerja <b>AI-Bootcamp</b>. Halaman 1 hingga 10 di awal berkas ini menyajikan "
            "pengujian <i>black-box end-to-end</i> untuk sistem <b>IT Helpdesk Assistant</b>, sedangkan bagian lanjutan ini "
            "mendokumentasikan empat modul fondasi lainnya beserta paket lengkap lima dokumen resmi <b>Capstone Business Project "
            "PT Lokal Komoditi Indonesia (Lokality)</b>.",
            ST["body"],
        )
    )

    add_matrix_table(
        story,
        ["No", "Nama Folder Proyek", "Fokus Rekayasa Sistem", "Metrik Kunci Terverifikasi"],
        [
            ["1", "assignment-data-pipeline-AhnafRifqi", "Pipeline ETL Otomotif (Pandas & NumPy)", "205 -> 200 baris, 30 -> 36 kolom, Min-Max & One-Hot"],
            ["2", "assignment-AI-Model-Experiment-AhnafRifqi", "Komparasi Sentimen: Klasik ML vs Gemini Zero-Shot", "StratifiedGroupKFold bebas bocor; Akurasi 0,6250 & Cache LLM"],
            ["3", "assignment-semantic-search-AhnafRifqi", "Semantic Search FAISS (3072-dim) & Grounded FAQ LLM", "59 entri FAQ; Top-1 Accuracy 5/5 (100%); 0 halusinasi"],
            ["4", "assignment-helpdesk-agent-AhnafRifqi", "FastAPI RAG + Intent Router + Deterministic Ticket Tool", "10/10 skenario Swagger UI lulus (Tercakup pada Hal. 1-10)"],
            ["5", "assignment-ai-evaluation-AhnafRifqi", "Evaluasi 12 Skenario, Safety Audit & Optimasi Latency", "Hybrid router fix; Latency EVAL-11 turun 7,37s -> 2,14s (-71%)"],
            ["6", "project-lokality-ai-finance", "Capstone LKI-01: AI Financial Recap & PnL Copilot", "18/18 pytest PASS; Revenue Rp 46,875 jt; Laba Bersih Rp 8,575 jt"],
        ],
        [22, 174, 138, CONTENT_W - 334],
    )

    # --- MODUL 1: DATA PIPELINE ---
    story.append(Paragraph("2. Modul 1 — Automated Data Pipeline ETL (assignment-data-pipeline-AhnafRifqi)", ST["h1"]))
    story.append(
        Paragraph(
            "Modul pertama membangun fondasi rekayasa data melalui pipeline <i>Extract-Transform-Load</i> (ETL) deterministik "
            "pada berkas <b>src/pipeline.py</b> untuk membersihkan dataset mentah <b>automobileEDA_dirty_training.csv</b> "
            "(205 baris, 30 kolom, 17 sel kosong, 4 baris duplikat identik, serta 4 format tanggal berbeda yang tercampur) "
            "tanpa menimpa berkas sumber di <b>data/raw/</b>.",
            ST["body"],
        )
    )

    add_figure(
        story,
        PIPELINE_DIAGRAM,
        "Gambar 11. Diagram Alur Data (Data Flow Diagram) Pipeline ETL Otomotif.",
        max_w=CONTENT_W - 10,
        max_h=150,
    )

    add_matrix_table(
        story,
        ["Tahap / Masalah Data", "Kolom Sasaran", "Metode Perbaikan & Transformasi", "Hasil Terukur"],
        [
            ["Deduplikasi & Identitas", "Seluruh baris & make", "drop_duplicates() + hapus baris make kosong", "205 -> 200 baris bersih (-4 duplikat, -1 tanpa merek)"],
            ["Standardisasi Kategori", "make, body-style, drive-wheels, fuel-system", ".str.strip().str.lower() + pemetaan semantik awd -> 4wd", "Kategori seragam tanpa duplikasi ejaan huruf besar/spasi"],
            ["Harmonisasi Tanggal", "transaction_date", "Multi-format parser ke YYYY-MM-DD; 2 NaT dipertahankan", "4 format tanggal berbeda diseragamkan tanpa membuang fitur"],
            ["Imputasi & Re-binning", "num-of-doors, stroke, horsepower, price", "Modus ('four'), median numerik, & pd.cut() 3-bin ulang", "Missing value turun dari 17 sel menjadi 2 sel metadata"],
            ["Feature Engineering", "horsepower & body-style", "Min-Max Scaling [0..1] + One-Hot Encoding 5 kategori", "Dimensi bertambah dari 30 kolom menjadi 36 kolom siap ML"],
        ],
        [98, 102, 145, CONTENT_W - 345],
    )

    add_code_box(
        story,
        "$ python src/pipeline.py\n"
        "[EXTRACT] Loaded data/raw/automobileEDA_dirty_training.csv -> shape=(205, 30)\n"
        "[CLEAN]   Removed 4 exact duplicates & 1 missing 'make' -> shape=(200, 30), missing=2 (transaction_date)\n"
        "[TRANS]   Added horsepower-normalized + 5 body-style one-hot columns -> shape=(200, 36)\n"
        "[LOAD]    Saved data/processed/automobileEDA_processed.csv",
        "Hasil: Pipeline idempoten berhasil menyimpan dataset bersih (200 baris x 36 kolom).",
    )

    # --- MODUL 2: AI MODEL EXPERIMENT ---
    story.append(Paragraph("3. Modul 2 — Eksperimen Model Klasik vs LLM API (assignment-AI-Model-Experiment-AhnafRifqi)", ST["h1"]))
    story.append(
        Paragraph(
            "Modul kedua mengevaluasi klasifikasi sentimen ulasan pelanggan e-commerce berbahasa Indonesia (<b>positif</b> vs "
            "<b>negatif</b>) pada <b>customer_reviews_sentiment.csv</b> (200 baris; 110 positif, 90 negatif; terdiri atas 40 teks "
            "ulasan unik). Temuan metodologis terpenting pada eksperimen ini adalah pencegahan <b>kebocoran data (data leakage)</b>: "
            "pembagian acak per baris menaruh 39/40 baris uji di data latih dan menghasilkan akurasi semu 100%. Oleh karena itu, "
            "eksperimen menerapkan <b>StratifiedGroupKFold</b> berbasis grup <b>review_text</b> (160 latih / 40 uji, 8 teks unik di set uji).",
            ST["body"],
        )
    )

    add_matrix_table(
        story,
        ["Aspek Pembanding", "Model Klasik (TF-IDF + LogisticRegression)", "LLM API (Gemini 2.5 Flash Zero-Shot)"],
        [
            ["Konfigurasi Teknis", "TfidfVectorizer + LogisticRegression(max_iter=1000)", "Prompt zero-shot 1 kata, temperature=0.2, deduplikasi 8 teks unik"],
            ["Metrik Evaluasi Uji", "Accuracy: 0,6250 | Precision: 0,6278 | Recall: 0,6288 | Macro-F1: 0,6248", "Arsitektur resume-cache (llm_predictions.csv) hemat kuota ~5x"],
            ["Confusion Matrix", "[[12, 6], [9, 13]] (25/40 tepat; 15 salah pada teks baru)", "Menolak kesimpulan prematur dari cache parsial (3/8 saat limit 429)"],
            ["Karakteristik Operasional", "Inferensi lokal < 5 ms, 0 biaya API, perlu data latih besar", "Tanpa training awal, namun bergantung jaringan & rate-limit kuota"],
        ],
        [105, 182, CONTENT_W - 287],
    )

    # --- MODUL 3: SEMANTIC SEARCH ---
    story.append(Paragraph("4. Modul 3 — Semantic Search & Grounded FAQ LLM (assignment-semantic-search-AhnafRifqi)", ST["h1"]))
    story.append(
        Paragraph(
            "Modul ketiga membangun purwarupa layanan pelanggan e-commerce berbasis pencarian makna (<i>semantic similarity</i>) "
            "atas <b>59 entri FAQ</b> lintas 8 kategori. Vektor dibangkitkan menggunakan <b>gemini-embedding-001</b> (dimensi 3072, "
            "dinormalisasi L2) pada indeks <b>FAISS IndexFlatL2</b>, lalu disuntikkan ke <b>gemini-flash-latest</b> dengan struktur "
            "prompt empat blok: <b>[PERSONA]</b>, <b>[TASK]</b> (wajib hanya dari konteks), <b>[CONTEXT]</b>, dan <b>[FORMAT]</b>.",
            ST["body"],
        )
    )

    add_matrix_table(
        story,
        ["#", "Tipe Uji", "Kueri Pelanggan", "Top-1 & Skor", "Perilaku Jawaban Sistem"],
        [
            ["1", "Eksplisit", "cara melacak paket yang sedang dikirim", "FAQ 10 (0,89)", "Akurat merujuk prosedur pelacakan pesanan"],
            ["2", "Eksplisit", "berapa lama proses refund disetujui", "FAQ 25 (0,92)", "Akurat menyebut estimasi SLA pengembalian dana"],
            ["3", "Parafrase", "uang sudah kepotong tapi status belum terbayar", "FAQ 21 (0,91)", "Memahami bahasa percakapan tanpa kata kunci persis"],
            ["4", "Parafrase", "barangku belum nyampe, udah lewat seminggu", "FAQ 12 (0,85)", "Tepat memetakan keluhan keterlambatan kurir"],
            ["5", "Parafrase", "boleh nggak dicicil per bulan?", "FAQ 20 (0,85)", "Tepat memetakan opsi pembayaran cicilan"],
            ["6", "Luar KB", "pembayaran mata uang kripto / Bitcoin", "FAQ 17 (0,71)", "Jujur menyatakan tidak tersedia & arahkan ke CS"],
        ],
        [18, 56, 162, 74, CONTENT_W - 310],
    )

    # --- MODUL 5: AI SYSTEM EVALUATION & OPTIMIZATION ---
    story.append(Paragraph("5. Modul 5 — Evaluasi, Safety Guardrails & Optimasi Sistem AI (assignment-ai-evaluation-AhnafRifqi)", ST["h1"]))
    story.append(
        Paragraph(
            "Melanjutkan sistem <b>IT Helpdesk Assistant</b> pada Halaman 1–10, modul kelima menjalankan pengujian terotomatisasi "
            "(<b>evaluate.py</b>) atas 12 skenario standar (<b>EVAL-01</b> s/d <b>EVAL-12</b>), audit ketahanan keamanan 4 pilar "
            "(<i>Instruction Override</i>, <i>Information Boundary</i>, <i>Scope Consistency</i>, dan <i>Malformed Input</i>), "
            "serta pembuktian optimasi <i>Before vs After</i> berbasis telemetri nyata.",
            ST["body"],
        )
    )

    add_matrix_table(
        story,
        ["Fokus Optimasi", "Kondisi Sebelum (Baseline)", "Tindakan Rekayasa Kode", "Bukti Sesudah (Terverifikasi)"],
        [
            [
                "Isu 1: Routing Ambigu (EVAL-09: laptop lambat + cek tiket)",
                "Router melempar error 'ID tiket tidak ditemukan' dan mengabaikan masalah teknis laptop.",
                "Menambahkan deteksi intent 'hybrid' di router.py yang menggabungkan solusi RAG FAQ + panduan format tiket.",
                "Status berubah menjadi [hybrid|success]; kedua kebutuhan karyawan terjawab utuh dalam satu respons.",
            ],
            [
                "Isu 2: Bottleneck Latency & Token pada Kueri Berat (EVAL-11)",
                "Latency mencapai 7,37 detik dengan konsumsi ~407 token akibat internal thinking bawaan.",
                "Menyetel ThinkingConfig(thinking_budget=0), max_output_tokens=1000, temperature=0.2, & conciseness prompt di rag.py.",
                "Latency turun ke 2,14 detik (-71%) dan konsumsi token turun ke ~226 token (-44,5%).",
            ],
        ],
        [105, 115, 130, CONTENT_W - 350],
    )

    add_section_footer(
        story,
        "Rekapitulasi Modul 1, 2, 3, 4 (Hal. 1-10), dan 5 tuntas. Halaman berikutnya menyajikan Paket 5 Dokumen Resmi Capstone Lokality (LKI-01).",
    )
    story.append(PageBreak())

    # =========================================================================
    # BAGIAN LANJUTAN II — DOKUMEN RESMI 1: BUSINESS REQUIREMENT DOCUMENT (BRD)
    # =========================================================================
    add_header_block(
        story,
        "Dokumen Resmi 1 — Business Requirement Document (BRD)",
        "Lokality AI Financial Recap & PnL Copilot — Studi Kasus PT Lokal Komoditi Indonesia (Kasus ID: LKI-01)",
        [
            ("Nama proyek", "Lokality AI Financial Recap & PnL Copilot"),
            ("Mitra studi kasus", "PT Lokal Komoditi Indonesia (Lokality) — Manufaktur Mi Gluten-Free Berbasis Komoditas Lokal"),
            ("Penyusun & versi", "Ahnaf Rifqi (Tim AI Engineering Batch 1) — Versi 1.1 (08 November 2026)"),
            ("Fokus solusi", "Otomasi Rekap Penjualan/Belanja, Kategorisasi HPP/OPEX (HITL), Draf PnL Audit & AI Copilot"),
            ("Status dokumen", "Disetujui & Sinkron 100% dengan Implementasi Aplikasi v1.1.0"),
        ],
    )

    story.append(Paragraph("1.1 Pernyataan Masalah Bisnis (Problem Statement)", ST["h1"]))
    add_matrix_table(
        story,
        ["Dimensi Analisis", "Uraian Fakta Operasional & Kebutuhan Mitra Lokality"],
        [
            [
                "Kondisi Saat Ini (As-Is)",
                "PT Lokal Komoditi Indonesia (Lokality) memproduksi mi gluten-free berbahan tepung mocaf, tepung beras, dan tepung jagung dengan fortifikasi tempe. Operasional harian menghasilkan catatan penjualan (income) lintas kanal serta pembelian bahan baku dan biaya pabrik (cash out). Tim internal telah terbiasa memakai ChatGPT untuk ide perencanaan umum, namun pencatatan keuangan bulanan masih terpisah dan direkap manual.",
            ],
            [
                "Masalah Utama",
                "Proses penggabungan data penjualan, belanja bahan baku, dan pengeluaran operasional memakan waktu lama, belum memiliki pemetaan baku antara Harga Pokok Penjualan (HPP) dan Beban Operasional (OPEX), serta menyulitkan penyusunan draf Laporan Laba Rugi (PnL) bulanan yang konsisten.",
            ],
            [
                "Dampak Bisnis",
                "Manajemen dan pemilik usaha tidak dapat segera melihat posisi laba kotor, laba bersih operasional, serta proporsi biaya bahan baku utama (mocaf, tempe, beras, kemasan) setiap bulan, sehingga keputusan penyesuaian harga maupun efisiensi produksi tertunda.",
            ],
            [
                "Item Klarifikasi Lanjutan",
                "1) Format berkas asli dari PIC Lokality (apakah seratus persen spreadsheet CSV/Excel atau disertai foto nota fisik).\n2) Kebijakan tanggal cut-off tutup buku bulanan serta metode pencatatan penyusutan peralatan pabrik.",
            ],
        ],
        [115, CONTENT_W - 115],
    )

    story.append(Paragraph("1.2 Pengguna Sasaran (Target Users) & Kebutuhan Pengguna (User Needs)", ST["h1"]))
    add_matrix_table(
        story,
        ["Peran Pengguna", "Tanggung Jawab Operasional", "Kebutuhan Fungsional Utama"],
        [
            [
                "Pengelola Data\n(Admin Keuangan / Staf Operasional)",
                "Mengunggah, memvalidasi, dan merapikan catatan transaksi penjualan serta pengeluaran bulanan.",
                "Unggah CSV/Excel yang toleran terhadap format penulisan Rupiah, filter periode tanggal/bulan, auto-kategorisasi biaya, dan tabel interaktif Human-in-the-Loop (HITL) untuk mengoreksi tipe akun.",
            ],
            [
                "Peninjau Hasil\n(Pemilik Usaha / Manajemen)",
                "Meninjau kesehatan laba rugi bulanan dan mengevaluasi efisiensi biaya produksi serta kanal penjualan.",
                "Draf PnL deterministik yang akurat 100%, banner kelengkapan data, drill-down keterlacakan angka ke baris sumber, ringkasan eksekutif AI, dan chatbot rincian item belanja.",
            ],
        ],
        [115, 145, CONTENT_W - 260],
    )

    add_matrix_table(
        story,
        ["ID", "Kebutuhan Pengguna", "Alasan Bisnis", "Target Keberhasilan Terukur"],
        [
            ["UN-01", "Rekap & filter transaksi berdasarkan bulan atau rentang tanggal", "Evaluasi performa paruh bulan maupun bulanan penuh", "Pembaruan rekap, PnL, dan konteks AI < 2 detik"],
            ["UN-02", "Auto-kategorisasi HPP/OPEX disertai koreksi manual (HITL)", "Mencegah salah pos akun sebelum laporan dipakai manajemen", "Setiap koreksi manual langsung menghitung ulang HPP & OPEX"],
            ["UN-03", "Draf PnL deterministik + cek kelengkapan + drill-down audit", "Angka keuangan wajib bebas halusinasi & terlacak ke sumber", "Selisih Rp 0 pada seluruh 8 kode akun terhadap baris sumber"],
            ["UN-04", "Narasi eksekutif & tanya-jawab rincian item (mocaf, tempe, dll.)", "Memanfaatkan kebiasaan percakapan alami namun terikat fakta", "Menjawab kode [EXP-xxx], nominal per item, & subtotal presisi"],
            ["UN-05", "Kontrol kuota sesi, cache jawaban, & saklar on/off AI", "Mengendalikan biaya API dan menjamin aplikasi jalan saat offline", "Cache 0 token; saat AI mati otomatis fallback deterministik"],
        ],
        [42, 138, 135, CONTENT_W - 315],
    )

    story.append(Paragraph("1.3 Ruang Lingkup (Project Scope), Use Cases & Kriteria Keberhasilan", ST["h1"]))
    add_matrix_table(
        story,
        ["Termasuk Ruang Lingkup (In-Scope)", "Di Luar Ruang Lingkup (Out-of-Scope)", "Batasan & Dependensi"],
        [
            [
                "- Ingestion & normalisasi CSV/Excel penjualan & belanja.\n"
                "- Filter Semua Periode, Per Bulan, & Rentang Tanggal.\n"
                "- Auto-kategorisasi 7 sub-akun + tabel koreksi HITL.\n"
                "- Mesin PnL deterministik, banner kelengkapan data, drill-down audit, & ekspor CSV.\n"
                "- AI Copilot rincian item + Guardrails + AIQuotaManager.",
                "- Integrasi mutasi bank otomatis (Open Banking).\n"
                "- Pelaporan perpajakan e-Faktur / SPT PPh Badan.\n"
                "- Sistem kasir POS & stok gudang real-time.\n"
                "- Ekstraksi OCR nota kertas (menunggu konfirmasi berkas fisik dari PIC).",
                "- GEMINI_API_KEY disimpan lokal pada berkas .env.\n"
                "- Verifikasi saat ini memakai dataset simulasi representatif Lokality sembari menunggu serah-terima data riil PIC.",
            ]
        ],
        [170, 155, CONTENT_W - 325],
        bold_first_col=False,
    )

    add_matrix_table(
        story,
        ["Kode", "Use Case Utama / Kriteria Keberhasilan", "Metode Pengukuran & Target"],
        [
            ["UC-01", "Rekap Periode & Koreksi Kategori (Human-in-the-Loop) oleh Pengelola Data", "Perubahan tipe_akun di Tab 1 menandai 'Koreksi Manual' & memperbarui PnL"],
            ["UC-02", "Peninjauan Draf PnL, Kelengkapan Data & Drill-Down Audit oleh Manajemen", "Pemilihan akun di Tab 2 menampilkan baris sumber tepat sama dengan nilai PnL"],
            ["UC-03", "Konsultasi Rincian Item Belanja & Margin melalui AI Financial Copilot", "Kueri mocaf & tempe merinci [EXP-001] Rp 7 jt + [EXP-004] Rp 2,4 jt = Rp 9,4 jt"],
            ["UC-04", "Pengendalian Kuota Sesi & Saklar AI oleh Admin", "Saklar AI dimatikan -> sistem tetap menjawab akurat via mesin lokal"],
            ["SC-01..05", "Kriteria Lulus Akurasi PnL, Traceability, Guardrails & Kuota", "18/18 pengujian otomatis pytest PASS (deviasi numerik Rp 0; blokir injeksi 100%)"],
        ],
        [52, 218, CONTENT_W - 270],
    )

    story.append(PageBreak())

    # =========================================================================
    # BAGIAN LANJUTAN II — DOKUMEN RESMI 2: AI SOLUTION BLUEPRINT & ARCHITECTURE
    # =========================================================================
    add_header_block(
        story,
        "Dokumen Resmi 2 — AI Solution Blueprint & Architecture",
        "Desain Alur Pengguna, Arsitektur Berlapis & Pemilihan Teknologi — Lokality AI Financial Recap & PnL Copilot",
        [
            ("Prinsip arsitektur", "Deterministic Accounting Core (Python/Pandas) + Grounded Generative AI Layer (Gemini 2.5 Flash)"),
            ("Antarmuka pengguna", "Streamlit 1.67 Web Dashboard (Sidebar Kontrol + 3 Tab Operasional & Analitik)"),
            ("Mekanisme kontrol", "Human-in-the-Loop Category Override, Drill-Down Traceability, Guardrails & AIQuotaManager"),
            ("Keterlacakan artefak", "Terpetakan langsung ke kebutuhan UN-01..UN-05 dan modul kode di direktori src/"),
        ],
    )

    story.append(Paragraph("2.1 Diagram Alur Pengguna (User Flow Diagram)", ST["h1"]))
    story.append(
        Paragraph(
            "Alur interaksi dirancang agar staf keuangan dapat memvalidasi berkas transaksi serta mengoreksi pemetaan akun biaya "
            "secara transparan sebelum angka draf Laporan Laba Rugi (PnL) ditinjau oleh manajemen maupun dianalisis oleh asisten AI.",
            ST["body"],
        )
    )

    add_figure(
        story,
        DIAGRAMS_DIR / "user_flow_diagram.png",
        "Gambar 12. User Flow Diagram — Lokality AI Financial Recap & PnL Copilot (v1.1).",
        max_w=CONTENT_W - 6,
        max_h=275,
    )

    story.append(Paragraph("2.2 Arsitektur Teknis Solusi AI (AI Solution Architecture)", ST["h1"]))
    story.append(
        Paragraph(
            "Sistem dipisahkan ke dalam empat lapisan modular. Seluruh penjumlahan pendapatan, HPP, laba kotor, OPEX, dan laba bersih "
            "dihitung secara deterministik oleh <b>pnl_engine.py</b>. Lapisan AI (<b>narrative_generator.py</b> dan <b>chatbot.py</b>) "
            "hanya menerima angka yang telah terverifikasi beserta daftar rincian baris transaksi, dilindungi oleh <b>guardrails.py</b> "
            "dan <b>quota_manager.py</b>.",
            ST["body"],
        )
    )

    add_figure(
        story,
        DIAGRAMS_DIR / "architecture_diagram.png",
        "Gambar 13. AI Solution Architecture Diagram — Pemisahan Deterministic Engine & Grounded AI Layer.",
        max_w=CONTENT_W - 6,
        max_h=285,
    )

    story.append(Paragraph("2.3 Matriks Pemilihan Teknologi & Keterlacakan Komponen", ST["h1"]))
    add_matrix_table(
        story,
        ["Komponen", "Teknologi Terpilih", "Peran dalam Sistem", "Alasan Teknis & Bisnis"],
        [
            ["Frontend Web", "Streamlit 1.67.0", "Sidebar filter/kuota, st.data_editor HITL, kartu KPI, & chat UI", "Interaktif untuk staf non-teknis, mendukung edit tabel langsung & ekspor CSV"],
            ["Accounting Core", "Python 3.14.3 + Pandas 3.1.1", "Pembersihan Rupiah, filter tanggal, agregasi PnL & traceability_map", "Bebas halusinasi angka (akurasi 100%) dan siap rekonsiliasi per baris"],
            ["Model AI", "Google GenAI SDK 3.0.0 (gemini-2.5-flash)", "Ringkasan eksekutif bulanan & Q&A rincian item terikat konteks", "Latensi rendah, bahasa bisnis Indonesia natural, & hemat kuota"],
            ["Proteksi & Kuota", "Regex Guardrails + AIQuotaManager", "Sanitasi 500 karakter, anti-injection, cache SHA-256, kuota 15/sesi", "Mencegah kebocoran sistem, memangkas biaya token berulang, & tahan offline"],
            ["Pengujian & I/O", "Pytest 9.2.0 + OpenPyXL 3.1.5", "18 unit test otomatis, UI AppTest, & pembacaan berkas Excel .xlsx", "Menjamin integritas perhitungan setiap ada perubahan kode"],
        ],
        [75, 108, 132, CONTENT_W - 315],
    )

    story.append(PageBreak())

    # =========================================================================
    # BAGIAN LANJUTAN II — DOKUMEN RESMI 3: TESTING & EVALUATION REPORT
    # =========================================================================
    add_header_block(
        story,
        "Dokumen Resmi 3 — Testing & Evaluation Report",
        "Laporan Verifikasi Matematis PnL, Audit Keterlacakan, Evaluasi Output AI & Ketahanan Guardrails",
        [
            ("Versi yang diuji", "Lokality AI Financial Recap & PnL Copilot v1.1.0"),
            ("Lingkungan uji", "Windows 11, Python 3.14.3, Pytest 9.2.0, Streamlit AppTest 1.67.0"),
            ("Dataset pengujian", "data/mock/sample_sales.csv (11 faktur) & data/mock/sample_expenses.csv (14 item pengeluaran)"),
            ("Ringkasan hasil", "18/18 Unit Test Pytest LULUS (PASS) & Integrasi Antarmuka AppTest LULUS (0 Error)"),
        ],
    )

    story.append(Paragraph("3.1 Visualisasi Hasil Perhitungan PnL Terverifikasi", ST["h1"]))
    story.append(
        Paragraph(
            "Pada periode penuh Oktober 2026, mesin deterministik mencatat Total Pendapatan sebesar <b>Rp 46.875.000</b> "
            "(2.520 pack dari 11 transaksi), Total HPP sebesar <b>Rp 29.800.000</b> (63,57%), Laba Kotor <b>Rp 17.075.000</b> "
            "(Gross Margin 36,43%), Total OPEX <b>Rp 8.500.000</b> (18,13%), dan Laba Bersih Operasional <b>Rp 8.575.000</b> "
            "(Net Margin 18,29%).",
            ST["body"],
        )
    )

    add_figure(
        story,
        DIAGRAMS_DIR / "pnl_visual_summary.png",
        "Gambar 14. Visualisasi Struktur Laba Rugi (PnL) dan Distribusi Biaya HPP/OPEX Lokality.",
        max_w=CONTENT_W - 6,
        max_h=205,
    )

    story.append(Paragraph("3.2 Matriks Skenario Pengujian Fungsional & Keamanan (TC-01 s/d TC-15)", ST["h1"]))
    add_matrix_table(
        story,
        ["ID", "Skenario / Masukan Uji", "Hasil Aktual Terverifikasi", "Status"],
        [
            ["TC-01", "Kalkulasi pendapatan penuh (sample_sales.csv)", "Revenue Rp 46.875.000; 2.520 pack; 11 faktur penjualan", "PASS"],
            ["TC-02", "Kalkulasi HPP penuh per sub-akun produksi", "HPP Rp 29.800.000 (Bahan Baku Rp 17,15 jt; Kemasan Rp 5,65 jt; Upah Rp 7,00 jt)", "PASS"],
            ["TC-03", "Identitas Laba Kotor (Revenue - HPP) & Margin", "Laba Kotor Rp 17.075.000 dengan Gross Margin 36,43%", "PASS"],
            ["TC-04", "Identitas OPEX & Laba Bersih Operasional", "OPEX Rp 8.500.000; Laba Bersih Rp 8.575.000 (Net Margin 18,29%)", "PASS"],
            ["TC-05", "Filter rentang tanggal 2026-10-01 s/d 2026-10-15", "6 faktur penjualan terfilter akurat; Revenue Rp 27.115.000", "PASS"],
            ["TC-06", "Koreksi HITL (OPEX_Logistik Rp 1,25 jt -> HPP_Bahan_Baku)", "manual_overrides=1; HPP Rp 31.050.000; OPEX Rp 7.250.000; Laba Bersih tetap Rp 8.575.000", "PASS"],
            ["TC-07", "Rekonsiliasi Drill-Down Traceability 8 kode akun", "Selisih Rp 0 antara nominal tabel PnL dan jumlah baris sumber di traceability_map", "PASS"],
            ["TC-08", "Deteksi ketidaklengkapan data (pengeluaran kosong)", "is_complete_for_pnl=False beserta peringatan eksplisit HPP & OPEX Rp 0", "PASS"],
            ["TC-09", "Auto-kategorisasi kata kunci & pelacakan sumber", "'Tepung Mocaf 100kg' -> HPP_Bahan_Baku dengan label 'Otomatis (Rule)'", "PASS"],
            ["TC-10", "Chatbot rincian item ('total belanja mocaf dan tempe')", "Merinci [EXP-001] Rp 7.000.000 + [EXP-004] Rp 2.400.000 = Subtotal Rp 9.400.000", "PASS"],
            ["TC-11", "Guardrail penolakan topik luar domain bisnis", "Pertanyaan presiden Prancis ditolak santun tanpa memotong kuota sesi", "PASS"],
            ["TC-12", "Guardrail ketahanan Prompt Injection (ID & EN)", "'Abaikan semua instruksi sebelumnya...' diblokir (is_safe=False)", "PASS"],
            ["TC-13", "Sanitasi batas panjang input (> 500 karakter)", "Teks dipotong otomatis tepat 500 karakter (truncated=True) tanpa galat", "PASS"],
            ["TC-14", "AIQuotaManager: Cache SHA-256, Kuota Habis & Saklar AI", "Cache hit tidak memotong kuota; kuota 0 / saklar mati otomatis fallback lokal", "PASS"],
            ["TC-15", "Integrasi UI Headless (Streamlit AppTest)", "Seluruh 3 tab & 8 metrik dirender utuh tanpa exception atau warning", "PASS"],
        ],
        [36, 152, 234, CONTENT_W - 422],
    )

    add_code_box(
        story,
        "$ .venv\\Scripts\\python.exe -m pytest tests/ -v\n"
        "tests/test_ai_guardrails.py::test_guardrails_block_prompt_injection PASSED\n"
        "tests/test_ai_guardrails.py::test_chatbot_granular_item_breakdown_mocaf_and_tempe PASSED\n"
        "tests/test_ai_guardrails.py::test_quota_manager_kill_switch_limit_and_cache PASSED\n"
        "tests/test_categorizer.py::test_apply_auto_categorization_tracks_source PASSED\n"
        "tests/test_pnl_engine.py::test_pnl_engine_deterministic_calculation PASSED\n"
        "tests/test_pnl_engine.py::test_pnl_period_filtering PASSED\n"
        "tests/test_pnl_engine.py::test_human_in_the_loop_manual_category_override PASSED\n"
        "tests/test_pnl_engine.py::test_traceability_drilldown_reconciles_with_pnl PASSED\n"
        "============================== 18 passed in 3.53s ==============================",
        "Hasil: 18 dari 18 skenario unit & integrasi lulus sempurna (100% PASS).",
    )

    story.append(Paragraph("3.3 Evaluasi Kualitas Output AI & Catatan Resolusi Bug", ST["h1"]))
    add_matrix_table(
        story,
        ["Kode", "Kasus Evaluasi / Temuan Bug", "Hasil Verifikasi & Penyelesaian"],
        [
            ["EV-01", "Evaluasi Rincian Bahan Baku Spesifik", "Skor 5/5 — Memisahkan [EXP-001] Mocaf Rp 7 jt dan [EXP-004] Tempe Rp 2,4 jt secara presisi."],
            ["EV-02", "Evaluasi Konsistensi Narasi Periode Filter", "Skor 5/5 — Saat difilter 1-15 Okt, narasi tepat merujuk Revenue Rp 27.115.000 (6 transaksi)."],
            ["BUG-01", "Sinkronisasi Angka Draf Awal vs Mesin PnL", "Selesai — Seluruh laporan diselaraskan ke output pasti mesin (HPP Rp 29,8 jt, Net Rp 8,575 jt)."],
            ["BUG-02", "Dukungan Konteks Baris Transaksi di Chatbot", "Selesai — expense_items_detail [EXP-001..014] disuntikkan ke prompt Gemini & kalkulator lokal."],
            ["BUG-03", "Peringatan Parameter Lebar Tabel Streamlit", "Selesai — Seluruh komponen diperbarui ke width='stretch' (0 deprecation warning)."],
        ],
        [48, 165, CONTENT_W - 213],
    )

    story.append(PageBreak())

    # =========================================================================
    # BAGIAN LANJUTAN II — DOKUMEN RESMI 4: TECHNICAL DOCUMENTATION
    # =========================================================================
    add_header_block(
        story,
        "Dokumen Resmi 4 — Technical Documentation",
        "Spesifikasi Implementasi Modul, Rumus Deterministik, Guardrails, Konfigurasi & Eksekusi Sistem",
        [
            ("Lokasi repository", r"d:\Rework Academy\Praktek\AI-Bootcamp\project-lokality-ai-finance"),
            ("Bahasa & runtime", "Python 3.14.3, Streamlit 1.67.0, Pandas 3.1.1, OpenPyXL 3.1.5, Pydantic 2.14.3"),
            ("Integrasi AI", "Google GenAI SDK 3.0.0 (gemini-2.5-flash) dengan Fallback Deterministik Lokal"),
            ("Pengamanan", "Isolasi .env (.gitignore), Regex Anti-Injection ID/EN, Sanitasi 500 Karakter & AIQuotaManager"),
        ],
    )

    story.append(Paragraph("4.1 Peta Implementasi Modul Kode Sumber", ST["h1"]))
    add_matrix_table(
        story,
        ["Berkas Kode", "Tanggung Jawab Teknis & Fungsi Kunci"],
        [
            ["src/config.py", "Mengelola path data, variabel .env, nama model, serta konstanta MAX_AI_CALLS_PER_SESSION=15, MIN_AI_COOLDOWN_SECONDS=2.0, MAX_QUERY_CHARS=500."],
            ["src/ingestion/loader.py", "Membaca CSV/Excel (load_sales_data, load_expenses_data), menormalisasi header snake_case, & mengonversi string Rupiah ke float."],
            ["src/ingestion/validator.py", "Memvalidasi kolom wajib (tanggal & total nominal) serta mendeteksi baris bernilai negatif atau tanggal tidak valid."],
            ["src/core/categorizer.py", "Memetakan belanja ke 7 sub-akun HPP/OPEX (apply_auto_categorization) & mencatat sumber_kategori ('Bawaan Data', 'Otomatis (Rule)', 'Koreksi Manual')."],
            ["src/core/pnl_engine.py", "Memfilter rentang tanggal, menghitung PnL deterministik, mengecek completeness_warnings, & membentuk traceability_map 8 kode akun."],
            ["src/ai/client.py", "Membungkus inisialisasi genai.Client secara aman dan mendeteksi kesiapan kunci API (is_configured)."],
            ["src/ai/guardrails.py", "Menjalankan sanitize_query_length (500 karakter) dan check_query_safety (anti-injection ID/EN & filter domain keuangan)."],
            ["src/ai/quota_manager.py", "Mengelola saklar AI (ai_enabled), batas panggilan sesi, jeda cooldown monotonik, & cache jawaban berbasis SHA-256."],
            ["src/ai/narrative_generator.py", "Menghasilkan ringkasan eksekutif terikat metrik PnL aktif beserta fallback naratif terstruktur saat offline."],
            ["src/ai/chatbot.py", "Menangani tanya-jawab multi-giliran (riwayat 6 pesan) dengan injeksi rincian item [EXP-001..014] & kalkulator item lokal."],
            ["src/ui/app.py", "Menyajikan aplikasi web Streamlit: Sidebar kontrol periode/kuota, Tab 1 Editor HITL, Tab 2 PnL & Drill-Down, Tab 3 AI Copilot."],
        ],
        [128, CONTENT_W - 128],
    )

    story.append(Paragraph("4.2 Logika Pemrosesan Data, Rumus PnL & Pengendalian Kuota AI", ST["h1"]))
    story.append(
        Paragraph(
            "<b>1. Perhitungan Deterministik & Keterlacakan:</b> Setiap transaksi diparse ke kolom tanggal terstandar sebelum difilter "
            "oleh parameter <i>start_date</i> dan <i>end_date</i>. Rumus baku yang dikunci di kode adalah: "
            "<b>Total HPP = HPP Bahan Baku + HPP Kemasan + HPP Tenaga Kerja</b>; "
            "<b>Laba Kotor = Total Pendapatan - Total HPP</b>; serta "
            "<b>Laba Bersih Operasional = Laba Kotor - Total OPEX</b>. Struktur <i>traceability_map</i> menyimpan daftar baris sumber "
            "untuk masing-masing dari 8 kode akun sehingga pengguna dapat melakukan audit silang secara langsung.",
            ST["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>2. Grounded Prompting & Proteksi Berlapis:</b> Sebelum kueri pengguna dikirim ke model <b>gemini-2.5-flash</b>, teks "
            "dipotong maksimal 500 karakter, diperiksa oleh regex anti-injeksi, lalu dicek terhadap cache <b>SHA-256</b> pada "
            "<b>AIQuotaManager</b>. Apabila jawaban identik sudah ada di cache, respons dikembalikan seketika dengan konsumsi 0 token. "
            "Apabila kuota sesi habis (15 panggilan), dalam masa jeda <i>cooldown</i> (2 detik), atau saklar AI dimatikan, sistem "
            "otomatis menjawab melalui mesin analitik deterministik lokal tanpa menghentikan pekerjaan pengguna.",
            ST["body"],
        )
    )

    story.append(Paragraph("4.3 Konfigurasi Lingkungan (.env) & Perintah Eksekusi Lokal", ST["h1"]))
    add_matrix_table(
        story,
        ["Variabel .env", "Nilai Default", "Keterangan Operasional"],
        [
            ["GEMINI_API_KEY", "(kosong)", "Kunci API Google AI Studio; bila dikosongkan sistem otomatis berjalan dalam mode lokal"],
            ["GEMINI_MODEL", "gemini-2.5-flash", "Model LLM utama untuk generasi ringkasan eksekutif dan tanya-jawab"],
            ["APP_PORT", "8501", "Port HTTP lokal untuk menjalankan server antarmuka Streamlit"],
            ["MAX_AI_CALLS_PER_SESSION", "15", "Batas maksimum pemanggilan API eksternal per sesi pengguna"],
            ["MIN_AI_COOLDOWN_SECONDS", "2.0", "Jeda minimum antar-pemanggilan API untuk mencegah rate-limit"],
            ["MAX_QUERY_CHARS", "500", "Batas maksimum karakter input kueri pada chatbot"],
        ],
        [164, 82, CONTENT_W - 246],
    )

    add_code_box(
        story,
        "# 1. Masuk ke folder proyek & aktifkan virtual environment\n"
        "cd \"d:\\Rework Academy\\Praktek\\AI-Bootcamp\\project-lokality-ai-finance\"\n"
        "& \"d:\\Rework Academy\\Praktek\\AI-Bootcamp\\.venv\\Scripts\\Activate.ps1\"\n\n"
        "# 2. Jalankan pengujian unit otomatis & aplikasi web Streamlit\n"
        "pytest tests/ -v\n"
        "streamlit run src/ui/app.py",
        "Hasil: Server lokal aktif pada http://localhost:8501 dengan proteksi penuh.",
    )

    story.append(PageBreak())

    # =========================================================================
    # BAGIAN LANJUTAN II — DOKUMEN RESMI 5: USER GUIDE (PANDUAN PENGGUNA)
    # =========================================================================
    add_header_block(
        story,
        "Dokumen Resmi 5 — User Guide (Panduan Pengguna)",
        "Panduan Operasional Langkah demi Langkah untuk Admin Keuangan & Manajemen PT Lokal Komoditi Indonesia",
        [
            ("Alamat akses lokal", "http://localhost:8501 (Peramban Chrome, Edge, atau Firefox modern)"),
            ("Format berkas didukung", "CSV (.csv) dan Microsoft Excel (.xlsx) untuk Penjualan & Pengeluaran"),
            ("Mode operasi AI", "Dual-Mode: AI Generatif Terikat Konteks (Gemini) & Mode Deterministik Lokal (Tanpa Kuota)"),
            ("Sasaran pengguna", "Pengelola Data (Staf Keuangan/Operasional) & Peninjau Hasil (Owner/Manajemen Lokality)"),
        ],
    )

    story.append(Paragraph("5.1 Langkah Memulai Aplikasi & Pengaturan Panel Samping (Sidebar)", ST["h1"]))
    story.append(
        Paragraph(
            "<b>Langkah 1 — Membuka Dashboard:</b> Jalankan perintah <i>streamlit run src/ui/app.py</i> pada terminal, lalu buka "
            "alamat <b>http://localhost:8501</b> di peramban web.<br/>"
            "<b>Langkah 2 — Memilih Sumber Data:</b> Pada sidebar kiri bagian <i>1. Sumber Data</i>, pilih <b>Gunakan Data Sampel "
            "Lokality</b> untuk simulasi instan, atau pilih <b>Unggah Berkas Baru (CSV/Excel)</b> untuk mengunggah berkas penjualan "
            "dan belanja aktual.<br/>"
            "<b>Langkah 3 — Mengatur Filter Periode:</b> Pada bagian <i>2. Filter Periode Laporan</i>, pilih <b>Semua Periode</b>, "
            "<b>Per Bulan</b> (contoh: 2026-10), atau <b>Rentang Tanggal Kustom</b> sesuai periode buku yang ingin ditinjau.<br/>"
            "<b>Langkah 4 — Mengatur Saklar & Kuota AI:</b> Pada bagian <i>3. Kontrol &amp; Kuota AI</i>, pantau sisa kuota panggilan "
            "atau matikan saklar <b>Aktifkan AI Generatif (Gemini)</b> apabila ingin bekerja 100% secara lokal.",
            ST["body"],
        )
    )

    story.append(Paragraph("5.2 Panduan Penggunaan Tiga Tab Utama", ST["h1"]))
    add_matrix_table(
        story,
        ["Tab Antarmuka", "Prosedur Penggunaan Langkah demi Langkah", "Keluaran yang Dilihat Pengguna"],
        [
            [
                "Tab 1:\nData Transaksi & Koreksi Kategori",
                "1) Tinjau 4 kartu ringkasan volume transaksi & status validasi kolom.\n"
                "2) Pada Tabel Pengeluaran Interaktif, klik sel kolom 'Tipe Akun PnL' jika ada biaya yang perlu direklasifikasi.",
                "Kolom 'Sumber Kategori' berubah menjadi 'Koreksi Manual' dan angka HPP/OPEX langsung diperbarui di seluruh tab.",
            ],
            [
                "Tab 2:\nLaporan Laba Rugi (PnL) & Audit",
                "1) Periksa Banner Kelengkapan Data di bagian atas.\n"
                "2) Amati 4 kartu KPI, tabel PnL standar, & kotak rumus perhitungan.\n"
                "3) Klik 'Unduh Laporan PnL (.CSV)' atau pilih kode akun pada menu Drill-Down Audit.",
                "Berkas CSV PnL terunduh; tabel Drill-Down menampilkan baris transaksi sumber [EXP-001..014] beserta nominalnya.",
            ],
            [
                "Tab 3:\nAI Financial Copilot",
                "1) Baca Ringkasan Eksekutif Finansial pada panel atas.\n"
                "2) Klik salah satu tombol pertanyaan cepat atau ketik pertanyaan rincian biaya di kotak chat (maks. 500 karakter).",
                "Jawaban ringkas berbahasa Indonesia lengkap dengan rujukan kode item dan angka Rupiah terverifikasi.",
            ],
        ],
        [95, 195, CONTENT_W - 290],
    )

    story.append(Paragraph("5.3 Contoh Penggunaan Nyata & Panduan Penanganan Kendala (Troubleshooting)", ST["h1"]))
    add_matrix_table(
        story,
        ["Masukan / Tindakan Pengguna", "Respons Aktual Aplikasi", "Catatan Manfaat"],
        [
            [
                "Memilih Semua Periode pada Data Sampel Lokality (Tab 2)",
                "Pendapatan Rp 46.875.000 | HPP Rp 29.800.000 | Laba Kotor Rp 17.075.000 (36,43%) | OPEX Rp 8.500.000 | Laba Bersih Rp 8.575.000 (18,29%)",
                "Memberikan potret utuh kinerja pabrik mi gluten-free dalam hitungan detik.",
            ],
            [
                "Memilih Rentang Tanggal Kustom 2026-10-01 s/d 2026-10-15",
                "Menampilkan 6 transaksi penjualan paruh pertama bulan dengan Total Pendapatan Rp 27.115.000.",
                "Memudahkan evaluasi target penjualan mingguan atau tengah bulan.",
            ],
            [
                "Klik tombol cepat: 'Berapa total belanja mocaf dan tempe?'",
                "Merinci [EXP-001] Tepung Mocaf Rp 7.000.000 (500 kg) + [EXP-004] Tempe Fermentasi Rp 2.400.000 (150 kg) = Subtotal Rp 9.400.000.",
                "Menjawab rincian bahan baku spesifik tanpa perlu menjumlahkan baris manual di Excel.",
            ],
        ],
        [135, 195, CONTENT_W - 330],
    )

    add_matrix_table(
        story,
        ["Pesan / Gejala pada Aplikasi", "Penyebab Umum", "Langkah Penyelesaian"],
        [
            [
                "Indikator Sidebar: Mode Lokal Deterministik Aktif",
                "GEMINI_API_KEY belum diisi di .env, kuota sesi (15 panggilan) habis, atau saklar AI sengaja dimatikan.",
                "Aplikasi tetap dapat digunakan penuh. Isi GEMINI_API_KEY pada berkas .env atau klik 'Reset Kuota Sesi' jika ingin memakai narasi Gemini.",
            ],
            [
                "Banner Kuning: Data Belum Lengkap untuk PnL Utuh",
                "Pada rentang tanggal terpilih, komponen Pendapatan, HPP Bahan Baku, atau OPEX bernilai Rp 0.",
                "Perluas rentang tanggal filter periode atau pastikan kedua berkas (penjualan & pengeluaran) telah diunggah lengkap.",
            ],
            [
                "Chatbot Menolak Menjawab Pertanyaan",
                "Pertanyaan berada di luar topik keuangan/operasional Lokality atau mengandung pola manipulasi instruksi.",
                "Ajukan pertanyaan seputar pendapatan, HPP, bahan baku (mocaf, tempe, beras, kemasan), OPEX, margin, atau kanal penjualan.",
            ],
        ],
        [135, 155, CONTENT_W - 290],
    )

    add_section_footer(
        story,
        "Akhir Dokumen Resmi Terpadu AI Engineering Bootcamp & Capstone PT Lokal Komoditi Indonesia (Lokality — LKI-01).",
    )

    return story


def main():
    if not SOURCE_PDF.exists():
        raise FileNotFoundError(f"Source PDF tidak ditemukan: {SOURCE_PDF}")

    # 1. Render halaman lanjutan (Page 11+) ke memori menggunakan ReportLab
    continuation_buf = io.BytesIO()
    doc = SimpleDocTemplate(
        continuation_buf,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Dokumentasi Resmi AI Engineering Bootcamp & Capstone Lokality (LKI-01)",
        author="Ahnaf Rifqi",
    )
    story = build_continuation_story()
    doc.build(story)
    continuation_buf.seek(0)

    # 2. Gabungkan Halaman 1-10 asli + Halaman Lanjutan 11..N secara utuh
    orig_reader = pypdf.PdfReader(str(SOURCE_PDF))
    cont_reader = pypdf.PdfReader(continuation_buf)

    writer = pypdf.PdfWriter()
    for p in orig_reader.pages:
        writer.add_page(p)
    for p in cont_reader.pages:
        writer.add_page(p)

    writer.add_metadata(
        {
            "/Title": "Dokumentasi Resmi AI-Bootcamp & Capstone PT Lokal Komoditi Indonesia (Lokality)",
            "/Author": "Ahnaf Rifqi",
            "/Subject": "IT Helpdesk Agent, Data Pipeline, Model Experiment, Semantic Search, AI Evaluation & Lokality Finance Copilot (BRD, Blueprint, Testing, Tech Docs, User Guide)",
            "/Producer": "ReportLab PDF Library + pypdf",
        }
    )

    for out_path in [WORKSPACE_PDF_OUT, PROJECT_PDF_OUT, ARTIFACT_PDF_OUT]:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            writer.write(f)
        print(f"Saved merged PDF ({len(orig_reader.pages)} orig + {len(cont_reader.pages)} new = {len(writer.pages)} pages): {out_path}")


if __name__ == "__main__":
    main()
