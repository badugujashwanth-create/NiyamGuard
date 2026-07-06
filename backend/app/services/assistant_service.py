from typing import Any

from app.models.assistant_models import AskResponse, SummaryResponse
from app.models.session_models import LanguagePreference
from app.services.field_detector import VALID_FIELDS, detect_field
from app.services.form_service import field_labels, load_income_certificate_form
from app.services.guidance_engine import generate_guidance
from app.services.income_calculator import calculate_annual_income
from app.services.language_helper import detect_language
from app.services.location_helper import (
    LOCATION_FIELDS,
    detect_location_intent,
    extract_pincode,
    location_help,
)
from app.services.session_service import SessionService, session_service
from app.services.validator import validate_field


def _required_warning(label: str, language: str) -> str:
    if language == "telugu":
        return f"{label} తప్పనిసరిగా నింపాలి."
    if language == "hindi":
        return f"{label} भरना आवश्यक है।"
    return f"{label} is required."


def _invalid_warning(label: str, message: str, language: str) -> str:
    if language == "telugu":
        return f"{label} విలువ సరైనది కాదు. దయచేసి సరిచూడండి."
    if language == "hindi":
        return f"{label} का मान सही नहीं है। कृपया जाँचें।"
    return message


def _income_mismatch_warning(
    monthly: Any, expected_annual: str, language: str
) -> str:
    if language == "telugu":
        return (
            "Annual income, monthly income × 12కి సరిపోలకపోవచ్చు. "
            f"Monthly income {monthly} అయితే annual income {expected_annual} కావాలి."
        )
    if language == "hindi":
        return (
            "Annual income, monthly income × 12 से मेल नहीं खा सकती। "
            f"Monthly income {monthly} है तो annual income {expected_annual} होनी चाहिए।"
        )
    return (
        "Annual income may not match monthly income multiplied by 12. "
        f"For monthly income {monthly}, check whether annual income should be "
        f"{expected_annual}."
    )


def _summary_text(
    form_values: dict[str, Any], missing_fields: list[str], language: str
) -> str:
    if missing_fields:
        if language == "telugu":
            return (
                "కొన్ని తప్పనిసరి వివరాలు ఇంకా నింపలేదు. ఆ వివరాలను మీరే టైప్ చేసి, "
                "తర్వాత మళ్లీ సరిచూడండి."
            )
        if language == "hindi":
            return (
                "कुछ आवश्यक विवरण अभी भी बाकी हैं। उन्हें स्वयं लिखकर फिर से जाँचें।"
            )
        return (
            "Some required details are still missing. Enter them yourself and "
            "review the form again."
        )

    if language == "telugu":
        return (
            "దయచేసి మీ వివరాలను సరిచూడండి. "
            f"Applicant name {form_values.get('applicant_name')}. "
            f"Father's name {form_values.get('father_name')}. "
            f"Mobile number {form_values.get('mobile_number')}. "
            f"Aadhaar number {form_values.get('aadhaar_number')}. "
            f"District {form_values.get('district')}, mandal "
            f"{form_values.get('mandal')}, గ్రామం {form_values.get('village')}. "
            f"Monthly income {form_values.get('monthly_income')}, annual income "
            f"{form_values.get('annual_income')}. Purpose {form_values.get('purpose')}. "
            f"పూర్తి చిరునామా {form_values.get('address')}. "
            "అన్నీ సరిగ్గా ఉంటే, applicationను మీరే మాన్యువల్‌గా submit చేయండి."
        )
    if language == "hindi":
        return (
            "कृपया अपने विवरण जाँचें। "
            f"Applicant name {form_values.get('applicant_name')}। "
            f"Father's name {form_values.get('father_name')}। "
            f"Mobile number {form_values.get('mobile_number')}। "
            f"Aadhaar number {form_values.get('aadhaar_number')}। "
            f"District {form_values.get('district')}, mandal "
            f"{form_values.get('mandal')}, गाँव {form_values.get('village')}। "
            f"Monthly income {form_values.get('monthly_income')} और annual income "
            f"{form_values.get('annual_income')}। Purpose {form_values.get('purpose')}। "
            f"पूरा पता {form_values.get('address')}। "
            "अगर सब सही है, तो application स्वयं submit करें।"
        )
    return (
        "Please review your details. "
        f"Applicant name is {form_values.get('applicant_name')}. "
        f"Father's name is {form_values.get('father_name')}. "
        f"Mobile number is {form_values.get('mobile_number')}. "
        f"Aadhaar number is {form_values.get('aadhaar_number')}. "
        f"District is {form_values.get('district')}, mandal is "
        f"{form_values.get('mandal')}, and village is {form_values.get('village')}. "
        f"Monthly income is {form_values.get('monthly_income')} and annual income is "
        f"{form_values.get('annual_income')}. Purpose is {form_values.get('purpose')}. "
        f"Address is {form_values.get('address')}. "
        "If everything is correct, you can submit the application yourself."
    )


class AssistantService:
    def __init__(self, sessions: SessionService = session_service) -> None:
        self.sessions = sessions

    def ask(
        self,
        session_id: str,
        message: str,
        current_field: str | None,
        selected_language: LanguagePreference = "auto",
    ) -> AskResponse:
        session = self.sessions.get(session_id)
        language_preference = (
            selected_language
            if selected_language != "auto"
            else session.last_detected_language
        )
        language_info = detect_language(
            message,
            language_preference,
        )
        language = str(language_info["detected_language"])
        location_requested = detect_location_intent(message) or (
            session.last_field in LOCATION_FIELDS
            and extract_pincode(message) is not None
        )
        location_matches: list[dict[str, str]] = []
        if location_requested:
            location_guidance = location_help(message, language)
            location_matches = location_guidance["matches"]
            detected_field = "mandal"
            reply = location_guidance["reply"]
            suggested_value = None
            related_values = (
                {
                    "district": location_matches[0]["district"],
                    "mandal": location_matches[0]["mandal"],
                    "village": location_matches[0]["village_or_locality"],
                }
                if len(location_matches) == 1
                else {}
            )
            warning = None
        else:
            detected_field = detect_field(
                message,
                current_field,
                session.last_field,
            )
            guidance = generate_guidance(
                message,
                detected_field,
                language,
            )
            reply = guidance.reply
            suggested_value = guidance.suggested_value
            related_values = guidance.related_values
            warning = guidance.warning
        response = AskResponse(
            field=detected_field,
            reply=reply,
            suggested_value=suggested_value,
            related_values=related_values,
            location_matches=location_matches,
            warning=warning,
            detected_language=language,
            language_code=language_info["language_code"],
            auto_fill=False,
            should_submit=False,
        )
        self.sessions.add_conversation_pair(
            session_id,
            message,
            response.reply,
            detected_language=response.detected_language,
            field=response.field,
        )
        return response

    def summary(
        self,
        session_id: str,
        form_values: dict[str, Any],
        selected_language: LanguagePreference = "auto",
    ) -> SummaryResponse:
        session = self.sessions.get(session_id)
        language_preference = (
            selected_language
            if selected_language != "auto"
            else session.last_detected_language
        )
        language_info = detect_language(
            "",
            language_preference,
        )
        language = str(language_info["detected_language"])
        schema = load_income_certificate_form()
        labels = field_labels()
        missing_fields = [
            item.key
            for item in schema.fields
            if item.required and (form_values.get(item.key) is None or not str(form_values[item.key]).strip())
        ]
        warnings = [
            _required_warning(labels[field], language) for field in missing_fields
        ]

        for field in VALID_FIELDS - set(missing_fields):
            if field in form_values:
                result = validate_field(field, form_values[field])
                if not result.valid:
                    warnings.append(
                        _invalid_warning(labels[field], result.message, language)
                    )

        monthly = form_values.get("monthly_income")
        annual = form_values.get("annual_income")
        if monthly and annual:
            try:
                expected_annual = calculate_annual_income(monthly)
                normalized_annual = str(annual).replace(",", "").strip()
                if expected_annual != normalized_annual:
                    warnings.append(
                        _income_mismatch_warning(
                            monthly,
                            expected_annual,
                            language,
                        )
                    )
            except ValueError:
                pass

        summary = _summary_text(form_values, missing_fields, language)
        return SummaryResponse(
            summary=summary,
            missing_fields=missing_fields,
            warnings=warnings,
            detected_language=language,
            language_code=language_info["language_code"],
            auto_fill=False,
            should_submit=False,
        )


assistant_service = AssistantService()
