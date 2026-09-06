from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, List, Optional
import datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("analyst", pattern="^(admin|analyst)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    role: str

# Ingestion schemas
class IngestRecord(BaseModel):
    duration: float = 0.0
    protocol_type: str = "tcp"
    service: str = "http"
    flag: str = "SF"
    src_bytes: float = 0.0
    dst_bytes: float = 0.0
    land: int = 0
    wrong_fragment: int = 0
    urgent: int = 0
    hot: int = 0
    num_failed_logins: int = 0
    logged_in: int = 0
    num_compromised: int = 0
    root_shell: int = 0
    su_attempted: int = 0
    num_root: int = 0
    num_file_creations: int = 0
    num_shells: int = 0
    num_access_files: int = 0
    num_outbound_cmds: int = 0
    is_host_login: int = 0
    is_guest_login: int = 0
    count: float = 0.0
    srv_count: float = 0.0
    serror_rate: float = 0.0
    srv_serror_rate: float = 0.0
    rerror_rate: float = 0.0
    srv_rerror_rate: float = 0.0
    same_srv_rate: float = 0.0
    diff_srv_rate: float = 0.0
    srv_diff_host_rate: float = 0.0
    dst_host_count: float = 0.0
    dst_host_srv_count: float = 0.0
    dst_host_same_srv_rate: float = 0.0
    dst_host_diff_srv_rate: float = 0.0
    dst_host_same_src_port_rate: float = 0.0
    dst_host_srv_diff_host_rate: float = 0.0
    dst_host_serror_rate: float = 0.0
    dst_host_srv_serror_rate: float = 0.0
    dst_host_rerror_rate: float = 0.0
    dst_host_srv_rerror_rate: float = 0.0
    
    # Custom fields for tracking source
    source_identifier: Optional[str] = "unknown"

class IngestBatch(BaseModel):
    records: List[IngestRecord]

# Alert schemas
class AlertResponse(BaseModel):
    id: int
    timestamp: datetime.datetime
    source_identifier: str
    predicted_label: str
    confidence: float
    anomaly_score: float
    severity: str
    status: str
    assigned_analyst: Optional[str] = None
    raw_features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Open|Acknowledged|Resolved|False Positive)$")
    assigned_analyst: Optional[str] = None

# Stats schemas
class StatsOverview(BaseModel):
    total_scanned: int
    total_alerts: int
    severity_distribution: Dict[str, int]
    label_distribution: Dict[str, int]
    recent_alerts: List[AlertResponse]

# Model run schemas
class ModelMetricsResponse(BaseModel):
    model_version: str
    trained_at: datetime.datetime
    metrics: Dict[str, Any]

    class Config:
        from_attributes = True
