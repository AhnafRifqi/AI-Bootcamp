"""Membangun FAISS index dari knowledge base FAQ e-commerce.

Alur: Ingest (baca CSV) -> Embed (Gemini Embeddings API) -> Store (FAISS).

Jalankan dari root project:
    python src/build_index.py

Output:
    data/faiss_index.index   # index FAISS (IndexFlatL2, vektor ternormalisasi)
    data/faq_metadata.json   # metadata FAQ sebaris dengan urutan vektor di index
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai

ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / 'data' / 'ecommerce_faq_knowledge_base.csv'
INDEX_PATH = ROOT / 'data' / 'faiss_index.index'
METADATA_PATH = ROOT / 'data' / 'faq_metadata.json'

EMBEDDING_MODEL = 'gemini-embedding-001'
EMBEDDING_DIM = 3072


def with_quota_retry(fn, max_retries: int = 6, base_delay: float = 20.0):
    """Panggil fn(); retry untuk error rate-limit (429), timeout jaringan, dan error server (5xx)."""
    permanent_tags = ('NOT_FOUND', 'INVALID_ARGUMENT', 'UNAUTHENTICATED',
                      'PERMISSION_DENIED', 'API_KEY_INVALID')
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as exc:
            message = str(exc)
            if any(tag in message for tag in permanent_tags) or attempt >= max_retries:
                raise
            if '429' in message:
                match = re.search(r'retry in ([\d.]+)s', message)
                delay = float(match.group(1)) + 2 if match else base_delay * attempt
                print(f'  Kuota API terlampaui (429) - tunggu {delay:.0f}s, coba lagi ({attempt}/{max_retries - 1})...')
            else:
                delay = 15
                print(f'  Gangguan API ({message[:60]}) - tunggu {delay}s, coba lagi ({attempt}/{max_retries - 1})...')
            time.sleep(delay)


def main() -> None:
    # API key: pakai env var, atau ambil dari .env di root project
    for env_path in (ROOT / '.env', Path('.env')):
        if env_path.exists():
            load_dotenv(env_path)
            break
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

    # --- Ingest: muat knowledge base (read-only) ---
    df = pd.read_csv(KB_PATH)
    documents = ('Q: ' + df['question'] + '\nA: ' + df['answer']).tolist()
    print(f'Ingest: {len(documents)} entri FAQ dari {KB_PATH}')

    # --- Embed: ubah unit retrievable menjadi vektor (per batch) ---
    embeddings = []
    for start in range(0, len(documents), 100):
        batch = documents[start:start + 100]
        result = with_quota_retry(
            lambda: client.models.embed_content(model=EMBEDDING_MODEL, contents=batch)
        )
        embeddings.extend(np.array(e.values, dtype='float32') for e in result.embeddings)
        print(f'  Batch {start // 100 + 1}: {len(batch)} teks ter-embed')
    embeddings = np.vstack(embeddings)

    if embeddings.shape != (len(documents), EMBEDDING_DIM):
        raise ValueError(f'Shape embedding {embeddings.shape} != ({len(documents)}, {EMBEDDING_DIM})')
    print(f'Embed: shape {embeddings.shape} ({embeddings.dtype})')

    # --- Store: simpan ke FAISS + metadata sebaris ---
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    if index.ntotal != len(documents):
        raise ValueError(f'Jumlah vektor {index.ntotal} != jumlah entri {len(documents)}')

    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(
        json.dumps(df[['faq_id', 'category', 'question', 'answer']].to_dict(orient='records'),
                   ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'Store: {index.ntotal} vektor tersimpan di {INDEX_PATH}')
    print(f'Metadata: {METADATA_PATH}')


if __name__ == '__main__':
    sys.exit(main())
