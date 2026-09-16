import re
import joblib

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "ml" / "models"

MODEL_PATH = MODEL_DIR / "logistic_regression.joblib"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"


# ============================================================
# LOAD ML MODEL
# ============================================================

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# ============================================================
# REGEX PATTERNS
# ============================================================
#
# IMPORTANT:
# Some patterns contain a named group called "value".
# The complete regex may match the surrounding label
# ("password is", "employee ID is", etc.), but only the
# "value" portion will be returned as the sensitive data.
# ============================================================

PATTERNS = {

    # --------------------------------------------------------
    # PII
    # --------------------------------------------------------

    "email": {
        "pattern": (
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "risk": "medium"
    },

    "phone": {
        "pattern": (
            r"(?<!\d)"
            r"(?:\+91[\s-]?)?"
            r"[6-9]\d{9}"
            r"(?!\d)"
        ),
        "risk": "medium"
    },

    "employee_id": {
        "pattern": (
            r"(?i)\b"
            r"(?:employee\s*(?:id|number)"
            r"|emp\s*(?:id|number)"
            r"|staff\s*(?:id|number))"
            r"\s*(?::|#|=|\bis\b)"
            r"\s*"
            r"(?P<value>[A-Z0-9][A-Z0-9-]{3,19})\b"
        ),
        "risk": "medium"
    },

    # --------------------------------------------------------
    # CREDENTIALS / SECRETS
    # --------------------------------------------------------

    "api_key": {
        "pattern": (
            r"\b(?:"
            r"sk-[A-Za-z0-9_-]{20,}"
            r"|AIza[A-Za-z0-9_-]{20,}"
            r"|AKIA[A-Z0-9]{16}"
            r")\b"
        ),
        "risk": "high"
    },

    "password": {
        "pattern": (
            r"(?i)\b"
            r"(?:password|passwd|pwd)"
            r"\s*(?::|=|\bis\b)"
            r"\s*"
            r"(?P<value>[^\s,;]+)"
        ),
        "risk": "high"
    },

    "token": {
        "pattern": (
            r"(?i)\b"
            r"(?:token|access[_-]?token|auth[_-]?token)"
            r"\s*(?::|=|\bis\b)"
            r"\s*"
            r"(?P<value>[A-Za-z0-9._-]{10,})"
        ),
        "risk": "high"
    },

    "database_credential": {
        "pattern": (
            r"(?i)"
            r"(?P<value>"
            r"(?:mysql|postgres(?:ql)?|mongodb)"
            r"://[^\s]+"
            r")"
        ),
        "risk": "high"
    },

    # --------------------------------------------------------
    # FINANCIAL
    # --------------------------------------------------------

    "credit_card": {
        "pattern": (
            r"(?<!\d)"
            r"(?P<value>(?:\d[ -]?){13,19})"
            r"(?!\d)"
        ),
        "risk": "high"
    },

    "account_number": {
        "pattern": (
            r"(?i)\b"
            r"(?:account(?:\s+number)?|a/c|acc)"
            r"\s*(?::|#|=|\bis\b)"
            r"\s*"
            r"(?P<value>\d{8,18})\b"
        ),
        "risk": "high"
    }
}


# ============================================================
# REGEX DETECTOR
# ============================================================

def detect_regex(text: str):

    detections = []

    for category, config in PATTERNS.items():

        matches = re.finditer(
            config["pattern"],
            text
        )

        for match in matches:

            # ------------------------------------------------
            # If the pattern contains a "value" group,
            # use only that portion.
            # ------------------------------------------------

            if "value" in match.groupdict():

                value = match.group("value")

                start = match.start("value")
                end = match.end("value")

            else:

                value = match.group()

                start = match.start()
                end = match.end()

            detections.append({
                "type": category,
                "value": value,
                "risk": config["risk"],
                "start": start,
                "end": end
            })

    return detections


# ============================================================
# ML DETECTOR
# ============================================================

def detect_ml(text: str):

    vector = vectorizer.transform([text])

    prediction = model.predict(vector)[0]

    return {
        "label": prediction
    }


# ============================================================
# RISK ENGINE
# ============================================================

def calculate_risk(
    regex_detections,
    ml_result
):

    high_risk_types = {
        "api_key",
        "password",
        "token",
        "database_credential",
        "credit_card",
        "account_number"
    }

    # --------------------------------------------------------
    # High-risk information
    # --------------------------------------------------------

    for detection in regex_detections:

        if detection["type"] in high_risk_types:

            return "HIGH_RISK"

    # --------------------------------------------------------
    # Other sensitive information
    # --------------------------------------------------------

    if regex_detections:

        return "SENSITIVE"

    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    if ml_result["label"] == "sensitive":

        return "SENSITIVE"

    return "SAFE"


# ============================================================
# ACTION ENGINE
# ============================================================

def determine_action(risk_level):

    if risk_level == "SAFE":
        return "ALLOW"

    if risk_level == "SENSITIVE":
        return "WARN"

    if risk_level == "HIGH_RISK":
        return "BLOCK"

    return "WARN"


# ============================================================
# REDACTION
# ============================================================

def redact_text(
    text,
    detections
):

    # Process from right to left so replacing one value
    # doesn't change the indexes of values before it.

    sorted_detections = sorted(
        detections,
        key=lambda x: x["start"],
        reverse=True
    )

    redacted = text

    for detection in sorted_detections:

        start = detection["start"]
        end = detection["end"]

        redacted = (
            redacted[:start]
            + "[REDACTED]"
            + redacted[end:]
        )

    return redacted


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_prompt(text: str):

    if not isinstance(text, str):

        raise ValueError(
            "Prompt must be a string."
        )

    # --------------------------------------------------------
    # Empty prompt
    # --------------------------------------------------------

    if not text.strip():

        return {
            "contains_sensitive": False,
            "risk_level": "SAFE",
            "action": "ALLOW",
            "detections": [],
            "ml_prediction": "safe",
            "redacted_text": text
        }

    # --------------------------------------------------------
    # Regex detection
    # --------------------------------------------------------

    regex_detections = detect_regex(text)

    # --------------------------------------------------------
    # ML detection
    # --------------------------------------------------------

    ml_result = detect_ml(text)

    # --------------------------------------------------------
    # Risk calculation
    # --------------------------------------------------------

    risk_level = calculate_risk(
        regex_detections,
        ml_result
    )

    # --------------------------------------------------------
    # Action
    # --------------------------------------------------------

    action = determine_action(
        risk_level
    )

    # --------------------------------------------------------
    # Sensitive flag
    # --------------------------------------------------------

    contains_sensitive = (
        risk_level != "SAFE"
    )

    # --------------------------------------------------------
    # Redaction
    # --------------------------------------------------------

    redacted_text = redact_text(
        text,
        regex_detections
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "contains_sensitive": contains_sensitive,
        "risk_level": risk_level,
        "action": action,
        "detections": regex_detections,
        "ml_prediction": ml_result["label"],
        "redacted_text": redacted_text
    }


# ============================================================
# LOCAL TESTING
# ============================================================

if __name__ == "__main__":

    test_prompts = [

        # ----------------------------------------------------
        # SAFE
        # ----------------------------------------------------

        "Explain how binary search works.",

        "How do I implement a stack using C++?",

        # ----------------------------------------------------
        # PII
        # ----------------------------------------------------

        "My email is student@example.com. Help me write an email.",

        "My phone number is 9876543210. Help me contact the company.",

        "My employee ID is EMP-2026-1234. Help me format this report.",

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        "My password is TestPass123. Help me debug my login.",

        "My password: TestPass123. Help me debug my login.",

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        "My API key is sk-abcdefghijklmnopqrstuvwxyz123456.",

        # ----------------------------------------------------
        # TOKEN
        # ----------------------------------------------------

        "My token is abcdefghijklmnopqrstuvwxyz123456.",

        # ----------------------------------------------------
        # FINANCIAL
        # ----------------------------------------------------

        "My account number is 123456789012. Please check this.",

        "My credit card number is 4111 1111 1111 1111.",

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        "My database connection is mysql://admin:password123@localhost:3306/appdb."
    ]


    for prompt in test_prompts:

        print("\n" + "=" * 70)

        print("PROMPT:")
        print(prompt)

        result = analyze_prompt(prompt)

        print("\nRISK LEVEL:")
        print(result["risk_level"])

        print("ACTION:")
        print(result["action"])

        print("ML PREDICTION:")
        print(result["ml_prediction"])

        print("DETECTIONS:")

        if result["detections"]:

            for detection in result["detections"]:

                print(
                    f"  - {detection['type']}: "
                    f"{detection['value']} "
                    f"({detection['risk']})"
                )

        else:

            print("  None")

        print("\nREDACTED TEXT:")
        print(result["redacted_text"])