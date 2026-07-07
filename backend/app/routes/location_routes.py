from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.language_helper import detect_language
from app.services.location_helper import (
    location_help,
    search_location,
)

router = APIRouter(prefix="/api/location", tags=["location"])


class LocationHelpRequest(BaseModel):
    message: str = Field(min_length=1)
    language: str = "auto"


class ReverseLocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    language: str = "auto"


@router.get("/search")
def search(
    query: str | None = Query(default=None),
    pincode: str | None = Query(default=None),
) -> dict:
    matches = search_location(query=query, pincode=pincode)
    return {"success": True, "matches": matches}


@router.post("/help")
def help_with_location(request: LocationHelpRequest) -> dict:
    selected = None if request.language == "auto" else request.language
    language_info = detect_language(request.message, selected)
    guidance = location_help(request.message, str(language_info["language"]))
    return {
        "success": True,
        "detected_language": language_info["detected_language"],
        "language_code": language_info["language_code"],
        **guidance,
    }


@router.post("/reverse")
def reverse_location(request: ReverseLocationRequest) -> dict:
    selected = None if request.language == "auto" else request.language
    language_info = detect_language("", selected)
    language = str(language_info["language"])
    messages = {
        "telugu": (
            "Location permission వచ్చింది, కానీ ఈ MVPలో GPSతో ఖచ్చితమైన మండలం "
            "lookup అందుబాటులో లేదు. దయచేసి pincode లేదా గ్రామం పేరు చెప్పండి."
        ),
        "hindi": (
            "Location permission मिल गई, लेकिन इस MVP में GPS से सही मंडल lookup "
            "उपलब्ध नहीं है। कृपया pincode या गाँव का नाम बताइए।"
        ),
        "english": (
            "Location permission received, but exact mandal lookup is not available "
            "in this MVP. Please enter a pincode or village name."
        ),
    }
    return {
        "success": True,
        "detected_language": language_info["detected_language"],
        "language_code": language_info["language_code"],
        "reply": messages.get(language, messages["english"]),
        "matches": [],
        "auto_fill": False,
        "should_submit": False,
    }
