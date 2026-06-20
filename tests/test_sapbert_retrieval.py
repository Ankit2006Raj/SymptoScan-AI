import unittest
from app.services.ai_service import AIService

class TestSapBERTRetrieval(unittest.TestCase):
    def setUp(self):
        self.ai_service = AIService()

    def run_symptom_test(self, test_name, symptoms, expected_disease, severity=5):
        print(f"\n--- Testing {test_name} ---")
        data = {
            "age": 45,
            "gender": "male",
            "symptoms": symptoms,
            "duration": "3 days",
            "severity": severity,
            "medical_history": "none"
        }
        
        result = self.ai_service.analyze_symptoms(data)
        conditions = [c['name'].lower() for c in result.get('conditions', [])]
        
        print(f"Input Symptoms: {symptoms}")
        print(f"Matched Conditions: {result.get('conditions')}")
        print(f"Risk Level: {result.get('risk_level')}")
        
        # Check if the expected disease is within top matches
        match_found = any(expected_disease.lower() in c for c in conditions)
        self.assertTrue(match_found, f"Expected {expected_disease} in conditions but got {conditions}")
        
        return result

    def test_emergency_heart_attack(self):
        result = self.run_symptom_test(
            "Emergency Heart Attack", 
            "chest pain, sweating, shortness of breath", 
            "heart attack",
            severity=9
        )
        self.assertTrue(result.get('risk_level') == 'High')
        
        has_warnings = len(result.get('red_flag_warnings', [])) > 0
        is_high_risk = result.get('risk_level') == 'High'
        self.assertTrue(has_warnings or is_high_risk, "Expected emergency warning or high risk")

    def test_diabetes(self):
        self.run_symptom_test(
            "Diabetes", 
            "fatigue, weight loss, excessive hunger, irregular sugar level", 
            "diabetes"
        )

    def test_liver_disease(self):
        self.run_symptom_test(
            "Liver Disease (Jaundice/Hepatitis)", 
            "yellowish skin, dark urine, abdominal pain, fatigue", 
            "hepatitis" # Hepatitis B, C, or Jaundice
        )

    def test_respiratory(self):
        self.run_symptom_test(
            "Respiratory (Asthma/Pneumonia)", 
            "cough, high fever, breathlessness, phlegm", 
            "pneumonia" # Or Bronchial Asthma
        )

if __name__ == '__main__':
    unittest.main()
