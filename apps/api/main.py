from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, Request

from packages.agents.graph import CareGraph
from packages.agents.models import AskRequest, AskResponse, Citation
from packages.core.config import get_settings
from packages.core.logging import RequestLoggerAdapter, configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger("careweave.api")

app = FastAPI(title="CareWeave API", version="0.1.0")
graph = CareGraph()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, request: Request) -> AskResponse:
    req_logger = RequestLoggerAdapter(logger, {"request_id": request.state.request_id})
    req_logger.info("received ask request")
    if settings.debug:
        req_logger.info("question=%s", payload.question)

    result = graph.run(payload.question, payload.top_k or settings.retrieval_top_k)
    return AskResponse(
        request_id=request.state.request_id,
        answer=result["answer"],
        citations=[Citation(**c) for c in result["citations"]],
        trace=result["trace"],
    )
