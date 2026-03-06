"""
Stage 1 — Train the fraud detection model

Run this after downloading the Kaggle dataset:
    python scripts/download_data.py
    python src/model/train.py

Saves model to models/model.joblib
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, roc_auc_score,
    precision_recall_curve, average_precision_score
)
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import mlflow
import mlflow.xgboost
import joblib
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)

# MLflow tracking URI — defaults to local docker-compose MLflow server.
# NOTE (Stage 2b): before CI can fetch the champion model from the registry,
# the backend store (currently ./mlruns, local only) must be moved to a shared
# location (e.g. S3-backed SQLite or hosted MLflow on EC2). See Stage 2b plan.
# MLflow 3.x uses aliases instead of Staging/Production stages.
# Promote a model version with alias "champion" in the UI.
# Fetch in CI with: mlflow.xgboost.load_model("models:/fraud-detector@champion")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")

DATA_PATH = "data/raw/creditcard.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")


def load_data(path: str) -> pd.DataFrame:
    logger.info(f"Loading data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Dataset: {df.shape[0]:,} rows | {df['Class'].sum():,} fraud cases ({df['Class'].mean()*100:.2f}%)")
    return df


def prepare_features(df: pd.DataFrame):
    """
    Drop Time (not predictive after PCA transform),
    scale Amount (only raw feature), keep V1-V28.
    """
    df = df.drop(columns=["Time"])
    X = df.drop(columns=["Class"])
    y = df["Class"]

    # Scale Amount to match V1-V28 range
    scaler = StandardScaler()
    X["Amount"] = scaler.fit_transform(X[["Amount"]])

    return X, y


def train(X_train, y_train):
    """
    XGBoost with class weighting for imbalance.
    SMOTE as an alternative — uncomment to compare.
    """
    logger.info("Training XGBoost classifier...")

    # Class weight approach
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    logger.info(f"scale_pos_weight: {scale_pos_weight:.1f} (handles {scale_pos_weight:.0f}:1 imbalance)")

    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,  # key param for imbalanced data
        random_state=42,
        eval_metric="aucpr",                # precision-recall AUC for imbalanced
        use_label_encoder=False
    )

    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_prob)
    avg_precision = average_precision_score(y_test, y_prob)

    logger.info("\n" + classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))
    logger.info(f"ROC-AUC: {roc_auc:.4f}")
    logger.info(f"Avg Precision (PR-AUC): {avg_precision:.4f}")

    return {
        "roc_auc": round(roc_auc, 4),
        "avg_precision": round(avg_precision, 4),
        "n_test": len(y_test),
        "n_fraud_test": int(y_test.sum())
    }


def main():
    # Load and prep
    df = load_data(DATA_PATH)
    X, y = prepare_features(df)

    # Split — stratify to preserve class ratio
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

    # MLflow setup
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("fraud-detection")

    with mlflow.start_run():
        # Train
        model = train(X_train, y_train)

        # Evaluate
        metrics = evaluate(model, X_test, y_test)

        # Log params
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 6)
        mlflow.log_param("learning_rate", 0.1)
        mlflow.log_param("scale_pos_weight", round((y_train == 0).sum() / (y_train == 1).sum(), 1))

        # Log metrics
        mlflow.log_metric("roc_auc", metrics["roc_auc"])
        mlflow.log_metric("avg_precision", metrics["avg_precision"])

        # Log model to MLflow registry (artifacts pushed to S3)
        mlflow.xgboost.log_model(
            model,
            artifact_path="model",
            registered_model_name="fraud-detector"
        )
        logger.info("✅ Model logged to MLflow registry as 'fraud-detector'")

        # Save locally too — FastAPI still loads from models/model.joblib
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        logger.info(f"✅ Model saved to {MODEL_PATH}")

        with open(METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✅ Metrics saved to {METRICS_PATH}")
        logger.info(f"\nFinal metrics: {metrics}")


if __name__ == "__main__":
    main()
