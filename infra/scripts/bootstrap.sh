#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e ".[dev]"
python -m packages.retrieval.build_index
