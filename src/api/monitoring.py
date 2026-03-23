from prometheus_client import Counter, Histogram

fraud_predictions_total = Counter(
    "fraud_predictions_total",
    "Count of fraud vs legit predictions",
    ["result"],
)

prediction_probability = Histogram(
    "prediction_probability",
    "Distribution of fraud probability scores",
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total number of /predict requests",
)
