import json
from functools import lru_cache
from pathlib import Path

from app.config import FORM_SCHEMA_PATH
from app.models.form_models import FormSchema


@lru_cache(maxsize=1)
def load_income_certificate_form(path: Path = FORM_SCHEMA_PATH) -> FormSchema:
    with path.open("r", encoding="utf-8") as form_file:
        return FormSchema.model_validate(json.load(form_file))


def field_labels() -> dict[str, str]:
    return {field.key: field.label for field in load_income_certificate_form().fields}
