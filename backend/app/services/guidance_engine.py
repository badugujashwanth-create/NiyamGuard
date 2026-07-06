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
    reply_language = _reply_language(language)
    if field_name == "annual_income":
        replies = {
            "english": (
                "Annual income means the total money your family gets in one year. "
                "It is usually monthly income multiplied by 12. For example, "
                "15000 per month becomes 180000 per year."
            ),
            "telugu": (
                "సంవత్సర ఆదాయం అంటే మీ కుటుంబానికి ఏడాదిలో వచ్చే మొత్తం డబ్బు. "
                "నెలవారీ ఆదాయాన్ని 12తో గుణించాలి. ఉదాహరణకు నెలకు 15000 అయితే, "
                "సంవత్సర ఆదాయం 180000 అవుతుంది."
            ),
            "hindi": (
                "साल की आमदनी का मतलब आपके परिवार को एक साल में मिलने वाला कुल पैसा। "
                "महीने की आमदनी को 12 से गुणा करें। जैसे महीने में 15000 हो तो "
                "साल की आमदनी 180000 होगी।"
            ),
        }
    else:
        replies = {
            "english": (
                "Monthly income means how much money your family gets in one month. "
                "If your family gets fifteen thousand per month, type 15000."
            ),
            "telugu": (
                "నెలవారీ ఆదాయం అంటే మీ కుటుంబానికి ఒక నెలలో వచ్చే మొత్తం డబ్బు. "
                "ఉదాహరణకు నెలకు పదిహేను వేలు వస్తే, ఈ బాక్స్‌లో 15000 అని టైప్ చేయండి."
            ),
            "hindi": (
                "महीने की आमदनी का मतलब आपके परिवार को एक महीने में मिलने वाला कुल पैसा। "
                "अगर महीने में पंद्रह हजार रुपये आते हैं, तो इस box में 15000 लिखें।"
            ),
        }
    return Guidance(field=field_name, reply=replies[reply_language])


def _income_guidance(message: str, detected_field: str, language: str) -> Guidance:
    amount = parse_spoken_number(message)
    if amount is None:
        return _missing_income_guidance(detected_field, language)
    if amount <= 0:
        reply_language = _reply_language(language)
        replies = {
            "english": "Income must be a number greater than 0.",
            "telugu": "ఆదాయం 0 కంటే ఎక్కువ సంఖ్యగా ఉండాలి. దయచేసి సరైన మొత్తాన్ని చెప్పండి.",
            "hindi": "आमदनी 0 से बड़ी संख्या होनी चाहिए। कृपया सही रकम बताइए।",
        }
        return Guidance(
            field=detected_field,
            reply=replies[reply_language],
            warning=replies[reply_language],
        )

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
                    f"మీ నెలవారీ ఆదాయం {amount} అయితే, సంవత్సర ఆదాయం {annual} అవుతుంది. "
                    f"Annual Income బాక్స్‌లో {annual} అని మీరే టైప్ చేయండి."
                ),
                "hindi": (
                    f"अगर आपकी महीने की आमदनी {amount} है, तो साल की आमदनी {annual} होगी। "
                    f"Annual Income box में {annual} स्वयं लिखें।"
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
            "telugu": (
                f"ఇది మీ సంవత్సర ఆదాయం. Annual Income బాక్స్‌లో {amount} అని "
                "సరిచూసుకుని మీరే టైప్ చేయండి."
            ),
            "hindi": (
                f"यह आपकी साल की आमदनी है। Annual Income box में {amount} जाँचकर "
                "स्वयं लिखें।"
            ),
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
            f"ఇది మీ నెలవారీ ఆదాయం, అంటే కుటుంబానికి ఒక నెలలో వచ్చే మొత్తం డబ్బు. "
            f"Monthly Income బాక్స్‌లో {amount} అని మీరే టైప్ చేయండి. "
            f"సంవత్సర ఆదాయం కూడా అడిగితే, {annual} అని టైప్ చేయండి. "
            f"ఎందుకంటే {amount} × 12 = {annual}."
        ),
        "hindi": (
            f"यह आपकी महीने की आमदनी है, यानी परिवार को एक महीने में मिलने वाला कुल पैसा। "
            f"Monthly Income box में {amount} स्वयं लिखें। अगर साल की आमदनी भी पूछी गई "
            f"है, तो {annual} लिखें, क्योंकि {amount} × 12 = {annual}।"
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
            "telugu": (
                f"ఇక్కడ మీ {expected} అంకెల {label.lower()} టైప్ చేయాలి. "
                f"దయచేసి numberను స్పష్టంగా చెప్పండి లేదా మీరే టైప్ చేయండి."
            ),
            "hindi": (
                f"यहाँ अपना {expected} अंकों का {label.lower()} लिखना है। "
                "कृपया number साफ़ बोलें या स्वयं लिखें।"
            ),
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
            f"ఈ {label.lower()}లో సరైన {expected} అంకెలు ఉన్నాయి. "
            "ఒకసారి సరిచూసుకుని మీరు దానిని మీరే టైప్ చేయండి."
        ),
        "hindi": (
            f"इस {label.lower()} में सही {expected} अंक हैं। "
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
                f"అవును. ఈ సర్టిఫికేట్ మీకు {selected.lower()} కోసం కావాలంటే, "
                f"Purpose of Certificate బాక్స్‌లో “{selected}” అని మీరే టైప్ చేయండి."
            ),
            "hindi": (
                f"हाँ। अगर यह certificate आपको {selected.lower()} के लिए चाहिए, "
                f"तो Purpose of Certificate box में “{selected}” स्वयं लिखें।"
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
            "ఇక్కడ ఈ సర్టిఫికేట్ మీకు ఎందుకు కావాలో టైప్ చేయాలి. Scholarship కోసం "
            "అయితే Scholarship, College admission కోసం అయితే College Admission అని టైప్ చేయండి."
        ),
        "hindi": (
            "यहाँ लिखना है कि आपको यह certificate किस काम के लिए चाहिए। Scholarship, "
            "College Admission, Job या Pension जैसा छोटा कारण स्वयं लिखें।"
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
            "ఇక్కడ మీ పూర్తి చిరునామా టైప్ చేయాలి. House number, street, గ్రామం లేదా "
            "city, మండలం, జిల్లా మరియు pincode ఉంటే వాటిని మీరే టైప్ చేయండి."
        ),
        "applicant_name": (
            "ఇక్కడ దరఖాస్తు చేసే వ్యక్తి పూర్తి పేరు టైప్ చేయాలి. Aadhaar లేదా "
            "official recordలో పేరు ఎలా ఉందో అలా టైప్ చేయండి."
        ),
        "father_name": "ఇక్కడ మీ తండ్రి పూర్తి పేరు మీరే టైప్ చేయాలి.",
        "district": (
            "ఇక్కడ మీరు ఉండే జిల్లా పేరు టైప్ చేయాలి. ఉదాహరణకు Hyderabad, "
            "Warangal లేదా Karimnagar."
        ),
        "mandal": (
            "మండలం అంటే మీ ఊరు ఏ mandal పరిధిలోకి వస్తుందో అది. మీకు మండలం "
            "తెలియకపోతే, మీ గ్రామం పేరు లేదా pincode చెప్పండి; నేను సహాయం చేస్తాను."
        ),
        "village": "ఇక్కడ మీ గ్రామం, ఊరు లేదా town పేరు మీరే టైప్ చేయాలి.",
    },
    "hindi": {
        "address": (
            "यहाँ अपना पूरा पता लिखना है। House number, street, गाँव या city, "
            "मंडल, जिला और pincode स्वयं लिखें।"
        ),
        "applicant_name": (
            "यहाँ आवेदन करने वाले व्यक्ति का पूरा नाम लिखना है। Aadhaar या official "
            "record में जैसा नाम है, वैसा ही लिखें।"
        ),
        "father_name": "यहाँ अपने पिता का पूरा नाम स्वयं लिखें।",
        "district": "यहाँ उस जिले का नाम लिखें जहाँ आप रहते हैं।",
        "mandal": (
            "मंडल का मतलब आपका गाँव किस mandal या taluk में आता है। अगर मंडल नहीं "
            "पता, तो अपना गाँव या pincode बताइए; मैं मदद करूँगा।"
        ),
        "village": "यहाँ अपने गाँव या town का नाम स्वयं लिखें।",
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
