from fastapi import APIRouter, HTTPException, status

from app.models.session_models import (
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionResponse,
)
from app.services.session_service import SessionNotFoundError, session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(request: CreateSessionRequest) -> CreateSessionResponse:
    session = session_service.create(request.form_id, request.language)
    return CreateSessionResponse(
        session_id=session.session_id,
        form_id=session.form_id,
        language=session.language,
    )


@router.get("/{session_id}", response_model=GetSessionResponse)
def get_session(session_id: str) -> GetSessionResponse:
    try:
        session = session_service.get(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found.") from exc
    return GetSessionResponse(session=session)
