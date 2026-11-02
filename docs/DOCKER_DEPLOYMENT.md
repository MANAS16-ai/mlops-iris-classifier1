# Docker Deployment

## Overview

The `Dockerfile` uses two stages:

- **Builder:** installs the pinned serving dependencies, reads
  `data/processed/iris_features.csv`, trains the Random Forest model, and
  writes the model and label encoder.
- **Runtime:** starts from `python:3.11-slim` and copies in the installed
  Python packages, model artifacts, and HTTP serving script. The dataset and
  training script are not copied into the runtime image.

Separating the stages keeps training inputs and code out of the running
container. The Python dependencies are also needed at inference time, however,
so the runtime image is not just the small Python base image.

## Build and run

Run these commands from the repository root:

```bash
docker build -t iris-classifier:v1 .
docker run -d --name iris-classifier-container -p 8000:8000 iris-classifier:v1
```

The server listens on port `8000`. Check container status and the health check:

```bash
docker ps
docker inspect --format='{{.State.Health.Status}}' iris-classifier-container
curl -i http://localhost:8000/health
```

The Docker health check requests `http://localhost:8000/health` every 30
seconds, allows 5 seconds for a response, waits 10 seconds before its first
check, and retries up to 3 times. A healthy response is:

```json
{"status": "healthy"}
```

## Prediction requests

`POST /predict` expects a JSON object with all seven feature names:

```bash
curl -i -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2, "sepal_area": 17.85, "petal_area": 0.28, "sepal_to_petal_length_ratio": 3.642857}'
```

For these sample values, the observed response was HTTP 200:

```json
{"prediction": "setosa", "probabilities": [1.0, 0.0, 0.0]}
```

An incomplete request is rejected with HTTP 400 and names the missing
features:

```bash
curl -i -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal length (cm)": 5.1}'
```

Observed response:

```json
{"error": "Missing features", "missing": ["sepal width (cm)", "petal length (cm)", "petal width (cm)", "sepal_area", "petal_area", "sepal_to_petal_length_ratio"]}
```

## Image size and layers

At inspection time, `docker image inspect` reported **680,336,529 bytes**
(about 649 MiB / 680 MB as displayed by Docker). `docker images iris-classifier`
reported 680 MB disk usage and 155 MB content size. These are Docker's reported
measurements, not a claim that the image is in the tens-of-megabytes range.

The image history showed about 383 MB in the copied Python package layer. This
is expected to dominate the image because the numerical and machine-learning
packages are required at prediction time. A naive single-stage build would
also retain the processed training CSV and training script in its image layers;
the multi-stage build excludes those files from the runtime image. No
single-stage comparison image was built, so a numerical size reduction versus
that baseline has not been measured.

Inspect the local image and its layers with:

```bash
docker images iris-classifier
docker history iris-classifier:v1
```

To check whether Docker can reuse layers on a subsequent build, repeat:

```bash
docker build -t iris-classifier:v1 .
```

On the verification rebuild, all unchanged dependency, training, and copy
steps were reported as cached.

## Logs and cleanup

View the server startup and request logs:

```bash
docker logs iris-classifier-container
```

The observed startup message is `Iris server listening on port 8000`.
Stop and remove the container when finished:

```bash
docker stop iris-classifier-container
docker rm iris-classifier-container
```

The image remains available locally after the container is removed.
