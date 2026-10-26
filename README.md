# mlops-iris-classifier — Version B 
A sample ML project used to demonstrate Git-based version control 
workflows in an MLOps context. 
 
## Setup 
```bash 
pip install -r requirements.txt 
python src/train.py 
```

## Continuous integration

GitHub Actions runs the build, lint, test, and model-quality checks on pushes
and pull requests targeting `main` or `develop`. See
[the CI workflow guide](docs/CI_WORKFLOW.md) for the jobs, reports, and local
validation commands.