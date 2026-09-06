import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from .auth import get_current_user, User

router = APIRouter(prefix="/model", tags=["model"])

@router.get("/metrics", response_model=Dict[str, Any])
def get_model_metrics(
    current_user: User = Depends(get_current_user)
):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, "ml", "models", "metrics.json")
    
    if not os.path.exists(metrics_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics file not found. Ensure models have been trained."
        )
        
    try:
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)
        return metrics_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read model metrics: {e}"
        )
