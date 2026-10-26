# Continuous Integration Workflow

The GitHub Actions workflow at `.github/workflows/ci.yml` checks changes pushed
to `main` and `develop`, as well as pull requests targeting those branches.
Each job runs on a fresh Ubuntu runner with Python 3.11.

## Jobs

The jobs run in sequence:

1. **build-and-lint** installs the project requirements and CI tools, compiles
   the Python files in `src/` and `tests/`, and lints `src/` with Flake8.
2. **test-suite** prepares Iris data through the collection, preprocessing, and
   feature-engineering scripts, then runs the complete pytest suite with
   coverage enabled.
3. **model-quality-gate** independently prepares the data and runs
   `tests/test_model_quality.py`. This explicitly checks the trained model's
   minimum accuracy threshold in a dedicated job.

The data-preparation steps are repeated in the last job because GitHub Actions
jobs use separate runners and do not share generated files by default.

## Reports

The test-suite job writes JUnit XML to `test-results.xml` and coverage XML to
`coverage.xml`. It uploads both as the
`test-and-coverage-reports` artifact, including when tests fail, when the files
were produced.

## Local checks

From the repository root, install the requirements and CI tools, then run:

```bash
python -m pip install -r requirements.txt
python -m pip install flake8 pytest-cov
python -m compileall -q src tests
python -m flake8 src/ --max-line-length=100 --extend-ignore=E203 --statistics
python src/pipeline/collect.py --output data/raw/iris_raw.csv
python src/pipeline/preprocess.py --input data/raw/iris_raw.csv --output data/processed/iris_preprocessed.csv
python src/pipeline/features.py --input data/processed/iris_preprocessed.csv --output data/processed/iris_features.csv
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=test-results.xml
python -m pytest tests/test_model_quality.py -v
```

To require these checks before merging, configure repository branch protection
or a ruleset on GitHub and mark the workflow's required jobs as required status
checks. The workflow itself does not change repository protection settings.
