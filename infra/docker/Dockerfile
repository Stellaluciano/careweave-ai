FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY apps /app/apps
COPY packages /app/packages
COPY data /app/data
RUN pip install --no-cache-dir -e .
RUN python -m packages.retrieval.build_index
EXPOSE 8000
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
