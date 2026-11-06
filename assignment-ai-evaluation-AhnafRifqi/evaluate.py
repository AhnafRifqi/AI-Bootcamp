"""
Automation script to run 12 evaluation test scenarios against the IT Helpdesk Assistant API.
Records latency, response data, token estimates, and exports results to evaluation_results.csv.
"""

import time
import requests
import pandas as pd
from pathlib import Path

BASE_URL = "http://localhost:8000"
SCENARIOS_PATH = Path(__file__).parent / "evaluation" / "evaluation_test_scenarios.csv"
RESULTS_PATH = Path(__file__).parent / "evaluation" / "evaluation_results.csv"


def check_api_health():
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def run_evaluation():
    if not check_api_health():
        print(f"[-] Error: Backend API is not accessible at {BASE_URL}.")
        print("[!] Make sure the system is running: 'cd system && uvicorn app.main:app --port 8000'")
        return

    print(f"[+] Connected to Helpdesk API at {BASE_URL}")
    print(f"[+] Loading scenarios from {SCENARIOS_PATH}...")

    df_scenarios = pd.read_csv(SCENARIOS_PATH)
    results = []

    for idx, row in df_scenarios.iterrows():
        s_id = row["scenario_id"]
        category = row["category"]
        query = str(row["query"]).strip()
        focus = row["evaluation_focus"]
        expected = row["expected_behavior_note"]

        print(f"\n--> Running [{s_id}] ({category}): '{query}'")

        start_time = time.perf_counter()
        try:
            resp = requests.post(
                f"{BASE_URL}/ask",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            elapsed = time.perf_counter() - start_time
            status_code = resp.status_code

            if status_code == 200:
                data = resp.json()
                resp_text = str(data.get("data", ""))
                intent = data.get("intent", "")
                status = data.get("status", "")
                actual_response = f"[{intent}|{status}] {resp_text}"
            else:
                actual_response = f"[HTTP {status_code}] {resp.text}"

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            actual_response = f"[EXCEPTION] {str(e)}"

        # Rough token approximation: ~4 characters per token
        approx_tokens = int((len(query) + len(actual_response)) / 4)

        print(f"    Latency: {elapsed:.2f}s | Tokens (est): ~{approx_tokens}")
        print(f"    Response snippet: {actual_response[:100]}...")

        results.append({
            "scenario_id": s_id,
            "category": category,
            "query": query,
            "evaluation_focus": focus,
            "expected_behavior_note": expected,
            "actual_response": actual_response,
            "latency_seconds": round(elapsed, 3),
            "estimated_tokens": approx_tokens,
            "observation": "",
            "status": "Evaluated"
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(f"\n[+] Successfully recorded {len(results)} scenarios to {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()
