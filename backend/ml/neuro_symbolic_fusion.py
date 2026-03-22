from typing import Dict, List, Any, Optional
import numpy as np
from backend.ml.random_forest_model import RandomForestModel
from backend.ml.cnn_model import CNNModel
from backend.ml.rule_based_system import RuleBasedSystem
from backend.ml.shap_explainer import SHAPExplainer
from backend.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuroSymbolicFusion:
    def __init__(self):
        self.rf_model = RandomForestModel()
        self.cnn_model = CNNModel()
        self.rule_system = RuleBasedSystem()
        self.shap_explainer = SHAPExplainer()
        
        # Fusion weights
        self.weights = {
            'random_forest': 0.4,
            'rule_based': 0.4,
            'cnn': 0.2  # Only used when image is provided
        }
        
    def predict_symptoms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict using symptom-based models (RF + Rules)"""
        try:
            # Get Random Forest prediction
            rf_result = self.rf_model.predict(data)
            
            # Get Rule-based prediction
            rule_result = self.rule_system.predict(data)
            
            # Prepare results for fusion
            models_results = {
                'random_forest': rf_result,
                'rule_based': rule_result
            }
            
            # Perform fusion
            fusion_result = self._fuse_predictions(models_results, use_cnn=False)
            
            # Get SHAP explanation for Random Forest
            if not rf_result.get('error'):
                try:
                    input_features = self.rf_model.prepare_features(data)
                    shap_explanation = self.shap_explainer.explain_prediction(input_features, data)
                    fusion_result['shap_explanation'] = shap_explanation
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {str(e)}")
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"Symptom prediction failed: {str(e)}")
            return {'error': str(e)}
    
    def predict_image(self, image_path: str, patient_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict using CNN for skin diseases"""
        try:
            # Get CNN prediction
            cnn_result = self.cnn_model.predict(image_path)
            
            if cnn_result.get('error'):
                return cnn_result
            
            # If patient data is provided, we can add contextual information
            if patient_data:
                # Adjust prediction based on patient demographics
                age = patient_data.get('age', 30)
                gender = patient_data.get('gender', '').lower()
                
                # Apply demographic adjustments
                adjusted_prob = self._adjust_for_demographics(
                    cnn_result['disease'], 
                    cnn_result['probability'], 
                    age, 
                    gender
                )
                
                cnn_result['probability'] = adjusted_prob
                cnn_result['demographic_adjustment'] = True
            
            # Add recommendations based on disease
            cnn_result['recommendations'] = self._get_skin_disease_recommendations(
                cnn_result['disease'], cnn_result['risk_level']
            )
            
            return cnn_result
            
        except Exception as e:
            logger.error(f"Image prediction failed: {str(e)}")
            return {'error': str(e)}
    
    def predict_combined(self, data: Dict[str, Any], image_path: str = None) -> Dict[str, Any]:
        """Predict using all available models and fuse results"""
        try:
            models_results = {}
            
            # Get symptom-based predictions
            rf_result = self.rf_model.predict(data)
            rule_result = self.rule_system.predict(data)
            
            models_results['random_forest'] = rf_result
            models_results['rule_based'] = rule_result
            
            # Get image prediction if image provided
            use_cnn = False
            if image_path:
                cnn_result = self.cnn_model.predict(image_path)
                if not cnn_result.get('error'):
                    models_results['cnn'] = cnn_result
                    use_cnn = True
            
            # Perform fusion
            fusion_result = self._fuse_predictions(models_results, use_cnn=use_cnn)
            
            # Add SHAP explanation
            if not rf_result.get('error'):
                try:
                    input_features = self.rf_model.prepare_features(data)
                    shap_explanation = self.shap_explainer.explain_prediction(input_features, data)
                    fusion_result['shap_explanation'] = shap_explanation
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {str(e)}")
            
            # Add comprehensive recommendations
            fusion_result['recommendations'] = self._get_comprehensive_recommendations(
                fusion_result, data, image_path is not None
            )
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"Combined prediction failed: {str(e)}")
            return {'error': str(e)}
    
    def _fuse_predictions(self, models_results: Dict[str, Dict], use_cnn: bool = False) -> Dict[str, Any]:
        """Fuse predictions from multiple models"""
        try:
            # Collect all diseases and their probabilities from each model
            disease_scores = {}
            total_weight = 0
            model_details = {}
            
            # Process each model result
            for model_name, result in models_results.items():
                if result.get('error'):
                    continue
                
                model_weight = self.weights.get(model_name, 0.1)
                if not use_cnn and model_name == 'cnn':
                    continue
                
                total_weight += model_weight
                model_details[model_name] = result
                
                # Get disease and probability
                disease = result.get('disease')
                probability = result.get('probability', 0)
                
                if disease:
                    if disease not in disease_scores:
                        disease_scores[disease] = 0
                    disease_scores[disease] += probability * model_weight
                
                # Also add all probabilities if available
                all_probs = result.get('all_probabilities', {})
                for disease_name, prob in all_probs.items():
                    if disease_name not in disease_scores:
                        disease_scores[disease_name] = 0
                    disease_scores[disease_name] += prob * model_weight * 0.5  # Reduced weight for secondary predictions
            
            if not disease_scores:
                return {
                    'disease': "Unknown",
                    'probability': 0.0,
                    'risk_level': "Low",
                    'model_type': "Fusion",
                    'fusion_details': model_details,
                    'explanation': "No valid predictions from any model"
                }
            
            # Normalize scores
            if total_weight > 0:
                for disease in disease_scores:
                    disease_scores[disease] /= total_weight
            
            # Find best prediction
            best_disease = max(disease_scores.items(), key=lambda x: x[1])
            disease_name = best_disease[0]
            confidence = best_disease[1]
            
            # Determine risk level
            if confidence < Config.RISK_THRESHOLDS["low"]:
                risk_level = "Low"
            elif confidence < Config.RISK_THRESHOLDS["moderate"]:
                risk_level = "Moderate"
            else:
                risk_level = "High"
            
            # Create explanation
            explanation = self._create_fusion_explanation(model_details, disease_name, confidence)
            
            return {
                'disease': disease_name,
                'probability': confidence,
                'risk_level': risk_level,
                'model_type': "Fusion",
                'all_probabilities': disease_scores,
                'fusion_details': model_details,
                'explanation': explanation,
                'models_used': list(model_details.keys()),
                'fusion_weights': {k: v for k, v in self.weights.items() if k in model_details}
            }
            
        except Exception as e:
            logger.error(f"Fusion failed: {str(e)}")
            return {'error': str(e)}
    
    def _create_fusion_explanation(self, model_details: Dict, disease: str, confidence: float) -> str:
        """Create explanation for fusion result"""
        explanation_parts = []
        explanation_parts.append(f"**Fusion Analysis for {disease}** (Confidence: {confidence:.3f})")
        explanation_parts.append("")
        
        for model_name, result in model_details.items():
            model_disease = result.get('disease', 'Unknown')
            model_prob = result.get('probability', 0)
            model_risk = result.get('risk_level', 'Unknown')
            
            explanation_parts.append(f"**{model_name.replace('_', ' ').title()}:**")
            explanation_parts.append(f"- Predicted: {model_disease} (Prob: {model_prob:.3f})")
            explanation_parts.append(f"- Risk Level: {model_risk}")
            
            # Add model-specific explanation
            if 'explanation' in result:
                explanation_parts.append(f"- Reasoning: {result['explanation'][:150]}...")
            
            explanation_parts.append("")
        
        explanation_parts.append("**Fusion Decision:**")
        explanation_parts.append(f"Combined evidence from {len(model_details)} models suggests {disease} with {confidence:.1%} confidence.")
        
        return "\n".join(explanation_parts)
    
    def _adjust_for_demographics(self, disease: str, probability: float, age: int, gender: str) -> float:
        """Adjust CNN prediction based on patient demographics"""
        adjustment = 1.0
        
        # Age-based adjustments
        if disease == "Melanoma":
            if age > 50:
                adjustment *= 1.2  # Higher risk in older patients
            elif age < 30:
                adjustment *= 0.8  # Lower risk in younger patients
        
        if disease == "Acne":
            if 13 <= age <= 25:
                adjustment *= 1.3  # Peak acne years
            elif age > 40:
                adjustment *= 0.6  # Less common in older adults
        
        # Gender-based adjustments (based on general medical statistics)
        if disease == "Eczema" and gender == "female":
            adjustment *= 1.1  # Slightly more common in females
        
        # Ensure probability stays within bounds
        adjusted_prob = min(1.0, max(0.0, probability * adjustment))
        return adjusted_prob
    
    def _get_skin_disease_recommendations(self, disease: str, risk_level: str) -> List[str]:
        """Get recommendations for skin diseases"""
        recommendations = []
        
        if disease == "Melanoma":
            if risk_level == "High":
                recommendations.extend([
                    "URGENT: Consult a dermatologist immediately",
                    "Get a biopsy as soon as possible",
                    "Avoid sun exposure"
                ])
            else:
                recommendations.extend([
                    "Schedule dermatologist appointment within 1-2 weeks",
                    "Monitor for changes in size, color, or shape",
                    "Use SPF 30+ sunscreen daily"
                ])
        
        elif disease == "Eczema":
            recommendations.extend([
                "Use fragrance-free, hypoallergenic moisturizers",
                "Avoid known triggers (certain soaps, fabrics)",
                "Consider topical corticosteroids if severe",
                "Consult dermatologist if symptoms persist"
            ])
        
        elif disease == "Psoriasis":
            recommendations.extend([
                "Use moisturizing creams regularly",
                "Consider coal tar or salicylic acid treatments",
                "Avoid stress and known triggers",
                "Consult dermatologist for treatment plan"
            ])
        
        elif disease == "Acne":
            recommendations.extend([
                "Use gentle, non-comedogenic cleansers",
                "Consider over-the-counter benzoyl peroxide or salicylic acid",
                "Avoid touching or picking at lesions",
                "Consult dermatologist if over-the-counter treatments fail"
            ])
        
        return recommendations
    
    def _get_comprehensive_recommendations(self, fusion_result: Dict, patient_data: Dict, has_image: bool) -> List[str]:
        """Get comprehensive recommendations based on all available information"""
        recommendations = []
        disease = fusion_result.get('disease', '')
        risk_level = fusion_result.get('risk_level', 'Low')
        confidence = fusion_result.get('probability', 0)
        
        # General recommendations based on disease type
        if disease in Config.SYMPTOM_DISEASES:
            if disease == "Dengue":
                recommendations.extend([
                    "Monitor platelet count closely",
                    "Maintain adequate fluid intake",
                    "Avoid aspirin and NSAIDs",
                    "Seek immediate medical attention if bleeding occurs"
                ])
            
            elif disease == "COVID-19":
                recommendations.extend([
                    "Self-isolate immediately",
                    "Monitor oxygen saturation",
                    "Get tested for COVID-19",
                    "Contact healthcare provider if symptoms worsen"
                ])
            
            elif disease == "Pneumonia":
                recommendations.extend([
                    "Seek medical attention for proper diagnosis",
                    "Monitor breathing and oxygen levels",
                    "Rest and stay hydrated",
                    "Complete any prescribed antibiotic course"
                ])
        
        elif disease in Config.SKIN_DISEASES:
            recommendations.extend(self._get_skin_disease_recommendations(disease, risk_level))
        
        # Risk-level based recommendations
        if risk_level == "High":
            recommendations.insert(0, "⚠️ HIGH RISK: Seek medical attention immediately")
        elif risk_level == "Moderate":
            recommendations.insert(0, "⚠️ MODERATE RISK: Schedule medical consultation within 24-48 hours")
        
        # Confidence-based recommendations
        if confidence < 0.6:
            recommendations.append("❗ Uncertain diagnosis: Consider getting a second opinion")
        
        # Age-specific recommendations
        age = patient_data.get('age', 0)
        if age > 65:
            recommendations.append("🧓 Elderly patient: Monitor symptoms more closely")
        elif age < 18:
            recommendations.append("👶 Pediatric patient: Consult pediatrician")
        
        return recommendations