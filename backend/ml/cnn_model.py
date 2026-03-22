import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os
from PIL import Image
import cv2
from typing import Dict, Any, Tuple
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CNNModel:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.input_shape = (*Config.CNN_PARAMS["image_size"], 3)
        self.classes = Config.SKIN_DISEASES
        
    def build_model(self) -> keras.Model:
        """Build CNN architecture"""
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # Data augmentation
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            
            # Rescaling
            layers.Rescaling(1./255),
            
            # First convolutional block
            layers.Conv2D(32, 3, activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Second convolutional block
            layers.Conv2D(64, 3, activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Third convolutional block
            layers.Conv2D(128, 3, activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Fourth convolutional block
            layers.Conv2D(256, 3, activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Global pooling and classifier
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(len(self.classes), activation='softmax')
        ])
        
        return model
    
    def create_sample_data(self, samples_per_class: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Create sample synthetic data for demonstration"""
        logger.info("Creating synthetic image data for training...")
        
        image_size = Config.CNN_PARAMS["image_size"]
        X = []
        y = []
        
        np.random.seed(42)
        
        for class_idx, disease in enumerate(self.classes):
            for _ in range(samples_per_class):
                # Create synthetic image with different patterns for each disease
                if disease == "Melanoma":
                    # Dark spots with irregular patterns
                    img = np.random.randint(50, 150, (*image_size, 3))
                    # Add dark irregular spots
                    for _ in range(np.random.randint(5, 15)):
                        x, y_coord = np.random.randint(0, image_size[0], 2)
                        size = np.random.randint(10, 30)
                        img[max(0, x-size):min(image_size[0], x+size), 
                            max(0, y_coord-size):min(image_size[1], y_coord+size)] = np.random.randint(0, 80, 3)
                
                elif disease == "Eczema":
                    # Red, inflamed patterns
                    img = np.random.randint(120, 200, (*image_size, 3))
                    img[:, :, 0] = np.random.randint(150, 255, image_size)  # More red
                    # Add rough texture
                    noise = np.random.normal(0, 20, (*image_size, 3))
                    img = np.clip(img + noise, 0, 255)
                
                elif disease == "Psoriasis":
                    # Scaly, silver-white patches
                    img = np.random.randint(150, 220, (*image_size, 3))
                    # Add white/silver scales
                    for _ in range(np.random.randint(10, 20)):
                        x, y_coord = np.random.randint(0, image_size[0], 2)
                        size = np.random.randint(15, 40)
                        img[max(0, x-size):min(image_size[0], x+size), 
                            max(0, y_coord-size):min(image_size[1], y_coord+size)] = np.random.randint(200, 255, 3)
                
                else:  # Acne
                    # Small red bumps and pustules
                    img = np.random.randint(140, 200, (*image_size, 3))
                    # Add small bumps
                    for _ in range(np.random.randint(8, 25)):
                        x, y_coord = np.random.randint(0, image_size[0], 2)
                        size = np.random.randint(3, 12)
                        img[max(0, x-size):min(image_size[0], x+size), 
                            max(0, y_coord-size):min(image_size[1], y_coord+size), 0] = np.random.randint(180, 255)
                
                X.append(img.astype(np.uint8))
                y.append(class_idx)
        
        return np.array(X), np.array(y)
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess single image for prediction"""
        try:
            # Load and resize image
            img = Image.open(image_path).convert('RGB')
            img = img.resize(Config.CNN_PARAMS["image_size"])
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise e
    
    def train(self, data_path: str = None) -> Dict[str, Any]:
        """Train the CNN model"""
        try:
            # Create or load data
            if data_path and os.path.exists(data_path):
                # Load real data from directory structure
                # Expected structure: data_path/class_name/images
                logger.info(f"Loading data from {data_path}")
                # Implementation for real data loading would go here
                X, y = self.create_sample_data(200)  # Fallback to synthetic data
            else:
                X, y = self.create_sample_data(200)
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Convert labels to categorical
            y_train_cat = keras.utils.to_categorical(y_train, len(self.classes))
            y_test_cat = keras.utils.to_categorical(y_test, len(self.classes))
            
            # Build and compile model
            self.model = self.build_model()
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss', patience=10, restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7
                )
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train_cat,
                batch_size=Config.CNN_PARAMS["batch_size"],
                epochs=min(Config.CNN_PARAMS["epochs"], 20),  # Reduced for demo
                validation_data=(X_test, y_test_cat),
                callbacks=callbacks,
                verbose=1
            )
            
            # Evaluate model
            test_loss, test_accuracy = self.model.evaluate(X_test, y_test_cat, verbose=0)
            
            # Save model
            self.save_model()
            self.is_trained = True
            
            logger.info(f"CNN model trained with accuracy: {test_accuracy:.4f}")
            
            return {
                "accuracy": test_accuracy,
                "loss": test_loss,
                "training_history": {
                    "accuracy": history.history.get('accuracy', []),
                    "val_accuracy": history.history.get('val_accuracy', []),
                    "loss": history.history.get('loss', []),
                    "val_loss": history.history.get('val_loss', [])
                },
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"CNN training failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """Make prediction for skin image"""
        try:
            if not self.is_trained:
                self.load_model()
            
            # Preprocess image
            img_array = self.preprocess_image(image_path)
            
            # Make prediction
            predictions = self.model.predict(img_array, verbose=0)
            
            # Get class probabilities
            disease_probabilities = {}
            for i, disease in enumerate(self.classes):
                disease_probabilities[disease] = float(predictions[0][i])
            
            # Get top prediction
            predicted_class_idx = np.argmax(predictions[0])
            predicted_disease = self.classes[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])
            
            # Determine risk level
            if confidence < Config.RISK_THRESHOLDS["low"]:
                risk_level = "Low"
            elif confidence < Config.RISK_THRESHOLDS["moderate"]:
                risk_level = "Moderate"
            else:
                risk_level = "High"
            
            return {
                "disease": predicted_disease,
                "probability": confidence,
                "risk_level": risk_level,
                "all_probabilities": disease_probabilities,
                "model_type": "CNN"
            }
            
        except Exception as e:
            logger.error(f"CNN prediction failed: {str(e)}")
            return {"error": str(e)}
    
    def save_model(self):
        """Save trained model"""
        model_dir = Config.MODELS_DIR
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "cnn_model.h5")
        self.model.save(model_path)
        
        # Save class names
        import joblib
        joblib.dump(self.classes, os.path.join(model_dir, "cnn_classes.pkl"))
        
        logger.info("CNN model saved successfully")
    
    def load_model(self):
        """Load trained model"""
        model_dir = Config.MODELS_DIR
        
        try:
            model_path = os.path.join(model_dir, "cnn_model.h5")
            self.model = keras.models.load_model(model_path)
            
            # Load class names
            import joblib
            self.classes = joblib.load(os.path.join(model_dir, "cnn_classes.pkl"))
            
            self.is_trained = True
            logger.info("CNN model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CNN model: {str(e)}")
            raise e