# CareWeave

Agentic Healthcare Intelligence Platform — Multi-Agent AI + RAG + Evaluation + CI/CD.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m packages.retrieval.build_index
uvicorn apps.api.main:app --reload
```

API endpoints:
- `GET /health`
- `POST /ask` with `{ "question": "...", "top_k": 3 }`

Run checks:

```bash
make lint
make test
make eval
```

## Architecture

```text
Client -> FastAPI (/ask)
           |
           v
      Agent Graph
    [Planner -> Retriever -> Synthesizer]
           |
           v
     Retrieval package (Chroma, local persist)
           |
           v
     data/sample_corpus -> data/chroma

Eval pipeline (packages/eval) -> artifacts/eval_report.json -> quality gate -> CI fail/pass
```

## Repository Layout
- `apps/api/` FastAPI application
- `packages/agents/` planner/retriever/synthesizer graph
- `packages/retrieval/` chunking, Chroma backend, index builder
- `packages/eval/` eval set, metrics, gate
- `packages/core/` config and logging
- `tests/` unit/integration tests
- `infra/docker/` Dockerfile
- `infra/scripts/` helper script
- `.github/workflows/` CI + CD workflow

## Evaluation + Quality Gate
Run:

```bash
python -m packages.eval.run_eval --n 4
```

Generates `artifacts/eval_report.json` with per-item scores and aggregates.
Quality gate uses:
- `citation_coverage >= 0.80`
- `groundedness_proxy >= 0.20`

Thresholds are configurable by env vars.

## Docker

```bash
docker build -f infra/docker/Dockerfile -t careweave:latest .
docker run -p 8000:8000 careweave:latest
```
