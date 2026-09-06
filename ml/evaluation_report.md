# Model Evaluation Report

## Supervised XGBoost Classifier Performance

- **Overall Accuracy**: 0.7761
- **ROC-AUC (Macro One-vs-Rest)**: 0.9491
- **False Positive Rate (FPR)**: 0.0279 (Benign vs. Any Attack)

### Per-Class Metrics

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| NORMAL | 0.6814 | 0.9721 | 0.8012 | 9711.0 |
| DOS | 0.9638 | 0.8359 | 0.8953 | 7458.0 |
| PROBE | 0.8005 | 0.6497 | 0.7173 | 2421.0 |
| R2L | 0.9798 | 0.0882 | 0.1619 | 2754.0 |
| U2R | 0.7000 | 0.0350 | 0.0667 | 200.0 |

### Confusion Matrix

```
[[9440   68  201    1    1]
 [1036 6234  188    0    0]
 [ 681  166 1573    1    0]
 [2508    0    1  243    2]
 [ 188    0    2    3    7]]
```

## Unsupervised Anomaly Detection (Isolation Forest)

Trained on normal/benign network traffic records only. Evaluated on full test set (Normal vs. Any Attack):

- **Precision (Treating attacks as outliers)**: 0.9755
- **Recall (Sensitivity to attacks)**: 0.6538
- **F1-Score**: 0.7829
- **False Positive Rate (FPR)**: 0.0217

### Anomaly Score Distribution Overview
- Min Score: -0.6552
- Max Score: -0.3168
- Mean Score: -0.4479
