import csv
import random
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT = BASE_DIR / "dataset" / "raw" / "shadowshield_synthetic.csv"


# ============================================================
# SYNTHETIC VALUES
# ============================================================

EMAILS = [
    "demo.student@example.com",
    "test.user@example.org",
    "sample.account@example.net",
    "mock.user@example.com",
    "demo.contact@example.org",
    "sample.person@example.net",
    "training.user@example.com",
    "example.student@example.org",
    "demo.account@example.com",
    "test.contact@example.net",
]

PHONES = [
    "9876501234",
    "9123405678",
    "9000012345",
    "8899776655",
    "9012345678",
    "9345678123",
    "8765432109",
    "9988776655",
    "9090901234",
    "8800123456",
]

ADDRESSES = [
    "42 Demo Street, Chennai",
    "18 Sample Road, Bengaluru",
    "77 Test Avenue, Hyderabad",
    "25 Example Street, Pune",
    "91 Mock Colony, Mumbai",
    "12 Training Road, Coimbatore",
    "55 Example Avenue, Delhi",
    "31 Demo Lane, Kochi",
    "64 Sample Street, Mysuru",
    "28 Test Road, Ahmedabad",
]

API_KEYS = [
    "sk-test-A7B82C91D4",
    "demo-api-key-83921",
    "test_key_X92K71",
    "mock-api-482917",
    "demo-secret-key-7291",
    "test-api-token-48291",
    "sample-key-73921",
    "demo-key-482910",
    "test-api-918273",
    "mock-key-X9281",
]

PASSWORDS = [
    "DemoPass482!",
    "TestPassword731!",
    "MockLogin92#",
    "SamplePwd821@",
    "DemoSecure44!",
    "TestingPass902$",
    "ExamplePass321!",
    "DemoLogin82#",
    "TestSecure719@",
    "MockPassword55!",
]

TOKENS = [
    "demo_token_83A91X",
    "test_access_token_7291",
    "mockBearerToken482",
    "sample_token_X72K",
    "demoAuthToken8392",
    "testToken92831",
    "mock_access_7192",
    "sampleBearer8291",
    "demoToken_X821",
    "testAuthToken472",
]

DB_CREDENTIALS = [
    "postgresql://demo_user:DemoPass482!@localhost:5432/testdb",
    "mysql://test_user:MockPass731@localhost:3306/sampledb",
    "mongodb://demo:DemoPass92@localhost:27017/testdb",
    "postgresql://sample:TestPass821@localhost:5432/sampledb",
    "mysql://demo_user:MockLogin92#@localhost:3306/testdb",
    "mongodb://test:ExamplePass321!@localhost:27017/demo",
]

CARD_NUMBERS = [
    "4111111111111111",
    "5555555555554444",
    "4000000000000002",
    "6011111111111117",
    "4012888888881881",
    "3530111333300000",
    "3566002020360505",
    "378282246310005",
]

ACCOUNT_NUMBERS = [
    "123456789012",
    "987654321098",
    "456789123456",
    "112233445566",
    "789012345678",
    "234567890123",
    "345678901234",
    "567890123456",
]

EMPLOYEE_IDS = [
    "EMP-DEMO-1024",
    "EMP-TEST-2048",
    "STAFF-DEMO-3812",
    "EMP-SAMPLE-7741",
    "EMP-DEV-4921",
    "STAFF-TEST-5832",
    "EMP-DEMO-7284",
    "WORKER-TEST-9132",
    "STAFF-DEV-6241",
    "EMP-SAMPLE-3519",
]


# ============================================================
# SAFE PROMPTS
# ============================================================

SAFE_TOPICS = [
    "binary search",
    "recursion",
    "linked lists",
    "binary trees",
    "sorting algorithms",
    "hash tables",
    "REST APIs",
    "HTTP requests",
    "cloud computing",
    "database normalization",
    "operating systems",
    "process scheduling",
    "virtual memory",
    "computer networks",
    "object oriented programming",
    "Python programming",
    "C++ programming",
    "Java programming",
    "machine learning",
    "linear regression",
    "classification algorithms",
    "Git and GitHub",
    "Docker",
    "Linux commands",
    "data structures",
    "dynamic programming",
    "graph algorithms",
    "software testing",
    "responsive web design",
    "SQL joins",
    "time complexity",
    "data preprocessing",
    "neural networks",
    "decision trees",
    "support vector machines",
    "database indexing",
    "REST architecture",
    "version control",
    "web development",
    "CSS Flexbox",
    "JavaScript",
    "React",
    "Django",
    "FastAPI",
    "computer architecture",
    "deadlocks",
    "page replacement algorithms",
    "Dijkstra's algorithm",
    "Kruskal's algorithm",
    "Floyd Warshall algorithm",
]

SAFE_ACTIONS = [
    "Explain {} in simple terms.",
    "How does {} work?",
    "Can you teach me {} with an example?",
    "Give me a beginner-friendly explanation of {}.",
    "What are the advantages and disadvantages of {}?",
    "Show me a simple example of {}.",
    "Help me understand {}.",
    "What are common mistakes when learning {}?",
    "How would I implement {} in Python?",
    "How would I implement {} in C++?",
    "Can you compare {} with a related concept?",
    "Give me some interview questions about {}.",
    "Explain the time complexity associated with {}.",
    "What are the real-world applications of {}?",
    "Can you provide a practice problem involving {}?",
    "How is {} used in software development?",
    "Can you give me a practical example of {}?",
    "What should a beginner know about {}?",
    "Can you summarize the key concepts of {}?",
    "Help me prepare for an interview about {}.",
    "Can you explain {} step by step?",
    "What are the important concepts behind {}?",
    "Can you provide notes about {}?",
    "Give me a coding example related to {}.",
    "How can I practice {} effectively?",
]


# ============================================================
# CONTEXT VARIATIONS
# ============================================================

CONTEXTS = [
    "for my test application",
    "for a college project",
    "in a demo application",
    "for a programming assignment",
    "in a sample project",
    "for my development environment",
    "while learning software development",
    "in a prototype",
    "for an academic project",
    "in a local test environment",
]


# ============================================================
# HELPER
# ============================================================

def make_row(text, category, subcategory):
    label = "safe" if category == "safe" else "sensitive"

    return {
        "text": text,
        "label": label,
        "category": category,
        "subcategory": subcategory,
        "source_type": "synthetic",
        "contains_sensitive": category != "safe",
    }


# ============================================================
# SAFE GENERATOR
# ============================================================

def generate_safe():
    topic = random.choice(SAFE_TOPICS)
    action = random.choice(SAFE_ACTIONS)

    text = action.format(topic)

    # Add context to create additional natural variation
    if random.random() < 0.65:
        text = text[:-1] + " " + random.choice(CONTEXTS) + "."

    return make_row(
        text,
        "safe",
        "none"
    )


# ============================================================
# PII
# ============================================================

PII_TEMPLATES = {
    "email": [
        "My email address is {}.",
        "Please use {} as my contact email.",
        "The user's email address is {}.",
        "The customer can be contacted at {}.",
        "My account is registered with {}.",
        "Please add {} to the contact information.",
        "Can you validate this email address: {}?",
        "This application uses {} as the user's email.",
        "Please include this email in the form: {}.",
        "The demo account email is {}.",
    ],

    "phone": [
        "My phone number is {}.",
        "Please add {} to the contact form.",
        "The user's phone number is {}.",
        "The customer can be reached at {}.",
        "Please include this contact number: {}.",
        "Can you validate this phone number: {}?",
        "The application stores the phone number {}.",
        "This is the user's contact number: {}.",
        "Please format this phone number correctly: {}.",
        "The demo user's mobile number is {}.",
    ],

    "address": [
        "My address is {}.",
        "Please use this address in the delivery form: {}.",
        "The user's address is {}.",
        "The customer lives at {}.",
        "Please include this address: {}.",
        "Can you validate this address: {}?",
        "The application contains this address: {}.",
        "This is the delivery address: {}.",
        "Please format this address correctly: {}.",
        "The demo user's address is {}.",
    ],
}


def generate_pii():
    subcategory = random.choice(
        ["email", "phone", "address"]
    )

    values = {
        "email": EMAILS,
        "phone": PHONES,
        "address": ADDRESSES,
    }

    value = random.choice(values[subcategory])
    template = random.choice(
        PII_TEMPLATES[subcategory]
    )

    text = template.format(value)

    if random.random() < 0.5:
        text += " " + random.choice([
            "Can you help me format this?",
            "Please check the format.",
            "This is for a test application.",
            "Can you include it in the example?",
            "Please process this information.",
        ])

    return make_row(
        text,
        "pii",
        subcategory
    )


# ============================================================
# CREDENTIALS
# ============================================================

CREDENTIAL_TEMPLATES = {
    "api_key": [
        "My API key is {}.",
        "The application uses this API key: {}.",
        "Please review this configuration: API_KEY={}.",
        "Why is authentication failing with this API key: {}?",
        "The test service uses the following API key: {}.",
        "Can you check this API configuration containing {}?",
        "I am debugging an API request that uses {}.",
        "The API request contains this credential: {}.",
        "Please help me troubleshoot this API key: {}.",
        "This development application is configured with {}.",
    ],

    "password": [
        "My password is {}.",
        "The test application's password is {}.",
        "Please review this configuration: PASSWORD={}.",
        "Can you debug authentication using this password: {}?",
        "The login configuration contains password {}.",
        "The application uses {} as its test password.",
        "Why does login fail with password {}?",
        "Please check the authentication configuration containing {}.",
        "The demo account password is {}.",
        "I am testing login with the password {}.",
    ],

    "access_token": [
        "The access token for my test application is {}.",
        "Can you debug this API call using token {}?",
        "Please check this authentication token: {}.",
        "The request uses this bearer token: {}.",
        "Why is this access token not working: {}?",
        "The application sends this access token: {}.",
        "Can you inspect the following token: {}?",
        "This API request contains the token {}.",
        "The demo application uses access token {}.",
        "Please troubleshoot authentication with {}.",
    ],

    "database_credential": [
        "Please review this database connection string: {}.",
        "My application uses this database credential: {}.",
        "Can you debug this database connection: {}?",
        "Why does this database connection fail: {}?",
        "Please check the database configuration {}.",
        "The test application contains this database credential: {}.",
        "Can you troubleshoot the following connection string: {}?",
        "The application connects using {}.",
        "Please review these database credentials: {}.",
        "This development environment contains {}.",
    ],
}


def generate_credential():
    subcategory = random.choice([
        "api_key",
        "password",
        "access_token",
        "database_credential",
    ])

    values = {
        "api_key": API_KEYS,
        "password": PASSWORDS,
        "access_token": TOKENS,
        "database_credential": DB_CREDENTIALS,
    }

    value = random.choice(values[subcategory])
    template = random.choice(
        CREDENTIAL_TEMPLATES[subcategory]
    )

    text = template.format(value)

    if random.random() < 0.5:
        text += " " + random.choice([
            "Can you help me debug the problem?",
            "This is part of a development test.",
            "Please identify the issue.",
            "Can you explain what is wrong?",
            "This is from my local environment.",
        ])

    return make_row(
        text,
        "credential",
        subcategory
    )


# ============================================================
# FINANCIAL
# ============================================================

FINANCIAL_TEMPLATES = {
    "card": [
        "My test card number is {}.",
        "Please check this card number: {}.",
        "The payment form contains this test card number: {}.",
        "Can you verify the formatting of this card number: {}?",
        "Please help me redact this card number: {}.",
        "The demo payment system uses card number {}.",
        "Can you validate this test payment card: {}?",
        "The card field contains the following number: {}.",
        "Please check the payment form containing {}.",
        "This test transaction uses card number {}.",
    ],

    "account": [
        "My test account number is {}.",
        "Please validate this account number: {}.",
        "The banking form contains this account number: {}.",
        "Can you check the formatting of account number {}?",
        "Please help me protect this financial identifier: {}.",
        "The demo bank account number is {}.",
        "Can you review this account number: {}?",
        "The application contains financial identifier {}.",
        "Please check this test banking value: {}.",
        "The account field contains {}.",
    ],
}


def generate_financial():
    subcategory = random.choice([
        "card",
        "account"
    ])

    values = {
        "card": CARD_NUMBERS,
        "account": ACCOUNT_NUMBERS,
    }

    value = random.choice(values[subcategory])

    template = random.choice(
        FINANCIAL_TEMPLATES[subcategory]
    )

    text = template.format(value)

    if random.random() < 0.5:
        text += " " + random.choice([
            "This is for a test application.",
            "Can you validate the format?",
            "Please explain how to protect it.",
            "Can you help me process this?",
            "This is synthetic test data.",
        ])

    return make_row(
        text,
        "financial",
        subcategory
    )


# ============================================================
# ORGANIZATIONAL
# ============================================================

ORGANIZATIONAL_TEMPLATES = {
    "employee_id": [
        "The employee ID is {}.",
        "Please include employee identifier {} in the internal report.",
        "Our internal application uses employee ID {}.",
        "Please validate employee ID {} in this test record.",
        "The staff identifier for this example is {}.",
        "I need to add employee {} to the internal database.",
        "Can you check the employee record associated with {}?",
        "Please include staff ID {} in the internal document.",
        "The internal HR system contains employee ID {}.",
        "Can you help process employee identifier {}?",
    ],

    "internal_server": [
        "Our internal server is 10.20.30.15.",
        "The development server is 10.10.20.25.",
        "Can you troubleshoot the internal server at 10.20.30.15?",
        "The application connects to internal server DEV-SERVER-07.",
        "Please review this internal server configuration.",
        "Can you diagnose connectivity to the internal server?",
        "Why is the internal development server unavailable?",
        "Please review our private server configuration.",
        "Can you troubleshoot this internal infrastructure?",
        "Help me document the internal server setup.",
    ],

    "private_configuration": [
        "The private configuration contains INTERNAL_DB_HOST=dev-db-01.",
        "Can you review this internal deployment configuration?",
        "The development environment contains a private configuration value.",
        "Please help document this internal application configuration.",
        "Can you check the private configuration used by our test system?",
        "Please review the configuration of our internal application.",
        "Can you help organize the private deployment settings?",
        "I need to document these internal configuration values.",
        "Please check the private environment configuration.",
        "Can you explain this internal configuration setup?",
    ],

    "confidential_information": [
        "This confidential company project is called Project Aurora.",
        "Please organize this confidential internal system information.",
        "Can you help document this private company project?",
        "Please prepare an internal summary of this confidential system.",
        "Can you format this confidential project information for internal documentation?",
        "The company is working on a confidential project called Project Aurora.",
        "Please help summarize this private organizational information.",
        "Can you prepare internal documentation for this confidential project?",
        "This information belongs to an internal company project.",
        "Please organize the confidential project details.",
    ],
}


def generate_organizational():
    subcategory = random.choice(
        list(ORGANIZATIONAL_TEMPLATES.keys())
    )

    template = random.choice(
        ORGANIZATIONAL_TEMPLATES[subcategory]
    )

    if "{}" in template:
        text = template.format(
            random.choice(EMPLOYEE_IDS)
        )
    else:
        text = template

    if random.random() < 0.5:
        text += " " + random.choice([
            "This is for internal documentation.",
            "Please keep this information private.",
            "Can you help me document it?",
            "This is part of a test environment.",
            "Please explain the configuration.",
        ])

    return make_row(
        text,
        "organizational",
        subcategory
    )


# ============================================================
# MIXED SENSITIVE PROMPTS
# ============================================================

MIXED_TEMPLATES = [
    (
        "Can you debug my Flask application? My API key is {}.",
        API_KEYS,
        "api_key"
    ),

    (
        "Why is my login system failing? The password is {}.",
        PASSWORDS,
        "password"
    ),

    (
        "Can you improve this REST API? The access token is {}.",
        TOKENS,
        "access_token"
    ),

    (
        "Please debug my PostgreSQL connection. The database credential is {}.",
        DB_CREDENTIALS,
        "database_credential"
    ),

    (
        "Can you improve this customer-management application? The customer email is {}.",
        EMAILS,
        "email"
    ),

    (
        "Please fix this contact form. The user's phone number is {}.",
        PHONES,
        "phone"
    ),

    (
        "Can you improve this payment application? The test card number is {}.",
        CARD_NUMBERS,
        "card"
    ),

    (
        "Help me debug this employee management system. Employee ID: {}.",
        EMPLOYEE_IDS,
        "employee_id"
    ),

    (
        "Can you refactor this customer application while preserving the address {}?",
        ADDRESSES,
        "address"
    ),

    (
        "Please review this application configuration containing API_KEY={}.",
        API_KEYS,
        "api_key"
    ),

    (
        "Can you analyze this login configuration? PASSWORD={}.",
        PASSWORDS,
        "password"
    ),

    (
        "Please check this payment processing code using card number {}.",
        CARD_NUMBERS,
        "card"
    ),
]


def generate_mixed():
    template, values, subcategory = random.choice(
        MIXED_TEMPLATES
    )

    value = random.choice(values)

    text = template.format(value)

    if random.random() < 0.7:
        text += " " + random.choice([
            "Can you help me identify the issue?",
            "This is from a development environment.",
            "Please suggest a solution.",
            "Can you explain what is wrong?",
            "This is for a test project.",
            "Please review the code.",
            "Can you help me troubleshoot this?",
        ])

    return make_row(
        text,
        "mixed",
        subcategory
    )


# ============================================================
# UNIQUE GENERATION
# ============================================================

def generate_unique(generator, target, existing_texts):
    results = []

    attempts = 0
    max_attempts = target * 5000

    while len(results) < target:

        sample = generator()

        text = sample["text"].strip()

        if text not in existing_texts:
            existing_texts.add(text)
            results.append(sample)

        attempts += 1

        if attempts >= max_attempts:
            raise RuntimeError(
                f"Could only generate {len(results)} "
                f"unique samples out of {target}."
            )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    all_rows = []
    existing_texts = set()

    print("Generating ShadowShield synthetic dataset...")

    print("\nGenerating SAFE...")
    all_rows += generate_unique(
        generate_safe,
        500,
        existing_texts
    )

    print("Generating PII...")
    all_rows += generate_unique(
        generate_pii,
        100,
        existing_texts
    )

    print("Generating CREDENTIAL...")
    all_rows += generate_unique(
        generate_credential,
        100,
        existing_texts
    )

    print("Generating FINANCIAL...")
    all_rows += generate_unique(
        generate_financial,
        100,
        existing_texts
    )

    print("Generating ORGANIZATIONAL...")
    all_rows += generate_unique(
        generate_organizational,
        100,
        existing_texts
    )

    print("Generating MIXED...")
    all_rows += generate_unique(
        generate_mixed,
        100,
        existing_texts
    )

    random.shuffle(all_rows)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "text",
                "label",
                "category",
                "subcategory",
                "source_type",
                "contains_sensitive",
            ]
        )

        writer.writeheader()
        writer.writerows(all_rows)

    print("\n" + "=" * 60)
    print("SHADOWSHIELD SYNTHETIC DATASET")
    print("=" * 60)

    print(f"Total samples: {len(all_rows)}")

    print("\nLabel distribution:")

    for label in ["safe", "sensitive"]:
        count = sum(
            r["label"] == label
            for r in all_rows
        )
        print(f"{label}: {count}")

    print("\nCategory distribution:")

    categories = [
        "safe",
        "pii",
        "credential",
        "financial",
        "organizational",
        "mixed",
    ]

    for category in categories:
        count = sum(
            r["category"] == category
            for r in all_rows
        )
        print(f"{category}: {count}")

    print("\nUnique texts:", len(existing_texts))
    print("Duplicate texts:", len(all_rows) - len(existing_texts))

    print("\nSaved to:")
    print(OUTPUT)


if __name__ == "__main__":
    main()