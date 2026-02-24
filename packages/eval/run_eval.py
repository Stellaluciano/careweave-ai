from __future__ import annotations

import argparse
import json
from pathlib import Path

from packages.agents.graph import CareGraph
from packages.core.config import get_settings


def citation_coverage(answer: str, citations: list[dict]) -> float:
    return 1.0 if answer and len(citations) > 0 else 0.0


def groundedness_proxy(answer: str, citations: list[dict]) -> float:
    if not answer or not citations:
        return 0.0
    answer_tokens = set(answer.lower().split())
    citation_tokens = set(" ".join(c["text"] for c in citations).lower().split())
    if not answer_tokens:
        return 0.0
    return len(answer_tokens & citation_tokens) / len(answer_tokens)


def refusal_policy(question: str, answer: str) -> float:
    out_of_scope = any(k in question.lower() for k in ["weather", "sports", "stocks"])
    if not out_of_scope:
        return 1.0
    return (
        1.0
        if "healthcare" in answer.lower()
        or "provide a domain-specific" in answer.lower()
        else 0.0
    )


def run_eval(n: int | None = None) -> dict:
    settings = get_settings()
    graph = CareGraph()
    data = []
    with open("packages/eval/eval_set.jsonl", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    if n is not None:
        data = data[:n]

    rows = []
    for item in data:
        result = graph.run(item["question"], top_k=item.get("top_k", settings.retrieval_top_k))
        rp = refusal_policy(item["question"], result["answer"])
        out_of_scope = any(
            k in item["question"].lower() for k in ["weather", "sports", "stocks"]
        )
        cc = (
            1.0
            if out_of_scope and rp == 1.0
            else citation_coverage(result["answer"], result["citations"])
        )
        gp = groundedness_proxy(result["answer"], result["citations"])
        rows.append(
            {
                "id": item["id"],
                "scores": {
                    "citation_coverage": cc,
                    "groundedness_proxy": gp,
                    "refusal_policy": rp,
                },
            }
        )

    metrics = {
        "citation_coverage": sum(r["scores"]["citation_coverage"] for r in rows) / len(rows),
        "groundedness_proxy": sum(r["scores"]["groundedness_proxy"] for r in rows) / len(rows),
        "refusal_policy": sum(r["scores"]["refusal_policy"] for r in rows) / len(rows),
    }
    report = {"items": rows, "aggregate": metrics, "quality_gate": quality_gate(metrics)}
    report_path = Path(settings.eval_report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def quality_gate(metrics: dict[str, float]) -> dict[str, object]:
    settings = get_settings()
    passed = (
        metrics["citation_coverage"] >= settings.threshold_citation_coverage
        and metrics["groundedness_proxy"] >= settings.threshold_groundedness_proxy
    )
    return {
        "pass": passed,
        "thresholds": {
            "citation_coverage": settings.threshold_citation_coverage,
            "groundedness_proxy": settings.threshold_groundedness_proxy,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=None)
    args = parser.parse_args()
    report = run_eval(args.n)
    print(json.dumps(report["aggregate"], indent=2))
    if not report["quality_gate"]["pass"]:
        raise SystemExit("Quality gate failed")


if __name__ == "__main__":
    main()
