from fastapi import APIRouter

from app.models.form_models import FormResponse
from app.services.form_service import load_income_certificate_form

router = APIRouter(prefix="/api/forms", tags=["forms"])


@router.get("/income-certificate", response_model=FormResponse)
def get_income_certificate_form() -> FormResponse:
    return FormResponse(form=load_income_certificate_form())
