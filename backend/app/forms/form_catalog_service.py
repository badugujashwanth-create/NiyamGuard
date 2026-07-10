from app.models.form_models import FormCatalogItem, FormSchema
from app.forms.form_service import (
    find_service_suggestion,
    list_form_catalog,
    load_all_forms,
    load_form_schema,
    search_services,
)


def get_service_catalog() -> list[FormCatalogItem]:
    return list_form_catalog()


def get_detailed_forms() -> tuple[FormSchema, ...]:
    return load_all_forms()
