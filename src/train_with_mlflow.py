"""Train multiple Iris models and log each run to MLflow."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    root = project_root()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("iris-classification-baseline")

    data_path = root / "data" / "processed" / "iris_features.csv"
    df = pd.read_csv(data_path)
    print("Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())

    feature_cols = [
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
        "sepal_area",
        "petal_area",
        "sepal_to_petal_length_ratio",
    ]
    target_col = "species"

    X = df[feature_cols].copy()
    X = X.fillna(X.median())

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=200, C=1.0),
        "random_forest_shallow": RandomForestClassifier(
            n_estimators=50,
            max_depth=3,
            random_state=42,
        ),
        "random_forest_deep": RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=42,
        ),
    }

    results = []

    for model_name, model in models.items():
        print("\n" + "=" * 60)
        print("Training:", model_name)
        print("=" * 60)

        with mlflow.start_run(run_name=model_name):
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
            recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

            mlflow.log_param("model_type", model_name)
            if model_name == "logistic_regression":
                mlflow.log_param("max_iter", 200)
                mlflow.log_param("C", 1.0)
            else:
                mlflow.log_param("n_estimators", model.n_estimators)
                mlflow.log_param("max_depth", model.max_depth)

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision_macro", precision)
            mlflow.log_metric("recall_macro", recall)
            mlflow.log_metric("f1_macro", f1)

            cm = confusion_matrix(y_test, y_pred)
            disp = ConfusionMatrixDisplay(
                confusion_matrix=cm,
                display_labels=label_encoder.classes_,
            )
            disp.plot()
            plt.title(f"Confusion Matrix - {model_name}")
            plt.tight_layout()

            artifact_path = root / f"confusion_matrix_{model_name}.png"
            plt.savefig(artifact_path)
            plt.close()
            mlflow.log_artifact(str(artifact_path))

            mlflow.sklearn.log_model(model, artifact_path="model")

            results.append(
                {
                    "run_id": mlflow.active_run().info.run_id,
                    "model": model_name,
                    "accuracy": accuracy,
                    "precision_macro": precision,
                    "recall_macro": recall,
                    "f1_macro": f1,
                }
            )

            print("Accuracy :", accuracy)
            print("Precision:", precision)
            print("Recall   :", recall)
            print("F1 Score :", f1)

    results_df = pd.DataFrame(results)
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(results_df.to_string(index=False))

    best_model = results_df.loc[results_df["f1_macro"].idxmax()]
    print("\nBest model based on F1 score:")
    print(best_model)


if __name__ == "__main__":
    main()
