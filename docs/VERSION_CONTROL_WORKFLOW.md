# Version Control Workflow — MLOps Iris Classifier

## 1. Overview

This document describes the Git-based version control workflow used for this Machine Learning project, developed as part of MLOps Lab Experiment 2.

- **Repository:** https://github.com/MANAS16-ai/mlops-iris-classifier1
- **Primary language:** Python
- **Maintainer:** MANAS

## 2. Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, always-deployable code |
| `develop` | Integration branch for day-to-day development |
| `feature/<name>` | Individual features, branched from and merged back into `develop` |
| `conflict-demo-*` | Demonstration branches created for conflict resolution practice |

**Rule:** No one commits directly to `main`.

Changes flow:

`feature/*` → Pull Request → `develop` → `main`

## 3. Commit Convention

Commits follow a short, imperative style with a type prefix:

- `feat:` — add new functionality
- `fix:` — correct a bug
- `docs:` — documentation changes
- `chore:` — tooling/configuration changes
- `refactor:` — code restructuring without behavior change

Example:

`feat: add classification report to training script`

## 4. Standard Workflow

```bash
git switch develop
git pull origin develop
git switch -c feature/<short-description>
# make changes
git add <files>
git commit -m "feat: <description>"
git push -u origin feature/<short-description>
# Open Pull Request into develop
# Review and merge through GitHub