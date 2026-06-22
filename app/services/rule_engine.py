import logging

logger = logging.getLogger(__name__)

class MedicalRuleEngine:
    """
    A deterministic rule engine to evaluate critical patient data and flag 
    emergencies, overriding general AI risk levels with hardcoded medical rules.
    """
    
    def __init__(self):
        pass

    def evaluate(self, data):
        """
        Evaluate the patient data and return structured flags.
        """
        logger.debug(f"RuleEngine evaluating data: {data}")
        symptoms = data.get('symptoms', '').lower()
        history = data.get('medical_history', '').lower()
        
        # Determine duration scale
        duration = data.get('duration', '').lower()
        
        flags = []
        warnings = []
        recommendations = []
        risk_level = None
        
        # 1. Cardiac Emergency Rules
        if 'chest pain' in symptoms or 'chest tightness' in symptoms:
            if 'shortness of breath' in symptoms or 'arm pain' in symptoms or 'jaw pain' in symptoms or 'sweating' in symptoms:
                flags.append("Cardiac Emergency Suspected")
                warnings.append("URGENT: Possible Myocardial Infarction (Heart Attack). Seek immediate emergency medical care (Call 911).")
                recommendations.append("Do not drive yourself to the hospital. Have someone call emergency services.")
                risk_level = "High"

        # 2. Stroke Rules
        if 'facial drooping' in symptoms or 'arm weakness' in symptoms or 'speech difficulty' in symptoms or 'slurred speech' in symptoms:
            flags.append("Stroke Suspected (FAST criteria)")
            warnings.append("URGENT: Possible Stroke. Time is critical. Seek emergency medical care immediately.")
            recommendations.append("Note the time symptoms started and call emergency services.")
            risk_level = "High"

        # 3. Severe Allergic Reaction / Anaphylaxis
        if 'swelling' in symptoms and ('face' in symptoms or 'lip' in symptoms or 'throat' in symptoms) and 'breathing' in symptoms:
            flags.append("Anaphylaxis Suspected")
            warnings.append("URGENT: Severe allergic reaction. Use an epinephrine auto-injector (EpiPen) if available and call 911.")
            risk_level = "High"

        # 4. Severe Respiratory Distress
        if 'difficulty breathing' in symptoms or 'severe shortness of breath' in symptoms or 'gasping' in symptoms:
            flags.append("Severe Respiratory Distress")
            warnings.append("URGENT: Critical breathing issues detected. Seek immediate emergency care.")
            risk_level = "High"

        # 5. Persistent High Fever / Sepsis Risk
        if 'high fever' in symptoms or 'persistent fever' in symptoms:
            if 'confusion' in symptoms or 'shivering' in symptoms or 'chills' in symptoms:
                flags.append("High Fever / Possible Sepsis Risk")
                warnings.append("Seek medical evaluation promptly for high fever accompanied by systemic symptoms.")
                if risk_level != "High":
                    risk_level = "Moderate"

        # 6. Loss of Consciousness
        if 'fainting' in symptoms or 'loss of consciousness' in symptoms or 'passed out' in symptoms:
            flags.append("Syncope / Loss of Consciousness")
            warnings.append("URGENT: Loss of consciousness requires immediate medical evaluation to rule out cardiac or neurological emergencies.")
            risk_level = "High"
            
        
        result = {
            "has_emergency": risk_level == "High",
            "flags": flags,
            "warnings": warnings,
            "recommendations": recommendations,
            "risk_override": risk_level
        }
        logger.debug(f"RuleEngine evaluation complete. Found flags: {flags}")
        return result
