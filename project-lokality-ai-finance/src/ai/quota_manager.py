import time
import hashlib
import json
from typing import Dict, Optional, Tuple, Any
from ..config import MAX_AI_CALLS_PER_SESSION, MIN_AI_COOLDOWN_SECONDS


class AIQuotaManager:
    """
    Manages LLM usage safeguards:
    1. Kill Switch (ai_enabled on/off toggle)
    2. Per-Session Call Quota Limit
    3. Minimum Cooldown Interval (rate limit protection)
    4. Deterministic Response Caching (prevents duplicate API token usage)
    """

    def __init__(
        self,
        max_calls: int = MAX_AI_CALLS_PER_SESSION,
        cooldown_seconds: float = MIN_AI_COOLDOWN_SECONDS,
        ai_enabled: bool = True,
    ):
        self.max_calls = max(1, int(max_calls))
        self.cooldown_seconds = max(0.0, float(cooldown_seconds))
        self.ai_enabled = bool(ai_enabled)
        self.calls_made: int = 0
        self.cache_hits: int = 0
        self.last_call_timestamp: float = 0.0
        self._cache: Dict[str, str] = {}

    @property
    def remaining_calls(self) -> int:
        return max(0, self.max_calls - self.calls_made)

    @staticmethod
    def build_cache_key(prefix: str, query: str, metrics_summary: Dict[str, Any]) -> str:
        raw = json.dumps(
            {"p": prefix, "q": query.strip().lower(), "s": metrics_summary},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def get_cached(self, cache_key: str) -> Optional[str]:
        if cache_key in self._cache:
            self.cache_hits += 1
            return self._cache[cache_key]
        return None

    def can_invoke_llm(self, cache_key: Optional[str] = None) -> Tuple[bool, str]:
        if cache_key and cache_key in self._cache:
            return True, "CACHE_HIT"

        if not self.ai_enabled:
            return False, "Saklar AI sedang dinonaktifkan oleh pengguna (Mode Deterministik Lokal aktif)."

        if self.calls_made >= self.max_calls:
            return (
                False,
                f"Batas kuota pemakaian AI sesi ini telah tercapai ({self.calls_made}/{self.max_calls} permintaan). "
                "Sistem otomatis beralih ke kalkulasi deterministik lokal.",
            )

        now = time.monotonic()
        elapsed = now - self.last_call_timestamp
        if self.last_call_timestamp > 0 and elapsed < self.cooldown_seconds:
            wait_left = round(self.cooldown_seconds - elapsed, 1)
            return (
                False,
                f"Jeda proteksi rate-limit aktif ({wait_left} detik tersisa). Menampilkan hasil deterministik lokal.",
            )

        return True, "OK"

    def record_call(self, cache_key: Optional[str] = None, response_text: Optional[str] = None) -> None:
        self.calls_made += 1
        self.last_call_timestamp = time.monotonic()
        if cache_key and response_text:
            self._cache[cache_key] = response_text

    def reset_quota(self) -> None:
        self.calls_made = 0
        self.last_call_timestamp = 0.0

    def status_dict(self) -> Dict[str, Any]:
        return {
            "ai_enabled": self.ai_enabled,
            "calls_made": self.calls_made,
            "max_calls": self.max_calls,
            "remaining_calls": self.remaining_calls,
            "cache_hits": self.cache_hits,
            "cached_entries": len(self._cache),
            "cooldown_seconds": self.cooldown_seconds,
        }
