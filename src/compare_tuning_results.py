"""Pulls baseline, grid-search, and random-search runs from MLflow and prints a consolidated comparison table."""

import mlflow
from mlflow.tracking import MlflowClient


mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()
experiment = client.get_experiment_by_name("iris-hyperparameter-tuning")

if experiment is None:
    raise RuntimeError("Experiment 'iris-hyperparameter-tuning' was not found in MLflow.")

runs = client.search_runs(experiment_ids=[experiment.experiment_id])

print(f"{'Run Name':<28}{'CV f1_macro':<15}{'Test Accuracy':<15}{'Total Fits':<12}")
print("-" * 70)

for run in sorted(runs, key=lambda r: r.data.tags.get("mlflow.runName", "")):
    name = run.data.tags.get("mlflow.runName", "unknown")
    cv_score = run.data.metrics.get("cv_f1_macro_mean", run.data.metrics.get("best_cv_f1_macro", 0.0))
    test_acc = run.data.metrics.get("test_accuracy", 0.0)

    total_combinations = run.data.params.get("total_combinations")
    n_iter = run.data.params.get("n_iter")

    if name == "baseline_decision_tree":
        total_fits = 5
    elif total_combinations is not None:
        total_fits = int(total_combinations) * 5
    elif n_iter is not None:
        total_fits = int(n_iter) * 5
    else:
        total_fits = 5

    print(f"{name:<28}{cv_score:<15.4f}{test_acc:<15.4f}{total_fits:<12}")
