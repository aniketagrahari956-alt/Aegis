import numpy as np
from typing import Dict, Any
from .preprocessing import INT_TO_CLASS_LABEL

def map_severity(label: str, confidence: float, anomaly_score: float) -> str:
    """
    Map label and scoring statistics to alert severity: Critical, High, Medium, Low
    """
    if label == "u2r":
        return "Critical" if confidence >= 0.7 else "High"
    elif label == "r2l":
        return "High" if confidence >= 0.7 else "Medium"
    elif label == "dos":
        return "High" if confidence >= 0.8 else "Medium"
    elif label == "probe":
        return "Medium"
    elif label == "suspicious":
        # Unclassified anomaly
        return "High" if anomaly_score < -0.65 else "Medium"
    return "Low"

class ThreatEnsembleScorer:
    def __init__(self, supervised_model, anomaly_model):
        self.supervised = supervised_model
        self.anomaly = anomaly_model
        
    def predict_record(self, X_transformed: np.ndarray) -> Dict[str, Any]:
        """
        X_transformed: preprocessed single record features as a 2D numpy array (1, N)
        """
        # 1. Supervised prediction
        supervised_probs = self.supervised.predict_proba(X_transformed)[0]
        pred_class_idx = np.argmax(supervised_probs)
        pred_class_label = INT_TO_CLASS_LABEL[pred_class_idx]
        supervised_conf = float(supervised_probs[pred_class_idx])
        
        # 2. Anomaly detection score
        # score_samples returns negative anomaly score: lower is more anomalous (outlier)
        anomaly_score = float(self.anomaly.score_samples(X_transformed)[0])
        # offset_ is the decision boundary (usually around -0.5)
        is_anomaly = anomaly_score < self.anomaly.offset_
        
        # 3. Decision Logic
        verdict_label = pred_class_label
        confidence = supervised_conf
        
        # If supervised says benign (normal) but unsupervised flags a significant anomaly, raise alert
        if pred_class_label == "normal" and is_anomaly:
            verdict_label = "suspicious" # Unclassified anomaly / Zero-day threat
            # Anomaly confidence approximation based on depth score
            # score_samples is in range [-1, 0]. Let's scale: higher severity for scores closer to -1
            confidence = float(np.clip((abs(anomaly_score) - 0.5) * 2, 0.5, 0.99))
            
        severity = map_severity(verdict_label, confidence, anomaly_score)
        
        return {
            "verdict": verdict_label,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "is_threat": verdict_label != "normal"
        }
