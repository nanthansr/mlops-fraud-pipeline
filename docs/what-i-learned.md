# What I Learned Building This

## Why I built it

I didn't build this to check a box. I built it because I kept reading job postings that said "production ML experience" and realized I had no idea what that actually meant beyond training a model and calling it done.

Most ML tutorials stop at "model achieved 95% accuracy." Nobody tells you what happens after that — when the model is sitting behind an API in production, and the data it's seeing starts to look different from the data it was trained on, and nobody notices for three weeks because there's no monitoring. That's the gap I wanted to understand.

Fraud detection was the vehicle because the class imbalance problem (577:1) forces you to think carefully about metrics and thresholds. But the real project is everything after the model: the deployment pipeline, the monitoring stack, the drift detection, and the alerting that proves the system can catch its own problems.

## The hardest part

Getting Evidently 0.7.x to work was brutal. The API changed significantly between 0.5 and 0.7 — `metric_preset` moved to `presets`, `Report.run()` now returns a `Snapshot` instead of mutating in place, and the dict structure for drift results changed completely. The official docs hadn't caught up. I spent about 3 hours reading Evidently source code on GitHub to figure out the new `Snapshot.dict()` structure and how to extract drift share.

The second hardest part was understanding why my Grafana alert rule kept saying "No data" even though Prometheus had the metrics. The issue was a PromQL label mismatch — `fraud_predictions_total` has a `result` label that `prediction_requests_total` doesn't. Dividing two counters with mismatched label sets returns empty in PromQL. The fix was one word: `ignoring(result)`. Finding that one word took two hours.

## What I'd change

1. **The S3 prediction logging** — logging every prediction as a separate S3 object works, but it's expensive at scale (one PUT per prediction). In a real system, I'd batch predictions in memory and flush to S3 every N seconds or N records, or use Kinesis Firehose.

2. **The model itself** — XGBoost on PCA-transformed features is fine for a demo, but in a real fraud system you'd want raw transaction features (merchant category, time since last transaction, transaction velocity) that have business meaning. PCA features make drift detection less interpretable — you can detect that V14 drifted, but you can't explain *why* to a product team.

3. **Authentication** — the API has none. In production, every endpoint would be behind an API key or OAuth2, and the monitoring endpoints would have different access controls than the prediction endpoint.

4. **Model retraining** — this pipeline deploys a static model. A production system needs a retraining trigger (scheduled or drift-triggered), a challenger model evaluation step, and a safe promotion flow. I built the monitoring that would trigger a retrain, but not the retrain loop itself.

## What this project doesn't do

- It doesn't do real-time feature engineering. Features come pre-computed from the dataset.
- It doesn't handle model A/B testing or canary deployments.
- It doesn't have a feedback loop — there's no way to tell the system "this prediction was wrong" and have it learn.
- The drift detection is batch, not streaming. In a low-latency system, you'd want windowed drift checks.
- It doesn't address data privacy or PII handling — real fraud systems have strict compliance requirements.

I'm not listing these as failures. I'm listing them because knowing what a system *doesn't* do is as important as knowing what it does, and because these are exactly the things I'd build next.
