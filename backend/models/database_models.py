from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class User(Base):
    """Patient information - like the cover page of someone's medical file! 📁👤
    
    This stores basic details about each person using our system, kind of like
    filling out forms at the doctor's office. We keep it simple but informative!
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)     # Unique patient ID number
    email = Column(String(100), unique=True, nullable=False, index=True)  # Login email address 📧
    first_name = Column(String(50), nullable=False)        # Patient's first name 
    last_name = Column(String(50), nullable=False)         # Patient's last name
    name = Column(String(100), nullable=False)             # Full name (computed from first + last)
    age = Column(Integer, nullable=False)                  # How many candles on their birthday cake 🎂
    gender = Column(String(10), nullable=False)            # Biological information for medical context
    phone = Column(String(20), nullable=True)              # Contact number 📞
    hashed_password = Column(String(255), nullable=False)   # Secure login protection (scrambled!)
    is_active = Column(Integer, default=1)                 # Account status (0 or 1)
    role = Column(String(20), default="user")              # User role (user/admin)
    created_at = Column(DateTime, default=datetime.utcnow) # When they joined our digital clinic
    
    # These connect to other parts of the patient's digital file 🔗
    symptoms_inputs = relationship("SymptomsInput", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

class SymptomsInput(Base):
    """Patient's symptoms and vital signs - like a detailed health questionnaire! 📋🩺
    
    This is where we carefully record everything the patient is experiencing,
    from their symptoms ("I have a headache") to their lab test results.
    Think of it as a digital version of what a nurse writes down during your visit!
    """
    __tablename__ = "symptoms_input"
    
    id = Column(Integer, primary_key=True, index=True)         # Unique record number
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Which patient this belongs to
    symptoms = Column(JSON, nullable=False)                    # List of what they're feeling ("fever", "cough", etc.)
    platelets = Column(Float, nullable=True)                   # Blood clotting helpers count 🩸
    oxygen = Column(Float, nullable=True)                      # How well they're breathing (percentage)
    wbc = Column(Float, nullable=True)                         # White blood cell count (infection fighters!)
    temperature = Column(Float, nullable=True)                 # Body temperature (am I running hot?) 🌡️
    created_at = Column(DateTime, default=datetime.utcnow)     # When this snapshot was taken
    
    # Links back to the patient and forward to AI predictions 🔗
    user = relationship("User", back_populates="symptoms_inputs")
    predictions = relationship("Prediction", back_populates="symptoms_input")

class Prediction(Base):
    """AI's medical diagnosis and explanation - like a digital doctor's note! 🤖📝
    
    This stores what our AI thinks is wrong, how confident it is, and why it thinks so.
    It's like having a smart medical assistant write down their findings with
    detailed explanations that both doctors and patients can understand!
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)                               # Unique prediction ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)               # Which patient this is for
    symptoms_input_id = Column(Integer, ForeignKey("symptoms_input.id"), nullable=True)  # Links to their symptoms
    disease = Column(String(50), nullable=False)                                     # What the AI thinks it might be
    probability = Column(Float, nullable=False)                                      # How sure the AI is (0-100%)
    risk_level = Column(String(20), nullable=False)                                  # "Low", "Moderate", or "High" concern
    explanation = Column(Text, nullable=True)                                        # AI's reasoning in plain English 🗣️
    model_type = Column(String(20), nullable=False)                                  # Which AI brain made this diagnosis
    shap_values = Column(JSON, nullable=True)                                       # Technical details about the decision
    image_path = Column(String(255), nullable=True)                                 # If they uploaded a medical image 🖼️
    created_at = Column(DateTime, default=datetime.utcnow)                           # When this diagnosis was made
    
    # Connects this prediction back to the patient and their symptoms 🔗
    user = relationship("User", back_populates="predictions")
    symptoms_input = relationship("SymptomsInput", back_populates="predictions")

class Dataset(Base):
    """Information about training data we use to teach our AI! 📚🧠
    
    This keeps track of all the medical datasets we've uploaded - like a library
    catalog for our AI's textbooks. Each dataset helps our AI learn new patterns
    and become better at diagnosing different conditions!
    """
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)        # Unique dataset identifier
    name = Column(String(100), nullable=False)                # Friendly name ("COVID-19 Symptoms Data")
    file_path = Column(String(255), nullable=False)           # Where we stored it on our server 🗂
    description = Column(Text, nullable=True)                 # What this dataset contains and where it came from
    dataset_type = Column(String(20), nullable=False)         # "symptoms" or "images" - what kind of medical data?
    uploaded_at = Column(DateTime, default=datetime.utcnow)   # When we added this to our AI's library
    rows_count = Column(Integer, nullable=True)               # How many patient cases it contains
    columns_count = Column(Integer, nullable=True)            # How many different pieces of info per case
    is_active = Column(Integer, default=1)  # 0 or 1 for boolean


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)