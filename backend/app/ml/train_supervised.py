import os
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
from xgboost import XGBClassifier

# Import preprocessor utilities
from preprocessing import ThreatPreprocessor, FEATURE_COLUMNS, ATTACK_MAPPING, CLASS_LABEL_TO_INT, INT_TO_CLASS_LABEL

def load_dataset(filepath):
    # Standard columns list (41 features + label + difficulty)
    columns = FEATURE_COLUMNS + ["label", "difficulty_level"]
    df = pd.read_csv(filepath, header=None, names=columns)
    
    # Map specific attack types to 5 main categories
    df["attack_class"] = df["label"].str.lower().map(ATTACK_MAPPING)
    
    # Fill any unmapped attacks as 'normal' or 'probe' or ignore, but actually let's check
    # default to 'normal' if unknown just in case, but map should cover it
    df["attack_class"] = df["attack_class"].fillna("normal")
    
    # Convert label class to integer index
    df["label_int"] = df["attack_class"].map(CLASS_LABEL_TO_INT)
    
    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, "ml", "data")
    models_dir = os.path.join(base_dir, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    train_path = os.path.join(data_dir, "KDDTrain+.csv")
    test_path = os.path.join(data_dir, "KDDTest+.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Dataset files not found. Ensure downloader ran successfully.")
        return
        
    print("Loading datasets...")
    df_train = load_dataset(train_path)
    df_test = load_dataset(test_path)
    
    print(f"Train set size: {len(df_train)}, Test set size: {len(df_test)}")
    
    # Instantiate and fit preprocessor
    print("Fitting preprocessor...")
    preprocessor = ThreatPreprocessor()
    preprocessor.fit(df_train[FEATURE_COLUMNS])
    
    # Save preprocessor
    preprocessor_path = os.path.join(models_dir, "preprocessor.joblib")
    preprocessor.save(preprocessor_path)
    
    # Transform features
    X_train = preprocessor.transform(df_train[FEATURE_COLUMNS])
    y_train = df_train["label_int"].values
    
    X_test = preprocessor.transform(df_test[FEATURE_COLUMNS])
    y_test = df_test["label_int"].values
    
    # Train supervised XGBoost model
    print("Training XGBoost Classifier...")
    # Calculate class weights or balance if needed. Since U2R/R2L are rare, let's keep max_depth reasonable
    clf = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective='multi:softprob',
        num_class=5,
        random_state=42,
        eval_metric='mlogloss'
    )
    clf.fit(X_train, y_train)
    
    # Save model
    model_path = os.path.join(models_dir, "supervised.joblib")
    joblib.dump(clf, model_path)
    print(f"Saved supervised model to {model_path}")
    
    # Evaluate
    print("Evaluating model...")
    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)
    
    # Classification report
    target_names = [INT_TO_CLASS_LABEL[i] for i in range(5)]
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    report_text = classification_report(y_test, y_pred, target_names=target_names)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Calculate ROC-AUC One-Vs-Rest
    roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='macro')
    
    # Compute False Positive Rate (FPR) specifically for threat detection (treating benign/normal as negative, any attack as positive)
    # y_test_binary: 0 if normal, 1 if attack
    y_test_binary = (y_test != 0).astype(int)
    y_pred_binary = (y_pred != 0).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test_binary, y_pred_binary).ravel()
    fpr = fp / (tn + fp) if (tn + fp) > 0 else 0.0
    
    print("\n--- Model Evaluation ---")
    print(report_text)
    print(f"ROC-AUC (Macro OVR): {roc_auc:.4f}")
    print(f"False Positive Rate: {fpr:.4f}")
    
    # Save evaluation report metadata or start writing evaluation_report.md
    report_path = os.path.join(base_dir, "ml", "evaluation_report.md")
    
    # We will write the report content
    with open(report_path, "w") as f:
        f.write("# Model Evaluation Report\n\n")
        f.write("## Supervised XGBoost Classifier Performance\n\n")
        f.write(f"- **Overall Accuracy**: {report['accuracy']:.4f}\n")
        f.write(f"- **ROC-AUC (Macro One-vs-Rest)**: {roc_auc:.4f}\n")
        f.write(f"- **False Positive Rate (FPR)**: {fpr:.4f} (Benign vs. Any Attack)\n\n")
        f.write("### Per-Class Metrics\n\n")
        f.write("| Class | Precision | Recall | F1-Score | Support |\n")
        f.write("|---|---|---|---|---|\n")
        for cls in target_names:
            metrics = report[cls]
            f.write(f"| {cls.upper()} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1-score']:.4f} | {metrics['support']} |\n")
        
        f.write("\n### Confusion Matrix\n\n")
        f.write("```\n")
        f.write(str(cm))
        f.write("\n```\n")
    
    # Save structured metrics to metrics.json
    import json
    metrics_json_path = os.path.join(models_dir, "metrics.json")
    metrics_data = {
        "accuracy": float(report['accuracy']),
        "roc_auc": float(roc_auc),
        "fpr": float(fpr),
        "per_class": {
            cls: {
                "precision": float(report[cls]["precision"]),
                "recall": float(report[cls]["recall"]),
                "f1_score": float(report[cls]["f1-score"]),
                "support": int(report[cls]["support"])
            } for cls in target_names
        },
        "confusion_matrix": cm.tolist()
    }
    with open(metrics_json_path, "w") as f:
        json.dump(metrics_data, f, indent=4)
        
    print(f"Evaluation report written to {report_path}")
    print(f"Structured metrics written to {metrics_json_path}")

if __name__ == "__main__":
    main()
