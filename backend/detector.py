import re
import joblib
from pathlib import Path
from collections import Counter


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
            r"(?P<value>[^\s,;.!?]+)"
        ),
        "risk": "high"
    },

    "token": {
        "pattern": (
            r"(?i)\b"
            r"(?:token|access[_-]?token|auth[_-]?token)"
            r"\s*(?::|=|\bis\b)"
            r"\s*"
            r"(?P<value>[A-Za-z0-9_-]{10,})"
        ),
        "risk": "high"
    },

    "database_credential": {
        "pattern": (
            r"(?i)"
            r"(?P<value>"
            r"(?:mysql|postgres(?:ql)?|mongodb)"
            r"://[^\s,;]+?"
            r")"
            r"(?=[\s,;.!?]|$)"
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
    },

    # --------------------------------------------------------
    # INTERNAL / PROJECT INFORMATION
    # --------------------------------------------------------

    "internal_url": {
        "pattern": (
            r"\b(?:"
            r"https?://"
            r"(?:localhost|127\.0\.0\.1|"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"192\.168\.\d{1,3}\.\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[0-1])\."
            r"\d{1,3}\.\d{1,3})"
            r"(?::\d+)?(?:/[^\s]*)?"
            r")"
        ),
        "risk": "high"
    },

    "private_ip": {
        "pattern": (
            r"(?<![\d.])"
            r"(?:"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[0-1])\."
            r"\d{1,3}\.\d{1,3}"
            r")"
            r"(?![\d.])"
        ),
        "risk": "high"
    },

    "environment_variable": {
        "pattern": (
            r"\b[A-Z][A-Z0-9_]{2,}"
            r"_(?:KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL)"
            r"\b"
        ),
        "risk": "high"
    },

    "secret_assignment": {
        "pattern": (
            r"(?i)\b"
            r"(?:api[_-]?key|secret|client[_-]?secret|"
            r"access[_-]?key|private[_-]?key)"
            r"\s*(?:=|:)\s*"
            r"(?P<value>[^\s,;.!?]+)"
        ),
        "risk": "high"
    },

    "project_identifier": {
        "pattern": (
            r"(?i)\b"
            r"(?:project\s*(?:id|code)|"
            r"application\s*(?:id|number)|"
            r"internal\s*(?:id|code))"
            r"\s*(?::|#|=|\bis\b)"
            r"\s*"
            r"(?P<value>[A-Z0-9][A-Z0-9_-]{3,30})\b"
        ),
        "risk": "medium"
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
            # Use only the sensitive value if a named
            # "value" group exists.
            # ------------------------------------------------

            if "value" in match.groupdict():

                value = match.group("value")

                start = match.start("value")
                end = match.end("value")

            else:

                value = match.group()

                start = match.start()
                end = match.end()

            # ------------------------------------------------
            # Remove sentence punctuation accidentally included
            # in the detection.
            # ------------------------------------------------

            while value and value[-1] in ".,!?;:":
                value = value[:-1]
                end -= 1

            # ------------------------------------------------
            # Line number.
            # ------------------------------------------------

            line_number = (
                text.count("\n", 0, start) + 1
            )

            # ------------------------------------------------
            # Context.
            # ------------------------------------------------

            line_start = (
                text.rfind("\n", 0, start) + 1
            )

            line_end = text.find(
                "\n",
                end
            )

            if line_end == -1:
                line_end = len(text)

            context = text[
                line_start:line_end
            ].strip()

            detections.append({
                "type": category,
                "value": value,
                "risk": config["risk"],
                "start": start,
                "end": end,
                "line": line_number,
                "context": context[:200]
            })

    return detections


# ============================================================
# DEDUPLICATION / LOGICAL FINDING CORRELATION
# ============================================================

def deduplicate_detections(detections):
    """
    Removes duplicate and logically overlapping detections.

    Special handling:
        CLIENT_SECRET
        CLIENT_SECRET=value

    are treated as one logical secret_assignment finding.

    The logical finding can still preserve a larger redaction
    range so that the complete secret assignment is removed.
    """

    if not detections:
        return []

    detections = sorted(
        detections,
        key=lambda x: (
            x["start"],
            -(x["end"] - x["start"])
        )
    )

    unique = []

    risk_priority = {
        "high": 3,
        "medium": 2,
        "low": 1
    }

    for detection in detections:

        merged = False

        for index, existing in enumerate(unique):

            same_line = (
                detection.get("line")
                == existing.get("line")
            )

            same_span = (
                detection["start"] == existing["start"]
                and detection["end"] == existing["end"]
            )

            overlapping = (
                detection["start"] < existing["end"]
                and detection["end"] > existing["start"]
            )

            # ------------------------------------------------
            # SPECIAL SECRET ASSIGNMENT CASE
            # ------------------------------------------------

            secret_assignment_pair = (
                same_line
                and (
                    (
                        detection["type"]
                        == "environment_variable"
                        and existing["type"]
                        == "secret_assignment"
                    )
                    or
                    (
                        detection["type"]
                        == "secret_assignment"
                        and existing["type"]
                        == "environment_variable"
                    )
                )
            )

            if secret_assignment_pair:

                if detection["type"] == "secret_assignment":

                    assignment = detection.copy()

                    env_detection = existing

                    assignment["redact_start"] = min(
                        assignment["start"],
                        env_detection["start"]
                    )

                    assignment["redact_end"] = max(
                        assignment["end"],
                        env_detection["end"]
                    )

                    unique[index] = assignment

                else:

                    existing_copy = existing.copy()

                    existing_copy["redact_start"] = min(
                        existing["start"],
                        detection["start"]
                    )

                    existing_copy["redact_end"] = max(
                        existing["end"],
                        detection["end"]
                    )

                    unique[index] = existing_copy

                merged = True
                break

            # ------------------------------------------------
            # GENERIC OVERLAPPING DETECTION
            # ------------------------------------------------

            if same_span or overlapping:

                current_priority = risk_priority.get(
                    detection["risk"],
                    0
                )

                existing_priority = risk_priority.get(
                    existing["risk"],
                    0
                )

                if current_priority > existing_priority:

                    replacement = detection.copy()

                    replacement.setdefault(
                        "redact_start",
                        replacement["start"]
                    )

                    replacement.setdefault(
                        "redact_end",
                        replacement["end"]
                    )

                    unique[index] = replacement

                merged = True
                break

        if not merged:

            detection_copy = detection.copy()

            detection_copy.setdefault(
                "redact_start",
                detection_copy["start"]
            )

            detection_copy.setdefault(
                "redact_end",
                detection_copy["end"]
            )

            unique.append(detection_copy)

    return sorted(
        unique,
        key=lambda x: x["start"]
    )


# ============================================================
# ML DETECTOR
# ============================================================

def detect_ml(text: str):

    vector = vectorizer.transform([text])

    prediction = model.predict(vector)[0]

    confidence = None

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(vector)[0]

        confidence = float(
            max(probabilities)
        )

    return {
        "label": str(prediction),
        "confidence": confidence
    }


# ============================================================
# RISK WEIGHTS
# ============================================================

RISK_WEIGHTS = {

    "email": 10,
    "phone": 10,
    "employee_id": 10,

    "project_identifier": 15,

    "internal_url": 20,
    "private_ip": 20,

    "password": 30,
    "token": 30,

    "environment_variable": 30,

    "secret_assignment": 35,

    "api_key": 40,
    "database_credential": 40,

    "credit_card": 40,
    "account_number": 40
}


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(
    detections,
    ml_result
):

    score = 0

    for detection in detections:

        score += RISK_WEIGHTS.get(
            detection["type"],
            10
        )

    # ML contributes supporting evidence when
    # deterministic rules did not find anything.

    if (
        ml_result["label"] == "sensitive"
        and not detections
    ):
        score += 20

    return min(score, 100)


# ============================================================
# RISK LEVEL
# ============================================================

def calculate_risk(
    regex_detections,
    ml_result,
    risk_score
):

    high_risk_types = {
        "api_key",
        "password",
        "token",
        "database_credential",
        "credit_card",
        "account_number",
        "internal_url",
        "private_ip",
        "environment_variable",
        "secret_assignment"
    }

    # Any high-risk finding causes HIGH_RISK.

    for detection in regex_detections:

        if detection["type"] in high_risk_types:
            return "HIGH_RISK"

    # Multiple findings can raise risk.

    if risk_score >= 50:
        return "HIGH_RISK"

    # Medium-risk sensitive information.

    if regex_detections:
        return "SENSITIVE"

    # ML-only signal.

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

    if not detections:
        return text

    # --------------------------------------------------------
    # Right-to-left replacement prevents index shifting.
    # --------------------------------------------------------

    sorted_detections = sorted(
        detections,
        key=lambda x: x.get(
            "redact_start",
            x["start"]
        ),
        reverse=True
    )

    redacted = text

    for detection in sorted_detections:

        start = detection.get(
            "redact_start",
            detection["start"]
        )

        end = detection.get(
            "redact_end",
            detection["end"]
        )

        redacted = (
            redacted[:start]
            + "[REDACTED]"
            + redacted[end:]
        )

    return redacted


# ============================================================
# FINDING COUNTS
# ============================================================

def get_finding_counts(detections):

    counter = Counter(
        detection["type"]
        for detection in detections
    )

    return dict(counter)


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_prompt(text: str):

    if not isinstance(text, str):

        raise ValueError(
            "Prompt must be a string."
        )

    # --------------------------------------------------------
    # EMPTY PROMPT
    # --------------------------------------------------------

    if not text.strip():

        return {
            "contains_sensitive": False,
            "risk_level": "SAFE",
            "action": "ALLOW",
            "detections": [],
            "ml_prediction": "safe",
            "ml_confidence": None,
            "redacted_text": text,

            "total_findings": 0,
            "finding_counts": {},
            "lines_analyzed": 0,
            "characters_analyzed": 0,
            "risk_score": 0
        }

    # --------------------------------------------------------
    # DOCUMENT STATISTICS
    # --------------------------------------------------------

    lines_analyzed = len(
        text.splitlines()
    )

    characters_analyzed = len(text)

    # --------------------------------------------------------
    # REGEX DETECTION
    # --------------------------------------------------------

    regex_detections = detect_regex(text)

    regex_detections = deduplicate_detections(
        regex_detections
    )

    # --------------------------------------------------------
    # ML DETECTION
    # --------------------------------------------------------

    ml_result = detect_ml(text)

    # --------------------------------------------------------
    # FINDING STATISTICS
    # --------------------------------------------------------

    total_findings = len(
        regex_detections
    )

    finding_counts = get_finding_counts(
        regex_detections
    )

    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    risk_score = calculate_risk_score(
        regex_detections,
        ml_result
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    risk_level = calculate_risk(
        regex_detections,
        ml_result,
        risk_score
    )

    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    action = determine_action(
        risk_level
    )

    # --------------------------------------------------------
    # SENSITIVE FLAG
    # --------------------------------------------------------

    contains_sensitive = (
        risk_level != "SAFE"
    )

    # --------------------------------------------------------
    # REDACTION
    # --------------------------------------------------------

    redacted_text = redact_text(
        text,
        regex_detections
    )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        # Existing API fields
        "contains_sensitive": contains_sensitive,
        "risk_level": risk_level,
        "action": action,
        "detections": regex_detections,
        "ml_prediction": ml_result["label"],
        "redacted_text": redacted_text,

        # Extended analysis fields
        "ml_confidence": ml_result["confidence"],
        "total_findings": total_findings,
        "finding_counts": finding_counts,
        "lines_analyzed": lines_analyzed,
        "characters_analyzed": characters_analyzed,
        "risk_score": risk_score
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

        "My database connection is mysql://admin:password123@localhost:3306/appdb.",

        # ----------------------------------------------------
        # INTERNAL URL
        # ----------------------------------------------------

        "The internal API is http://192.168.1.20:8080/api/users.",

        # ----------------------------------------------------
        # PROJECT INFORMATION
        # ----------------------------------------------------

        "Project ID: SHADOW-2026-001.",

        # ----------------------------------------------------
        # ENVIRONMENT / SECRET ASSIGNMENT
        # ----------------------------------------------------

        "Set OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456.",

        "CLIENT_SECRET=fake-client-secret-2026"
    ]

    for prompt in test_prompts:

        print("\n" + "=" * 80)

        print("PROMPT:")
        print(prompt)

        result = analyze_prompt(prompt)

        print("\nRISK LEVEL:")
        print(result["risk_level"])

        print("ACTION:")
        print(result["action"])

        print("RISK SCORE:")
        print(result["risk_score"])

        print("ML PREDICTION:")
        print(result["ml_prediction"])

        print("ML CONFIDENCE:")
        print(result["ml_confidence"])

        print("LINES:")
        print(result["lines_analyzed"])

        print("TOTAL FINDINGS:")
        print(result["total_findings"])

        print("FINDING COUNTS:")
        print(result["finding_counts"])

        print("\nDETECTIONS:")

        if result["detections"]:

            for detection in result["detections"]:

                print(
                    f"  - {detection['type']}: "
                    f"{detection['value']} "
                    f"({detection['risk']}) "
                    f"[line {detection['line']}]"
                )

        else:

            print("  None")

        print("\nREDACTED TEXT:")
        print(result["redacted_text"])