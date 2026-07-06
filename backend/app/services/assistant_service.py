from typing import Any

from app.models.assistant_models import AskResponse, SummaryResponse
from app.services.field_detector import VALID_FIELDS, detect_field
from app.services.form_service import field_labels, load_income_certificate_form
from app.services.guidance_engine import generate_guidance
from app.services.income_calculator import calculate_annual_income
from app.services.session_service import SessionService, session_service
from app.services.validator import validate_field


class AssistantService:
    def __init__(self, sessions: SessionService = session_service) -> None:
        self.sessions = sessions

    def ask(self, session_id: str, message: str, current_field: str | None) -> AskResponse:
        self.sessions.get(session_id)
        detected_field = detect_field(message, current_field)
        guidance = generate_guidance(message, detected_field)
        response = AskResponse(
            field=guidance.field,
            reply=guidance.reply,
            suggested_value=guidance.suggested_value,
            related_values=guidance.related_values,
            warning=guidance.warning,
            auto_fill=False,
            should_submit=False,
        )
        self.sessions.add_conversation_pair(session_id, message, response.reply)
        return response

    def summary(self, session_id: str, form_values: dict[str, Any]) -> SummaryResponse:
        self.sessions.get(session_id)
        schema = load_income_certificate_form()
        labels = field_labels()
        missing_fields = [
            item.key
            for item in schema.fields
            if item.required and (form_values.get(item.key) is None or not str(form_values[item.key]).strip())
        ]
        warnings = [f"{labels[field]} is required." for field in missing_fields]

        for field in VALID_FIELDS - set(missing_fields):
            if field in form_values:
                result = validate_field(field, form_values[field])
                if not result.valid:
                    warnings.append(result.message)

        monthly = form_values.get("monthly_income")
        annual = form_values.get("annual_income")
        if monthly and annual:
            try:
                expected_annual = calculate_annual_income(monthly)
                normalized_annual = str(annual).replace(",", "").strip()
                if expected_annual != normalized_annual:
                    warnings.append(
                        f"Annual income may not match monthly income multiplied by 12. "
                        f"For monthly income {monthly}, check whether annual income should be {expected_annual}."
                    )
            except ValueError:
                pass

        if missing_fields:
            summary = "Some required details are still missing."
        else:
            summary = (
                "Please review your details. "
                f"Applicant name is {form_values.get('applicant_name')}. "
                f"Father's name is {form_values.get('father_name')}. "
                f"Mobile number is {form_values.get('mobile_number')}. "
                f"District is {form_values.get('district')}. "
                f"Monthly income is {form_values.get('monthly_income')} and annual income is "
                f"{form_values.get('annual_income')}. Purpose is {form_values.get('purpose')}. "
                "If everything is correct, you can submit the application yourself."
            )
        return SummaryResponse(
            summary=summary,
            missing_fields=missing_fields,
            warnings=warnings,
            auto_fill=False,
            should_submit=False,
        )


assistant_service = AssistantService()
