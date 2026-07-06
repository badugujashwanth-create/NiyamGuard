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
}
TELUGU_ROMAN_PHRASES = {
    "aadhaar number tappu",
    "scholarship kosam",
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
}
HINDI_ROMAN_PHRASES = {"kis liye"}

INDIC_NUMBER_PHRASES = {
    "పదిహేను వేలు": 15_000,
    "పదిహేను వేల": 15_000,
    "పదిహేను వెయ్యి": 15_000,
    "पंद्रह हजार": 15_000,
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
) -> dict[str, str]:
    """Detect the citizen's language, using the selector as a fallback preference."""
    normalized = " ".join(message.casefold().split())
    selected: LanguageName | None = (
        selected_language
        if selected_language in LANGUAGE_CODES
        else None
    )

    if _contains_script(normalized, 0x0C00, 0x0C7F):
        return {"language": "telugu", "language_code": "te-IN"}
    if _contains_script(normalized, 0x0900, 0x097F):
        return {"language": "hindi", "language_code": "hi-IN"}

    tokens = set(re.findall(r"[a-z]+", normalized))
    telugu_markers = tokens & TELUGU_ROMAN_MARKERS
    hindi_markers = tokens & HINDI_ROMAN_MARKERS
    telugu_score = len(telugu_markers) + sum(
        2 for phrase in TELUGU_ROMAN_PHRASES if _has_phrase(normalized, phrase)
    )
    hindi_score = len(hindi_markers) + sum(
        2 for phrase in HINDI_ROMAN_PHRASES if _has_phrase(normalized, phrase)
    )

    if telugu_score and hindi_score:
        if selected in {"telugu", "hindi"}:
            language = selected
            return {
                "language": language,
                "language_code": LANGUAGE_CODES[language],
            }
        return {"language": "mixed", "language_code": "en-IN"}
    if telugu_score:
        return {"language": "telugu", "language_code": "te-IN"}
    if hindi_score:
        return {"language": "hindi", "language_code": "hi-IN"}

    language = selected or "english"
    return {
        "language": language,
        "language_code": LANGUAGE_CODES[language],
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
