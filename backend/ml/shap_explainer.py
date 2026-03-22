import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import os
import base64
import io
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SHAPExplainer:
    def __init__(self):
        self.explainer = None
        self.model = None
        self.feature_names = []
        self.background_data = None
        
    def initialize(self, model, background_data: np.ndarray, feature_names: List[str]):
        """Initialize SHAP explainer with model and background data"""
        try:
            self.model = model
            self.feature_names = feature_names
            self.background_data = background_data
            
            # Create TreeExplainer for Random Forest
            self.explainer = shap.TreeExplainer(model)
            
            logger.info("SHAP explainer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {str(e)}")
            raise e
    
    def get_shap_values(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Get SHAP values for input data"""
        try:
            if self.explainer is None:
                raise ValueError("SHAP explainer not initialized")
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(input_data)
            
            # For multi-class, shap_values is a list of arrays (one for each class)
            if isinstance(shap_values, list):
                # Get SHAP values for the predicted class
                predicted_class = np.argmax(self.model.predict_proba(input_data)[0])
                class_shap_values = shap_values[predicted_class][0]
            else:
                class_shap_values = shap_values[0]
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                feature_importance[feature_name] = float(class_shap_values[i])
            
            # Sort by absolute importance
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            
            return {
                'feature_importance': feature_importance,
                'sorted_features': sorted_features[:10],  # Top 10 features
                'shap_values': class_shap_values.tolist(),
                'base_value': float(self.explainer.expected_value[predicted_class] if isinstance(self.explainer.expected_value, np.ndarray) else self.explainer.expected_value)
            }
            
        except Exception as e:
            logger.error(f"Error getting SHAP values: {str(e)}")
            return {'error': str(e)}
    
    def explain_prediction(self, input_data: np.ndarray, 
                          actual_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable explanation of prediction"""
        try:
            shap_result = self.get_shap_values(input_data)
            
            if 'error' in shap_result:
                return shap_result
            
            sorted_features = shap_result['sorted_features']
            
            # Generate explanation text
            explanation_parts = []
            explanation_parts.append("## Prediction Explanation\n")
            
            # Top contributing factors
            explanation_parts.append("### Key Contributing Factors:\n")
            
            for feature, importance in sorted_features[:5]:
                direction = "increases" if importance > 0 else "decreases"
                abs_importance = abs(importance)
                
                # Map feature names to human-readable descriptions
                feature_description = self._get_feature_description(feature, actual_input)
                
                explanation_parts.append(
                    f"- **{feature_description}**: {direction} prediction confidence by {abs_importance:.3f}"
                )
            
            # Risk factors
            positive_factors = [f for f, imp in sorted_features if imp > 0][:3]
            negative_factors = [f for f, imp in sorted_features if imp < 0][:3]
            
            if positive_factors:
                explanation_parts.append("\n### Factors Supporting This Diagnosis:")
                for feature in positive_factors:
                    description = self._get_feature_description(feature, actual_input)
                    explanation_parts.append(f"- {description}")
            
            if negative_factors:
                explanation_parts.append("\n### Factors Against This Diagnosis:")
                for feature in negative_factors:
                    description = self._get_feature_description(feature, actual_input)
                    explanation_parts.append(f"- {description}")
            
            explanation_text = "\n".join(explanation_parts)
            
            # Generate visualization
            plot_base64 = self._create_shap_plot(shap_result, actual_input)
            
            return {
                'explanation_text': explanation_text,
                'feature_importance': shap_result['feature_importance'],
                'top_features': sorted_features[:10],
                'plot_base64': plot_base64,
                'shap_values': shap_result['shap_values'],
                'base_value': shap_result['base_value']
            }
            
        except Exception as e:
            logger.error(f"Error explaining prediction: {str(e)}")
            return {'error': str(e)}
    
    def _get_feature_description(self, feature_name: str, actual_input: Dict[str, Any]) -> str:
        """Convert feature names to human-readable descriptions"""
        
        # Get actual value for context
        symptoms = actual_input.get('symptoms', [])
        
        # Symptom features
        if feature_name in Config.COMMON_SYMPTOMS:
            status = "Present" if feature_name in symptoms else "Absent"
            symptom_readable = feature_name.replace('_', ' ').title()
            return f"{symptom_readable} ({status})"
        
        # Lab value features
        feature_mapping = {
            'platelets_normalized': f"Platelet Count ({actual_input.get('platelets', 'N/A')})",
            'oxygen': f"Oxygen Saturation ({actual_input.get('oxygen', 'N/A')}%)",
            'wbc_normalized': f"White Blood Cell Count ({actual_input.get('wbc', 'N/A')})",
            'temperature': f"Body Temperature ({actual_input.get('temperature', 'N/A')}°F)",
            'age': f"Patient Age ({actual_input.get('age', 'N/A')} years)",
            'gender_male': f"Gender ({actual_input.get('gender', 'N/A')})"
        }
        
        return feature_mapping.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _create_shap_plot(self, shap_result: Dict[str, Any], 
                         actual_input: Dict[str, Any]) -> Optional[str]:
        """Create SHAP waterfall plot and return as base64 string"""
        try:
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Get top 8 features for visualization
            top_features = shap_result['sorted_features'][:8]
            features = [f[0] for f in top_features]
            values = [f[1] for f in top_features]
            
            # Create horizontal bar plot
            colors = ['red' if v < 0 else 'green' for v in values]
            y_pos = np.arange(len(features))
            
            bars = ax.barh(y_pos, [abs(v) for v in values], color=colors, alpha=0.7)
            
            # Customize plot
            ax.set_yticks(y_pos)
            ax.set_yticklabels([self._get_feature_description(f, actual_input) for f in features])
            ax.set_xlabel('SHAP Value (Impact on Prediction)')
            ax.set_title('Feature Importance for Prediction')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, values)):
                width = bar.get_width()
                ax.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                       f'{value:.3f}', ha='left', va='center', fontsize=9)
            
            # Add legend
            ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plot_data = buffer.getvalue()
            buffer.close()
            plt.close(fig)
            
            plot_base64 = base64.b64encode(plot_data).decode('utf-8')
            return plot_base64
            
        except Exception as e:
            logger.error(f"Error creating SHAP plot: {str(e)}")
            return None
    
    def generate_report(self, input_data: np.ndarray, 
                       actual_input: Dict[str, Any],
                       prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive explanation report"""
        try:
            explanation = self.explain_prediction(input_data, actual_input)
            
            if 'error' in explanation:
                return explanation
            
            # Combine with prediction information
            report = {
                'prediction': {
                    'disease': prediction_result.get('disease'),
                    'probability': prediction_result.get('probability'),
                    'risk_level': prediction_result.get('risk_level')
                },
                'explanation': explanation['explanation_text'],
                'feature_analysis': {
                    'top_positive_factors': [
                        f for f, imp in explanation['top_features'] if imp > 0
                    ][:3],
                    'top_negative_factors': [
                        f for f, imp in explanation['top_features'] if imp < 0
                    ][:3],
                    'feature_importance_scores': explanation['feature_importance']
                },
                'visualization': explanation.get('plot_base64'),
                'technical_details': {
                    'shap_values': explanation['shap_values'],
                    'base_value': explanation['base_value'],
                    'model_type': 'Random Forest with SHAP'
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating SHAP report: {str(e)}")
            return {'error': str(e)}
    
    def batch_explain(self, batch_data: np.ndarray, 
                     batch_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Explain multiple predictions at once"""
        explanations = []
        
        for i, (data_point, input_dict) in enumerate(zip(batch_data, batch_inputs)):
            try:
                explanation = self.explain_prediction(
                    data_point.reshape(1, -1), input_dict
                )
                explanations.append(explanation)
            except Exception as e:
                explanations.append({'error': f"Failed to explain sample {i}: {str(e)}"})
        
        return explanations