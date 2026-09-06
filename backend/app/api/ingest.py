from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..db.session import get_db
from ..db.models import Alert, IngestStats, ModelRun
from ..schemas.schemas import IngestRecord, IngestBatch
from ..ml.inference import ThreatInferenceEngine

router = APIRouter(prefix="/ingest", tags=["ingest"])

# Global inference engine singleton
inference_engine = ThreatInferenceEngine()

def get_inference_engine() -> ThreatInferenceEngine:
    if not inference_engine.is_loaded:
        try:
            inference_engine.load_models()
        except FileNotFoundError:
            # Let the API remain online but return 503 for scoring
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML Models are not trained or loaded yet. Run training scripts first."
            )
    return inference_engine

def update_stats(db: Session, scanned_increment: int, alert_increment: int, severity_distribution: Dict[str, int]):
    # Get or create the single row in ingest_stats
    stats = db.query(IngestStats).order_by(IngestStats.id.desc()).first()
    if not stats:
        stats = IngestStats(
            total_scanned=0,
            total_alerts=0,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)
        
    stats.total_scanned += scanned_increment
    stats.total_alerts += alert_increment
    stats.critical_count += severity_distribution.get("Critical", 0)
    stats.high_count += severity_distribution.get("High", 0)
    stats.medium_count += severity_distribution.get("Medium", 0)
    stats.low_count += severity_distribution.get("Low", 0)
    
    db.commit()

@router.post("", status_code=status.HTTP_202_ACCEPTED)
def ingest_logs(
    payload: IngestRecord, 
    db: Session = Depends(get_db),
    engine: ThreatInferenceEngine = Depends(get_inference_engine)
):
    # Convert Pydantic object to dict
    record_dict = payload.model_dump()
    
    # Run scoring
    verdict = engine.score_record(record_dict)
    
    # Update Stats
    severity_distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    alert_increment = 0
    
    if verdict["is_threat"]:
        alert_increment = 1
        severity_distribution[verdict["severity"]] = 1
        
        # Save Alert
        # Keep raw features of interest
        raw_features = {k: v for k, v in record_dict.items() if k not in ["source_identifier"]}
        alert = Alert(
            source_identifier=record_dict.get("source_identifier") or "unknown",
            predicted_label=verdict["verdict"],
            confidence=verdict["confidence"],
            anomaly_score=verdict["anomaly_score"],
            severity=verdict["severity"],
            status="Open",
            raw_features=raw_features
        )
        db.add(alert)
        db.commit()
        
    update_stats(db, scanned_increment=1, alert_increment=alert_increment, severity_distribution=severity_distribution)
    
    return {
        "status": "processed",
        "verdict": verdict["verdict"],
        "severity": verdict["severity"] if verdict["is_threat"] else None,
        "is_threat": verdict["is_threat"]
    }

@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def ingest_batch_logs(
    payload: IngestBatch,
    db: Session = Depends(get_db),
    engine: ThreatInferenceEngine = Depends(get_inference_engine)
):
    records = [rec.model_dump() for rec in payload.records]
    if not records:
        return {"status": "empty_batch", "processed_count": 0}
        
    verdicts = engine.score_batch(records)
    
    scanned_increment = len(records)
    alert_increment = 0
    severity_distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    
    new_alerts = []
    for record_dict, verdict in zip(records, verdicts):
        if verdict["is_threat"]:
            alert_increment += 1
            severity_distribution[verdict["severity"]] += 1
            
            raw_features = {k: v for k, v in record_dict.items() if k not in ["source_identifier"]}
            alert = Alert(
                source_identifier=record_dict.get("source_identifier") or "unknown",
                predicted_label=verdict["verdict"],
                confidence=verdict["confidence"],
                anomaly_score=verdict["anomaly_score"],
                severity=verdict["severity"],
                status="Open",
                raw_features=raw_features
            )
            new_alerts.append(alert)
            
    if new_alerts:
        db.bulk_save_objects(new_alerts)
        db.commit()
        
    update_stats(db, scanned_increment=scanned_increment, alert_increment=alert_increment, severity_distribution=severity_distribution)
    
    return {
        "status": "processed",
        "processed_count": scanned_increment,
        "threats_detected": alert_increment
    }
