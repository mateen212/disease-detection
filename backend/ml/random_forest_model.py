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
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from input data"""
        features = []
        
        # Symptoms (one-hot encoded)
        symptoms = data.get('symptoms', [])
        for symptom in Config.COMMON_SYMPTOMS:
            features.append(1 if symptom in symptoms else 0)
        
        # Lab values
        features.append(data.get('platelets', 150000) / 1000)  # Normalize platelets
        features.append(data.get('oxygen', 98))                # Oxygen saturation
        features.append(data.get('wbc', 7000) / 1000)          # Normalize WBC
        features.append(data.get('temperature', 98.6))         # Temperature
        features.append(data.get('age', 30))                   # Age
        features.append(1 if data.get('gender', '').lower() == 'male' else 0)  # Gender
        
        return np.array(features).reshape(1, -1)
    
    def create_sample_data(self) -> pd.DataFrame:
        """Create sample training data for demonstration"""
        np.random.seed(42)
        n_samples = 1000
        
        data = []
        diseases = Config.SYMPTOM_DISEASES
        
        for _ in range(n_samples):
            # Generate random patient data
            age = np.random.randint(18, 80)
            gender = np.random.choice(['male', 'female'])
            
            # Randomly select a disease
            disease = np.random.choice(diseases)
            
            # Generate symptoms based on disease patterns
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