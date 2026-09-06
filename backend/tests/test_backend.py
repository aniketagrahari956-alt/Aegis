import pytest
import os
import sys
import numpy as np
import pandas as pd

# Add backend to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.preprocessing import ThreatPreprocessor, FEATURE_COLUMNS, CLASS_LABEL_TO_INT
from app.ml.ensemble import ThreatEnsembleScorer, map_severity

class DummySupervisedModel:
    def predict_proba(self, X):
        # Always predict normal with 0.9 confidence (index 0)
        probs = np.zeros((X.shape[0], 5))
        probs[:, 0] = 0.9
        probs[:, 1] = 0.1
        return probs

class DummyAnomalyModel:
    def __init__(self, offset=-0.5):
        self.offset_ = offset
    def score_samples(self, X):
        # Return a non-anomalous score
        return np.array([-0.3])

class DummyAnomalyModelOutlier(DummyAnomalyModel):
    def score_samples(self, X):
        # Return an anomalous score (lower than offset)
        return np.array([-0.7])

def test_map_severity():
    assert map_severity("u2r", 0.9, -0.1) == "Critical"
    assert map_severity("u2r", 0.5, -0.1) == "High"
    assert map_severity("dos", 0.9, -0.1) == "High"
    assert map_severity("probe", 0.5, -0.1) == "Medium"
    assert map_severity("suspicious", 0.8, -0.7) == "High"
    assert map_severity("normal", 0.9, -0.1) == "Low"

def test_ensemble_scorer_benign():
    supervised = DummySupervisedModel()
    anomaly = DummyAnomalyModel()
    scorer = ThreatEnsembleScorer(supervised, anomaly)
    
    # Mock transformed features
    X_mock = np.zeros((1, 10))
    res = scorer.predict_record(X_mock)
    
    assert res["verdict"] == "normal"
    assert res["is_threat"] is False
    assert res["severity"] == "Low"

def test_ensemble_scorer_suspicious():
    supervised = DummySupervisedModel()
    anomaly = DummyAnomalyModelOutlier() # Trigger anomaly
    scorer = ThreatEnsembleScorer(supervised, anomaly)
    
    X_mock = np.zeros((1, 10))
    res = scorer.predict_record(X_mock)
    
    assert res["verdict"] == "suspicious"
    assert res["is_threat"] is True
    assert res["severity"] in ["Medium", "High"]

# Test client endpoints
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_protected_endpoints_unauthorized():
    # Alerts requires auth
    response = client.get("/api/alerts")
    assert response.status_code == 401

    # Overview stats requires auth
    response = client.get("/api/stats/overview")
    assert response.status_code == 401
