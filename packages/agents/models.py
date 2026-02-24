from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_id: str
    text: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int | None = None
    session_id: str | None = None


class AskResponse(BaseModel):
    request_id: str
    answer: str
    citations: list[Citation]
    trace: dict[str, list[dict[str, str | bool | int]]]
