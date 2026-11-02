# CI Pipeline

## Overview

The GitHub Actions workflow in `.github/workflows/ci.yml` runs for pushes to
`main` and `develop` and pull requests targeting those branches. Each job uses
a fresh Ubuntu runner with Python 3.11.

## Jobs and dependency order

The workflow runs jobs in this order:

```text
build-and-lint
      |
      v
test-suite
      |
      v
model-quality-gate
```

- **build-and-lint** installs project and CI dependencies, compiles `src/` and
  `tests/`, and runs Flake8 against `src/`.
- **test-suite** depends on `build-and-lint`. It collects the Iris data, runs
  preprocessing and feature engineering, and executes the complete pytest
  suite with coverage and JUnit XML output.
- **model-quality-gate** depends on `test-suite`. It prepares its own Iris
  feature data and runs `tests/test_model_quality.py` in a dedicated job. Data
  preparation is repeated because jobs do not share files between runners.

When a dependency fails, dependent jobs are skipped by default. The full
pytest suite includes the model-quality test, so a threshold regression fails
`test-suite`; `model-quality-gate` is then skipped because it requires the
successful completion of `test-suite`.

## Reports

The test job creates `test-results.xml` and `coverage.xml` and uploads them as
the `test-and-coverage-reports` artifact, including on failure if the files
were generated. When JUnit output exists, the workflow publishes a
`Pytest Results` check using `dorny/test-reporter`. That check is skipped for
pull requests from forks because their workflow token cannot write checks;
report artifacts continue to be uploaded.

## Branch protection

The workflow cannot configure GitHub repository settings. To enforce CI before
merging to `main`, configure a branch ruleset or branch-protection rule in
GitHub. Require pull requests and require the status checks
`build-and-lint`, `test-suite`, and `model-quality-gate` to pass. Optionally
require branches to be up to date before merging.

Repository settings and GitHub run history are external to this source tree;
their configuration and execution must be verified in the repository's
Settings and Actions pages.

## Regression verification

The intended regression demonstration is to change
`MIN_ACCEPTABLE_ACCURACY` in `tests/test_model_quality.py` from `0.90` to
`0.999` on a temporary feature branch, then open a pull request without
merging it. The model-quality assertion should fail if measured accuracy is
below `0.999`. Because this test also runs in `test-suite`, that job should
fail and `model-quality-gate` should be skipped due to its `needs: test-suite`
dependency.

Do not treat this scenario as evidence of a completed GitHub run until the
Actions logs have been inspected. Restore the threshold to `0.90` and close
the demonstration pull request without merging it.

## Local verification

Run the local checks from the repository root:

```bash
python -m pip install -r requirements.txt
python -m pip install flake8 pytest-cov
python -m compileall -q src tests
python -m flake8 src/ --max-line-length=100 --extend-ignore=E203 --statistics
python src/pipeline/collect.py --output data/raw/iris_raw.csv
python src/pipeline/preprocess.py --input data/raw/iris_raw.csv --output data/processed/iris_preprocessed.csv
python src/pipeline/features.py --input data/processed/iris_preprocessed.csv --output data/processed/iris_features.csv
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=test-results.xml
```
