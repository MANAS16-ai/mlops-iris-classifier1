"""Load the best registered Iris model from the MLflow Model Registry."""

from __future__ import annotations

import os

import mlflow
import mlflow.sklearn


def main() -> None:
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))

    model_uri = "models:/iris-classifier-prod/Staging"
    print("=" * 60)
    print("LOADING REGISTERED MODEL")
    print("=" * 60)
    print("Model URI:", model_uri)

    model = mlflow.sklearn.load_model(model_uri)
    print("\nModel loaded successfully!")
    print("Model type:", type(model))
    print("\nLoaded Model:")
    print(model)


if __name__ == "__main__":
    main()
