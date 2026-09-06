import os
import time
import argparse
import pandas as pd
import requests
import random

# NSL-KDD column structure
COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", 
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", 
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations", 
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", 
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate", 
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", 
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", 
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate", 
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty_level"
]

FEATURE_COLUMNS = COLUMNS[:-2]

def get_auth_token(api_url, email, password):
    login_url = f"{api_url}/auth/login"
    register_url = f"{api_url}/auth/register"
    
    # Try to login
    print(f"Attempting to log in as {email}...")
    try:
        response = requests.post(login_url, data={"username": email, "password": password})
        if response.status_code == 200:
            print("Login successful.")
            return response.json()["access_token"]
    except requests.exceptions.RequestException:
        pass
        
    # If login fails (or server is not running, we'll hit error later), try registering
    print("Login failed or user doesn't exist. Attempting to register...")
    try:
        reg_response = requests.post(register_url, json={
            "email": email,
            "password": password,
            "role": "admin"
        })
        if reg_response.status_code == 201:
            print("Registration successful. Logging in...")
            response = requests.post(login_url, data={"username": email, "password": password})
            if response.status_code == 200:
                return response.json()["access_token"]
    except Exception as e:
        print(f"Auth error: {e}")
        
    print("Could not obtain auth token. Ingestion might run unauthenticated if endpoint allows it (or fail if protected).")
    return None

def generate_random_ip():
    return f"{random.randint(10, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"

def main():
    parser = argparse.ArgumentParser(description="NSL-KDD Threat Replay Simulator")
    parser.add_argument("--url", default="http://localhost:8000/api", help="FastAPI API URL prefix")
    parser.add_argument("--rate", type=float, default=2.0, help="Records to send per second")
    parser.add_argument("--batch", type=int, default=1, help="Batch size (if > 1, sends batches)")
    parser.add_argument("--email", default="admin@threat.local", help="User email")
    parser.add_argument("--password", default="admin_secure_pass", help="User password")
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_csv = os.path.join(base_dir, "ml", "data", "KDDTest+.csv")
    
    if not os.path.exists(test_csv):
        print(f"Test CSV not found at {test_csv}. Please download dataset first.")
        return
        
    print(f"Loading replay dataset: {test_csv}")
    df = pd.read_csv(test_csv, header=None, names=COLUMNS)
    print(f"Loaded {len(df)} records.")
    
    token = get_auth_token(args.url, args.email, args.password)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    print(f"Starting stream replay. Rate: {args.rate} rec/sec. Batch size: {args.batch}")
    
    idx = 0
    try:
        while True:
            # Replay indefinitely (wrap around)
            batch_records = []
            for _ in range(args.batch):
                row = df.iloc[idx % len(df)]
                idx += 1
                
                # Build feature dict
                record = {col: row[col] for col in FEATURE_COLUMNS}
                # Cast standard datatypes
                for col in record:
                    if col in ["duration", "src_bytes", "dst_bytes", "count", "srv_count", 
                               "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate", 
                               "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", 
                               "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate", 
                               "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", 
                               "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate", 
                               "dst_host_srv_rerror_rate"]:
                        record[col] = float(record[col])
                    elif col in ["land", "wrong_fragment", "urgent", "hot", "num_failed_logins", 
                                 "logged_in", "num_compromised", "root_shell", "su_attempted", 
                                 "num_root", "num_file_creations", "num_shells", "num_access_files", 
                                 "num_outbound_cmds", "is_host_login", "is_guest_login"]:
                        record[col] = int(record[col])
                        
                record["source_identifier"] = generate_random_ip()
                batch_records.append(record)
                
            # Send requests
            try:
                if args.batch == 1:
                    # Single ingestion
                    resp = requests.post(f"{args.url}/ingest", json=batch_records[0], headers=headers)
                    if resp.status_code == 202:
                        res_json = resp.json()
                        if res_json["is_threat"]:
                            print(f"[ALERT] Threat: {res_json['verdict']} | Severity: {res_json['severity']} | IP: {batch_records[0]['source_identifier']}")
                        else:
                            print(f"[OK] Benign traffic from {batch_records[0]['source_identifier']}")
                    else:
                        print(f"Error {resp.status_code}: {resp.text}")
                else:
                    # Batch ingestion
                    resp = requests.post(f"{args.url}/ingest/batch", json={"records": batch_records}, headers=headers)
                    if resp.status_code == 202:
                        res_json = resp.json()
                        print(f"[BATCH] Processed {res_json['processed_count']} | Threats: {res_json['threats_detected']}")
                    else:
                        print(f"Error {resp.status_code}: {resp.text}")
            except requests.exceptions.RequestException as e:
                print(f"Connection error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                continue
                
            time.sleep(1.0 / args.rate)
            
    except KeyboardInterrupt:
        print("\nReplay stopped.")

if __name__ == "__main__":
    main()
