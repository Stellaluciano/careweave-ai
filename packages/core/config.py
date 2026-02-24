from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "CareWeave")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "420"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    chroma_path: str = os.getenv("CHROMA_PATH", "data/chroma")
    corpus_path: str = os.getenv("CORPUS_PATH", "data/sample_corpus")
    eval_report_path: str = os.getenv("EVAL_REPORT_PATH", "artifacts/eval_report.json")
    threshold_citation_coverage: float = float(os.getenv("THRESHOLD_CITATION_COVERAGE", "0.80"))
    threshold_groundedness_proxy: float = float(os.getenv("THRESHOLD_GROUNDEDNESS_PROXY", "0.20"))


def get_settings() -> Settings:
    return Settings()
