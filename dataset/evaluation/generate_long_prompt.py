import json
import random
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "dataset" / "evaluation"

PROMPT_FILE = OUTPUT_DIR / "long_prompt_1000.txt"
GROUND_TRUTH_FILE = OUTPUT_DIR / "ground_truth.json"

random.seed(42)


# ============================================================
# FAKE SYNTHETIC VALUES
# ============================================================
# These values are intentionally fake and are used only
# for evaluation. They are NOT real credentials or PII.


SENSITIVE_ITEMS = [

    {
        "type": "email",
        "value": "developer1042@example.com",
        "template": "Contact email: developer1042@example.com"
    },

    {
        "type": "email",
        "value": "qa.engineer@example.com",
        "template": "QA contact: qa.engineer@example.com"
    },

    {
        "type": "email",
        "value": "project.owner@example.com",
        "template": "Project owner email: project.owner@example.com"
    },

    {
        "type": "phone",
        "value": "9876543210",
        "template": "Support phone: 9876543210"
    },

    {
        "type": "phone",
        "value": "9123456789",
        "template": "Emergency contact: 9123456789"
    },

    {
        "type": "employee_id",
        "value": "EMP-2026-1042",
        "template": "Employee ID: EMP-2026-1042"
    },

    {
        "type": "employee_id",
        "value": "EMP-2026-2087",
        "template": "Developer employee ID: EMP-2026-2087"
    },

    {
        "type": "employee_id",
        "value": "STAFF-2026-3311",
        "template": "Staff ID: STAFF-2026-3311"
    },

    {
        "type": "project_identifier",
        "value": "SHADOW-2026-001",
        "template": "Project ID: SHADOW-2026-001"
    },

    {
        "type": "project_identifier",
        "value": "TRUST-2026-014",
        "template": "Application ID: TRUST-2026-014"
    },

    {
        "type": "api_key",
        "value": "sk-fakeabcdefghijklmnopqrstuvwxyz123456",
        "template": (
            "API key configuration: "
            "sk-fakeabcdefghijklmnopqrstuvwxyz123456"
        )
    },

    {
        "type": "api_key",
        "value": "AIzaFakeKeyabcdefghijklmnopqrstuvwxyz123",
        "template": (
            "Google service key: "
            "AIzaFakeKeyabcdefghijklmnopqrstuvwxyz123"
        )
    },

    {
        "type": "password",
        "value": "DemoPass2026",
        "template": "Database password: DemoPass2026"
    },

    {
        "type": "token",
        "value": "FakeAuthToken2026ABCDEF",
        "template": (
            "Authentication token: "
            "FakeAuthToken2026ABCDEF"
        )
    },

    {
        "type": "database_credential",
        "value": (
            "mysql://demo_user:fake_password@localhost:3306/"
            "shadowshield_demo"
        ),
        "template": (
            "Database connection: "
            "mysql://demo_user:fake_password@localhost:3306/"
            "shadowshield_demo"
        )
    },

    {
        "type": "internal_url",
        "value": "http://192.168.1.20:8080/api/users",
        "template": (
            "Internal user service: "
            "http://192.168.1.20:8080/api/users"
        )
    },

    {
        "type": "internal_url",
        "value": "http://10.0.0.15:9000/api/v1",
        "template": (
            "Internal API endpoint: "
            "http://10.0.0.15:9000/api/v1"
        )
    },

    {
        "type": "private_ip",
        "value": "192.168.1.55",
        "template": "Internal server address: 192.168.1.55"
    },

    {
        "type": "private_ip",
        "value": "10.0.0.42",
        "template": "Database server address: 10.0.0.42"
    },

    {
        "type": "environment_variable",
        "value": "OPENAI_API_KEY",
        "template": "Environment variable: OPENAI_API_KEY"
    },

    {
        "type": "secret_assignment",
        "value": "fake-client-secret-2026",
        "template": (
            "CLIENT_SECRET=fake-client-secret-2026"
        )
    },

    {
        "type": "account_number",
        "value": "123456789012",
        "template": "Demo account number: 123456789012"
    },

    {
        "type": "credit_card",
        "value": "4111 1111 1111 1111",
        "template": (
            "Test payment card: "
            "4111 1111 1111 1111"
        )
    }
]


# ============================================================
# NORMAL PROJECT CONTENT
# ============================================================

NORMAL_SECTIONS = [

    "The application follows a modular architecture.",

    "The frontend communicates with the backend through REST APIs.",

    "The backend validates incoming requests before processing them.",

    "The system uses structured logging for debugging and monitoring.",

    "Authentication middleware is applied to protected routes.",

    "The database layer is separated from the business logic.",

    "The application supports role-based access control.",

    "Unit tests are executed before each release.",

    "Integration testing validates communication between services.",

    "The frontend uses reusable components for maintainability.",

    "The API follows standard HTTP request and response conventions.",

    "Error handling is implemented at the service boundary.",

    "The project uses version control for source-code management.",

    "Continuous integration is used to validate changes.",

    "Documentation is maintained alongside the source code.",

    "The system records application events for troubleshooting.",

    "The service architecture supports future horizontal scaling.",

    "Performance testing is conducted using representative workloads.",

    "The deployment pipeline contains development and production stages.",

    "Code reviews are performed before important changes are merged.",

    "The system uses configuration files to separate deployment settings.",

    "The application is divided into presentation, service, and data layers.",

    "Automated tests help identify regressions during development.",

    "The project uses a structured directory layout.",

    "Developers follow consistent naming conventions.",

    "The user interface provides feedback for invalid input.",

    "The service returns appropriate status codes for API failures.",

    "The database schema is version controlled.",

    "The application contains monitoring hooks for operational analysis.",

    "The project documentation describes installation and deployment steps."
]


# ============================================================
# DOCUMENT GENERATOR
# ============================================================

def generate_document(target_lines=1200):

    lines = []

    ground_truth = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    lines.append("# ShadowShield Synthetic Project Documentation")
    lines.append("")
    lines.append("This document is generated for privacy detection evaluation.")
    lines.append("All sensitive values contained in this document are synthetic.")
    lines.append("")

    # --------------------------------------------------------
    # Project metadata
    # --------------------------------------------------------

    lines.append("## 1. Project Overview")

    for _ in range(20):
        lines.append(random.choice(NORMAL_SECTIONS))

    # --------------------------------------------------------
    # Generate normal project documentation
    # --------------------------------------------------------

    sensitive_insertions = [
        (120, SENSITIVE_ITEMS[0]),
        (180, SENSITIVE_ITEMS[5]),
        (240, SENSITIVE_ITEMS[10]),
        (300, SENSITIVE_ITEMS[12]),
        (360, SENSITIVE_ITEMS[15]),
        (420, SENSITIVE_ITEMS[16]),
        (480, SENSITIVE_ITEMS[6]),
        (540, SENSITIVE_ITEMS[8]),
        (600, SENSITIVE_ITEMS[17]),
        (660, SENSITIVE_ITEMS[18]),
        (720, SENSITIVE_ITEMS[13]),
        (780, SENSITIVE_ITEMS[20]),
        (840, SENSITIVE_ITEMS[21]),
        (900, SENSITIVE_ITEMS[2]),
        (960, SENSITIVE_ITEMS[3]),
        (1020, SENSITIVE_ITEMS[9]),
        (1080, SENSITIVE_ITEMS[19]),
        (1140, SENSITIVE_ITEMS[7])
    ]

    insertion_map = {
        position: item
        for position, item in sensitive_insertions
    }

    while len(lines) < target_lines:

        current_line = len(lines) + 1

        if current_line in insertion_map:

            item = insertion_map[current_line]

            lines.append(item["template"])

            ground_truth.append({
                "type": item["type"],
                "value": item["value"],
                "line": current_line
            })

        else:

            # Create numbered technical documentation
            section_number = (
                len(lines) // 25
            ) + 1

            normal_text = random.choice(
                NORMAL_SECTIONS
            )

            lines.append(
                f"Section {section_number}: {normal_text}"
            )

    return lines, ground_truth


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    target_lines = 1200

    lines, ground_truth = generate_document(
        target_lines
    )

    prompt_text = "\n".join(lines)

    # --------------------------------------------------------
    # Save prompt
    # --------------------------------------------------------

    PROMPT_FILE.write_text(
        prompt_text,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Count ground truth
    # --------------------------------------------------------

    counts = {}

    for item in ground_truth:

        category = item["type"]

        counts[category] = (
            counts.get(category, 0) + 1
        )

    # --------------------------------------------------------
    # Ground truth structure
    # --------------------------------------------------------

    ground_truth_data = {

        "description": (
            "Synthetic long-prompt evaluation dataset "
            "for ShadowShield."
        ),

        "synthetic_only": True,

        "target_lines": target_lines,

        "actual_lines": len(lines),

        "total_ground_truth_findings": len(
            ground_truth
        ),

        "finding_counts": counts,

        "findings": ground_truth
    }

    # --------------------------------------------------------
    # Save ground truth
    # --------------------------------------------------------

    GROUND_TRUTH_FILE.write_text(
        json.dumps(
            ground_truth_data,
            indent=4
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Display summary
    # --------------------------------------------------------

    print("=" * 70)
    print("SHADOWSHIELD LONG-PROMPT DATASET")
    print("=" * 70)

    print()
    print(f"Prompt file:")
    print(PROMPT_FILE)

    print()
    print(f"Ground truth file:")
    print(GROUND_TRUTH_FILE)

    print()
    print(f"Lines generated: {len(lines)}")

    print(
        f"Ground-truth findings: "
        f"{len(ground_truth)}"
    )

    print()
    print("GROUND-TRUTH COUNTS:")

    for category, count in counts.items():

        print(
            f"  {category}: {count}"
        )

    print()
    print("Dataset generation complete.")


if __name__ == "__main__":
    main()