from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    symptoms_inputs = relationship("SymptomsInput", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

class SymptomsInput(Base):
    __tablename__ = "symptoms_input"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptoms = Column(JSON, nullable=False)  # List of symptoms
    platelets = Column(Float, nullable=True)
    oxygen = Column(Float, nullable=True)
    wbc = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="symptoms_inputs")
    predictions = relationship("Prediction", back_populates="symptoms_input")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptoms_input_id = Column(Integer, ForeignKey("symptoms_input.id"), nullable=True)
    disease = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # Low, Moderate, High
    explanation = Column(Text, nullable=True)
    model_type = Column(String(20), nullable=False)  # RandomForest, CNN, RuleBased, Fusion
    shap_values = Column(JSON, nullable=True)
    image_path = Column(String(255), nullable=True)  # For CNN predictions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    symptoms_input = relationship("SymptomsInput", back_populates="predictions")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    dataset_type = Column(String(20), nullable=False)  # symptoms, images
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    rows_count = Column(Integer, nullable=True)
    columns_count = Column(Integer, nullable=True)
    is_active = Column(Integer, default=1)  # 0 or 1 for boolean


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)