from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os

from backend.db.database import get_db
from backend.models.pydantic_models import HealthResponse
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        try:
            db.execute("SELECT 1")
            database_status = "healthy"
        except SQLAlchemyError:
            database_status = "unhealthy"
        
        # Check if models are available
        models_loaded = {
            "random_forest": os.path.exists(os.path.join(Config.MODELS_DIR, "random_forest_model.pkl")),
            "cnn": os.path.exists(os.path.join(Config.MODELS_DIR, "cnn_model.h5")),
            "scaler": os.path.exists(os.path.join(Config.MODELS_DIR, "scaler.pkl")),
            "label_encoder": os.path.exists(os.path.join(Config.MODELS_DIR, "label_encoder.pkl"))
        }
        
        # Determine overall status
        if database_status == "healthy":
            status = "healthy"
        else:
            status = "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            database_status=database_status,
            models_loaded=models_loaded
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            database_status="error",
            models_loaded={}
        )