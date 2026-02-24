.PHONY: lint test eval run build-index

lint:
	ruff check .
	mypy apps packages

test:
	pytest -q

eval:
	python -m packages.eval.run_eval --n 4

build-index:
	python -m packages.retrieval.build_index

run:
	uvicorn apps.api.main:app --reload
