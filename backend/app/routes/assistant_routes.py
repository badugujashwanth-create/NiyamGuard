from fastapi import APIRouter, HTTPException

from app.models.assistant_models import (
    AskRequest,
    AskResponse,
    SummaryRequest,
    SummaryResponse,
    ValidateRequest,
    ValidateResponse,
)
from app.services.assistant_service import assistant_service
from app.services.session_service import SessionNotFoundError
from app.services.validator import validate_field

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/ask", response_model=AskResponse)
def ask_assistant(request: AskRequest) -> AskResponse:
    try:
        return assistant_service.ask(request.session_id, request.message, request.current_field)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc


@router.post("/validate", response_model=ValidateResponse)
def validate_input(request: ValidateRequest) -> ValidateResponse:
    result = validate_field(request.field, request.value)
    return ValidateResponse(
        field=request.field,
        valid=result.valid,
        message=result.message,
        auto_fill=False,
        should_submit=False,
    )


@router.post("/summary", response_model=SummaryResponse)
def generate_summary(request: SummaryRequest) -> SummaryResponse:
    try:
        return assistant_service.summary(request.session_id, request.form_values)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc
