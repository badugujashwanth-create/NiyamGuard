import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR.parent / ".env")

APP_NAME = "NiyamGuard Call Assistant Backend"
APP_VERSION = "1.0.0"
PYTHON_REQUIREMENT = "3.12"
SUPPORTED_LANGUAGES = {"english", "telugu", "hindi", "mixed"}

FORMS_DIR = APP_DIR / "data" / "forms"
FORM_SCHEMA_PATH = FORMS_DIR / "income_certificate.json"
TELANGANA_LOCATIONS_PATH = APP_DIR / "data" / "telangana_locations.json"
SESSION_STORAGE_PATH = APP_DIR / "storage" / "sessions.json"
TTS_CACHE_DIR = APP_DIR / "storage" / "tts_cache"
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "auto").strip().lower() or "auto"
ENABLE_GTTS = os.getenv("ENABLE_GTTS", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
ENABLE_BHASHINI = os.getenv("ENABLE_BHASHINI", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
