from typing import Dict, List, Any, Tuple
import logging
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Rule:
    def __init__(self, name: str, conditions: List[Dict], conclusion: str, confidence: float):
        self.name = name
        self.conditions = conditions  # List of condition dictionaries
        self.conclusion = conclusion  # Disease name
        self.confidence = confidence  # Rule confidence (0-1)
    
    def evaluate(self, facts: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Evaluate if rule conditions are met
        Returns: (rule_fired, confidence_score, explanation)
        """
        explanations = []
        total_conditions = len(self.conditions)
        met_conditions = 0
        
        for condition in self.conditions:
            condition_met = self._evaluate_condition(condition, facts)
            if condition_met:
                met_conditions += 1
                explanations.append(f"✓ {condition['explanation']}")
            else:
                explanations.append(f"✗ {condition['explanation']}")
        
        # Rule fires if all conditions are met
        rule_fired = met_conditions == total_conditions
        
        # Confidence adjusted by how many conditions were met
        adjusted_confidence = self.confidence * (met_conditions / total_conditions)
        
        return rule_fired, adjusted_confidence, explanations
    
    def _evaluate_condition(self, condition: Dict, facts: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        param = condition['parameter']
        operator = condition['operator']
        value = condition['value']
        
        if param not in facts:
            return False
        
        fact_value = facts[param]
        
        if operator == '==':
            return fact_value == value
        elif operator == '!=':
            return fact_value != value
        elif operator == '<':
            return float(fact_value) < float(value)
        elif operator == '<=':
            return float(fact_value) <= float(value)
        elif operator == '>':
            return float(fact_value) > float(value)
        elif operator == '>=':
            return float(fact_value) >= float(value)
        elif operator == 'in':
            return value in fact_value if isinstance(fact_value, list) else str(value) in str(fact_value)
        elif operator == 'not_in':
            return value not in fact_value if isinstance(fact_value, list) else str(value) not in str(fact_value)
        
        return False

class RuleBasedSystem:
    def __init__(self):
        self.rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize medical diagnosis rules"""
        
        # Dengue Rules
        dengue_rule_1 = Rule(
            name="Dengue_Classic",
            conditions=[
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fever', 'explanation': 'Patient has fever'},
                {'parameter': 'platelets', 'operator': '<', 'value': 100000, 'explanation': 'Platelet count is low (<100,000)'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'headache', 'explanation': 'Patient has headache'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'muscle_pain', 'explanation': 'Patient has muscle pain'}
            ],
            conclusion="Dengue",
            confidence=0.85
        )
        
        dengue_rule_2 = Rule(
            name="Dengue_Severe",
            conditions=[
                {'parameter': 'platelets', 'operator': '<', 'value': 50000, 'explanation': 'Severe low platelet count (<50,000)'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fever', 'explanation': 'Patient has fever'},
                {'parameter': 'wbc', 'operator': '<', 'value': 4000, 'explanation': 'Low white blood cell count'}
            ],
            conclusion="Dengue",
            confidence=0.95
        )
        
        # COVID-19 Rules
        covid_rule_1 = Rule(
            name="COVID_Respiratory",
            conditions=[
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'cough', 'explanation': 'Patient has cough'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'shortness_of_breath', 'explanation': 'Patient has breathing difficulties'},
                {'parameter': 'oxygen', 'operator': '<', 'value': 95, 'explanation': 'Low oxygen saturation (<95%)'},
                {'parameter': 'temperature', 'operator': '>', 'value': 100.4, 'explanation': 'High temperature (>100.4°F)'}
            ],
            conclusion="COVID-19",
            confidence=0.80
        )
        
        covid_rule_2 = Rule(
            name="COVID_Classic",
            conditions=[
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fever', 'explanation': 'Patient has fever'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'cough', 'explanation': 'Patient has cough'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fatigue', 'explanation': 'Patient feels fatigued'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'sore_throat', 'explanation': 'Patient has sore throat'}
            ],
            conclusion="COVID-19",
            confidence=0.70
        )
        
        # Pneumonia Rules
        pneumonia_rule_1 = Rule(
            name="Pneumonia_Severe",
            conditions=[
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'cough', 'explanation': 'Patient has cough'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'chest_pain', 'explanation': 'Patient has chest pain'},
                {'parameter': 'oxygen', 'operator': '<', 'value': 92, 'explanation': 'Severe low oxygen saturation (<92%)'},
                {'parameter': 'wbc', 'operator': '>', 'value': 12000, 'explanation': 'High white blood cell count (>12,000)'}
            ],
            conclusion="Pneumonia",
            confidence=0.90
        )
        
        pneumonia_rule_2 = Rule(
            name="Pneumonia_Moderate",
            conditions=[
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'cough', 'explanation': 'Patient has cough'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fever', 'explanation': 'Patient has fever'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'shortness_of_breath', 'explanation': 'Patient has breathing difficulties'},
                {'parameter': 'temperature', 'operator': '>', 'value': 101, 'explanation': 'High temperature (>101°F)'}
            ],
            conclusion="Pneumonia",
            confidence=0.75
        )
        
        # Age and gender specific rules
        elderly_covid_rule = Rule(
            name="Elderly_COVID_Risk",
            conditions=[
                {'parameter': 'age', 'operator': '>', 'value': 65, 'explanation': 'Patient is elderly (>65 years)'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'fever', 'explanation': 'Patient has fever'},
                {'parameter': 'symptoms', 'operator': 'in', 'value': 'cough', 'explanation': 'Patient has cough'}
            ],
            conclusion="COVID-19",
            confidence=0.85
        )
        
        # Add rules to the system
        self.rules.extend([
            dengue_rule_1, dengue_rule_2,
            covid_rule_1, covid_rule_2,
            pneumonia_rule_1, pneumonia_rule_2,
            elderly_covid_rule
        ])
    
    def forward_chain(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform forward chaining inference
        """
        results = {}
        all_explanations = []
        
        # Evaluate each rule
        for rule in self.rules:
            rule_fired, confidence, explanations = rule.evaluate(facts)
            
            if rule_fired:
                # Update disease confidence (take maximum if multiple rules for same disease)
                disease = rule.conclusion
                if disease not in results or confidence > results[disease]['confidence']:
                    results[disease] = {
                        'confidence': confidence,
                        'rule_name': rule.name,
                        'explanations': explanations
                    }
                
                all_explanations.append({
                    'rule': rule.name,
                    'disease': disease,
                    'confidence': confidence,
                    'explanations': explanations
                })
        
        return {
            'results': results,
            'all_explanations': all_explanations
        }
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction using rule-based system
        """
        try:
            # Prepare facts from input data
            facts = {
                'symptoms': data.get('symptoms', []),
                'platelets': data.get('platelets', 150000),
                'oxygen': data.get('oxygen', 98),
                'wbc': data.get('wbc', 7000),
                'temperature': data.get('temperature', 98.6),
                'age': data.get('age', 30),
                'gender': data.get('gender', '').lower()
            }
            
            # Perform forward chaining
            inference_results = self.forward_chain(facts)
            
            if not inference_results['results']:
                return {
                    'disease': "Unknown",
                    'probability': 0.0,
                    'risk_level': "Low",
                    'explanation': "No rules matched the given symptoms and lab values",
                    'model_type': "RuleBased",
                    'all_probabilities': {},
                    'matched_rules': []
                }
            
            # Find the disease with highest confidence
            best_disease = max(inference_results['results'].items(), 
                             key=lambda x: x[1]['confidence'])
            
            disease_name = best_disease[0]
            confidence = best_disease[1]['confidence']
            rule_explanations = best_disease[1]['explanations']
            
            # Determine risk level
            if confidence < Config.RISK_THRESHOLDS["low"]:
                risk_level = "Low"
            elif confidence < Config.RISK_THRESHOLDS["moderate"]:
                risk_level = "Moderate"
            else:
                risk_level = "High"
            
            # Prepare all disease probabilities
            all_probabilities = {}
            for disease, result in inference_results['results'].items():
                all_probabilities[disease] = result['confidence']
            
            # Create explanation
            explanation_text = f"Based on rule '{best_disease[1]['rule_name']}':\n"
            explanation_text += "\n".join(rule_explanations)
            
            return {
                'disease': disease_name,
                'probability': confidence,
                'risk_level': risk_level,
                'explanation': explanation_text,
                'model_type': "RuleBased",
                'all_probabilities': all_probabilities,
                'matched_rules': inference_results['all_explanations']
            }
            
        except Exception as e:
            logger.error(f"Rule-based prediction failed: {str(e)}")
            return {'error': str(e)}
    
    def add_rule(self, rule: Rule):
        """Add a new rule to the system"""
        self.rules.append(rule)
    
    def get_rules_for_disease(self, disease: str) -> List[Rule]:
        """Get all rules that conclude a specific disease"""
        return [rule for rule in self.rules if rule.conclusion == disease]
    
    def explain_reasoning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed explanation of reasoning process"""
        facts = {
            'symptoms': data.get('symptoms', []),
            'platelets': data.get('platelets', 150000),
            'oxygen': data.get('oxygen', 98),
            'wbc': data.get('wbc', 7000),
            'temperature': data.get('temperature', 98.6),
            'age': data.get('age', 30),
            'gender': data.get('gender', '').lower()
        }
        
        detailed_explanation = {
            'facts': facts,
            'rule_evaluations': [],
            'conclusion': None
        }
        
        for rule in self.rules:
            rule_fired, confidence, explanations = rule.evaluate(facts)
            
            detailed_explanation['rule_evaluations'].append({
                'rule_name': rule.name,
                'rule_fired': rule_fired,
                'confidence': confidence,
                'conditions_met': explanations,
                'conclusion': rule.conclusion if rule_fired else None
            })
        
        # Get final prediction
        prediction = self.predict(data)
        detailed_explanation['conclusion'] = prediction
        
        return detailed_explanation