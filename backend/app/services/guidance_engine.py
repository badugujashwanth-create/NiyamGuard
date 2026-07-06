from dataclasses import dataclass, field

from app.services.income_calculator import calculate_annual_income, calculate_monthly_income
from app.services.language_helper import extract_digits, parse_spoken_number
from app.services.validator import validate_field


@dataclass(frozen=True)
class Guidance:
    field: str | None
    reply: str
    suggested_value: str | None = None
    related_values: dict[str, str] = field(default_factory=dict)
    warning: str | None = None
    auto_fill: bool = False
    should_submit: bool = False


def _reply_language(language: str) -> str:
    return language if language in {"telugu", "hindi"} else "english"


def _unknown_guidance(language: str) -> Guidance:
    replies = {
        "english": (
            "Sure, I will help you. Please tell me which field you are filling now, "
            "for example Mobile Number, Aadhaar Number, Monthly Income, Annual Income, "
            "Purpose, or Address."
        ),
        "telugu": (
            "సరే, నేను సహాయం చేస్తాను. మీరు ఏ ఫీల్డ్ నింపుతున్నారో చెప్పండి. "
            "ఉదాహరణకు Mobile Number, Aadhaar Number, Monthly Income, Annual Income, "
            "Purpose లేదా Address."
        ),
        "hindi": (
            "ठीक है, मैं मदद करूँगा। कृपया बताइए कि आप कौन सा field भर रहे हैं, "
            "जैसे Mobile Number, Aadhaar Number, Monthly Income, Annual Income, "
            "Purpose या Address।"
        ),
    }
    return Guidance(field=None, reply=replies[_reply_language(language)])


def _missing_income_guidance(field_name: str, language: str) -> Guidance:
    replies = {
        "english": (
            "Please repeat the income amount clearly, for example fifteen thousand or 15000."
        ),
        "telugu": (
            "ఆదాయ మొత్తాన్ని స్పష్టంగా మళ్లీ చెప్పండి. ఉదాహరణకు పదిహేను వేలు లేదా 15000."
        ),
        "hindi": (
            "कृपया आय की राशि साफ़-साफ़ दोबारा बताइए, जैसे पंद्रह हजार या 15000।"
        ),
    }
    warnings = {
        "english": "Income must be a number greater than 0.",
        "telugu": "ఆదాయం 0 కంటే ఎక్కువ సంఖ్యగా ఉండాలి.",
        "hindi": "आय 0 से बड़ी संख्या होनी चाहिए।",
    }
    reply_language = _reply_language(language)
    return Guidance(
        field=field_name,
        reply=replies[reply_language],
        warning=warnings[reply_language],
    )


def _income_guidance(message: str, detected_field: str, language: str) -> Guidance:
    amount = parse_spoken_number(message)
    if amount is None or amount <= 0:
        return _missing_income_guidance(detected_field, language)

    reply_language = _reply_language(language)
    normalized = message.casefold()
    if detected_field == "annual_income":
        if "monthly" in normalized or "per month" in normalized:
            annual = calculate_annual_income(amount)
            replies = {
                "english": (
                    f"For {amount} monthly income, annual income is {annual}. "
                    f"You can enter {annual} in the Annual Income field."
                ),
                "telugu": (
                    f"మీ monthly income {amount} అయితే, annual income {annual} అవుతుంది. "
                    f"Annual Income ఫీల్డ్‌లో {annual} అని టైప్ చేయండి."
                ),
                "hindi": (
                    f"अगर आपकी monthly income {amount} है, तो annual income {annual} होगी। "
                    f"Annual Income field में {annual} लिखें।"
                ),
            }
            return Guidance(
                field="annual_income",
                reply=replies[reply_language],
                suggested_value=annual,
                related_values={"monthly_income": str(amount)},
            )

        monthly = calculate_monthly_income(amount)
        replies = {
            "english": f"You can enter {amount} in the Annual Income field.",
            "telugu": f"Annual Income ఫీల్డ్‌లో {amount} అని టైప్ చేయవచ్చు.",
            "hindi": f"आप Annual Income field में {amount} लिख सकते हैं।",
        }
        return Guidance(
            field="annual_income",
            reply=replies[reply_language],
            suggested_value=str(amount),
            related_values={"monthly_income": monthly},
        )

    annual = calculate_annual_income(amount)
    replies = {
        "english": (
            f"You can enter {amount} in the Monthly Income field. If the form also asks "
            f"Annual Income, you can enter {annual} because {amount} multiplied by 12 is {annual}."
        ),
        "telugu": (
            f"మీరు Monthly Income ఫీల్డ్‌లో {amount} అని టైప్ చేయవచ్చు. "
            f"Annual Income కూడా అడిగితే, {annual} అని టైప్ చేయండి. "
            f"ఎందుకంటే {amount} × 12 = {annual}."
        ),
        "hindi": (
            f"आप Monthly Income field में {amount} लिख सकते हैं। अगर Annual Income भी "
            f"पूछी गई है, तो {annual} लिखें, क्योंकि {amount} × 12 = {annual}।"
        ),
    }
    return Guidance(
        field="monthly_income",
        reply=replies[reply_language],
        suggested_value=str(amount),
        related_values={"annual_income": annual},
    )


def _identity_number_guidance(
    message: str, field_name: str, language: str
) -> Guidance:
    digits = extract_digits(message)
    expected = 10 if field_name == "mobile_number" else 12
    label = "Mobile number" if field_name == "mobile_number" else "Aadhaar number"
    reply_language = _reply_language(language)
    warning_templates = {
        "english": f"{label} must be {expected} digits.",
        "telugu": f"{label} {expected} digits ఉండాలి.",
        "hindi": f"{label} {expected} digits का होना चाहिए।",
    }

    if not digits:
        replies = {
            "english": f"Please say or type the {expected}-digit {label.lower()} clearly.",
            "telugu": f"దయచేసి {expected}-digit {label.lower()}ను స్పష్టంగా చెప్పండి లేదా టైప్ చేయండి.",
            "hindi": f"कृपया {expected}-digit {label.lower()} साफ़-साफ़ बोलें या लिखें।",
        }
        return Guidance(
            field=field_name,
            reply=replies[reply_language],
            warning=warning_templates[reply_language],
        )

    validation = validate_field(field_name, digits)
    if not validation.valid:
        digit_count = len(digits)
        replies = {
            "english": (
                f"{validation.message} Please check and enter the correct "
                f"{expected}-digit {label.lower()}."
            ),
            "telugu": (
                f"ఈ {label.lower()}లో {digit_count} digits మాత్రమే ఉన్నాయి. "
                f"{label} {expected} digits ఉండాలి. దయచేసి సరైన "
                f"{expected}-digit number టైప్ చేయండి."
            ),
            "hindi": (
                f"इस {label.lower()} में केवल {digit_count} digits हैं। "
                f"{label} {expected} digits का होना चाहिए। कृपया सही "
                f"{expected}-digit number लिखें।"
            ),
        }
        return Guidance(
            field=field_name,
            reply=replies[reply_language],
            warning=warning_templates[reply_language],
        )

    replies = {
        "english": (
            f"This {label.lower()} has {expected} digits. "
            "You can type it manually after checking it."
        ),
        "telugu": (
            f"ఈ {label.lower()}లో {expected} digits ఉన్నాయి. "
            "ఒకసారి సరిచూసుకుని మీరు దానిని మాన్యువల్‌గా టైప్ చేయండి."
        ),
        "hindi": (
            f"इस {label.lower()} में {expected} digits हैं। "
            "जाँचने के बाद इसे स्वयं लिखें।"
        ),
    }
    return Guidance(
        field=field_name,
        reply=replies[reply_language],
        suggested_value=digits,
    )


def _purpose_guidance(message: str, language: str) -> Guidance:
    purposes = {
        "scholarship": "Scholarship",
        "college admission": "College Admission",
        "admission": "College Admission",
        "job": "Job",
        "pension": "Pension",
    }
    normalized = message.casefold()
    selected = next((value for key, value in purposes.items() if key in normalized), None)
    reply_language = _reply_language(language)
    if selected:
        replies = {
            "english": (
                f"Yes. If you need the income certificate for {selected.lower()}, "
                f"you can enter {selected} in the Purpose of Certificate field."
            ),
            "telugu": (
                f"అవును. మీకు income certificate {selected.lower()} కోసం కావాలంటే, "
                f"Purpose of Certificate ఫీల్డ్‌లో “{selected}” అని టైప్ చేయండి."
            ),
            "hindi": (
                f"हाँ। अगर आपको income certificate {selected.lower()} के लिए चाहिए, "
                f"तो Purpose of Certificate field में “{selected}” लिख सकते हैं।"
            ),
        }
        return Guidance(
            field="purpose",
            reply=replies[reply_language],
            suggested_value=selected,
        )

    replies = {
        "english": (
            "Purpose means why you need the certificate. You can type a short reason such as "
            "Scholarship, College Admission, Job, or Pension."
        ),
        "telugu": (
            "Purpose అంటే మీకు certificate ఎందుకు కావాలో చెప్పడం. Scholarship, "
            "College Admission, Job లేదా Pension వంటి చిన్న కారణాన్ని టైప్ చేయండి."
        ),
        "hindi": (
            "Purpose का अर्थ है कि आपको certificate क्यों चाहिए। Scholarship, "
            "College Admission, Job या Pension जैसा छोटा कारण लिखें।"
        ),
    }
    return Guidance(field="purpose", reply=replies[reply_language])


SIMPLE_FIELD_REPLIES = {
    "english": {
        "address": (
            "In the Address field, enter your house number, street name, village or city, "
            "mandal, district, and pin code. Example: House No 1-2-33, Main Road, "
            "Ameerpet, Hyderabad, 500016."
        ),
        "applicant_name": "Enter your full name as it appears on Aadhaar or another official record.",
        "father_name": "Enter your father's full name as it appears on official records.",
        "district": "Enter the name of the district where you live.",
        "mandal": "Enter the name of the mandal where you live.",
        "village": "Enter your village or town name.",
    },
    "telugu": {
        "address": (
            "Address ఫీల్డ్‌లో మీ house number, street, village లేదా city, mandal, "
            "district మరియు pin code టైప్ చేయండి."
        ),
        "applicant_name": (
            "Aadhaar లేదా మరో అధికారిక రికార్డులో ఉన్నట్లే మీ పూర్తి పేరును టైప్ చేయండి."
        ),
        "father_name": "అధికారిక రికార్డులో ఉన్నట్లే మీ తండ్రి పూర్తి పేరును టైప్ చేయండి.",
        "district": "మీరు నివసించే district పేరును టైప్ చేయండి.",
        "mandal": "మీరు నివసించే mandal పేరును టైప్ చేయండి.",
        "village": "మీ village లేదా town పేరును టైప్ చేయండి.",
    },
    "hindi": {
        "address": (
            "Address field में house number, street, village या city, mandal, "
            "district और pin code लिखें।"
        ),
        "applicant_name": (
            "Aadhaar या किसी अन्य आधिकारिक रिकॉर्ड में जैसा है, वैसा अपना पूरा नाम लिखें।"
        ),
        "father_name": "आधिकारिक रिकॉर्ड में जैसा है, वैसा अपने पिता का पूरा नाम लिखें।",
        "district": "जिस district में आप रहते हैं उसका नाम लिखें।",
        "mandal": "जिस mandal में आप रहते हैं उसका नाम लिखें।",
        "village": "अपने village या town का नाम लिखें।",
    },
}


def _simple_field_guidance(field_name: str, language: str) -> Guidance:
    reply_language = _reply_language(language)
    return Guidance(field=field_name, reply=SIMPLE_FIELD_REPLIES[reply_language][field_name])


def generate_guidance(
    message: str, detected_field: str | None, language: str = "english"
) -> Guidance:
    if detected_field is None:
        return _unknown_guidance(language)
    if detected_field in {"monthly_income", "annual_income"}:
        return _income_guidance(message, detected_field, language)
    if detected_field in {"mobile_number", "aadhaar_number"}:
        return _identity_number_guidance(message, detected_field, language)
    if detected_field == "purpose":
        return _purpose_guidance(message, language)
    return _simple_field_guidance(detected_field, language)
