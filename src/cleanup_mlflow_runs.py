"""Delete extra MLflow runs so the experiment matches the intended three-model comparison."""

from __future__ import annotations

from mlflow.tracking import MlflowClient


def main() -> None:
    client = MlflowClient()
    experiment = client.get_experiment_by_name("iris-classification-baseline")
    if experiment is None:
        raise RuntimeError("Experiment 'iris-classification-baseline' not found.")

    runs = client.search_runs([experiment.experiment_id])
    print(f"Current run count: {len(runs)}")

    keep = min(3, len(runs))
    for run in runs[keep:]:
        client.delete_run(run.info.run_id)
        print(f"Deleted run {run.info.run_id} ({run.info.run_name})")

    remaining = client.search_runs([experiment.experiment_id])
    print(f"Remaining run count: {len(remaining)}")


if __name__ == "__main__":
    main()
