import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file (like reading a settings notebook!)

class Config:
    """Our system's main settings and preferences! ⚙️📋
    
    Think of this as the central control panel where we keep all the important
    numbers, paths, and preferences that make our AI medical system work smoothly.
    It's like having all the hospital's operational guidelines in one place!
    """
    
    # Where to find our patient database - like the address of our digital filing cabinet! 🗄
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:password@localhost:3306/disease_diagnosis")
    
    # Server settings - where our digital clinic will operate! 🏥🌍
    HOST = os.getenv("HOST", "0.0.0.0")      # What address to listen on (0.0.0.0 means "welcome everyone!")
    PORT = int(os.getenv("PORT", 8000))      # Which door number patients knock on (port 8000)
    
    # File storage locations - organized folders for different types of files! 📁✨
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")      # Patient-uploaded files
    DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")   # Training data for our AI
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models") # Trained AI brains
    
    # Upload safety rules - keeping our system secure and speedy! 🔒⚡
    MAX_FILE_SIZE = 10 * 1024 * 1024           # Max 10MB files (prevents huge uploads from slowing us down)
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "csv"}  # Only these file types are welcome in our clinic
    
    # Random Forest AI settings - how our tree-based doctor thinks! 🌳🤖
    RANDOM_FOREST_PARAMS = {
        "n_estimators": 100,    # Use 100 virtual doctors for each diagnosis (more opinions = better accuracy!)
        "max_depth": 10,       # How deep each doctor can think (prevents overthinking)
        "random_state": 42      # Lucky number for consistent results! 🍀
    }
    
    # Image AI settings - how our visual diagnosis system works! 🖼️👁️
    CNN_PARAMS = {
        "image_size": (224, 224),  # Resize all images to this size (like standardizing photo formats)
        "batch_size": 32,         # Train on 32 images at once (efficient learning!)
        "epochs": 50              # Go through the training data 50 times to learn patterns
    }
    
    # Risk assessment rules - when should we be concerned? ⚠️📊
    RISK_THRESHOLDS = {
        "low": 0.4,        # Below 40% confidence = "Probably not too serious" 😌
        "moderate": 0.7     # 40-70% = "Keep an eye on this", Above 70% = "Seek medical attention!" ⚡
    }
    
    # Medical conditions our AI can diagnose - our areas of expertise! 🩺👩‍⚕️
    SYMPTOM_DISEASES = ["Dengue", "COVID-19", "Pneumonia"]               # From symptoms & lab values
    SKIN_DISEASES = ["Melanoma", "Eczema", "Psoriasis", "Acne"]          # From skin images
    
    # Symptoms our AI knows how to interpret - the medical vocabulary it understands! 🧠📚
    COMMON_SYMPTOMS = [
        "fever", "headache", "cough", "fatigue", "muscle_pain",         # The classic "I don't feel well" signs
        "nausea", "vomiting", "diarrhea", "shortness_of_breath",        # Digestive & respiratory troubles  
        "chest_pain", "sore_throat", "runny_nose"                       # More specific warning signs
    ]