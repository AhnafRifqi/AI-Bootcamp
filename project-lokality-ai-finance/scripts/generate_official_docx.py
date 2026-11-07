"""Generator paket dokumen resmi Word (.docx) Deliverable 1 s/d 5 untuk proyek Lokality (Tanpa PPTX)."""

import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT_DIR / "docs" / "official_docx"
DIAGRAMS_DIR = ROOT_DIR / "docs" / "diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _set_cell_shading(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def _style_doc(doc: Document, title: str, subtitle: str):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run(title)
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(17)
    r_title.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    p_title.paragraph_format.space_after = Pt(2)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(subtitle)
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    p_sub.paragraph_format.space_after = Pt(10)


def _add_h1(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)


def _add_p(doc: Document, text: str, italic: bool = False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(text)
    r.italic = italic
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)


def _add_table(doc: Document, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    for idx, h in enumerate(headers):
        hdr_cells[idx].text = ""
        p = hdr_cells[idx].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _set_cell_shading(hdr_cells[idx], "2B2B2B")

    for r_idx, row_data in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8F9FA"
        for c_idx, val in enumerate(row_data):
            cells[c_idx].text = ""
            p = cells[c_idx].paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if c_idx == 0:
                r.bold = True
            _set_cell_shading(cells[c_idx], bg)

    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def _add_image(doc: Document, img_path: Path, caption: str, width_inches: float = 6.2):
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(img_path), width=Inches(width_inches))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run(caption)
        r_cap.italic = True
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(9.0)
        r_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        p_cap.paragraph_format.space_after = Pt(8)


def build_doc_1_brd():
    doc = Document()
    _style_doc(
        doc,
        "Business Requirement Document (BRD)",
        "PT Lokal Komoditi Indonesia (Lokality) — Studi Kasus LKI-01 | Versi 1.1",
    )
    _add_h1(doc, "Informasi Project")
    _add_table(
        doc,
        ["Atribut", "Isian Proyek"],
        [
            ["Nama Project", "Lokality AI Financial Recap & PnL Copilot"],
            ["Mitra Studi Kasus", "PT Lokal Komoditi Indonesia (Lokality) — Kasus ID: LKI-01"],
            ["Penyusun", "Ahnaf Rifqi (AI Engineering Bootcamp)"],
            ["Tanggal / Versi", "08 November 2026 / v1.1.0"],
        ],
    )

    _add_h1(doc, "1. Problem Statement")
    _add_table(
        doc,
        ["Komponen", "Uraian Fakta & Analisis Kasus"],
        [
            [
                "Kondisi Saat Ini (As-Is)",
                "PT Lokal Komoditi Indonesia memproduksi mi gluten-free berbahan tepung mocaf, tepung beras, dan tepung jagung dengan fortifikasi tempe. Aktivitas harian mencakup produksi, pencatatan income penjualan, dan cash out belanja bahan baku/operasional. Tim sudah terbiasa menggunakan ChatGPT untuk perencanaan umum, tetapi rekap keuangan bulanan masih dilakukan manual secara terpisah.",
            ],
            [
                "Masalah Utama",
                "Rekapitulasi data penjualan dan pengeluaran memakan waktu lama, belum memiliki pemetaan baku pos HPP vs OPEX, serta menghambat penyusunan Laporan Laba Rugi (PnL) bulanan yang akurat dan dapat ditelusuri.",
            ],
            [
                "Dampak Bisnis",
                "Manajemen terlambat mengetahui margin laba kotor, laba bersih operasional, serta proporsi biaya bahan baku utama (mocaf, tempe, beras, kemasan) untuk evaluasi harga jual dan efisiensi pabrik.",
            ],
            [
                "Hal yang Perlu Diklarifikasi",
                "1) Bentuk berkas asli dari PIC Lokality (spreadsheet CSV/Excel vs nota fisik kertas).\n2) Kebijakan cut-off tanggal pembukuan bulanan serta pencatatan penyusutan alat.",
            ],
        ],
    )

    _add_h1(doc, "2. Target User")
    _add_table(
        doc,
        ["Peran Pengguna", "Tanggung Jawab", "Kebutuhan Sistem"],
        [
            [
                "Pengelola Data (Admin Keuangan / Operasional)",
                "Mengunggah, memvalidasi, dan merekap transaksi penjualan serta belanja pabrik.",
                "Ingestion CSV/Excel toleran format Rupiah, filter periode tanggal/bulan, auto-kategorisasi biaya, serta editor interaktif Human-in-the-Loop untuk mengoreksi tipe akun.",
            ],
            [
                "Peninjau Hasil (Pemilik / Manajemen Lokality)",
                "Mengevaluasi kinerja laba rugi bulanan dan struktur biaya produksi.",
                "Draf PnL deterministik bebas halusinasi, indikator kelengkapan data, drill-down keterlacakan transaksi sumber, ringkasan eksekutif AI, dan tanya-jawab rincian item.",
            ],
        ],
    )

    _add_h1(doc, "3. User Needs")
    _add_table(
        doc,
        ["ID", "Kebutuhan Pengguna", "Konteks Bisnis", "Target Keberhasilan"],
        [
            ["UN-01", "Rekap & filter transaksi per bulan atau rentang tanggal", "Evaluasi performa paruh bulan maupun bulanan penuh", "Pembaruan tabel & PnL < 2 detik secara akurat"],
            ["UN-02", "Auto-kategorisasi HPP/OPEX dengan koreksi manual (HITL)", "Menghindari salah klasifikasi akun biaya sebelum PnL dipakai", "Setiap koreksi manual langsung menghitung ulang HPP & OPEX"],
            ["UN-03", "Draf PnL deterministik + penanda kelengkapan + drill-down", "Angka laporan keuangan wajib 100% terverifikasi ke baris sumber", "Selisih Rp 0 antara tabel PnL dan penjumlahan baris sumber"],
            ["UN-04", "Narasi eksekutif & chatbot rincian item (mis. mocaf & tempe)", "Memudahkan manajemen berkonsultasi dengan bahasa sehari-hari", "Menyebutkan ID [EXP-xxx], nominal per item, dan subtotal tepat"],
            ["UN-05", "Pembatas kuota sesi, cache jawaban, dan saklar on/off AI", "Mengamankan biaya token API & kontinuitas saat offline", "Cache 0 token; saklar mati otomatis fallback ke mesin lokal"],
        ],
    )

    _add_h1(doc, "4. Project Scope")
    _add_table(
        doc,
        ["In-Scope (Termasuk)", "Out-of-Scope (Di Luar Lingkup)", "Batasan & Dependensi"],
        [
            [
                "1) Ingestion & normalisasi CSV/Excel.\n2) Filter Semua Periode / Bulanan / Rentang Tanggal.\n3) Auto-kategorisasi 7 sub-akun + editor HITL.\n4) Mesin PnL deterministik, cek kelengkapan, drill-down audit, & ekspor CSV.\n5) AI Copilot rincian item + Guardrails + AIQuotaManager.",
                "1) Mutasi bank otomatis (Open Banking).\n2) Pelaporan pajak e-Faktur / SPT Badan.\n3) Kasir POS & manajemen stok fisik gudang.\n4) OCR foto struk kertas (menunggu konfirmasi berkas PIC).",
                "1) GEMINI_API_KEY disimpan lokal di .env.\n2) Pengujian saat ini memakai dataset simulasi Lokality sambil menunggu data riil dari PIC.",
            ]
        ],
    )

    _add_h1(doc, "5. Main Use Cases & 6. Success Criteria")
    _add_table(
        doc,
        ["Kode", "Deskripsi Use Case / Kriteria Keberhasilan", "Target Terukur"],
        [
            ["UC-01", "Rekap Periode & Koreksi Kategori (Human-in-the-Loop) di Tab 1", "Status baris berubah ke 'Koreksi Manual' & PnL terhitung ulang"],
            ["UC-02", "Peninjauan Draf PnL, Banner Kelengkapan & Drill-Down Audit di Tab 2", "8/8 kode akun cocok 100% dengan baris transaksi sumber"],
            ["UC-03", "Konsultasi Rincian Item Belanja (Mocaf & Tempe) di Tab 3", "Menampilkan [EXP-001] Rp 7 jt + [EXP-004] Rp 2,4 jt = Rp 9,4 jt"],
            ["UC-04", "Pengendalian Kuota & Saklar Mati AI di Sidebar", "Fallback deterministik berjalan tanpa error saat AI dimatikan"],
            ["SC-01..05", "Verifikasi Otomatis 18 Unit Test Pytest & Streamlit AppTest", "18/18 unit test PASS, deviasi perhitungan Rp 0"],
        ],
    )

    path = OUT_DIR / "1 - Business Requirement Document - Lokality.docx"
    doc.save(path)
    print(f"Saved: {path}")


def build_doc_2_blueprint():
    doc = Document()
    _style_doc(
        doc,
        "AI Solution Blueprint & Architecture",
        "PT Lokal Komoditi Indonesia (Lokality) — Studi Kasus LKI-01 | Versi 1.1",
    )
    _add_h1(doc, "1. User Flow Diagram")
    _add_p(
        doc,
        "Alur pengguna dirancang untuk memisahkan peran Pengelola Data (validasi spreadsheet dan koreksi kategori Human-in-the-Loop) serta Peninjau Hasil (audit keterlacakan PnL dan konsultasi AI Copilot).",
    )
    _add_image(doc, DIAGRAMS_DIR / "user_flow_diagram.png", "Gambar 1. User Flow Diagram Lokality AI Financial Recap & PnL Copilot (v1.1).")

    _add_h1(doc, "2. AI Solution Architecture Diagram")
    _add_p(
        doc,
        "Arsitektur sistem memisahkan secara tegas Deterministic Accounting Layer (Python + Pandas) dari Grounded Generative AI Layer (Gemini 2.5 Flash + Guardrails + AIQuotaManager) sehingga tidak ada risiko halusinasi matematis.",
    )
    _add_image(doc, DIAGRAMS_DIR / "architecture_diagram.png", "Gambar 2. AI Solution Architecture Diagram Lokality (v1.1).")

    _add_h1(doc, "3. Technology Selection")
    _add_table(
        doc,
        ["Komponen", "Teknologi", "Peran Teknis", "Alasan Pemilihan"],
        [
            ["UI / Frontend", "Streamlit 1.67.0", "Dashboard 3-tab, st.data_editor HITL, kontrol filter & chat", "Interaktif, mendukung edit tabel langsung, dan dapat diuji headless dengan AppTest"],
            ["Accounting Engine", "Python 3.14.3 + Pandas 3.1.1", "Normalisasi Rupiah, filter periode, kalkulasi PnL & traceability_map", "Akurasi matematis 100% (deviasi Rp 0) dan keterlacakan baris sumber"],
            ["AI / LLM", "Google GenAI SDK 3.0.0 (gemini-2.5-flash)", "Narasi eksekutif & tanya-jawab rincian item terikat konteks", "Cepat, akurat untuk Bahasa Indonesia bisnis, dan hemat token"],
            ["Safety & Quota", "Guardrails Regex + AIQuotaManager", "Batas 500 karakter, anti-injection, cache SHA-256, kuota 15/sesi", "Mencegah kebocoran prompt, menghemat kuota API, dan menjamin mode offline"],
            ["Testing", "Pytest 9.2.0 + OpenPyXL 3.1.5", "18 pengujian unit otomatis & dukungan berkas Excel .xlsx", "Menjamin stabilitas regresi kode dan kompatibilitas kerja staf admin"],
        ],
    )

    path = OUT_DIR / "2 - AI Solution Blueprint Architecture - Lokality.docx"
    doc.save(path)
    print(f"Saved: {path}")


def build_doc_3_testing():
    doc = Document()
    _style_doc(
        doc,
        "Testing & Evaluation Report",
        "PT Lokal Komoditi Indonesia (Lokality) — Versi Aplikasi v1.1.0 | 18 Unit Tests & UI AppTest",
    )
    _add_h1(doc, "1. Ringkasan Lingkungan & Cakupan Pengujian")
    _add_table(
        doc,
        ["Parameter", "Spesifikasi Pengujian"],
        [
            ["Versi Aplikasi", "v1.1.0 (Step 2 Upgraded Build)"],
            ["Lingkungan Uji", "Windows 11, Python 3.14.3, Streamlit 1.67.0, Pandas 3.1.1, Pytest 9.2.0"],
            ["Dataset Uji", "Dataset simulasi operasional Lokality (sample_sales.csv: 11 faktur; sample_expenses.csv: 14 baris belanja)"],
            ["Hasil Eksekusi", "18/18 Unit Test Pytest LULUS (PASS) & Headless Streamlit AppTest LULUS (0 Exception)"],
        ],
    )

    _add_image(doc, DIAGRAMS_DIR / "pnl_visual_summary.png", "Gambar 1. Visualisasi Terverifikasi Struktur Laba Rugi (PnL) & Pos Biaya Lokality.")

    _add_h1(doc, "2. Matriks Hasil Skenario Pengujian (TC-01 s/d TC-15)")
    _add_table(
        doc,
        ["ID", "Skenario Pengujian", "Hasil Aktual Terverifikasi", "Status"],
        [
            ["TC-01", "Kalkulasi Revenue Penuh (11 faktur)", "Total Revenue Rp 46.875.000 (2.520 pack terjual)", "PASS"],
            ["TC-02", "Kalkulasi HPP Penuh per Sub-Akun", "Total HPP Rp 29.800.000 (Bahan Baku Rp 17,15 jt; Kemasan Rp 5,65 jt; Upah Rp 7,00 jt)", "PASS"],
            ["TC-03", "Verifikasi Laba Kotor & Gross Margin", "Laba Kotor Rp 17.075.000 (Gross Margin 36,43%)", "PASS"],
            ["TC-04", "Verifikasi OPEX & Laba Bersih Operasional", "Total OPEX Rp 8.500.000; Laba Bersih Rp 8.575.000 (Net Margin 18,29%)", "PASS"],
            ["TC-05", "Filter Periode 2026-10-01 s/d 2026-10-15", "6 faktur penjualan terfilter, Revenue tepat Rp 27.115.000", "PASS"],
            ["TC-06", "Koreksi Kategori HITL (OPEX_Logistik -> HPP_Bahan_Baku)", "manual_overrides_count=1; HPP Rp 31.050.000; OPEX Rp 7.250.000; Net Profit tetap Rp 8.575.000", "PASS"],
            ["TC-07", "Rekonsiliasi Drill-Down Traceability 8 Kode Akun", "Selisih Rp 0 antara nominal PnL dan penjumlahan baris sumber di traceability_map", "PASS"],
            ["TC-08", "Deteksi Ketidaklengkapan Data (Pengeluaran Kosong)", "is_complete_for_pnl=False dengan peringatan eksplisit komponen Rp 0", "PASS"],
            ["TC-09", "Auto-Kategorisasi Kata Kunci & Pelacakan Sumber", "Item baru otomatis dipetakan & ditandai 'Otomatis (Rule)'", "PASS"],
            ["TC-10", "Chatbot Rincian Item ('belanja mocaf dan tempe')", "Menampilkan [EXP-001] Rp 7.000.000 + [EXP-004] Rp 2.400.000 = Rp 9.400.000", "PASS"],
            ["TC-11", "Guardrail Penolakan Topik Luar Domain", "Pertanyaan presiden Prancis ditolak santun tanpa memotong kuota API", "PASS"],
            ["TC-12", "Guardrail Anti-Prompt Injection (ID & EN)", "Instruksi 'Abaikan semua instruksi sebelumnya...' diblokir di gerbang awal", "PASS"],
            ["TC-13", "Sanitasi Panjang Input (> 500 karakter)", "Input dipotong aman tepat 500 karakter (truncated=True)", "PASS"],
            ["TC-14", "Manajer Kuota Sesi, Cache SHA-256 & Saklar AI", "Cache hit hemat kuota; saklar mati / kuota habis otomatis fallback lokal", "PASS"],
            ["TC-15", "Integrasi Antarmuka Streamlit AppTest", "8 kartu metrik & 3 tab dirender utuh tanpa error maupun warning", "PASS"],
        ],
    )

    _add_h1(doc, "3. Catatan Perbaikan & Sinkronisasi (Bug Log)")
    _add_table(
        doc,
        ["ID", "Temuan Awal", "Tindakan Penyelesaian", "Status"],
        [
            ["BUG-01", "Selisih angka estimasi manual pada dokumen draf awal v1.0 vs mesin PnL", "Seluruh dokumen disinkronkan ke angka pasti mesin (Revenue Rp 46.875.000, HPP Rp 29.800.000, Net Profit Rp 8.575.000) & dikunci di pytest", "Selesai"],
            ["BUG-02", "Chatbot v1.0 belum merinci transaksi bahan baku per baris", "Ditambahkan injeksi expense_items_detail [EXP-001..014] ke konteks LLM & mesin lokal", "Selesai"],
            ["BUG-03", "Deprecation warning use_container_width pada Streamlit 1.67", "Diganti menjadi width='stretch' pada seluruh tabel dan tombol UI", "Selesai"],
        ],
    )

    path = OUT_DIR / "3 - Testing Evaluation Report - Lokality.docx"
    doc.save(path)
    print(f"Saved: {path}")


def build_doc_4_tech():
    doc = Document()
    _style_doc(
        doc,
        "Technical Documentation",
        "Lokality AI Financial Recap & PnL Copilot (v1.1.0) — Dokumentasi Teknis & Implementasi",
    )
    _add_h1(doc, "1. Pemetaan Komponen & Kode Sumber")
    _add_table(
        doc,
        ["Modul / Berkas", "Tanggung Jawab Utama"],
        [
            ["src/config.py", "Memuat variabel .env, path direktori, model Gemini, serta batas MAX_AI_CALLS_PER_SESSION=15, MIN_AI_COOLDOWN_SECONDS=2.0, MAX_QUERY_CHARS=500."],
            ["src/ingestion/loader.py", "Membaca CSV/Excel, menormalisasi nama kolom snake_case, dan membersihkan format mata uang Rupiah menjadi float."],
            ["src/ingestion/validator.py", "Memvalidasi keberadaan kolom wajib (tanggal & nominal) serta mendeteksi nilai negatif atau tanggal rusak."],
            ["src/core/categorizer.py", "Mengklasifikasikan belanja ke 7 sub-akun HPP/OPEX dan melacak sumber_kategori ('Bawaan Data', 'Otomatis (Rule)', 'Koreksi Manual')."],
            ["src/core/pnl_engine.py", "Mengeksekusi filter periode tanggal, kalkulasi deterministik PnL, cek completeness_warnings, dan menyusun traceability_map."],
            ["src/ai/guardrails.py", "Sanitasi panjang kueri (500 karakter), deteksi domain keuangan, dan pemblokiran prompt injection Bahasa Indonesia & Inggris."],
            ["src/ai/quota_manager.py", "Mengelola saklar AI (ai_enabled), kuota panggilan sesi, jeda cooldown, dan cache respons berbasis hash SHA-256."],
            ["src/ai/narrative_generator.py", "Menyusun ringkasan eksekutif performa bulanan berbasis angka PnL terverifikasi dengan fallback offline."],
            ["src/ai/chatbot.py", "Menangani tanya-jawab multi-turn beserta rincian item [EXP-001..014] via Gemini maupun kalkulator lokal."],
            ["src/ui/app.py", "Antarmuka web Streamlit (Sidebar kontrol + Tab 1 Editor HITL + Tab 2 PnL & Drill-Down + Tab 3 AI Copilot)."],
        ],
    )

    _add_h1(doc, "2. Konfigurasi Variabel Lingkungan (.env)")
    _add_table(
        doc,
        ["Variabel", "Default", "Fungsi"],
        [
            ["GEMINI_API_KEY", "(kosong)", "Kunci API Google AI Studio; bila kosong otomatis masuk mode deterministik lokal"],
            ["GEMINI_MODEL", "gemini-2.5-flash", "Model generatif utama untuk narasi dan chatbot"],
            ["APP_PORT", "8501", "Port server lokal Streamlit"],
            ["MAX_AI_CALLS_PER_SESSION", "15", "Batas maksimum pemanggilan API per sesi pengguna"],
            ["MIN_AI_COOLDOWN_SECONDS", "2.0", "Jeda minimum antar-pemanggilan API dalam detik"],
            ["MAX_QUERY_CHARS", "500", "Batas panjang karakter pertanyaan pengguna"],
        ],
    )

    _add_h1(doc, "3. Perintah Menjalankan Aplikasi & Pengujian")
    _add_p(doc, "Menjalankan unit test: .venv\\Scripts\\python.exe -m pytest tests/ -v")
    _add_p(doc, "Menjalankan aplikasi web: .venv\\Scripts\\streamlit.exe run src/ui/app.py")

    path = OUT_DIR / "4 - Technical Documentation - Lokality.docx"
    doc.save(path)
    print(f"Saved: {path}")


def build_doc_5_user_guide():
    doc = Document()
    _style_doc(
        doc,
        "User Guide (Panduan Pengguna)",
        "Lokality AI Financial Recap & PnL Copilot (v1.1.0) — Panduan Operasional Langkah demi Langkah",
    )
    _add_h1(doc, "1. Memulai Aplikasi & Pengaturan Sidebar")
    _add_p(doc, "1. Jalankan perintah streamlit run src/ui/app.py lalu buka http://localhost:8501 di peramban.")
    _add_p(doc, "2. Pada Sidebar kiri, pilih 'Gunakan Data Sampel Lokality' atau 'Unggah Berkas Baru (CSV/Excel)'.")
    _add_p(doc, "3. Pilih Filter Periode Laporan: Semua Periode, Per Bulan (mis. 2026-10), atau Rentang Tanggal Kustom.")
    _add_p(doc, "4. Gunakan saklar 'Aktifkan AI Generatif (Gemini)' dan indikator kuota untuk mengatur pemakaian AI.")

    _add_h1(doc, "2. Panduan Tiga Tab Utama")
    _add_table(
        doc,
        ["Tab Antarmuka", "Langkah Penggunaan Utama", "Hasil yang Diperoleh"],
        [
            [
                "Tab 1: Data Transaksi & Koreksi Kategori",
                "Periksa status validasi data, lalu klik kolom 'Tipe Akun PnL' pada tabel pengeluaran interaktif bila ada kategori biaya yang ingin dikoreksi manual.",
                "Baris ditandai 'Koreksi Manual' dan angka HPP/OPEX di seluruh laporan langsung diperbarui.",
            ],
            [
                "Tab 2: Laporan Laba Rugi (PnL) & Audit",
                "Tinjau Banner Kelengkapan Data, 4 kartu KPI, tabel PnL, rumus perhitungan, tombol Unduh CSV, serta pilih akun pada menu Drill-Down Keterlacakan.",
                "Menampilkan draf PnL presisi beserta daftar baris transaksi sumber yang membentuk tiap nominal.",
            ],
            [
                "Tab 3: AI Financial Copilot",
                "Baca Ringkasan Eksekutif Finansial di atas, lalu klik tombol pertanyaan cepat atau ketik pertanyaan rincian belanja di kotak chat bawah.",
                "Jawaban bahasa alami lengkap dengan rujukan kode item [EXP-xxx] dan nominal Rupiah akurat.",
            ],
        ],
    )

    _add_h1(doc, "3. Contoh Interaksi & Penanganan Kendala")
    _add_table(
        doc,
        ["Skenario / Kendala", "Output / Langkah Solusi"],
        [
            ["Pertanyaan: 'Berapa total belanja mocaf dan tempe?'", "Menampilkan [EXP-001] Tepung Mocaf Rp 7.000.000 + [EXP-004] Tempe Fermentasi Rp 2.400.000 = Subtotal Rp 9.400.000."],
            ["Status Sidebar: Mode Lokal Deterministik Aktif", "Aplikasi tetap berfungsi penuh tanpa koneksi API. Isi GEMINI_API_KEY di .env atau tekan Reset Kuota Sesi bila ingin mengaktifkan LLM kembali."],
            ["Banner Kuning: Data Belum Lengkap untuk PnL Utuh", "Periksa apakah filter tanggal terlalu sempit atau berkas penjualan/pengeluaran bulan terkait belum diunggah."],
        ],
    )

    path = OUT_DIR / "5 - User Guide - Lokality.docx"
    doc.save(path)
    print(f"Saved: {path}")


if __name__ == "__main__":
    build_doc_1_brd()
    build_doc_2_blueprint()
    build_doc_3_testing()
    build_doc_4_tech()
    build_doc_5_user_guide()
