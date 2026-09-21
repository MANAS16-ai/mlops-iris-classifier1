# prepare_feature_source.py
"""Prepare the Experiment 4 Iris feature table for Feast."""

from pathlib import Path

import pandas as pd

repo_root = Path(__file__).resolve().parents[3]
input_file = repo_root / "data" / "processed" / "iris_features.csv"
output_file = Path(__file__).resolve().parent / "data" / "iris_features.parquet"

if not input_file.exists():
    raise FileNotFoundError(f"Input feature file not found: {input_file}")

df = pd.read_csv(input_file)

if "sample_id" not in df.columns:
    df.insert(0, "sample_id", range(len(df)))

start_time = pd.Timestamp("2026-08-15 15:20:02", tz="UTC")
df["event_timestamp"] = pd.date_range(start=start_time, periods=len(df), freq="min")
df["created_timestamp"] = df["event_timestamp"]

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_file, index=False)

print(f"Wrote {len(df)} rows to {output_file}")