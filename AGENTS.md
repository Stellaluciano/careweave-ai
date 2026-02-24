# CareWeave Agent Instructions

## Scope
These instructions apply to the entire repository.

## Engineering Rules
- Keep code modular and strongly typed.
- Avoid hidden chain-of-thought output. Only include high-level traces.
- Do not log full user prompts unless `DEBUG=true`.
- Keep all corpus content synthetic and non-PHI.

## Development Workflow
1. Build index before running retrieval-backed tests.
2. Run `make lint`, `make test`, and `make eval` before committing.
3. Keep CI quality gate thresholds in `packages/core/config.py`.

## PR Guidance
- Summarize architecture impact, tests run, and evaluation metrics.
- Include any known follow-ups explicitly.
