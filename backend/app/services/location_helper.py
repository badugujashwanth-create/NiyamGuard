import json
import re
from pathlib import Path

from app.config import TELANGANA_LOCATIONS_PATH

LOCATION_FIELDS = {"district", "mandal", "village"}
LOCATION_INTENT_PHRASES = {
    "mandal teliyadu",
    "mandal telidu",
    "mandal name telidu",
    "na mandal enti",
    "mandal lo emi rayali",
    "mujhe mandal nahi pata",
    "mandal nahi pata",
    "don't know my mandal",
    "do not know my mandal",
    "find my mandal",
    "help me find my mandal",
    "మండలం తెలియదు",
    "मंडल नहीं पता",
}


def load_locations(
    data_path: Path = TELANGANA_LOCATIONS_PATH,
) -> list[dict[str, str]]:
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Location data is unavailable.") from exc
    if not isinstance(data, list):
        raise RuntimeError("Location data must be a list.")
    return [
        {
            "state": str(item.get("state", "")),
            "district": str(item.get("district", "")),
            "mandal": str(item.get("mandal", "")),
            "village_or_locality": str(item.get("village_or_locality", "")),
            "pincode": str(item.get("pincode", "")),
        }
        for item in data
        if isinstance(item, dict)
    ]


def detect_location_intent(message: str) -> bool:
    normalized = " ".join(message.casefold().replace("’", "'").split())
    if any(phrase in normalized for phrase in LOCATION_INTENT_PHRASES):
        return True
    return "mandal" in normalized and any(
        marker in normalized
        for marker in {
            "help",
            "which",
            "what",
            "enti",
            "emi",
            "teliy",
            "pata",
            "find",
            "pincode",
            "village",
        }
    )


def extract_pincode(message: str) -> str | None:
    match = re.search(r"(?<!\d)([1-9]\d{5})(?!\d)", message)
    return match.group(1) if match else None


def search_location(
    query: str | None = None,
    pincode: str | None = None,
) -> list[dict[str, str]]:
    locations = load_locations()
    normalized_pincode = (pincode or "").strip()
    normalized_query = " ".join((query or "").casefold().split())

    if normalized_pincode:
        return [
            location
            for location in locations
            if location["pincode"] == normalized_pincode
        ]
    if not normalized_query:
        return []
    return [
        location
        for location in locations
        if any(
            normalized_query in location[key].casefold()
            for key in ("district", "mandal", "village_or_locality", "pincode")
        )
    ]


def _ask_for_details(language: str) -> str:
    if language == "telugu":
        return (
            "పరవాలేదు. మీ మండలం తెలుసుకోవడానికి నేను సహాయం చేస్తాను. "
            "మీ గ్రామం లేదా ఊరి పేరు, లేదా pincode చెప్పగలరా?"
        )
    if language == "hindi":
        return (
            "कोई बात नहीं। मंडल पता करने में मैं मदद करूँगा। "
            "कृपया अपने गाँव का नाम या pincode बताइए।"
        )
    return (
        "No problem. I can help you identify the mandal. "
        "Please tell me your village name or pincode."
    )


def _no_match(language: str) -> str:
    if language == "telugu":
        return (
            "ఈ వివరాలతో మండలం ఖచ్చితంగా దొరకలేదు. మీ గ్రామం పేరు, దగ్గరలోని "
            "town, లేదా pincode మళ్లీ చెప్పండి. అవసరమైతే MeeSeva centerలో verify చేయండి."
        )
    if language == "hindi":
        return (
            "इन विवरणों से मंडल पक्का नहीं मिला। कृपया अपने गाँव का नाम, "
            "पास का town या pincode दोबारा बताइए और जरूरत हो तो MeeSeva center में जाँचें।"
        )
    return (
        "I could not identify the mandal from those details. Please provide the "
        "village name, nearby town, or pincode again, and confirm at a local office if needed."
    )


def _single_match(match: dict[str, str], language: str) -> str:
    district = match["district"]
    mandal = match["mandal"]
    locality = match["village_or_locality"]
    pincode = match["pincode"]
    if language == "telugu":
        return (
            f"మీ pincode {pincode} ప్రకారం, ఈ ప్రాంతం {locality}, మండలం {mandal}, "
            f"జిల్లా {district} పరిధిలో ఉండవచ్చు. దయచేసి confirm చేసిన తర్వాత "
            f"District fieldలో {district}, Mandal fieldలో {mandal} అని మీరే టైప్ చేయండి. "
            "ఖచ్చితంగా తెలియకపోతే దగ్గరలోని MeeSeva center లేదా local officeలో verify చేయండి."
        )
    if language == "hindi":
        return (
            f"आपके pincode {pincode} के आधार पर यह क्षेत्र {locality}, मंडल {mandal}, "
            f"जिला {district} हो सकता है। कृपया confirm करके District field में "
            f"{district} और Mandal field में {mandal} स्वयं लिखें। जरूरत हो तो "
            "MeeSeva center या local office में जाँचें।"
        )
    return (
        f"Based on pincode {pincode}, this may be {mandal} mandal, {district} "
        f"district ({locality}). Please confirm before manually entering "
        f"{district} in District and {mandal} in Mandal."
    )


def _multiple_matches(matches: list[dict[str, str]], language: str) -> str:
    options = " ".join(
        f"{index}. {match['village_or_locality']} — {match['mandal']} mandal — "
        f"{match['district']} district."
        for index, match in enumerate(matches, start=1)
    )
    if language == "telugu":
        return (
            "ఈ వివరాలకు ఒకటి కంటే ఎక్కువ results వచ్చాయి. మీ ప్రాంతం వీటిలో ఏది? "
            f"{options} దయచేసి confirm చేయండి; నేను ఏదీ auto-select చేయను."
        )
    if language == "hindi":
        return (
            "इन विवरणों के लिए एक से अधिक results मिले हैं। आपका क्षेत्र इनमें कौन सा है? "
            f"{options} कृपया confirm करें; कोई value अपने-आप नहीं चुनी जाएगी।"
        )
    return (
        "More than one location matched. Which of these is your area? "
        f"{options} Please confirm; no value will be selected automatically."
    )


def build_location_guidance(
    matches: list[dict[str, str]],
    language: str,
    *,
    had_lookup_details: bool = False,
) -> dict:
    if not matches:
        reply = _no_match(language) if had_lookup_details else _ask_for_details(language)
    elif len(matches) == 1:
        reply = _single_match(matches[0], language)
    else:
        reply = _multiple_matches(matches, language)
    return {
        "reply": reply,
        "matches": matches,
        "auto_fill": False,
        "should_submit": False,
    }


def location_help(
    message: str,
    language: str,
) -> dict:
    pincode = extract_pincode(message)
    normalized = " ".join(message.casefold().split())
    query = None
    if not pincode:
        for location in load_locations():
            for key in ("village_or_locality", "mandal", "district"):
                value = location[key]
                if value and value.casefold() in normalized:
                    query = value
                    break
            if query:
                break
    matches = search_location(query=query, pincode=pincode)
    return build_location_guidance(
        matches,
        language,
        had_lookup_details=bool(pincode or query),
    )
