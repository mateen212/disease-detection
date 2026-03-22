from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# User models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., pattern="^(Male|Female|male|female)$")

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Prediction models
class PredictionRequest(BaseModel):
    user_id: Optional[int] = None
    user_info: Optional[UserCreate] = None
    symptoms: List[str] = Field(default_factory=list)
    platelets: Optional[float] = Field(None, ge=0)
    oxygen: Optional[float] = Field(None, ge=0, le=100)
    wbc: Optional[float] = Field(None, ge=0)
    temperature: Optional[float] = Field(None, ge=90, le=110)

class PredictionResponse(BaseModel):
    id: int
    disease: str
    probability: float
    risk_level: str
    explanation: Optional[str]
    model_type: str
    shap_values: Optional[Dict[str, Any]]
    recommendations: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MultiplePredictionResponse(BaseModel):
    user_id: int
    predictions: List[PredictionResponse]
    fusion_result: Optional[Dict[str, Any]]
    timestamp: datetime

# Dataset models
class DatasetUpload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    dataset_type: str = Field(..., pattern="^(symptoms|images)$")

class DatasetResponse(BaseModel):
    id: int
    name: str
    file_path: str
    description: Optional[str]
    dataset_type: str
    uploaded_at: datetime
    rows_count: Optional[int]
    columns_count: Optional[int]
    is_active: bool
    
    class Config:
        from_attributes = True

# Training models
class TrainingRequest(BaseModel):
    dataset_ids: List[int]
    model_type: str = Field(..., pattern="^(random_forest|cnn|all)$")
    parameters: Optional[Dict[str, Any]] = None

class TrainingResponse(BaseModel):
    status: str
    message: str
    model_type: str
    accuracy: Optional[float]
    training_time: Optional[float]
    timestamp: datetime

# Health check model
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_status: str
    models_loaded: Dict[str, bool]

# Error models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str]
    timestamp: datetime