import os
import mlflow
import mlflow.xgboost
import joblib


def fetch_champion_model():
    """Fetch the champion model from MLflow registry and save it for API loading."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        raise ValueError("MLFLOW_TRACKING_URI environment variable is not set")

    mlflow.set_tracking_uri(tracking_uri)
    os.makedirs("models", exist_ok=True)

    # Load the XGBoost model from MLflow registry using the xgboost flavor loader.
    # download_artifacts would dump the raw MLflow artifact directory (MLmodel, model.xgb, etc.)
    # but main.py expects joblib.load("models/model.joblib") — so we load + re-serialize.
    try:
        model = mlflow.xgboost.load_model("models:/fraud-detector@champion")
        joblib.dump(model, "models/model.joblib")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch champion model from MLflow: {exc}") from exc

    print("✅ Champion model fetched from MLflow and saved to models/model.joblib")


if __name__ == "__main__":
    fetch_champion_model()
