import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

# The original 41 features of NSL-KDD (excluding target label and difficulty level)
FEATURE_COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", 
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", 
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations", 
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", 
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate", 
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", 
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", 
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate", 
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate"
]

CATEGORICAL_FEATURES = ["protocol_type", "service", "flag"]
NUMERICAL_FEATURES = [col for col in FEATURE_COLUMNS if col not in CATEGORICAL_FEATURES]

# Attack mappings to broad categories
ATTACK_MAPPING = {
    'normal': 'normal',
    
    # DoS
    'back': 'dos',
    'land': 'dos',
    'neptune': 'dos',
    'pod': 'dos',
    'smurf': 'dos',
    'teardrop': 'dos',
    'mailbomb': 'dos',
    'apache2': 'dos',
    'processtable': 'dos',
    'udpstorm': 'dos',
    
    # Probe
    'ipsweep': 'probe',
    'nmap': 'probe',
    'portsweep': 'probe',
    'satan': 'probe',
    'mscan': 'probe',
    'saint': 'probe',
    
    # R2L
    'ftp_write': 'r2l',
    'guess_passwd': 'r2l',
    'imap': 'r2l',
    'multihop': 'r2l',
    'phf': 'r2l',
    'spy': 'r2l',
    'warezclient': 'r2l',
    'warezmaster': 'r2l',
    'sendmail': 'r2l',
    'named': 'r2l',
    'snmpgetattack': 'r2l',
    'snmpguess': 'r2l',
    'xlock': 'r2l',
    'xsnoop': 'r2l',
    'worm': 'r2l',
    
    # U2R
    'buffer_overflow': 'u2r',
    'loadmodule': 'u2r',
    'perl': 'u2r',
    'rootkit': 'u2r',
    'httptunnel': 'u2r',
    'ps': 'u2r',
    'sqlattack': 'u2r',
    'xterm': 'u2r'
}

CLASS_LABEL_TO_INT = {
    'normal': 0,
    'dos': 1,
    'probe': 2,
    'r2l': 3,
    'u2r': 4
}

INT_TO_CLASS_LABEL = {v: k for k, v in CLASS_LABEL_TO_INT.items()}

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies feature engineering:
    1. duration_bucket (log-scale groupings)
    2. byte_ratio (src_bytes / dst_bytes ratio)
    """
    df = df.copy()
    
    # Avoid div-by-zero
    dst_bytes_safe = df["dst_bytes"].astype(float) + 1.0
    df["byte_ratio"] = df["src_bytes"].astype(float) / dst_bytes_safe
    
    # Duration buckets (log based)
    df["duration_bucket"] = np.floor(np.log1p(df["duration"].astype(float)))
    
    return df

class ThreatPreprocessor:
    def __init__(self):
        self.preprocessor = None
        self.feature_names_ = None
        self.is_fit = False

    def fit(self, df: pd.DataFrame):
        # Apply feature engineering
        df_engineered = engineer_features(df)
        
        # Prepare list of numeric features including engineered ones
        numeric_cols = NUMERICAL_FEATURES + ["byte_ratio", "duration_bucket"]
        
        # Setup ColumnTransformer
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
            ]
        )
        
        self.preprocessor.fit(df_engineered)
        self.is_fit = True
        
        # Get feature names after encoding
        cat_encoder = self.preprocessor.named_transformers_['cat']
        encoded_cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
        self.feature_names_ = numeric_cols + encoded_cat_names

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fit:
            raise ValueError("Preprocessor is not fit yet.")
        df_engineered = engineer_features(df)
        return self.preprocessor.transform(df_engineered)

    def save(self, filepath: str):
        joblib.dump(self, filepath)
        print(f"Saved preprocessor to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'ThreatPreprocessor':
        return joblib.load(filepath)
