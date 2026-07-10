from __future__ import annotations

import re


TELUGU_RE = re.compile(r"[\u0c00-\u0c7f]")
HINDI_RE = re.compile(r"[\u0900-\u097f]")
TELUGU_WORDS = {
    "enti",
    "entha",
    "ela",
    "kavali",
    "cheppandi",
    "patralu",
    "aadayam",
    "kosam",
    "ga",
}
HINDI_WORDS = {"kya", "kaise", "kitna", "kitne", "chahiye", "bataiye", "hai", "ke", "liye"}


def detect_language(text: str, requested: str = "auto") -> dict:
    if requested and requested != "auto":
        normalized = requested.strip().lower()
        return {
            "language": normalized,
            "language_code": {"telugu": "te-IN", "hindi": "hi-IN", "english": "en-IN"}.get(normalized, "en-IN"),
            "confidence": 1.0,
        }
    normalized = text.casefold()
    has_telugu_script = bool(TELUGU_RE.search(text))
    has_hindi_script = bool(HINDI_RE.search(text))
    words = set(re.findall(r"[a-zA-Z]+", normalized))
    telugu_hits = len(words & TELUGU_WORDS)
    hindi_hits = len(words & HINDI_WORDS)
    if has_telugu_script or telugu_hits >= 1:
        return {"language": "telugu", "language_code": "te-IN", "confidence": 0.92 if has_telugu_script else 0.78}
    if has_hindi_script or hindi_hits >= 2:
        return {"language": "hindi", "language_code": "hi-IN", "confidence": 0.92 if has_hindi_script else 0.78}
    if telugu_hits and hindi_hits:
        return {"language": "mixed", "language_code": "en-IN", "confidence": 0.6}
    return {"language": "english", "language_code": "en-IN", "confidence": 0.74}
