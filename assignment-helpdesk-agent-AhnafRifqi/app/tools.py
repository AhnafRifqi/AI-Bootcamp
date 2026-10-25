"""
Tool call module untuk Helpdesk Agent.
Menyediakan fungsi pencarian status tiket berdasarkan ticket_id pada data mock.
"""

import os
import pandas as pd


def _load_tickets():
    """Memuat data mock_tickets.csv dari folder data/."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "mock_tickets.csv")
    return pd.read_csv(csv_path)


def get_ticket_status(ticket_id: str) -> dict | None:
    """
    Mencari status tiket berdasarkan ticket_id.

    Args:
        ticket_id: ID tiket, misal "TICKET-0042".

    Returns:
        Dict berisi informasi tiket jika ditemukan, None jika tidak ditemukan.
        Fungsi ini tidak raise exception untuk mencegah aplikasi crash.
    """
    try:
        df = _load_tickets()
        ticket_id_clean = ticket_id.strip().upper()
        match = df[df["ticket_id"].str.strip().str.upper() == ticket_id_clean]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "ticket_id": row["ticket_id"],
            "employee_name": row["employee_name"],
            "category": row["category"],
            "subject": row["subject"],
            "status": row["status"],
            "last_update": row["last_update"],
        }
    except Exception as e:
        return {"error": f"Gagal mencari tiket: {str(e)}"}
