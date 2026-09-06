import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from .session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst") # admin, analyst
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_identifier = Column(String, index=True) # e.g. source IP or description
    predicted_label = Column(String, index=True) # normal, dos, probe, r2l, u2r, suspicious
    confidence = Column(Float)
    anomaly_score = Column(Float)
    severity = Column(String, index=True) # Critical, High, Medium, Low
    status = Column(String, default="Open") # Open, Acknowledged, Resolved, False Positive
    assigned_analyst = Column(String, nullable=True)
    raw_features = Column(JSON) # Store raw features of interest

class ModelRun(Base):
    __tablename__ = "model_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, unique=True)
    trained_at = Column(DateTime, default=datetime.datetime.utcnow)
    metrics = Column(JSON)

class IngestStats(Base):
    __tablename__ = "ingest_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    total_scanned = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
