import time
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/ask"

def test():
    print("Testing EVAL-09 (After Fix)...")
    q9 = "kenapa laptop saya lambat dan gimana cara cek tiket yang saya buat soal itu?"
    t0 = time.perf_counter()
    r9 = requests.post(BASE_URL, json={"query": q9})
    el9 = time.perf_counter() - t0
    d9 = r9.json()
    ans9 = d9.get("data", {}).get("answer", "")
    print(f"Status: {r9.status_code} | Intent: {d9.get('intent')} | Latency: {el9:.2f}s")
    print(f"Tokens est: {int((len(q9) + len(ans9))/4)}")
    print(f"Answer snippet:\n{ans9}\n")

    print("="*60)
    print("Testing EVAL-11 (After Fix)...")
    q11 = "Tolong jelaskan sedetail-detailnya seluruh kebijakan cuti, reset password, permintaan perangkat, dan proses onboarding sekaligus dalam satu jawaban."
    t0 = time.perf_counter()
    r11 = requests.post(BASE_URL, json={"query": q11})
    el11 = time.perf_counter() - t0
    d11 = r11.json()
    ans11 = d11.get("data", {}).get("answer", "")
    print(f"Status: {r11.status_code} | Intent: {d11.get('intent')} | Latency: {el11:.2f}s")
    print(f"Tokens est: {int((len(q11) + len(ans11))/4)}")
    print(f"Answer snippet:\n{ans11}\n")

if __name__ == "__main__":
    test()
