# -*- coding: utf-8 -*-
"""Helper sementara: melengkapi data/llm_predictions.csv dengan prediksi Gemini.

Mereplikasi persis prompt, model, dan train/test split (StratifiedGroupKFold
berbasis review_text) dari notebook agar hasilnya identik dengan notebook.

Efisiensi kuota: test set berisi 40 baris tetapi hanya 8 teks unik. API dipanggil
sekali per TEKS UNIK (maksimal 8 permintaan, muat dalam kuota free-tier harian),
kemudian hasil dipetakan ke semua baris dengan teks sama.

Resume: cache dibaca dulu; hanya teks unik yang belum punya prediksi valid yang
dipanggil ke API. Skrip aman dihentikan kapan pun (progress disimpan per teks).
"""
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sklearn.model_selection import StratifiedGroupKFold
import pandas as pd

PROJ = Path(r'd:\Rework Academy\Praktek\AI-Bootcamp\assignment-AI-Model-Experiment-AhnafRifqi')
load_dotenv(PROJ / '.env')

LABELS = ['negatif', 'positif']
MODEL_NAME = 'gemini-3.8-flash'
CACHE_PATH = PROJ / 'data' / 'llm_predictions.csv'

if not os.environ.get('GEMINI_API_KEY'):
    raise SystemExit('GEMINI_API_KEY tidak tersedia di .env')

# Reproduksi split yang sama persis dengan notebook (elemen grup = review_text).
df = pd.read_csv(PROJ / 'data' / 'customer_reviews_sentiment.csv')
y = df['sentiment']
groups = df['review_text']
splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
_, test_idx = next(splitter.split(df['review_text'], y, groups=groups))
test_df = df.iloc[test_idx].copy()
print('Test size:', len(test_df))


def normalize_raw(raw):
    if raw is None:
        return 'unknown'
    m = re.search(r'\b(positif|negatif)\b', raw.strip().lower())
    return m.group(1) if m else 'unknown'


def classify(review):
    prompt = (f'Klasifikasikan sentimen ulasan berikut sebagai "positif" atau "negatif".\n'
              'Jawab hanya dengan satu kata: positif atau negatif.\n\n'
              f'Ulasan: "{review}"\nSentimen:')
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return normalize_raw(resp.text)


client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
print('Model:', MODEL_NAME)

# Prediksi yang sudah valid per teks unik (dari cache ID+teks milik test set ini).
valid_keys = {(int(rid), str(rev)) for rid, rev in zip(test_df['review_id'], test_df['review_text'])}
text_pred = {}
if CACHE_PATH.exists():
    for row in pd.read_csv(CACHE_PATH).itertuples(index=False):
        try:
            key = (int(row.review_id), str(row.review_text))
        except (AttributeError, TypeError, ValueError):
            continue
        if key in valid_keys:
            pred = normalize_raw(row.pred_llm)
            if pred in LABELS:
                text_pred.setdefault(str(row.review_text), pred)

unique_reviews = sorted(test_df['review_text'].unique().tolist())
todo = [t for t in unique_reviews if t not in text_pred]
print(f'Prediksi valid dari cache: {len(text_pred)}/{len(unique_reviews)} teks unik; perlu API: {len(todo)}')

QUOTA_EXHAUSTED_STREAK = 0
for i, text in enumerate(todo, start=1):
    pred = 'unknown'
    for attempt in range(8):
        try:
            pred = classify(text)
            break
        except Exception as exc:
            msg = str(exc)[:160]
            print(f'  [{i}/{len(todo)}] error {type(exc).__name__}: {msg}', flush=True)
            if type(exc).__name__ == 'ClientError' and '429' in msg:
                QUOTA_EXHAUSTED_STREAK += 1
                if QUOTA_EXHAUSTED_STREAK >= 3:
                    print('Kuota harian habis (429). Progress tersimpan; jalankan ulang setelah reset.', flush=True)
                    raise SystemExit(1)
            time.sleep(5 * (attempt + 1))
    text_pred[text] = pred
    # Progress disimpan setelah tiap teks unik selesai diproses.
    rows = [
        {'review_id': rid, 'review_text': rev, 'pred_llm': text_pred.get(str(rev), 'unknown')}
        for rid, rev in zip(test_df['review_id'], test_df['review_text'])
    ]
    valid = pd.DataFrame([r for r in rows if r['pred_llm'] in LABELS])
    valid.to_csv(CACHE_PATH, index=False)
    print(f'progress {i}/{len(todo)} -> total teks unik terprediksi {sum(p in LABELS for p in text_pred.values())}/{len(unique_reviews)}', flush=True)

rows = [
    {'review_id': rid, 'review_text': rev, 'pred_llm': text_pred.get(str(rev), 'unknown')}
    for rid, rev in zip(test_df['review_id'], test_df['review_text'])
]
valid = pd.DataFrame([r for r in rows if r['pred_llm'] in LABELS])
valid.to_csv(CACHE_PATH, index=False)
unique_ok = sum(p in LABELS for p in text_pred.values())
print('SELESAI. Teks unik terprediksi:', f'{unique_ok}/{len(unique_reviews)}')
if unique_ok < len(unique_reviews):
    print('Kurang', len(unique_reviews) - unique_ok, 'teks unik -> jalankan ulang setelah kuota reset.')
else:
    print('Test set lengkap 100%: semua 40 baris mendapat prediksi LLM yang valid.')