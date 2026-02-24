from __future__ import annotations

from dataclasses import dataclass

from packages.retrieval.store import RetrievedDoc, default_backend


@dataclass
class GraphState:
    question: str
    top_k: int
    retrieval_used: bool = False
    plan_summary: str = ""
    docs: list[RetrievedDoc] | None = None
    answer: str = ""


class CareGraph:
    def __init__(self) -> None:
        self.retriever = default_backend()

    def run(self, question: str, top_k: int) -> dict:
        state = GraphState(question=question, top_k=top_k)
        trace: list[dict[str, str | bool | int]] = []

        self._planner(state)
        trace.append(
            {
                "step": "planner",
                "retrieval_used": state.retrieval_used,
                "summary": state.plan_summary,
            }
        )

        if state.retrieval_used:
            self._retriever(state)
            trace.append({"step": "retriever", "num_docs": len(state.docs or [])})

        self._synthesizer(state)
        trace.append({"step": "synthesizer", "summary": "generated grounded response"})

        return {
            "answer": state.answer,
            "citations": [
                {"source_id": d.source_id, "text": d.text[:280]} for d in (state.docs or [])
            ],
            "trace": {"steps": trace},
        }

    def _planner(self, state: GraphState) -> None:
        keywords = ["trial", "treatment", "clinical", "disease", "biomarker", "care"]
        state.retrieval_used = any(k in state.question.lower() for k in keywords)
        state.plan_summary = (
            "retrieve evidence" if state.retrieval_used else "general safe response"
        )

    def _retriever(self, state: GraphState) -> None:
        state.docs = self.retriever.retrieve(state.question, state.top_k)

    def _synthesizer(self, state: GraphState) -> None:
        if not state.retrieval_used:
            state.answer = (
                "I can help with healthcare intelligence questions. "
                "Please provide a domain-specific question."
            )
            return
        if not state.docs:
            state.answer = "I couldn't find supporting evidence in the local corpus."
            return
        summary = " ".join(d.text for d in state.docs[:2])
        state.answer = f"Based on retrieved evidence: {summary[:500]}"
