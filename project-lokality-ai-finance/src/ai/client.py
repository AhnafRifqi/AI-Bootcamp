import os
from typing import Optional
from google import genai
from ..config import GEMINI_API_KEY, GEMINI_MODEL

_client: Optional[genai.Client] = None

def get_gemini_client() -> Optional[genai.Client]:
    """Initializes and returns a singleton Google GenAI client if GEMINI_API_KEY is available."""
    global _client
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return None
    
    if _client is None:
        try:
            _client = genai.Client(api_key=api_key)
        except Exception:
            _client = None
    return _client

def is_gemini_available() -> bool:
    """Returns True if Gemini API Key is configured."""
    return bool(GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", ""))
