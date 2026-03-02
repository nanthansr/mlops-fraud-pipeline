from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import joblib
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Model loading ──
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.joblib")
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info(f"✅ Model loaded from {MODEL_PATH}")
    else:
        logger.warning(f"⚠️  No model at {MODEL_PATH} — run src/model/train.py first")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="MLOps pipeline — predicts whether a transaction is fraudulent",
    version="0.1.0",
    lifespan=lifespan
)

# Expose /metrics endpoint for Prometheus to scrape
Instrumentator().instrument(app).expose(app)


# ── Request / Response schemas ──
class TransactionFeatures(BaseModel):
    """
    Features for a single transaction.
    V1-V28 are PCA-transformed features from the Kaggle dataset.
    Amount is the transaction amount in USD.
    """
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38,
                "V5": -0.34, "V6": 0.46, "V7": 0.24, "V8": 0.10,
                "V9": 0.36, "V10": 0.09, "V11": -0.55, "V12": -0.62,
                "V13": -0.99, "V14": -0.31, "V15": 1.47, "V16": -0.47,
                "V17": 0.21, "V18": 0.03, "V19": 0.40, "V20": 0.25,
                "V21": -0.02, "V22": 0.28, "V23": -0.11, "V24": 0.07,
                "V25": 0.13, "V26": -0.19, "V27": 0.13, "V28": -0.02,
                "Amount": 149.62
            }
        }
    }


class PredictionResponse(BaseModel):
    prediction: int           # 0 = legitimate, 1 = fraud
    fraud_probability: float  # model confidence
    is_fraud: bool
    model_version: str


# ── Endpoints ──
@app.get("/")
def root():
    return {"status": "running", "model_loaded": model is not None}


@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}


@app.post("/predict", response_model=PredictionResponse)
def predict(transaction: TransactionFeatures):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded — run train.py first")

    features = np.array([[
        transaction.V1, transaction.V2, transaction.V3, transaction.V4,
        transaction.V5, transaction.V6, transaction.V7, transaction.V8,
        transaction.V9, transaction.V10, transaction.V11, transaction.V12,
        transaction.V13, transaction.V14, transaction.V15, transaction.V16,
        transaction.V17, transaction.V18, transaction.V19, transaction.V20,
        transaction.V21, transaction.V22, transaction.V23, transaction.V24,
        transaction.V25, transaction.V26, transaction.V27, transaction.V28,
        transaction.Amount
    ]])

    prediction = int(model.predict(features)[0])
    fraud_prob = float(model.predict_proba(features)[0][1])

    logger.info(f"Prediction: {prediction} | Fraud probability: {fraud_prob:.4f} | Amount: {transaction.Amount}")

    return PredictionResponse(
        prediction=prediction,
        fraud_probability=round(fraud_prob, 4),
        is_fraud=bool(prediction),
        model_version="0.1.0"
    )
