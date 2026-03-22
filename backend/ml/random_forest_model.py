import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from typing import Dict, List, Tuple, Any
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RandomForestModel:
    """Our smart Random Forest doctor! 🌳👩‍⚕️
    
    This AI model is like having thousands of virtual doctors each giving their opinion,
    then taking the majority vote to make a diagnosis. It's particularly great at
    understanding patterns in symptoms and lab values to predict diseases.
    
    Think of it as a wise medical committee that never gets tired! 🧝‍♂️✨
    """
    def __init__(self):
        self.model = None                    # Our AI brain (starts empty, learns from data!)
        self.scaler = StandardScaler()       # Helps normalize numbers so they play nice together
        self.label_encoder = LabelEncoder()  # Converts disease names to numbers the AI understands
        self.feature_names = []              # Keeps track of what symptoms/values we're looking at
        self.is_trained = False              # Whether our AI has graduated medical school yet! 🎓
        
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Transform human symptoms and lab values into numbers our AI can understand!
        
        It's like translating from 'human language' to 'computer language' - 
        converting things like 'I have a fever' into mathematical patterns
        that our AI doctor can analyze. 🌡️➡️🔢
        """
        features = []
        
        # Let's check each possible symptom - like going through a medical checklist! 📋✅
        symptoms = data.get('symptoms', [])
        for symptom in Config.COMMON_SYMPTOMS:
            features.append(1 if symptom in symptoms else 0)  # 1 = "yes I have this", 0 = "nope!"
        
        # Now for the lab values - these are like vital signs that tell us a lot! 🩺
        features.append(data.get('platelets', 150000) / 1000)  # Blood clotting helpers (normalized)
        features.append(data.get('oxygen', 98))                # How well you're breathing (percentage)
        features.append(data.get('wbc', 7000) / 1000)          # Infection-fighting cells (normalized)
        features.append(data.get('temperature', 98.6))         # Body heat level
        features.append(data.get('age', 30))                   # How many birthdays you've celebrated! 🎂
        features.append(1 if data.get('gender', '').lower() == 'male' else 0)  # Biological factor
        
        return np.array(features).reshape(1, -1)
    
    def create_sample_data(self) -> pd.DataFrame:
        """Create some practice patients for our AI to learn from! 📚
        
        Since we need training data, this creates fictional (but realistic) patient cases.
        It's like having our AI study from a medical textbook full of example cases
        before it starts seeing real patients. Each 'patient' has symptoms, lab values,
        and a known diagnosis for the AI to learn patterns from! 👩‍💻📊
        """
        np.random.seed(42)  # Makes our 'random' patients predictable for testing!
        n_samples = 1000    # Let's create 1000 practice cases
        
        data = []
        diseases = Config.SYMPTOM_DISEASES
        
        for _ in range(n_samples):
            # Create a fictional patient with random characteristics 👤
            age = np.random.randint(18, 80)  # Adults from 18 to 80 years old
            gender = np.random.choice(['male', 'female'])
            
            # Pick a disease for this practice case 🎲
            disease = np.random.choice(diseases)
            
            # Now let's give them realistic symptoms for their condition 🩺
            symptoms = []
            if disease == "Dengue":
                if np.random.random() > 0.2: symptoms.append("fever")
                if np.random.random() > 0.3: symptoms.append("headache")
                if np.random.random() > 0.4: symptoms.append("muscle_pain")
                if np.random.random() > 0.6: symptoms.append("nausea")
                platelets = np.random.normal(80000, 20000)
                oxygen = np.random.normal(96, 2)
                wbc = np.random.normal(4000, 1000)
                temperature = np.random.normal(102, 1)
                
            elif disease == "COVID-19":
                if np.random.random() > 0.1: symptoms.append("cough")
                if np.random.random() > 0.3: symptoms.append("fever")
                if np.random.random() > 0.4: symptoms.append("fatigue")
                if np.random.random() > 0.5: symptoms.append("shortness_of_breath")
                if np.random.random() > 0.7: symptoms.append("sore_throat")
                platelets = np.random.normal(150000, 30000)
                oxygen = np.random.normal(94, 3)
                wbc = np.random.normal(6000, 2000)
                temperature = np.random.normal(101, 1.5)
                
            else:  # Pneumonia
                if np.random.random() > 0.2: symptoms.append("cough")
                if np.random.random() > 0.3: symptoms.append("chest_pain")
                if np.random.random() > 0.4: symptoms.append("shortness_of_breath")
                if np.random.random() > 0.5: symptoms.append("fever")
                platelets = np.random.normal(200000, 40000)
                oxygen = np.random.normal(92, 4)
                wbc = np.random.normal(12000, 3000)
                temperature = np.random.normal(103, 1.2)
            
            # Create feature vector
            features = []
            for symptom in Config.COMMON_SYMPTOMS:
                features.append(1 if symptom in symptoms else 0)
            
            features.extend([
                max(10000, platelets) / 1000,  # Normalized platelets
                max(80, min(100, oxygen)),      # Oxygen saturation
                max(2000, wbc) / 1000,          # Normalized WBC
                max(96, min(108, temperature)), # Temperature
                age,                            # Age
                1 if gender == 'male' else 0    # Gender
            ])
            
            row = features + [disease]
            data.append(row)
        
        # Create column names
        columns = Config.COMMON_SYMPTOMS + [
            'platelets_normalized', 'oxygen', 'wbc_normalized', 
            'temperature', 'age', 'gender_male', 'disease'
        ]
        
        return pd.DataFrame(data, columns=columns)
    
    def train(self, data_path: str = None) -> Dict[str, Any]:
        """Train the Random Forest model"""
        try:
            # Load data
            if data_path and os.path.exists(data_path):
                df = pd.read_csv(data_path)
            else:
                logger.info("Creating sample data for training...")
                df = self.create_sample_data()
            
            # Prepare features and target
            X = df.drop('disease', axis=1)
            y = df['disease']
            
            self.feature_names = X.columns.tolist()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Encode labels
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
            
            # Train model
            self.model = RandomForestClassifier(**Config.RANDOM_FOREST_PARAMS)
            self.model.fit(X_train_scaled, y_train_encoded)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            # Save model
            self.save_model()
            self.is_trained = True
            
            logger.info(f"Model trained with accuracy: {accuracy:.4f}")
            
            return {
                "accuracy": accuracy,
                "feature_importance": dict(zip(self.feature_names, self.model.feature_importances_)),
                "classification_report": classification_report(y_test_encoded, y_pred, 
                                                             target_names=self.label_encoder.classes_,
                                                             output_dict=True),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for given input data"""
        try:
            if not self.is_trained:
                self.load_model()
            
            # Prepare features
            features = self.prepare_features(data)
            features_scaled = self.scaler.transform(features)
            
            # Get predictions and probabilities
            predictions = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)
            
            # Get disease name
            disease = self.label_encoder.inverse_transform(predictions)[0]
            confidence = np.max(probabilities[0])
            
            # Determine risk level
            if confidence < Config.RISK_THRESHOLDS["low"]:
                risk_level = "Low"
            elif confidence < Config.RISK_THRESHOLDS["moderate"]:
                risk_level = "Moderate"
            else:
                risk_level = "High"
            
            # Get all disease probabilities
            disease_probabilities = {}
            for i, disease_name in enumerate(self.label_encoder.classes_):
                disease_probabilities[disease_name] = probabilities[0][i]
            
            return {
                "disease": disease,
                "probability": confidence,
                "risk_level": risk_level,
                "all_probabilities": disease_probabilities,
                "model_type": "RandomForest"
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {"error": str(e)}
    
    def save_model(self):
        """Save trained model"""
        model_dir = Config.MODELS_DIR
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(model_dir, "random_forest_model.pkl"))
        joblib.dump(self.scaler, os.path.join(model_dir, "scaler.pkl"))
        joblib.dump(self.label_encoder, os.path.join(model_dir, "label_encoder.pkl"))
        joblib.dump(self.feature_names, os.path.join(model_dir, "feature_names.pkl"))
        
        logger.info("Model saved successfully")
    
    def load_model(self):
        """Load trained model"""
        model_dir = Config.MODELS_DIR
        
        try:
            self.model = joblib.load(os.path.join(model_dir, "random_forest_model.pkl"))
            self.scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
            self.label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.pkl"))
            self.feature_names = joblib.load(os.path.join(model_dir, "feature_names.pkl"))
            self.is_trained = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise e