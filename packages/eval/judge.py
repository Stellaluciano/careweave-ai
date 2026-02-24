from __future__ import annotations

import os


def llm_judge_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def judge_score(*_: object, **__: object) -> float | None:
    if not llm_judge_available():
        return None
    return 0.5
