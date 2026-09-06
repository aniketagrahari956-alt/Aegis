import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Import preprocessor utilities
from preprocessing import ThreatPreprocessor, FEATURE_COLUMNS, ATTACK_MAPPING

def load_dataset(filepath):
    columns = FEATURE_COLUMNS + ["label", "difficulty_level"]
    df = pd.read_csv(filepath, header=None, names=columns)
    df["attack_class"] = df["label"].str.lower().map(ATTACK_MAPPING).fillna("normal")
    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, "ml", "data")
    models_dir = os.path.join(base_dir, "ml", "models")
    
    train_path = os.path.join(data_dir, "KDDTrain+.csv")
    test_path = os.path.join(data_dir, "KDDTest+.csv")
    preprocessor_path = os.path.join(models_dir, "preprocessor.joblib")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Dataset files not found.")
        return
    if not os.path.exists(preprocessor_path):
        print("Preprocessor not found. Please train the supervised model first.")
        return
        
    print("Loading datasets...")
    df_train = load_dataset(train_path)
    df_test = load_dataset(test_path)
    
    # Filter train data to NORMAL only
    df_train_normal = df_train[df_train["attack_class"] == "normal"]
    print(f"Training Isolation Forest on {len(df_train_normal)} normal/benign records (out of {len(df_train)} total).")
    
    # Load preprocessor
    preprocessor = ThreatPreprocessor.load(preprocessor_path)
    
    # Transform
    X_train_normal = preprocessor.transform(df_train_normal[FEATURE_COLUMNS])
    X_test = preprocessor.transform(df_test[FEATURE_COLUMNS])
    
    # Train Isolation Forest
    print("Training Isolation Forest...")
    # contamination = ratio of outliers expected in training, but we trained on purely benign
    # So we keep it default or small, and tune threshold.
    iforest = IsolationForest(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    iforest.fit(X_train_normal)
    
    # Save anomaly detector
    model_path = os.path.join(models_dir, "anomaly.joblib")
    joblib.dump(iforest, model_path)
    print(f"Saved anomaly detector model to {model_path}")
    
    # Evaluate anomaly detector
    print("Evaluating anomaly detector on test set...")
    # Isolation Forest: score_samples returns raw scores where lower is more anomalous
    # predict() returns 1 for inliers (normal) and -1 for outliers (anomalous)
    scores = iforest.score_samples(X_test) # range usually [-1, 0]
    predictions = iforest.predict(X_test) # 1 or -1
    
    # Let's map predictions: if prediction == -1, then threat/outlier
    # For evaluation, we treat "any attack class" as positive threat (1) and normal as negative (0)
    y_test_binary = (df_test["attack_class"] != "normal").astype(int).values
    
    # Let's evaluate using standard threshold (prediction == -1)
    y_pred_binary = (predictions == -1).astype(int)
    
    tn, fp, fn, tp = confusion_matrix(y_test_binary, y_pred_binary).ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (tn + fp) if (tn + fp) > 0 else 0
    
    print("\n--- Anomaly Detection Evaluation (Threshold = default) ---")
    print(f"Precision (Detecting any attack): {precision:.4f}")
    print(f"Recall (Detecting any attack): {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"False Positive Rate: {fpr:.4f}")
    
    # Append to evaluation_report.md
    report_path = os.path.join(base_dir, "ml", "evaluation_report.md")
    if os.path.exists(report_path):
        with open(report_path, "a") as f:
            f.write("\n## Unsupervised Anomaly Detection (Isolation Forest)\n\n")
            f.write("Trained on normal/benign network traffic records only. Evaluated on full test set (Normal vs. Any Attack):\n\n")
            f.write(f"- **Precision (Treating attacks as outliers)**: {precision:.4f}\n")
            f.write(f"- **Recall (Sensitivity to attacks)**: {recall:.4f}\n")
            f.write(f"- **F1-Score**: {f1:.4f}\n")
            f.write(f"- **False Positive Rate (FPR)**: {fpr:.4f}\n\n")
            f.write("### Anomaly Score Distribution Overview\n")
            f.write(f"- Min Score: {scores.min():.4f}\n")
            f.write(f"- Max Score: {scores.max():.4f}\n")
            f.write(f"- Mean Score: {scores.mean():.4f}\n")
    
    print(f"Anomaly report appended to {report_path}")

if __name__ == "__main__":
    main()
