"""
RAG module untuk Helpdesk Agent.
Membangun index FAISS dari knowledge base, melakukan semantic search,
dan menghasilkan jawaban melalui LLM (Gemini).
"""

import os
import time
import pandas as pd
import faiss
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-flash-latest"

_client = None


def _get_client():
    global _client
    if _client is None:
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY tidak ditemukan di environment variables.")
        _client = genai.Client(api_key=API_KEY)
    return _client


def _load_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "it_helpdesk_knowledge_base.csv")
    return pd.read_csv(csv_path)


def _embed_texts(client, texts: list[str], max_retries: int = 5) -> np.ndarray:
    all_embeddings = []
    batch_size = 50

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        for attempt in range(max_retries):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                )
                embs = [np.array(e.values, dtype=np.float32) for e in response.embeddings]
                all_embeddings.extend(embs)
                break
            except Exception:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt
                time.sleep(wait)

    return np.vstack(all_embeddings).astype(np.float32)


def build_index():
    df = _load_knowledge_base()
    texts = (df["question"].fillna("") + " " + df["answer"].fillna("")).tolist()

    client = _get_client()
    embeddings = _embed_texts(client, texts)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, df


def semantic_search(index, df, query: str, top_k: int = 3) -> list[dict]:
    client = _get_client()
    query_embedding = _embed_texts(client, [query])

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        row = df.iloc[idx]
        similarity = 1.0 / (1.0 + float(dist))
        results.append(
            {
                "faq_id": int(row["faq_id"]),
                "category": row["category"],
                "question": row["question"],
                "answer": row["answer"],
                "score": similarity,
            }
        )

    return results


def generate_answer(context_items: list[dict], query: str) -> str:
    client = _get_client()

    context_lines = []
    for item in context_items:
        context_lines.append(
            f"- Pertanyaan: {item['question']}\n  Jawaban: {item['answer']}"
        )
    context_text = "\n".join(context_lines) if context_lines else "(tidak ada konteks relevan)"

    prompt = f"""
Anda adalah asisten HR & IT Helpdesk yang ramah, profesional, dan akurat.

Tugas:
Jawab pertanyaan karyawan berdasarkan konteks knowledge base yang diberikan di bawah ini.
Gunakan HANYA informasi dari konteks tersebut. Jika informasi yang ditanyakan tidak tersedia
dalam konteks, sampaikan dengan jujur bahwa informasi tidak tersedia dan arahkan ke tim HR atau IT Support.

Konteks Knowledge Base:
{context_text}

Pertanyaan pengguna:
{query}

Format jawaban:
- Berikan jawaban yang jelas, ringkas, dan mudah dimengerti dalam bahasa Indonesia.
- Jika ada langkah-langkah, tulis dalam bentuk daftar (bullet points).
- Akhiri dengan penawaran bantuan lebih lanjut jika diperlukan.

Jawaban:
"""

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception:
            if attempt == 4:
                return "Maaf, Layanan LLM saat ini tidak tersedia."
            wait = 2 ** attempt
            time.sleep(wait)

    return "Maaf, Layanan LLM saat ini tidak tersedia setelah beberapa kali percobaan."
