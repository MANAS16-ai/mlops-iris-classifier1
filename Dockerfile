# Build dependencies and train the model in an isolated stage.
FROM python:3.11-slim AS builder
WORKDIR /build

COPY requirements-serving.txt .
RUN pip install --no-cache-dir --user -r requirements-serving.txt

COPY data/processed/iris_features.csv data/processed/iris_features.csv
COPY src/train_final_model.py src/train_final_model.py
RUN python src/train_final_model.py

# Runtime contains only inference dependencies, model artifacts, and server code.
FROM python:3.11-slim AS runtime
WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY --from=builder /build/models/ models/
COPY src/serve.py src/serve.py

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["python", "src/serve.py"]
