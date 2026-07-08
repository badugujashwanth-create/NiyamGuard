from pydantic import BaseModel


class ReportMetadata(BaseModel):
    generated_at: str
    generated_by: str
    report_type: str
    filters: dict
    total_records: int
