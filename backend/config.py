import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:password@localhost:3306/disease_diagnosis")
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # File upload configuration
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models")
    
    # ML configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "csv"}
    
    # Model parameters
    RANDOM_FOREST_PARAMS = {
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42
    }
    
    # CNN parameters
    CNN_PARAMS = {
        "image_size": (224, 224),
        "batch_size": 32,
        "epochs": 50
    }
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        "low": 0.4,
        "moderate": 0.7
    }
    
    # Supported diseases
    SYMPTOM_DISEASES = ["Dengue", "COVID-19", "Pneumonia"]
    SKIN_DISEASES = ["Melanoma", "Eczema", "Psoriasis", "Acne"]
    
    # Common symptoms
    COMMON_SYMPTOMS = [
        "fever", "headache", "cough", "fatigue", "muscle_pain",
        "nausea", "vomiting", "diarrhea", "shortness_of_breath",
        "chest_pain", "sore_throat", "runny_nose"
    ]