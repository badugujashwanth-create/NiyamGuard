from __future__ import annotations

from typing import Any

from app.services.form_service import list_form_catalog


def _text(value: Any) -> str:
    return str(value or "").strip().casefold()


def _number(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return default


def _catalog_by_id() -> dict[str, dict]:
    return {item.form_id: item.model_dump() for item in list_form_catalog()}


def _result(
    catalog: dict[str, dict],
    form_id: str,
    *,
    score: float,
    why: str,
    eligibility: list[str],
    documents: list[str],
    source_label: str = "NiyamGuard demo service catalog",
) -> dict:
    service = catalog.get(form_id) or {}
    return {
        "form_id": form_id,
        "service_name": service.get("service_name") or form_id.replace("_", " ").title(),
        "department": service.get("department") or "Department not found",
        "category": service.get("category") or "Service",
        "why_it_may_match": why,
        "basic_eligibility": eligibility,
        "required_documents": documents,
        "confidence": round(score, 2),
        "status": service.get("status") or "catalog_only",
        "start_application_available": bool(service.get("has_detailed_schema")),
        "safe_note": "You may be eligible. Please verify with official rules before applying.",
        "source": {
            "type": "local_demo_rules",
            "label": source_label,
            "verified": False,
        },
    }


def recommend_schemes(profile: dict[str, Any]) -> dict:
    catalog = _catalog_by_id()
    purpose = _text(profile.get("purpose"))
    occupation = _text(profile.get("occupation"))
    category = _text(profile.get("category"))
    student = bool(profile.get("student"))
    widow = bool(profile.get("widow"))
    disability = bool(profile.get("disability"))
    age = _number(profile.get("age"))
    income = _number(profile.get("income"))
    results: list[dict] = []

    if student or "scholarship" in purpose or "education" in purpose:
        results.append(
            _result(
                catalog,
                "income_certificate",
                score=0.92,
                why="Scholarship and fee reimbursement workflows commonly require an income certificate.",
                eligibility=[
                    "Citizen needs income proof for a scholarship, admission, or welfare service.",
                    "Receiving scheme may apply separate income limits.",
                ],
                documents=["Aadhaar Card", "Income Proof", "Address Proof"],
                source_label="Verified GO-138 public rule plus local form catalog",
            )
        )
        results.append(
            _result(
                catalog,
                "caste_community_certificate",
                score=0.78 if category and category not in {"general", "none"} else 0.58,
                why="Education and scholarship workflows may require caste or community proof where applicable.",
                eligibility=["Use only if the citizen belongs to a category that requires official community proof."],
                documents=["Aadhaar Card", "School record if requested", "Parent/community proof if requested"],
            )
        )

    if "pension" in purpose or age >= 60:
        results.append(
            _result(
                catalog,
                "no_earning_member_certificate",
                score=0.74,
                why="Pension and family-support services may require proof that no earning member supports the household.",
                eligibility=["Commonly relevant for welfare and pension support workflows."],
                documents=["Aadhaar Card", "Family details", "Income or no-earning proof"],
            )
        )

    if widow:
        results.append(
            _result(
                catalog,
                "widow_pension_assistance",
                score=0.9,
                why="Widow status was selected and the service catalog includes widow pension preparation guidance.",
                eligibility=["Applicant should verify widow pension eligibility with the official department."],
                documents=["Aadhaar Card", "Death certificate of spouse", "Income proof", "Bank passbook"],
            )
        )

    if disability:
        results.append(
            _result(
                catalog,
                "disability_certificate_assistance",
                score=0.9,
                why="Disability status was voluntarily selected and certificate guidance may be relevant.",
                eligibility=["Medical board and department rules decide final eligibility."],
                documents=["Aadhaar Card", "Medical records", "Photograph", "Address proof"],
            )
        )

    if "farmer" in occupation or "agriculture" in purpose or "loan" in purpose:
        results.append(
            _result(
                catalog,
                "loan_eligibility_card",
                score=0.82,
                why="Agriculture, farmer benefit, or loan purpose matches loan eligibility card guidance.",
                eligibility=["Farmer or agriculture-linked applicant may need local revenue/agriculture verification."],
                documents=["Land record if applicable", "Aadhaar Card", "Bank passbook", "Income proof"],
            )
        )

    if income and income <= 800000 and ("ews" in purpose or category == "general"):
        results.append(
            _result(
                catalog,
                "ews_certificate",
                score=0.73,
                why="Income and category details may match EWS certificate use cases, subject to official criteria.",
                eligibility=["Final EWS eligibility depends on current official income and asset rules."],
                documents=["Income Proof", "Address Proof", "Aadhaar Card", "Asset declaration if requested"],
            )
        )

    if not results:
        results.append(
            _result(
                catalog,
                "residence_certificate",
                score=0.55,
                why="Residence certificate is a common supporting service when no more specific match is available.",
                eligibility=["Citizen needs address or local residence proof."],
                documents=["Aadhaar Card", "Address Proof", "Photograph if requested"],
            )
        )

    unique: dict[str, dict] = {}
    for result in sorted(results, key=lambda item: item["confidence"], reverse=True):
        unique.setdefault(result["form_id"], result)
    return {
        "success": True,
        "profile_summary": {
            "age": age or None,
            "income": income or None,
            "student": student,
            "purpose": profile.get("purpose") or None,
            "district": profile.get("district") or None,
        },
        "recommendations": list(unique.values())[:5],
        "limitations": "Demo recommendations are guidance only and do not replace official eligibility verification.",
    }
