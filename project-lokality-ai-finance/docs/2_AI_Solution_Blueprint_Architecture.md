# AI Solution Blueprint & Architecture
## AI Solution for Enterprise — Capstone Business Project

---

### Tujuan Dokumen
Dokumen ini mendefinisikan arsitektur teknis, alur pengguna (*User Flow*), dan pemilihan teknologi untuk aplikasi **Lokality AI Financial Recap & PnL Copilot** (Versi 1.1) pada PT Lokal Komoditi Indonesia (Kasus ID: `LKI-01`). Dokumen ini menjembatani kebutuhan bisnis pada BRD dengan implementasi modular di repository kode.

---

### 1. User Flow Diagram

Diagram berikut menggambarkan interaksi dua persona pengguna (**Pengelola Data** dan **Peninjau Hasil / Manajemen Lokality**), termasuk filter periode, koreksi kategori *Human-in-the-Loop*, *drill-down* keterlacakan angka PnL, serta pengendalian kuota & *guardrails* AI.

> Berkas diagram resolusi tinggi juga tersedia pada [`docs/diagrams/user_flow_diagram.png`](diagrams/user_flow_diagram.png) dan sumber [`docs/diagrams/user_flow_diagram.mmd`](diagrams/user_flow_diagram.mmd).

```mermaid
flowchart TD
    Start(["Mulai Aplikasi Web Streamlit"]) --> SidebarCtrl["Sidebar: Pilih Sumber Data, Filter Periode & Saklar AI"]
    
    SidebarCtrl -->|Data Standar| LoadSample["Muat Data Sampel Lokality (CSV)"]
    SidebarCtrl -->|Unggah Mandiri| UploadFiles["Unggah CSV / Excel Penjualan & Pengeluaran"]
    
    UploadFiles --> Validasi{"Validasi Skema & Kolom Wajib"}
    Validasi -->|Kolom Kurang / Format Rusak| ShowError["Tampilkan Peringatan Validasi Eksplisit"]
    ShowError --> UploadFiles
    
    Validasi -->|Valid| Cleaning["Normalisasi Nama Kolom, Mata Uang Rupiah & Tanggal"]
    LoadSample --> Cleaning
    
    Cleaning --> AutoCat["Auto-Kategorisasi Belanja (HPP vs OPEX) + Pelacakan Sumber"]
    AutoCat --> Tab1Edit{"Tab 1: Koreksi Manual Human-in-the-Loop?"}
    
    Tab1Edit -->|Koreksi tipe_akun di Tabel Editor| ApplyOverride["Tandai 'Koreksi Manual' & Rekalkulasi Seketika"]
    Tab1Edit -->|Sudah Sesuai| PeriodFilter["Terapkan Filter Periode (Semua / Bulanan / Rentang Tanggal)"]
    ApplyOverride --> PeriodFilter
    
    PeriodFilter --> PnLEngine["Kalkulasi Deterministik PnL + Cek Kelengkapan Data"]
    
    PnLEngine --> TabNav{"Pilih Tampilan Analitik"}
    
    TabNav -->|Tab 2: Laporan PnL| ViewPnL["Tinjau Banner Kelengkapan, Kartu KPI, Rumus & Tabel PnL"]
    ViewPnL --> DrillDown["Pilih Akun pada Panel Drill-Down Audit Transaksi Sumber"]
    ViewPnL --> DownloadCSV["Unduh Draf Laporan PnL (.CSV)"]
    
    TabNav -->|Tab 3: AI Copilot| AICopilot["Baca Ringkasan Eksekutif & Ajukan Pertanyaan Rincian Item"]
    AICopilot --> Sanitize["Sanitasi Panjang Kueri (Maks. 500 Karakter)"]
    Sanitize --> GuardrailCheck{"Lolos Domain & Safety Guardrails?"}
    
    GuardrailCheck -->|Luar Topik / Prompt Injection| RejectQuery["Tolak Santun Tanpa Memotong Kuota API"]
    GuardrailCheck -->|Lolos| QuotaCheck{"Cek Cache, Saklar AI & Kuota Sesi"}
    QuotaCheck -->|Cache Hit| ReturnCache["Kembalikan Jawaban Tersimpan (0 Token)"]
    QuotaCheck -->|Saklar Mati / Kuota Habis / Offline| LocalEngine["Jawab via Mesin Deterministik Rincian Item Lokal"]
    QuotaCheck -->|Kuota Tersedia & Online| LLMAnswer["Gemini 2.5 Flash: Jawab Terikat Data & Kode [EXP-xxx]"]
```

---

### 2. AI Solution Architecture Diagram

Arsitektur sistem menerapkan pemisahan tegas antara **Deterministic Accounting Engine** (menjamin akurasi matematis 100% dan keterlacakan baris sumber) dan **Grounded Generative AI Layer** (dilengkapi *Guardrails*, *Session Quota Manager*, *Response Cache*, dan *Deterministic Offline Fallback*).

> Berkas diagram resolusi tinggi tersedia pada [`docs/diagrams/architecture_diagram.png`](diagrams/architecture_diagram.png) dan sumber [`docs/diagrams/architecture_diagram.mmd`](diagrams/architecture_diagram.mmd).

```mermaid
flowchart TB
    subgraph UI_Layer ["Presentation Layer (Streamlit 1.67 — src/ui/app.py)"]
        UI_Sidebar["Sidebar: Sumber Data, Filter Periode, Saklar & Bar Kuota AI"]
        UI_Tab1["Tab 1: Rekap Transaksi, Validasi & Editor Human-in-the-Loop"]
        UI_Tab2["Tab 2: Kartu KPI, Tabel PnL, Rumus & Drill-Down Traceability"]
        UI_Tab3["Tab 3: Ringkasan Eksekutif & Chatbot Rincian Item"]
    end

    subgraph Logic_Layer ["Deterministic Business & Accounting Layer"]
        Loader["Data Loader & Currency Normalizer (src/ingestion/loader.py)"]
        Validator["Schema & Anomaly Validator (src/ingestion/validator.py)"]
        Categorizer["Rule-Based Categorizer + Override Tracker (src/core/categorizer.py)"]
        PnL_Core["Deterministic PnL, Period Filter & Traceability Engine (src/core/pnl_engine.py)"]
    end

    subgraph AI_Layer ["Grounded AI, Safety & Quota Layer"]
        Guardrails["Length Sanitizer & Anti-Injection Guardrails (src/ai/guardrails.py)"]
        QuotaMgr["Session Quota, Cooldown, Kill-Switch & SHA-256 Cache (src/ai/quota_manager.py)"]
        NarrativeGen["Executive Summary Generator + Fallback (src/ai/narrative_generator.py)"]
        ChatEngine["Item-Level Financial Q&A Copilot + Fallback (src/ai/chatbot.py)"]
        GeminiClient["Google GenAI SDK Wrapper — gemini-2.5-flash (src/ai/client.py)"]
    end

    subgraph Data_Storage ["Data & Session Storage"]
        RawStore["CSV / Excel Files (data/mock & User Uploads)"]
        SessionStore["Streamlit Session State (Edited DataFrames, PnL Snapshot, Quota & Cache)"]
    end

    RawStore --> Loader
    UI_Sidebar --> Loader
    Loader --> Validator
    Validator --> Categorizer
    UI_Tab1 -->|Human-in-the-Loop Edit| Categorizer
    Categorizer --> PnL_Core
    UI_Sidebar -->|start_date, end_date| PnL_Core
    PnL_Core --> SessionStore
    SessionStore --> UI_Tab1
    SessionStore --> UI_Tab2

    SessionStore -->|Verified PnL + Item Details| NarrativeGen
    SessionStore -->|Verified PnL + Item Details| ChatEngine
    UI_Tab3 --> Guardrails
    Guardrails -->|Safe & Sanitized Query| ChatEngine
    NarrativeGen --> QuotaMgr
    ChatEngine --> QuotaMgr
    QuotaMgr -->|Allowed & Online| GeminiClient
    QuotaMgr -->|Disabled / Exhausted / Offline| ChatEngine
    GeminiClient -->|Grounded Response| UI_Tab3
```

---

### 3. Technology Selection

| Komponen | Teknologi Terpilih | Peran dalam Sistem | Alasan Pemilihan |
| :--- | :--- | :--- | :--- |
| **UI / Frontend** | Streamlit `1.67.0` | Antarmuka web 3-tab, `st.data_editor` interaktif, kontrol periode, indikator kuota AI, dan antarmuka chat. | Mendukung tabel interaktif *Human-in-the-Loop*, ekspor CSV instan, dan pengujian antarmuka terotomatisasi via `AppTest`. |
| **Backend & Accounting Engine** | Python `3.14.3` + Pandas `3.1.1` | Pembersihan string Rupiah, filter rentang tanggal, agregasi HPP/OPEX, dan pemetaan keterlacakan baris (`traceability_map`). | Menjamin deviasi matematis **Rp 0** (bebas halusinasi angka LLM) dan memungkinkan rekonsiliasi audit per baris transaksi. |
| **AI / LLM Service** | Google Gemini API (`gemini-2.5-flash`) via `google-genai 3.0.0` | Penyusunan narasi eksekutif bulanan dan tanya-jawab rincian item belanja/penjualan terikat konteks. | Latensi rendah, pemahaman Bahasa Indonesia bisnis sangat baik, dan efisien dalam pemakaian token untuk skala UMKM/manufaktur. |
| **Safety & Cost Control** | Regex Guardrails + `AIQuotaManager` (SHA-256 Cache) | Sanitasi input (500 karakter), blokir *prompt injection* ID/EN, batas kuota sesi (15 panggilan), *cooldown* (2 detik), dan saklar on/off AI. | Melindungi kunci/kuota API dari penyalahgunaan sekaligus menjamin kontinuitas operasional 100% saat offline atau tanpa API key. |
| **Data & Testing** | CSV / OpenPyXL `3.1.5` + Pytest `9.2.0` | Kompatibilitas berkas kerja harian Lokality serta verifikasi regresi otomatis (18 unit test + `AppTest`). | Adopsi langsung oleh staf admin tanpa migrasi database rumit serta kepastian kualitas rilis kode. |

---

### 4. Hubungan Antar-Artefak
1. **BRD ↔ User Flow:** Seluruh kebutuhan pengguna (`UN-01` s/d `UN-05`) dan skenario utama (`UC-01` s/d `UC-04`) direpresentasikan secara utuh mulai dari pemilihan periode di sidebar, koreksi manual di Tab 1, *drill-down* audit PnL di Tab 2, hingga konsultasi rincian bahan baku di Tab 3.
2. **User Flow ↔ Architecture:** Setiap simpul keputusan pada *User Flow* dipetakan satu-ke-satu ke modul kode terisolasi (`validator.py`, `categorizer.py`, `pnl_engine.py`, `guardrails.py`, `quota_manager.py`, `chatbot.py`), memudahkan pengujian unit dan pemeliharaan jangka panjang.
