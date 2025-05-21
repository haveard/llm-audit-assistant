# Pydantic models

from typing import Optional

from pydantic import BaseModel


class DocumentUploadRequest(BaseModel):
    filename: str
    filetype: str
    size: int
    date: Optional[str] = None
    content: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


class LLMResponse(BaseModel):
    answer: str
    sources: Optional[list] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
