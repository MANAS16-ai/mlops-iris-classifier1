# Practical 10: Docker Containerization of the Iris ML Application

## Objective and architecture

The Iris classifier is packaged as a Python HTTP service with a model trained during the Docker image build. The multi-stage build separates model creation from serving:

- **Builder:** installs pinned dependencies, reads `data/processed/iris_features.csv`, and writes `models/final_model.joblib` and `models/label_encoder.joblib`.
- **Runtime:** copies the installed Python packages, model artifacts, and `src/serve.py` into a fresh Python runtime image. Training data and training code are not included in this stage.

Dependencies are installed before application files are copied, so source-only changes can reuse the dependency build layer. `.dockerignore` excludes Git history, virtual environments, caches, experiment output, and documentation while retaining the processed CSV needed by the builder.

## Build and run

Run from the repository root:

```bash
docker build -t iris-classifier:v1 .
docker run -d --name iris-classifier-container -p 8000:8000 iris-classifier:v1
```

The application listens on container port `8000`, published as host port `8000`. Check its status and Docker health:

```bash
docker ps
docker inspect --format='{{.State.Health.Status}}' iris-classifier-container
```

The image defines a health check against `/health` every 30 seconds, with a 5-second timeout, a 10-second start period, and 3 retries.

## API verification

Check health:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy"}
```

Submit all seven model features to `POST /predict`:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal length (cm)":5.1,"sepal width (cm)":3.5,"petal length (cm)":1.4,"petal width (cm)":0.2,"sepal_area":17.85,"petal_area":0.28,"sepal_to_petal_length_ratio":3.642857}'
```

The verified response was:

```json
{"prediction":"setosa","probabilities":[1.0,0.0,0.0]}
```

A request missing required fields returns HTTP 400 and a JSON `missing` list. The incomplete payload `{"sepal length (cm)":5.1}` was verified to return HTTP 400.

## Image size, layers, and cache

The verified image was reported as **680 MB disk usage** and **155 MB content size** by `docker images`. This is not a tens-of-megabytes image: scikit-learn, NumPy, pandas, and SciPy make up a significant runtime dependency footprint.

The multi-stage build keeps training-only data and code out of the final runtime stage. A single-stage baseline was not built, so no measured size comparison is claimed. Inspect the image layers with:

```bash
docker history iris-classifier:v1
```

Rebuild without changing inputs to check layer cache reuse:

```bash
docker build -t iris-classifier:v1 .
```

## Logs and cleanup

View startup and request logs:

```bash
docker logs iris-classifier-container
```

Stop and remove the container after use:

```bash
docker stop iris-classifier-container
docker rm iris-classifier-container
```

The image remains available locally after removing the container.

## Verification results

- The image built and trained the model from 149 CSV rows.
- The container started healthy with port `8000` published.
- `GET /health` returned `{"status":"healthy"}`.
- The sample prediction returned `setosa` and probabilities `[1.0, 0.0, 0.0]`.
- An incomplete prediction request returned HTTP 400.
- Container logs showed service startup and health/prediction requests.
- The container was stopped and removed after testing.
