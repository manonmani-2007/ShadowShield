from fastapi import FastAPI
from pydantic import BaseModel

from backend.detector import analyze_prompt


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="ShadowShield API",
    description="Privacy-aware sensitive information detection API",
    version="1.0.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class PromptRequest(BaseModel):

    text: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "ShadowShield",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# ANALYZE ENDPOINT
# ============================================================

@app.post("/analyze")
def analyze(request: PromptRequest):

    result = analyze_prompt(
        request.text
    )

    return result