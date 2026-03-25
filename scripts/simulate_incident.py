"""
Simulate incidents against the fraud detection API.

Usage:
  python scripts/simulate_incident.py --incident fraud_spike
  python scripts/simulate_incident.py --incident distribution_shift
"""
import argparse
import random
import requests

BASELINE = {
    "V1": 0.0, "V2": 0.0, "V3": 0.0, "V4": 0.0, "V5": 0.0,
    "V6": 0.0, "V7": 0.0, "V8": 0.0, "V9": 0.0, "V10": 0.0,
    "V11": 0.0, "V12": 0.0, "V13": 0.0, "V14": 0.0, "V15": 0.0,
    "V16": 0.0, "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0,
    "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0, "V25": 0.0,
    "V26": 0.0, "V27": 0.0, "V28": 0.0,
    "Amount": 50.0,
}


def fraud_spike(url: str, n: int = 50):
    """Send transactions with feature values strongly associated with fraud."""
    print(f"[fraud_spike] Sending {n} high-fraud-probability transactions to {url}")

    fraud_count = 0
    for i in range(n):
        payload = {
            **BASELINE,
            "V1":  random.uniform(-5.0, -3.0),
            "V3":  random.uniform(-5.0, -3.0),
            "V4":  random.uniform(3.0, 5.0),
            "V10": random.uniform(-5.0, -3.0),
            "V11": random.uniform(3.0, 5.0),
            "V14": random.uniform(-7.0, -4.0),
            "Amount": random.uniform(1.0, 300.0),
        }
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        if result["is_fraud"]:
            fraud_count += 1

    fraud_rate = fraud_count / n
    print(f"[fraud_spike] Done. Fraud rate observed: {fraud_count}/{n} ({fraud_rate:.1%})")


def distribution_shift(url: str, n: int = 50):
    """Send transactions with Amount 100x normal and V1-V5 shifted outside training distribution."""
    print(f"[distribution_shift] Sending {n} out-of-distribution transactions to {url}")

    for i in range(n):
        payload = {
            **BASELINE,
            "V1": BASELINE["V1"] + 5.0,
            "V2": BASELINE["V2"] + 5.0,
            "V3": BASELINE["V3"] + 5.0,
            "V4": BASELINE["V4"] + 5.0,
            "V5": BASELINE["V5"] + 5.0,
            "Amount": random.uniform(5000.0, 15000.0),
        }
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()

    print(f"[distribution_shift] Done.")
    print(f"  Amount range : 5000 - 15000 (baseline ~50)")
    print(f"  V1-V5 shift  : +5.0 (pushed outside training distribution)")
    print(f"  Requests sent: {n}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--incident",
        required=True,
        choices=["fraud_spike", "distribution_shift"],
        help="Incident type to simulate",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/predict",
        help="Prediction endpoint URL",
    )
    args = parser.parse_args()

    if args.incident == "fraud_spike":
        fraud_spike(args.url)
    elif args.incident == "distribution_shift":
        distribution_shift(args.url)


if __name__ == "__main__":
    main()
