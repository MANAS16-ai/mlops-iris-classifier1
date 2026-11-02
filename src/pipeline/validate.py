"""Stage 4: Data validation.

Schema and statistical checks that must pass before data can flow downstream.
"""
import argparse
import logging
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate")

EXPECTED_COLUMNS = {
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
    "species",
    "sepal_area",
    "petal_area",
    "sepal_to_petal_length_ratio",
    "petal_length_bin",
}
VALID_SPECIES = {"setosa", "versicolor", "virginica"}
RANGE_CHECKS = {
    "sepal length (cm)": (3.0, 9.0),
    "sepal width (cm)": (1.5, 5.5),
    "petal length (cm)": (0.5, 8.0),
    "petal width (cm)": (0.05, 3.0),
}


class DataValidationError(Exception):
    """Raised when input data fails validation."""


def validate(input_path: str) -> pd.DataFrame:
    """Validate a feature CSV and return it when every check passes."""
    df = pd.read_csv(input_path)
    validation_errors = []

    missing_cols = EXPECTED_COLUMNS - set(df.columns)
    if missing_cols:
        validation_errors.append(f"Missing expected columns: {sorted(missing_cols)}")

    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        validation_errors.append(f"Unexpected null values in columns: {null_cols}")

    # Only inspect columns after confirming they exist; report schema problems
    # as DataValidationError rather than leaking a KeyError.
    if "species" in df.columns:
        invalid_species = set(df["species"].dropna().unique()) - VALID_SPECIES
        if invalid_species:
            validation_errors.append(
                f"Unexpected species values: {sorted(invalid_species)}"
            )

    for col, (low, high) in RANGE_CHECKS.items():
        if col not in df.columns:
            continue
        values = pd.to_numeric(df[col], errors="coerce")
        invalid_numeric = values.isna()
        if invalid_numeric.any():
            validation_errors.append(f"Non-numeric values found in column '{col}'")
            continue
        out_of_range = values[(values < low) | (values > high)]
        if not out_of_range.empty:
            validation_errors.append(
                f"{len(out_of_range)} rows out of expected range for "
                f"'{col}' ({low}-{high})"
            )

    if validation_errors:
        raise DataValidationError(
            f"Validation failed with {len(validation_errors)} error(s): "
            + "; ".join(validation_errors)
        )

    logger.info(
        "Validation PASSED: %d rows, %d columns, all checks satisfied",
        len(df),
        df.shape[1],
    )
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/iris_features.csv")
    args = parser.parse_args()
    try:
        validate(args.input)
    except (DataValidationError, FileNotFoundError, pd.errors.ParserError) as exc:
        logger.error("Pipeline halted: %s", exc)
        sys.exit(1)
