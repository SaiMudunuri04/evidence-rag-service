"""Grounded retrieval API over an operator-provided document directory."""

import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .llm import ChatClient
from .observability import RequestLoggingMiddleware
from .rag import BM25Index, answer, load_documents

app = FastAPI(title="Evidence RAG", version="0.1.0")
app.add_middleware(RequestLoggingMiddleware)


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


@lru_cache(maxsize=1)
def index() -> BM25Index:
    root = Path(os.getenv("DOCUMENT_ROOT", "/data/documents"))
    if not root.is_dir():
        raise FileNotFoundError(root)
    records = load_documents(root)
    if not records:
        raise ValueError("Document directory is empty")
    return BM25Index(records)


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready():
    try:
        index()
    except (FileNotFoundError, ValueError):
        raise HTTPException(503, "Document index unavailable")
    return {"status": "ready"}


@app.post("/answer")
def generate(request: Question):
    try:
        search = index()
    except (FileNotFoundError, ValueError):
        raise HTTPException(503, "Document index unavailable")
    base_url, model = os.getenv("LLM_BASE_URL"), os.getenv("LLM_MODEL")
    if not base_url or not model:
        raise HTTPException(503, "Inference endpoint unavailable")
    return answer(request.question, search, ChatClient(base_url, model))
