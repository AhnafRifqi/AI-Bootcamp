# -*- coding: utf-8 -*-
"""Pre-fill data/llm_predictions.csv dengan prediksi Gemini (helper sementara).

Mereplikasi persis prompt, model, dan train/test split dari notebook agar
hasilnya identik dengan yang akan dihasilkan notebook (membaca cache langsung).
"""
import os, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from google import genai
from google.genai import types
from sklearn.model_selection import train_test_split

PROJ = Path(r'd:\Rework Academy\Praktek\AI-Bootcamp\assignment-AI-Model-Experiment-AhnafRifqi')
load_dotenv(PROJ / '.env')
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
MODEL_NAME = 'gemini-3.8-flash'

df = pd.read_csv(PROJ / 'data' / 'customer_reviews_sentiment.csv')
X = df['review_text']
y = df['sentiment']
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
test_ids = df.loc[y_test.index, 'review_id'].reset_index(drop=True).tolist()
reviews = X_test.reset_index(drop=True).tolist()
print('Test reviews:', len(reviews))


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
        model=MODEL_NAME, contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return normalize_raw(resp.text)


def classify_retry(rid, review):
    for attempt in range(7):
        try:
            return rid, review, classify(review)
        except Exception as e:
            print(f'  rid={rid} try={attempt + 1} {type(e).__name__} -> sleep {4 * (attempt + 1)}s', flush=True)
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f'Gagal untuk rid={rid}')


results = []
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(classify_retry, rid, rev): rid for rid, rev in zip(test_ids, reviews)}
    done = 0
    for fut in as_completed(futs):
        rid, rev, pred = fut.result()
        results.append({'review_id': rid, 'review_text': rev, 'pred_llm': pred})
        done += 1
        if done % 5 == 0 or done == len(futs):
            pd.DataFrame(results).to_csv(PROJ / 'data' / 'llm_predictions.csv', index=False)
            print(f'progress {done}/{len(futs)}', flush=True)

cache = pd.DataFrame(results).sort_values('review_id')
cache.to_csv(PROJ / 'data' / 'llm_predictions.csv', index=False)
print('SELESAI total:', len(cache))
print(cache['pred_llm'].value_counts().to_string())