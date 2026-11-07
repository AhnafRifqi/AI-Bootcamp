import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MOCK_DATA_DIR = DATA_DIR / "mock"
DOCS_DIR = PROJECT_ROOT / "docs"

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
APP_PORT = int(os.getenv("APP_PORT", "8501"))

# AI Quota & Safety Limits
MAX_AI_CALLS_PER_SESSION = int(os.getenv("MAX_AI_CALLS_PER_SESSION", "15"))
MIN_AI_COOLDOWN_SECONDS = float(os.getenv("MIN_AI_COOLDOWN_SECONDS", "2.0"))
MAX_QUERY_CHARS = int(os.getenv("MAX_QUERY_CHARS", "500"))

# Lokality Business Profile Constants
COMPANY_NAME = "PT Lokal Komoditi Indonesia"
BRAND_NAME = "Lokality"
PRODUCT_FOCUS = "Mi Gluten-Free Fortifikasi Tempe"
