import argparse
import datetime
import io
import json
import sys

import boto3
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway

BUCKET = "mlops-fraud-pipeline-artifacts-nanthan"
REFERENCE_PATH = "data/processed/reference.csv"
PUSHGATEWAY = "localhost:9091"
FEATURE_COLS = [f"V{i}" for i in range(1, 29)] + ["Amount"]


def load_predictions(date_str: str) -> pd.DataFrame:
    s3 = boto3.client("s3")
    prefix = f"prediction-logs/date={date_str}/"

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    objects = response.get("Contents", [])

    if not objects:
        print(f"No prediction logs found for {date_str} — exiting.")
        sys.exit(0)

    records = []
    for obj in objects:
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read().decode("utf-8")
        for line in body.strip().splitlines():
            records.append(json.loads(line))

    df = pd.DataFrame(records)
    return df[FEATURE_COLS]


def load_reference() -> pd.DataFrame:
    df = pd.read_csv(REFERENCE_PATH)
    return df[FEATURE_COLS]


def run_drift(reference: pd.DataFrame, current: pd.DataFrame) -> dict:
    preset = DataDriftPreset()
    report = Report(metrics=[preset])
    snapshot = report.run(current_data=current, reference_data=reference)
    result = snapshot.dict()

    # In evidently 0.7.x, DataDriftPreset expands into individual metrics.
    # The first metric is always DriftedColumnsCount with value={count, share}.
    drift_counts = result["metrics"][0]["value"]
    share = float(drift_counts["share"])
    dataset_drift_detected = int(share >= preset.drift_share)

    return {
        "dataset_drift_detected": dataset_drift_detected,
        "share_of_drifted_columns": share,
    }


def push_metrics(metrics: dict, date_str: str) -> None:
    registry = CollectorRegistry()

    Gauge(
        "drift_dataset_drift_detected",
        "1 if dataset drift detected, 0 otherwise",
        registry=registry,
    ).set(metrics["dataset_drift_detected"])

    Gauge(
        "drift_share_of_drifted_columns",
        "Share of features showing drift",
        registry=registry,
    ).set(metrics["share_of_drifted_columns"])

    pushadd_to_gateway(PUSHGATEWAY, job="drift_check", registry=registry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    args = parser.parse_args()

    print(f"Running drift check for date: {args.date}")

    current = load_predictions(args.date)
    print(f"Loaded {len(current)} predictions from S3")

    reference = load_reference()
    print(f"Loaded {len(reference)} reference rows")

    metrics = run_drift(reference, current)

    push_metrics(metrics, args.date)

    print(f"Drift detected     : {bool(metrics['dataset_drift_detected'])}")
    print(f"Drifted columns    : {metrics['share_of_drifted_columns']:.2%}")
    print("Metrics pushed to Pushgateway.")


if __name__ == "__main__":
    main()
