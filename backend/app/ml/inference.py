import os
import pandas as pd
import joblib
from typing import Dict, Any, List

# Relative imports from the current package/directory
from .preprocessing import ThreatPreprocessor, FEATURE_COLUMNS
from .ensemble import ThreatEnsembleScorer

class ThreatInferenceEngine:
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            # Locate relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            models_dir = os.path.join(base_dir, "ml", "models")
            
        self.preprocessor_path = os.path.join(models_dir, "preprocessor.joblib")
        self.supervised_path = os.path.join(models_dir, "supervised.joblib")
        self.anomaly_path = os.path.join(models_dir, "anomaly.joblib")
        
        self.preprocessor = None
        self.supervised_model = None
        self.anomaly_model = None
        self.ensemble_scorer = None
        self.is_loaded = False

    def load_models(self):
        if not os.path.exists(self.preprocessor_path) or \
           not os.path.exists(self.supervised_path) or \
           not os.path.exists(self.anomaly_path):
            raise FileNotFoundError(f"Model artifacts not found in directory. Train models first.")
            
        print(f"Loading preprocessor from {self.preprocessor_path}...")
        self.preprocessor = ThreatPreprocessor.load(self.preprocessor_path)
        
        print(f"Loading supervised classifier from {self.supervised_path}...")
        self.supervised_model = joblib.load(self.supervised_path)
        
        print(f"Loading anomaly detector from {self.anomaly_path}...")
        self.anomaly_model = joblib.load(self.anomaly_path)
        
        self.ensemble_scorer = ThreatEnsembleScorer(self.supervised_model, self.anomaly_model)
        self.is_loaded = True
        print("Threat Detection Inference Engine successfully loaded.")

    def score_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        raw_record: Dictionary containing the 41 network features of NSL-KDD
        """
        if not self.is_loaded:
            self.load_models()
            
        # Convert dictionary to single-row dataframe with specific columns
        df = pd.DataFrame([raw_record])
        
        # Ensure all columns exist, fill with default zeros if missing
        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0
                
        # Select correct columns order
        df_selected = df[FEATURE_COLUMNS]
        
        # Preprocess features
        X_transformed = self.preprocessor.transform(df_selected)
        
        # Score via Ensemble
        verdict = self.ensemble_scorer.predict_record(X_transformed)
        return verdict

    def score_batch(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score a batch of records
        """
        if not self.is_loaded:
            self.load_models()
            
        df = pd.DataFrame(raw_records)
        
        # Ensure columns
        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0
                
        df_selected = df[FEATURE_COLUMNS]
        X_transformed = self.preprocessor.transform(df_selected)
        
        results = []
        for i in range(len(raw_records)):
            row_features = X_transformed[i : i + 1]
            verdict = self.ensemble_scorer.predict_record(row_features)
            results.append(verdict)
            
        return results
