import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from claude_client import ClaudeClient
from json_utils import parse_json_response, safe_json_dumps
from prompts import build_chat_prompt, build_extract_prompt, build_markdown_prompt

load_dotenv()

app = FastAPI(
    title="BriefForge Backend",
    description="Sheet metal engineering briefing agent API",
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

claude_client = ClaudeClient()


class ChatRequest(BaseModel):
    history: list[dict[str, str]] = Field(default_factory=list)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    response: str


class ExtractBriefRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ExtractBriefResponse(BaseModel):
    brief: Dict[str, Any]


class GenerateMarkdownRequest(BaseModel):
    brief: Dict[str, Any]


class GenerateMarkdownResponse(BaseModel):
    markdown: str


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    prompt = build_chat_prompt(payload.message)
    response_text = claude_client.complete(prompt, history=payload.history)
    return ChatResponse(response=response_text)


@app.post("/extract-brief", response_model=ExtractBriefResponse)
def extract_brief(payload: ExtractBriefRequest) -> ExtractBriefResponse:
    prompt = build_extract_prompt(payload.text)
    response_text = claude_client.complete(prompt)
    try:
        brief = parse_json_response(response_text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model returned invalid JSON: {str(exc)}",
        ) from exc
    return ExtractBriefResponse(brief=brief)


@app.post("/generate-md", response_model=GenerateMarkdownResponse)
def generate_md(payload: GenerateMarkdownRequest) -> GenerateMarkdownResponse:
    brief_json = safe_json_dumps(payload.brief)
    prompt = build_markdown_prompt(brief_json)
    markdown = claude_client.complete(prompt)
    return GenerateMarkdownResponse(markdown=markdown)
