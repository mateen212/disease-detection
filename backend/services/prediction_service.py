from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
import os
import pandas as pd
from datetime import datetime
import shutil

from models.database_models import User, SymptomsInput, Prediction, Dataset
from models.pydantic_models import UserCreate, DatasetUpload
from db.database import get_db
from ml.neuro_symbolic_fusion import NeuroSymbolicFusion
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.fusion_system = NeuroSymbolicFusion()
    
    async def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            db_user = User(**user_data.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise e
    
    async def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    async def save_symptoms_input(self, db: Session, user_id: int, 
                                 symptoms_data: Dict[str, Any]) -> SymptomsInput:
        """Save symptoms input to database"""
        try:
            db_symptoms = SymptomsInput(
                user_id=user_id,
                symptoms=symptoms_data.get('symptoms', []),
                platelets=symptoms_data.get('platelets'),
                oxygen=symptoms_data.get('oxygen'),
                wbc=symptoms_data.get('wbc'),
                temperature=symptoms_data.get('temperature')
            )
            db.add(db_symptoms)
            db.commit()
            db.refresh(db_symptoms)
            return db_symptoms
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error saving symptoms: {str(e)}")
            raise e
    
    async def save_prediction(self, db: Session, user_id: int, 
                             symptoms_input_id: Optional[int],
                             prediction_data: Dict[str, Any],
                             image_path: Optional[str] = None) -> Prediction:
        """Save prediction to database"""
        try:
            # Prepare SHAP values for storage
            shap_values = None
            if 'shap_explanation' in prediction_data:
                shap_values = prediction_data['shap_explanation'].get('feature_importance', {})
            
            db_prediction = Prediction(
                user_id=user_id,
                symptoms_input_id=symptoms_input_id,
                disease=prediction_data.get('disease', 'Unknown'),
                probability=prediction_data.get('probability', 0.0),
                risk_level=prediction_data.get('risk_level', 'Low'),
                explanation=prediction_data.get('explanation', ''),
                model_type=prediction_data.get('model_type', 'Unknown'),
                shap_values=shap_values,
                image_path=image_path
            )
            
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            return db_prediction
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error saving prediction: {str(e)}")
            raise e
    
    async def make_prediction(self, db: Session, 
                             prediction_request: Dict[str, Any],
                             image_file=None) -> Dict[str, Any]:
        """Make prediction using fusion system"""
        try:
            user_id = prediction_request.get('user_id')
            user_info = prediction_request.get('user_info')
            
            # Create user if needed
            if not user_id and user_info:
                user_create = UserCreate(**user_info)
                user = await self.create_user(db, user_create)
                user_id = user.id
            elif user_id:
                user = await self.get_user(db, user_id)
                if not user:
                    raise ValueError(f"User with id {user_id} not found")
            else:
                raise ValueError("Either user_id or user_info must be provided")
            
            # Prepare input data
            input_data = {
                'symptoms': prediction_request.get('symptoms', []),
                'platelets': prediction_request.get('platelets'),
                'oxygen': prediction_request.get('oxygen'),
                'wbc': prediction_request.get('wbc'),
                'temperature': prediction_request.get('temperature'),
                'age': user.age if user_id else user_info['age'],
                'gender': user.gender if user_id else user_info['gender']
            }
            
            # Save symptoms input
            symptoms_input = await self.save_symptoms_input(db, user_id, input_data)
            
            # Handle image upload if provided
            image_path = None
            if image_file:
                # Save uploaded image
                upload_dir = os.path.join(Config.UPLOAD_DIR, "images")
                os.makedirs(upload_dir, exist_ok=True)
                
                image_filename = f"user_{user_id}_{int(datetime.now().timestamp())}_{image_file.filename}"
                image_path = os.path.join(upload_dir, image_filename)
                
                with open(image_path, "wb") as buffer:
                    shutil.copyfileobj(image_file.file, buffer)
            
            # Make prediction
            if image_path and not any([input_data['symptoms'], input_data['platelets'], 
                                     input_data['oxygen'], input_data['wbc']]):
                # Only image provided - use CNN only
                prediction_result = self.fusion_system.predict_image(image_path, input_data)
            elif image_path:
                # Both symptoms and image - use combined prediction
                prediction_result = self.fusion_system.predict_combined(input_data, image_path)
            else:
                # Only symptoms - use symptom-based models
                prediction_result = self.fusion_system.predict_symptoms(input_data)
            
            if 'error' in prediction_result:
                raise Exception(prediction_result['error'])
            
            # Save prediction to database
            db_prediction = await self.save_prediction(
                db, user_id, symptoms_input.id, prediction_result, image_path
            )
            
            # Prepare response
            response = {
                'id': db_prediction.id,
                'user_id': user_id,
                'disease': prediction_result['disease'],
                'probability': prediction_result['probability'],
                'risk_level': prediction_result['risk_level'],
                'explanation': prediction_result.get('explanation', ''),
                'model_type': prediction_result['model_type'],
                'recommendations': prediction_result.get('recommendations', []),
                'all_probabilities': prediction_result.get('all_probabilities', {}),
                'shap_explanation': prediction_result.get('shap_explanation'),
                'fusion_details': prediction_result.get('fusion_details'),
                'created_at': db_prediction.created_at
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise e
    
    async def get_prediction_history(self, db: Session, user_id: int) -> List[Prediction]:
        """Get prediction history for a user"""
        return db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(Prediction.created_at.desc()).all()

class DatasetService:
    def __init__(self):
        pass
    
    async def upload_dataset(self, db: Session, dataset_info: DatasetUpload, 
                           file_path: str) -> Dataset:
        """Upload and register a new dataset"""
        try:
            # Analyze dataset
            if dataset_info.dataset_type == "symptoms":
                df = pd.read_csv(file_path)
                rows_count = len(df)
                columns_count = len(df.columns)
            else:
                # For image datasets, count files in directory
                rows_count = None
                columns_count = None
            
            # Create dataset record
            db_dataset = Dataset(
                name=dataset_info.name,
                file_path=file_path,
                description=dataset_info.description,
                dataset_type=dataset_info.dataset_type,
                rows_count=rows_count,
                columns_count=columns_count
            )
            
            db.add(db_dataset)
            db.commit()
            db.refresh(db_dataset)
            
            return db_dataset
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error uploading dataset: {str(e)}")
            raise e
    
    async def get_datasets(self, db: Session) -> List[Dataset]:
        """Get all datasets"""
        return db.query(Dataset).filter(Dataset.is_active == 1).all()
    
    async def get_dataset(self, db: Session, dataset_id: int) -> Optional[Dataset]:
        """Get dataset by ID"""
        return db.query(Dataset).filter(
            Dataset.id == dataset_id, 
            Dataset.is_active == 1
        ).first()

class TrainingService:
    def __init__(self):
        self.fusion_system = NeuroSymbolicFusion()
    
    async def train_models(self, db: Session, dataset_ids: List[int], 
                          model_type: str) -> Dict[str, Any]:
        """Train specified models with given datasets"""
        try:
            results = {}
            
            # Get datasets
            datasets = []
            for dataset_id in dataset_ids:
                dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if dataset:
                    datasets.append(dataset)
            
            if not datasets:
                raise ValueError("No valid datasets found")
            
            # Train models based on type
            if model_type in ["random_forest", "all"]:
                rf_result = await self._train_random_forest(datasets)
                results['random_forest'] = rf_result
            
            if model_type in ["cnn", "all"]:
                cnn_result = await self._train_cnn(datasets)
                results['cnn'] = cnn_result
            
            return {
                'status': 'success',
                'results': results,
                'datasets_used': [d.name for d in datasets]
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _train_random_forest(self, datasets: List[Dataset]) -> Dict[str, Any]:
        """Train Random Forest model with multiple datasets"""
        try:
            # Find all symptoms datasets
            symptoms_datasets = [d for d in datasets if d.dataset_type == "symptoms"]
            
            if symptoms_datasets:
                # Combine multiple datasets for same disease
                combined_data = self._combine_datasets(symptoms_datasets)
                data_path = combined_data if combined_data else symptoms_datasets[0].file_path
            else:
                data_path = None  # Will use sample data
            
            result = self.fusion_system.rf_model.train(data_path)
            
            # Initialize SHAP explainer if training successful
            if result.get('status') == 'success' and self.fusion_system.rf_model.is_trained:
                try:
                    # Create background data for SHAP
                    sample_data = self.fusion_system.rf_model.create_sample_data()
                    X = sample_data.drop('disease', axis=1)
                    background = X.sample(100)  # Use 100 samples as background
                    
                    self.fusion_system.shap_explainer.initialize(
                        self.fusion_system.rf_model.model,
                        self.fusion_system.rf_model.scaler.transform(background),
                        self.fusion_system.rf_model.feature_names
                    )
                except Exception as e:
                    logger.warning(f"SHAP initialization failed: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Random Forest training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _train_cnn(self, datasets: List[Dataset]) -> Dict[str, Any]:
        """Train CNN model"""
        try:
            # Find image dataset
            image_datasets = [d for d in datasets if d.dataset_type == "images"]
            
            if image_datasets:
                data_path = image_datasets[0].file_path
            else:
                data_path = None  # Will use sample data
            
            result = self.fusion_system.cnn_model.train(data_path)
            return result
            
        except Exception as e:
            logger.error(f"CNN training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _combine_datasets(self, datasets: List[Dataset]) -> Optional[str]:
        """Combine multiple datasets into a single training file"""
        try:
            import pandas as pd
            import os
            from datetime import datetime
            
            if len(datasets) <= 1:
                return None
                
            combined_dfs = []
            dataset_info = []
            
            # Load and combine all datasets
            for dataset in datasets:
                if os.path.exists(dataset.file_path):
                    df = pd.read_csv(dataset.file_path)
                    
                    # Add metadata columns to track source
                    df['source_dataset'] = dataset.name
                    df['source_id'] = dataset.id
                    
                    combined_dfs.append(df)
                    dataset_info.append({
                        'name': dataset.name,
                        'rows': len(df),
                        'file': dataset.file_path
                    })
                    
                    logger.info(f"Loaded dataset '{dataset.name}': {len(df)} rows")
            
            if not combined_dfs:
                return None
            
            # Combine all dataframes
            combined_df = pd.concat(combined_dfs, ignore_index=True)
            
            # Remove duplicates based on key columns (excluding metadata)
            key_columns = [col for col in combined_df.columns 
                          if col not in ['source_dataset', 'source_id']]
            combined_df = combined_df.drop_duplicates(subset=key_columns, keep='first')
            
            # Save combined dataset
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            combined_filename = f"combined_datasets_{timestamp}.csv"
            combined_path = os.path.join(os.path.dirname(datasets[0].file_path), combined_filename)
            
            combined_df.to_csv(combined_path, index=False)
            
            logger.info(f"Combined {len(datasets)} datasets into {combined_path}")
            logger.info(f"Total rows: {len(combined_df)}, Unique rows: {len(combined_df)} after deduplication")
            logger.info(f"Dataset sources: {[info['name'] for info in dataset_info]}")
            
            return combined_path
            
        except Exception as e:
            logger.error(f"Failed to combine datasets: {str(e)}")
            return None