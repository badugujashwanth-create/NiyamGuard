import re
from typing import Literal

LanguageName = Literal["telugu", "hindi", "english", "mixed"]

LANGUAGE_CODES: dict[LanguageName, str] = {
    "telugu": "te-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
    "mixed": "en-IN",
}

TELUGU_ROMAN_MARKERS = {
    "lo",
    "emi",
    "rayali",
    "rayacha",
    "enduku",
    "kavali",
    "entha",
    "peru",
    "ooru",
    "mandal",
    "tappu",
    "kosam",
    "ani",
    "cheppandi",
    "ikkada",
    "ela",
    "petali",
    "cheyali",
    "teliyadu",
    "telidu",
    "enti",
    "ante",
    "nenu",
    "na",
    "veyyi",
    "velu",
    "padiheenu",
    "padihenu",
    "motham",
}
TELUGU_ROMAN_PHRASES = {
    "aadhaar number tappu",
    "scholarship kosam",
    "type cheyali",
    "na mandal",
    "padiheenu velu",
    "padihenu velu",
}
HINDI_ROMAN_MARKERS = {
    "kya",
    "likhna",
    "hai",
    "mein",
    "kitna",
    "naam",
    "pata",
    "galat",
    "bharna",
    "dalna",
    "likhu",
    "nahi",
    "mujhe",
    "kis",
    "liye",
    "hazar",
    "lakh",
    "pandrah",
}
HINDI_ROMAN_PHRASES = {"kis liye", "pandrah hazar"}
ENGLISH_MARKERS = {
    "what",
    "should",
    "enter",
    "where",
    "which",
    "how",
    "monthly",
    "annual",
    "income",
    "address",
    "please",
    "type",
}
ENGLISH_PHRASES = {
    "i don't know my mandal",
    "i do not know my mandal",
    "help me find my mandal",
}

INDIC_NUMBER_PHRASES = {
    "పదిహేను వేలు": 15_000,
    "పదిహేను వేల": 15_000,
    "పదిహేను వెయ్యి": 15_000,
    "पंद्रह हजार": 15_000,
    "padiheenu velu": 15_000,
    "padihenu velu": 15_000,
    "padiheenu veyyi": 15_000,
    "pandrah hazar": 15_000,
    "ek lakh": 100_000,
    "do lakh": 200_000,
}

ONES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}
TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
SCALES = {"hundred": 100, "thousand": 1_000, "lakh": 100_000, "lakhs": 100_000}
NUMBER_WORDS = set(ONES) | set(TENS) | set(SCALES) | {"and"}


def _contains_script(text: str, start: int, end: int) -> bool:
    return any(start <= ord(character) <= end for character in text)


def _has_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None


def detect_language(
    message: str, selected_language: str | None = None
) -> dict[str, str | float]:
    """Detect the citizen's language, using the selector as a fallback preference."""
    normalized = " ".join(message.casefold().split())
    selected: LanguageName | None = (
        selected_language
        if selected_language in LANGUAGE_CODES
        else None
    )

    if _contains_script(normalized, 0x0C00, 0x0C7F):
        return {
            "language": "telugu",
            "detected_language": "telugu",
            "language_code": "te-IN",
            "confidence": 1.0,
        }
    if _contains_script(normalized, 0x0900, 0x097F):
        return {
            "language": "hindi",
            "detected_language": "hindi",
            "language_code": "hi-IN",
            "confidence": 1.0,
        }

    tokens = set(re.findall(r"[a-z]+", normalized))
    telugu_markers = tokens & TELUGU_ROMAN_MARKERS
    hindi_markers = tokens & HINDI_ROMAN_MARKERS
    telugu_score = len(telugu_markers) + sum(
        2 for phrase in TELUGU_ROMAN_PHRASES if _has_phrase(normalized, phrase)
    )
    hindi_score = len(hindi_markers) + sum(
        2 for phrase in HINDI_ROMAN_PHRASES if _has_phrase(normalized, phrase)
    )
    english_score = len(tokens & ENGLISH_MARKERS) + sum(
        3 for phrase in ENGLISH_PHRASES if phrase in normalized
    )

    if english_score >= 3 and telugu_score <= 1 and not hindi_score:
        return {
            "language": "english",
            "detected_language": "english",
            "language_code": "en-IN",
            "confidence": 0.9,
        }
    if telugu_score and hindi_score:
        if telugu_score == hindi_score and selected in {"telugu", "hindi"}:
            language = selected
        else:
            language = "telugu" if telugu_score >= hindi_score else "hindi"
        return {
            "language": language,
            "detected_language": language,
            "language_code": LANGUAGE_CODES[language],
            "confidence": 0.75,
        }
    if telugu_score:
        return {
            "language": "telugu",
            "detected_language": "telugu",
            "language_code": "te-IN",
            "confidence": min(0.95, 0.65 + telugu_score * 0.08),
        }
    if hindi_score:
        return {
            "language": "hindi",
            "detected_language": "hindi",
            "language_code": "hi-IN",
            "confidence": min(0.95, 0.65 + hindi_score * 0.08),
        }
    if english_score >= 2:
        return {
            "language": "english",
            "detected_language": "english",
            "language_code": "en-IN",
            "confidence": min(0.95, 0.7 + english_score * 0.05),
        }

    language = selected or "english"
    return {
        "language": language,
        "detected_language": language,
        "language_code": LANGUAGE_CODES[language],
        "confidence": 0.6 if selected else 0.8,
    }


def _parse_words(words: list[str]) -> int | None:
    if not words:
        return None

    # Common Indian-English shorthand: "one fifty thousand" means 150 thousand.
    if (
        len(words) == 3
        and words[0] in ONES
        and words[1] in TENS
        and words[2] in {"thousand", "lakh", "lakhs"}
    ):
        prefix = ONES[words[0]] * 100 + TENS[words[1]]
        return prefix * SCALES[words[2]]

    total = 0
    current = 0
    saw_number = False
    for word in words:
        if word == "and":
            continue
        if word in ONES:
            current += ONES[word]
            saw_number = True
        elif word in TENS:
            current += TENS[word]
            saw_number = True
        elif word == "hundred":
            current = max(current, 1) * 100
            saw_number = True
        elif word in {"thousand", "lakh", "lakhs"}:
            total += max(current, 1) * SCALES[word]
            current = 0
            saw_number = True
        else:
            break
    return total + current if saw_number else None


def parse_spoken_number(text: str) -> int | None:
    """Extract one useful non-negative integer from digits or simple English words."""
    normalized = text.lower().replace("-", " ")
    digit_with_scale = re.search(
        r"(?<!\w)(\d[\d,\s]*\d|\d)\s*(thousand|lakh|lakhs|hazar|हजार|लाख|वेలు|వేలు|వెయ్యి)(?!\w)",
        normalized,
    )
    if digit_with_scale:
        digits = re.sub(r"\D", "", digit_with_scale.group(1))
        scale_word = digit_with_scale.group(2)
        if digits:
            if scale_word in {"lakh", "lakhs", "लाख"}:
                return int(digits) * 100_000
            return int(digits) * 1_000

    digit_match = re.search(r"(?<!\w)(\d[\d,\s]*\d|\d)(?!\w)", normalized)
    if digit_match:
        digits = re.sub(r"\D", "", digit_match.group(1))
        return int(digits) if digits else None

    for phrase, value in INDIC_NUMBER_PHRASES.items():
        if phrase in normalized:
            return value

    tokens = re.findall(r"[a-z]+", normalized)
    best: list[str] = []
    current: list[str] = []
    for token in tokens + ["<end>"]:
        if token in NUMBER_WORDS:
            current.append(token)
        else:
            if len(current) > len(best):
                best = current
            current = []
    return _parse_words(best)


def extract_digits(text: str) -> str:
    return "".join(re.findall(r"\d", text))
