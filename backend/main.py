from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.detector import analyze_prompt


app = FastAPI(
    title="ShadowShield API",
    description="Privacy-aware sensitive information detection API",
    version="1.0.0"
)


# Allow requests from the ShadowShield Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ShadowShield",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
def analyze(request: PromptRequest):
    result = analyze_prompt(request.text)
    return result