# Feature Store Analysis

## Objective
This project demonstrates how Feast centralizes feature definitions for an Iris ML workflow and makes the same feature pipeline reusable across training, online serving, and alternative model consumers.

## Observed benefits

### 1. Elimination of training-serving skew
The same feature definitions are registered once in the Feast repository and retrieved through `get_online_features` and `get_historical_features`. The online feature path serves the latest values for inference, while the historical path serves point-in-time-correct values for training. Because both are built from the same Feast feature views, there is no independent reimplementation that can drift over time.

### 2. Feature reusability
The feature service `iris_feature_service` exposes the same registered `iris_measurements` and `iris_engineered_features` definitions to multiple consumers. The retrieval script reuses these without re-deriving `sepal_area`, `petal_area`, or `sepal_to_petal_length_ratio` inside a second consumer workflow.

### 3. Centralized governance
The source of truth for the feature schema lives in the Feast repository rather than in scattered model-specific scripts. This makes ownership, validation, and reuse much easier than keeping duplicated logic across model pipelines.

## Summary
The Iris experiment confirms that Feast provides a single versioned place to define, register, materialize, and retrieve features. This reduces duplication, lowers the risk of inconsistent values between offline and online paths, and makes the same validated feature set available to different ML tasks.
