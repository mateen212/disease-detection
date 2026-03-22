from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from backend.db.database import get_db
from backend.models.pydantic_models import DatasetResponse, TrainingRequest, TrainingResponse
from backend.services.prediction_service import DatasetService, TrainingService
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
dataset_service = DatasetService()
training_service = TrainingService()

@router.post("/upload-dataset", response_model=DatasetResponse)
async def upload_dataset(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    dataset_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new dataset
    
    - **name**: Dataset name
    - **description**: Dataset description (optional)
    - **dataset_type**: Type of dataset ('symptoms' or 'images')
    - **file**: CSV file for symptoms dataset or ZIP file for images
    """
    try:
        # Validate dataset type
        if dataset_type not in ["symptoms", "images"]:
            raise HTTPException(
                status_code=400,
                detail="dataset_type must be 'symptoms' or 'images'"
            )
        
        # Validate file
        if dataset_type == "symptoms" and not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Symptoms dataset must be a CSV file"
            )
        
        if file.size and file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Create dataset directory
        dataset_dir = os.path.join(Config.DATASET_DIR, dataset_type)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Save file
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"{name}_{timestamp}_{file.filename}"
        file_path = os.path.join(dataset_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create dataset record
        from backend.models.pydantic_models import DatasetUpload
        dataset_info = DatasetUpload(
            name=name,
            description=description,
            dataset_type=dataset_type
        )
        
        dataset = await dataset_service.upload_dataset(db, dataset_info, file_path)
        
        return dataset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload dataset error: {str(e)}")
        # Clean up file if database operation failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(db: Session = Depends(get_db)):
    """Get all datasets"""
    try:
        datasets = await dataset_service.get_datasets(db)
        return datasets
    except Exception as e:
        logger.error(f"Get datasets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Get dataset by ID"""
    try:
        dataset = await dataset_service.get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get dataset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-model", response_model=dict)
async def train_model(
    dataset_ids: str = Form(...),  # JSON string of dataset IDs
    model_type: str = Form(...),   # 'random_forest', 'cnn', or 'all'
    db: Session = Depends(get_db)
):
    """
    Train models with specified datasets
    
    - **dataset_ids**: JSON string of dataset IDs (e.g., '[1, 2, 3]')
    - **model_type**: Type of model to train ('random_forest', 'cnn', or 'all')
    """
    try:
        # Validate model type
        if model_type not in ["random_forest", "cnn", "all"]:
            raise HTTPException(
                status_code=400,
                detail="model_type must be 'random_forest', 'cnn', or 'all'"
            )
        
        # Parse dataset IDs
        try:
            import json
            dataset_id_list = json.loads(dataset_ids)
            if not isinstance(dataset_id_list, list) or not all(isinstance(x, int) for x in dataset_id_list):
                raise ValueError("Dataset IDs must be a list of integers")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid dataset_ids format: {str(e)}")
        
        if not dataset_id_list:
            raise HTTPException(status_code=400, detail="At least one dataset ID must be provided")
        
        # Start training
        training_start = datetime.utcnow()
        result = await training_service.train_models(db, dataset_id_list, model_type)
        training_end = datetime.utcnow()
        
        # Calculate training time
        training_time = (training_end - training_start).total_seconds()
        
        response = {
            "status": result.get("status", "unknown"),
            "message": result.get("message", "Training completed"),
            "model_type": model_type,
            "datasets_used": result.get("datasets_used", []),
            "training_time": training_time,
            "results": result.get("results", {}),
            "timestamp": training_end.isoformat()
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Train model error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Delete a dataset (mark as inactive)"""
    try:
        dataset = await dataset_service.get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Mark as inactive instead of deleting
        dataset.is_active = 0
        db.commit()
        
        return {"status": "success", "message": "Dataset deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete dataset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))