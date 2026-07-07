from fastapi import APIRouter, HTTPException, Query

from app.models.form_models import FormResponse, FormsResponse, ServicesResponse
from app.services.form_service import (
    list_form_catalog,
    load_form_schema,
    load_income_certificate_form,
    search_services,
)

router = APIRouter(tags=["forms"])


@router.get("/api/forms", response_model=FormsResponse)
def get_forms() -> FormsResponse:
    return FormsResponse(forms=list_form_catalog())


@router.get("/api/forms/income-certificate", response_model=FormResponse)
def get_income_certificate_form() -> FormResponse:
    return FormResponse(form=load_income_certificate_form())


@router.get("/api/forms/{form_id}", response_model=FormResponse)
def get_form(form_id: str) -> FormResponse:
    try:
        return FormResponse(form=load_form_schema(form_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Form not found.") from exc


@router.get("/api/services", response_model=ServicesResponse)
def get_services() -> ServicesResponse:
    return ServicesResponse(services=list_form_catalog())


@router.get("/api/services/search", response_model=ServicesResponse)
def search_available_services(q: str = Query(default="")) -> ServicesResponse:
    return ServicesResponse(services=search_services(q))
