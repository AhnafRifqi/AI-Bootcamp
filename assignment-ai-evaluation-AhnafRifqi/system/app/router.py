"""
Router module untuk Helpdesk Agent (mini-agent).
Mendeteksi intent user (faq vs ticket_status) dan mengekstrak ticket_id,
lalu mengarahkan ke komponen yang sesuai (RAG atau tool call).
"""

import re

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from .tools import get_ticket_status
from .rag import build_index, semantic_search, generate_answer

_index = None
_df = None


def _get_index():
    global _index, _df
    if _index is None:
        _index, _df = build_index()
    return _index, _df


TICKET_KEYWORDS = [
    "status tiket",
    "cek tiket",
    "lihat tiket",
    "track tiket",
    "ticket status",
    "cek status",
    "lihat status",
    "status ticket",
    "nomor tiket",
    "no tiket",
    "tiket saya",
]

FAQ_KEYWORDS = [
    "cuti",
    "absen",
    "izin sakit",
    "password",
    "vpn",
    "login",
    "email",
    "akun",
    "akses",
    "laptop",
    "perangkat",
    "hardware",
    "software",
    "resign",
    "karyawan baru",
    "onboarding",
    "slip gaji",
    "gaji",
    "rekening",
    "asuransi",
    "reimbursement",
    "atasan",
    "hr",
    "kerja",
    "hybrid",
    "lembur",
    "jam kerja",
    "melahirkan",
    "paternity",
    "slack",
    "google meet",
    "workspace",
    "pelatihan",
    "tools internal",
]

TICKET_ID_PATTERN = re.compile(r"TICKET[-\s]?(\d{3,})", re.IGNORECASE)


def detect_intent(query: str) -> str:
    q = query.lower().strip()

    has_ticket_id = bool(TICKET_ID_PATTERN.search(q))
    has_ticket_kw = any(kw in q for kw in TICKET_KEYWORDS)
    has_faq_kw = any(kw in q for kw in FAQ_KEYWORDS)

    # Hybrid / Ambiguous: query memuat topik FAQ sekaligus keyword aksi tiket tanpa nomor tiket spesifik
    if has_ticket_kw and has_faq_kw and not has_ticket_id:
        return "hybrid"

    if has_ticket_id or has_ticket_kw:
        return "ticket_status"

    if has_faq_kw:
        return "faq"

    return "unknown"


def extract_ticket_id(query: str) -> str | None:
    match = TICKET_ID_PATTERN.search(query)
    if match:
        number = match.group(1)
        return f"TICKET-{number}"
    return None


@traceable(name="helpdesk_route", run_type="chain")
def route(query: str) -> dict:
    intent = detect_intent(query)

    if intent == "ticket_status":
        ticket_id = extract_ticket_id(query)
        if not ticket_id:
            return {
                "status": "error",
                "intent": "ticket_status",
                "data": "ID tiket tidak ditemukan dalam query. Mohon sertakan nomor tiket (contoh: TICKET-0042).",
            }

        result = get_ticket_status(ticket_id)
        if result is None:
            return {
                "status": "not_found",
                "intent": "ticket_status",
                "data": f"Tiket {ticket_id} tidak ditemukan dalam database.",
            }
        if "error" in result:
            return {
                "status": "error",
                "intent": "ticket_status",
                "data": result["error"],
            }

        return {
            "status": "success",
            "intent": "ticket_status",
            "data": result,
        }

    if intent == "hybrid":
        try:
            index, df = _get_index()
            context_items = semantic_search(index, df, query, top_k=3)
            faq_answer = generate_answer(context_items, query)
            ticket_note = (
                "\n\n---\n**[INFO] Panduan Status Tiket:** Untuk melacak progress atau status "
                "tiket kendala ini secara langsung, silakan sertakan nomor tiket Anda (contoh: 'TICKET-0042')."
            )
            return {
                "status": "success",
                "intent": "hybrid",
                "data": {
                    "answer": faq_answer + ticket_note,
                    "sources": [
                        {"faq_id": item["faq_id"], "question": item["question"]}
                        for item in context_items
                    ],
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "intent": "hybrid",
                "data": f"Gagal memproses pertanyaan campuran: {str(e)}",
            }

    if intent == "faq":
        try:
            index, df = _get_index()
            context_items = semantic_search(index, df, query, top_k=3)
            answer = generate_answer(context_items, query)
            return {
                "status": "success",
                "intent": "faq",
                "data": {
                    "answer": answer,
                    "sources": [
                        {"faq_id": item["faq_id"], "question": item["question"]}
                        for item in context_items
                    ],
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "intent": "faq",
                "data": f"Gagal memproses pertanyaan: {str(e)}",
            }

    return {
        "status": "error",
        "intent": "unknown",
        "data": "Maaf, saya tidak dapat memahami pertanyaan Anda. Mohon ajukan pertanyaan seputar kebijakan HR/IT atau cek status tiket (contoh: TICKET-0042).",
    }
