from pathlib import Path

APP_NAME = "NiyamGuard Call Assistant Backend"
APP_VERSION = "1.0.0"
PYTHON_REQUIREMENT = "3.12"
SUPPORTED_LANGUAGES = {"english", "telugu", "hindi", "mixed"}
SUPPORTED_FORM_ID = "income_certificate"

APP_DIR = Path(__file__).resolve().parent
FORM_SCHEMA_PATH = APP_DIR / "data" / "income_certificate_form.json"
SESSION_STORAGE_PATH = APP_DIR / "storage" / "sessions.json"
