from typing import Any

from app.models.assistant_models import AskResponse, SummaryResponse
from app.models.session_models import LanguagePreference
from app.citizen_assistant.field_detector import VALID_FIELDS, detect_field
from app.forms.form_service import (
    field_labels,
    find_service_suggestion,
    load_form_schema,
)
from app.citizen_assistant.guidance_engine import generate_guidance
from app.citizen_assistant.income_calculator import calculate_annual_income
from app.citizen_assistant.language_helper import detect_language
from app.citizen_assistant.location_helper import (
    LOCATION_FIELDS,
    detect_location_intent,
    extract_pincode,
    location_help,
)
from app.citizen_assistant.session_service import SessionService, session_service
from app.citizen_assistant.validator import validate_field


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return not value
    return not str(value).strip()


def _localized(value: dict[str, str], language: str) -> str:
    return value.get(language) or value.get("english") or ""


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
    form_name: str,
    labels: dict[str, str],
    form_values: dict[str, Any],
    missing_fields: list[str],
    missing_documents: list[str],
    language: str,
) -> str:
    if missing_fields or missing_documents:
        if language == "telugu":
            return (
                "కొన్ని తప్పనిసరి వివరాలు లేదా documents ఇంకా పూర్తి కాలేదు. "
                "వాటిని మీరు స్వయంగా పూర్తి చేసి, తర్వాత మళ్లీ సరిచూడండి."
            )
        if language == "hindi":
            return (
                "कुछ जरूरी details या documents अभी बाकी हैं। उन्हें स्वयं पूरा करके फिर से जाँचें।"
            )
        return (
            "Some required details or documents are still missing. Enter or upload "
            "them yourself and review the form again."
        )

    visible_values = [
        f"{labels.get(key, key)}: {value}"
        for key, value in form_values.items()
        if not _is_empty(value) and key in labels
    ]
    details = "; ".join(visible_values[:16])
    if language == "telugu":
        return (
            f"{form_name} కోసం మీ వివరాలను దయచేసి మీరే సరిచూడండి. "
            f"{details}. అన్నీ సరిగ్గా ఉంటే మాత్రమే demo submit button నొక్కండి. "
            "AI application submit చేయదు."
        )
    if language == "hindi":
        return (
            f"{form_name} के लिए अपने details कृपया खुद जाँचें। "
            f"{details}. सब सही हो तभी demo submit button दबाएँ. AI application submit नहीं करता."
        )
    return (
        f"Please review your {form_name} details yourself. {details}. "
        "If everything is correct, you can use the demo submit button. "
        "The AI does not submit the application."
    )


def _document_warning(label: str, language: str) -> str:
    if language == "telugu":
        return f"{label} document upload చేయాలి."
    if language == "hindi":
        return f"{label} document upload करना जरूरी है."
    return f"{label} document is required."


def _uploaded_document_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return bool(value.get("name") or value.get("file_name") or value.get("uploaded"))
    return bool(value)


def _has_document_intent(message: str, detected_field: str | None) -> bool:
    normalized = message.casefold()
    return detected_field == "document_upload" or any(
        marker in normalized
        for marker in (
            "document",
            "upload",
            "proof",
            "photo",
            "file",
            "certificate ledu",
            "income proof",
            "address proof",
            "aadhaar upload",
            "karna hai",
            "cheyali",
        )
    )


def _document_guidance(
    message: str,
    current_field: str | None,
    current_document: str | None,
    form_id: str,
    language: str,
) -> tuple[str, str | None] | None:
    schema = load_form_schema(form_id)
    if not schema.required_documents:
        return None

    normalized = message.casefold()
    selected = None
    focused_document = current_document
    if not focused_document and current_field and current_field.startswith("document:"):
        focused_document = current_field.split(":", 1)[1]
    if focused_document:
        selected = next(
            (document for document in schema.required_documents if document.key == focused_document),
            None,
        )
    if selected is None:
        for document in schema.required_documents:
            searchable = " ".join(
                [
                    document.key.replace("_", " "),
                    document.label,
                    *document.examples,
                ]
            ).casefold()
            if any(part and part in normalized for part in searchable.split()):
                selected = document
                break

    if selected is None:
        required = [document.label for document in schema.required_documents if document.required]
        optional = [document.label for document in schema.required_documents if not document.required]
        if language == "telugu":
            reply = (
                f"ఈ formకు సాధారణంగా ఇవి upload చేయాలి: {', '.join(required)}. "
                "Documentsను మీరు స్వయంగా upload చేయాలి; AI file upload చేయదు."
            )
            if optional:
                reply += f" Optional documents: {', '.join(optional)}."
        elif language == "hindi":
            reply = (
                f"इस form में आम तौर पर ये documents upload करने हैं: {', '.join(required)}. "
                "Documents आपको खुद upload करने हैं; AI file upload नहीं करता."
            )
            if optional:
                reply += f" Optional documents: {', '.join(optional)}."
        else:
            reply = (
                f"For this form, upload these required documents: {', '.join(required)}. "
                "You must upload files manually; the AI does not upload documents."
            )
            if optional:
                reply += f" Optional documents: {', '.join(optional)}."
        return reply, None

    accepted = ", ".join(selected.accepted_file_types)
    examples = ", ".join(selected.examples) if selected.examples else selected.label
    help_text = _localized(selected.help, language)
    if language == "telugu":
        reply = (
            f"{selected.label} upload చేయాలి. {help_text} ఉదాహరణలు: {examples}. "
            f"Accepted file types: {accepted}. Max size {selected.max_size_mb} MB. "
            "Fileను మీరు స్వయంగా select చేసి upload చేయాలి. AI file upload చేయదు."
        )
    elif language == "hindi":
        reply = (
            f"{selected.label} upload करना है. {help_text} उदाहरण: {examples}. "
            f"Accepted file types: {accepted}. Max size {selected.max_size_mb} MB. "
            "File आपको खुद select करके upload करना है. AI file upload नहीं करता."
        )
    else:
        reply = (
            f"Upload {selected.label}. {help_text} Examples: {examples}. "
            f"Accepted file types: {accepted}. Max size {selected.max_size_mb} MB. "
            "Choose and upload the file manually. The AI does not upload files."
        )
    return reply, selected.key


def _service_suggestion_reply(message: str, language: str) -> tuple[str, str, str] | None:
    suggestion = find_service_suggestion(message)
    if suggestion is None:
        return None
    if not suggestion.has_detailed_schema or suggestion.status == "catalog_only":
        if language == "telugu":
            reply = (
                f"{suggestion.service_name} service à°•à°¾à°µà°¾à°²à°¿ à°…à°¨à°¿ à°…à°¨à°¿à°ªà°¿à°¸à±à°¤à±‹à°‚à°¦à°¿. "
                "à°ˆ service à°•à±‹à°¸à°‚ general requirements à°¨à±‡à°¨à± à°šà±†à°ªà±à°ªà°—à°²à°¨à±, à°•à°¾à°¨à±€ detailed guided form à°‡à°‚à°•à°¾ coming soon."
            )
        elif language == "hindi":
            reply = (
                f"à¤†à¤ªà¤•à¥‹ {suggestion.service_name} service à¤šà¤¾à¤¹à¤¿à¤ à¤²à¤—à¤¤à¤¾ à¤¹à¥ˆ. "
                "à¤®à¥ˆà¤‚ general requirements à¤¬à¤¤à¤¾ à¤¸à¤•à¤¤à¤¾ à¤¹à¥‚à¤, à¤²à¥‡à¤•à¤¿à¤¨ detailed guided form à¤…à¤­à¥€ coming soon à¤¹à¥ˆ."
            )
        else:
            reply = (
                f"It looks like you may need {suggestion.service_name}. "
                "I can explain general requirements, but the detailed guided form is coming soon."
            )
        return reply, suggestion.form_id, suggestion.service_name
    if language == "telugu":
        reply = (
            f"మీ అవసరానికి {suggestion.service_name} form సరిపోవచ్చు అనిపిస్తోంది. "
            f"{suggestion.service_name} form open చేయాలా? మీరు button నొక్కితేనే form open అవుతుంది."
        )
    elif language == "hindi":
        reply = (
            f"आपकी जरूरत के लिए {suggestion.service_name} form सही हो सकता है. "
            f"{suggestion.service_name} form खोलना है? Button आप खुद दबाएँगे तभी form खुलेगा."
        )
    else:
        reply = (
            f"It looks like you may need the {suggestion.service_name} form. "
            "Open it only if you choose the Start Application button."
        )
    return reply, suggestion.form_id, suggestion.service_name


def _first_language_intro(language: str) -> str:
    if language == "telugu":
        return "సరే. నేను తెలుగులో సహాయం చేస్తాను. మీకు ఏ field దగ్గర doubt ఉంది?"
    if language == "hindi":
        return "ठीक है. मैं हिंदी में मदद करूँगा. आपको किस field में सहायता चाहिए?"
    return "Okay. I will help in English. Which field do you need help with?"


class AssistantService:
    def __init__(self, sessions: SessionService = session_service) -> None:
        self.sessions = sessions

    def ask(
        self,
        session_id: str,
        form_id: str,
        message: str,
        current_field: str | None,
        current_document: str | None,
        last_visible_section: str | None,
        selected_language: LanguagePreference = "auto",
    ) -> AskResponse:
        session = self.sessions.get(session_id)
        active_form_id = form_id or session.form_id or "income_certificate"
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
        if active_form_id == "catalog" or session.form_id == "catalog":
            service_suggestion = _service_suggestion_reply(message, language)
            if service_suggestion is not None:
                reply, suggested_form_id, suggested_form_name = service_suggestion
                response = AskResponse(
                    field=None,
                    reply=reply,
                    suggested_form_id=suggested_form_id,
                    suggested_form_name=suggested_form_name,
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
            document_guidance = (
                _document_guidance(message, current_field, current_document, active_form_id, language)
                if active_form_id != "catalog" and _has_document_intent(message, detected_field)
                else None
            )
            if document_guidance:
                reply, document_key = document_guidance
                detected_field = "document_upload"
                suggested_value = None
                related_values = {"document": document_key} if document_key else {}
                warning = None
            else:
                guidance = generate_guidance(
                    message,
                    detected_field,
                    language,
                )
                reply = guidance.reply
                suggested_value = guidance.suggested_value
                related_values = guidance.related_values
                warning = guidance.warning
        if not session.conversation and active_form_id != "catalog":
            reply = f"{_first_language_intro(language)} {reply}"
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
        form_id: str,
        form_values: dict[str, Any],
        uploaded_documents: dict[str, Any] | None = None,
        selected_language: LanguagePreference = "auto",
    ) -> SummaryResponse:
        session = self.sessions.get(session_id)
        active_form_id = form_id or session.form_id or "income_certificate"
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
        schema = load_form_schema(active_form_id)
        labels = field_labels(schema.form_id)
        uploaded_documents = uploaded_documents or {}
        missing_fields = [
            item.key
            for item in schema.fields
            if item.required and _is_empty(form_values.get(item.key))
        ]
        missing_documents = [
            document.key
            for document in schema.required_documents
            if document.required and not _uploaded_document_present(uploaded_documents.get(document.key))
        ]
        warnings = [
            _required_warning(labels[field], language) for field in missing_fields
        ]
        warnings.extend(
            _document_warning(document.label, language)
            for document in schema.required_documents
            if document.key in missing_documents
        )

        for field in (set(labels) & VALID_FIELDS) - set(missing_fields):
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

        summary = _summary_text(
            schema.form_name or schema.service_name,
            labels,
            form_values,
            missing_fields,
            missing_documents,
            language,
        )
        return SummaryResponse(
            summary=summary,
            missing_fields=missing_fields,
            missing_documents=missing_documents,
            warnings=warnings,
            detected_language=language,
            language_code=language_info["language_code"],
            auto_fill=False,
            should_submit=False,
        )


assistant_service = AssistantService()
