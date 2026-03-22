from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
import os
import shutil

from backend.db.database import get_db
from backend.models.pydantic_models import (
    PredictionRequest, PredictionResponse, MultiplePredictionResponse,
    UserCreate, UserResponse, ErrorResponse
)
from backend.services.prediction_service import PredictionService
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
prediction_service = PredictionService()

@router.post("/predict", response_model=dict)
async def predict_disease(
    symptoms: Optional[str] = Form(None),
    platelets: Optional[float] = Form(None),
    oxygen: Optional[float] = Form(None),
    wbc: Optional[float] = Form(None),
    temperature: Optional[float] = Form(None),
    user_id: Optional[int] = Form(None),
    user_name: Optional[str] = Form(None),
    user_age: Optional[int] = Form(None),
    user_gender: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Make disease prediction based on symptoms and/or image
    
    - **symptoms**: JSON string of symptoms list (e.g., '["fever", "cough"]')
    - **platelets**: Platelet count
    - **oxygen**: Oxygen saturation percentage
    - **wbc**: White blood cell count
    - **temperature**: Body temperature in Fahrenheit
    - **user_id**: Existing user ID (optional)
    - **user_name**: New user name (required if no user_id)
    - **user_age**: New user age (required if no user_id)
    - **user_gender**: New user gender (required if no user_id)
    - **image**: Image file for skin disease analysis (optional)
    """
    try:
        # Validate inputs
        if not user_id and not all([user_name, user_age, user_gender]):
            raise HTTPException(
                status_code=400,
                detail="Either user_id or complete user info (name, age, gender) must be provided"
            )
        
        # Parse symptoms
        symptoms_list = []
        if symptoms:
            try:
                symptoms_list = json.loads(symptoms)
                if not isinstance(symptoms_list, list):
                    raise ValueError("Symptoms must be a list")
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid symptoms format: {str(e)}")
        
        # Validate image file if provided
        if image and image.filename:
            file_extension = image.filename.split('.')[-1].lower() if '.' in image.filename else ''
            if file_extension not in Config.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed types: {Config.ALLOWED_EXTENSIONS}"
                )
            
            if image.size and image.size > Config.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size too large. Maximum size: {Config.MAX_FILE_SIZE} bytes"
                )
        
        # Prepare request data
        prediction_request = {
            'user_id': user_id,
            'symptoms': symptoms_list,
            'platelets': platelets,
            'oxygen': oxygen,
            'wbc': wbc,
            'temperature': temperature
        }
        
        # Add user info if creating new user
        if not user_id:
            prediction_request['user_info'] = {
                'name': user_name,
                'age': user_age,
                'gender': user_gender
            }
        
        # Make prediction
        result = await prediction_service.make_prediction(db, prediction_request, image)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/predictions/{user_id}", response_model=List[dict])
async def get_prediction_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get prediction history for a specific user"""
    try:
        predictions = await prediction_service.get_prediction_history(db, user_id)
        
        result = []
        for pred in predictions:
            result.append({
                "id": pred.id,
                "disease": pred.disease,
                "probability": pred.probability,
                "risk_level": pred.risk_level,
                "explanation": pred.explanation,
                "model_type": pred.model_type,
                "created_at": pred.created_at.isoformat(),
                "image_path": pred.image_path
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    try:
        user = await prediction_service.create_user(db, user_data)
        return user
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    try:
        user = await prediction_service.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))