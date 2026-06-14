import os
import json
from openai import OpenAI

class AIService:
    def __init__(self):
        # We will initialize the client inside the method to allow app context to load env vars
        pass
        
    def _get_client(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)

    def analyze_symptoms(self, data):
        """
        data: dict containing age, gender, symptoms, duration, severity, medical_history
        """
        client = self._get_client()
        if not client:
            # Return dummy data if no API key is present for development/testing purposes
            return self._get_dummy_response()

        system_prompt = """
        You are an advanced AI Medical Assistant. Your task is to analyze the patient's symptoms and provide possible conditions, risk level, explanation, and recommendations.
        You MUST respond ONLY with a valid JSON object matching this strict schema:
        {
          "conditions": [
            { "name": "Condition Name", "match_percentage": 85 }
          ],
          "risk_level": "Low" | "Moderate" | "High",
          "explanation": "Brief explanation of why these conditions were selected based on the symptoms.",
          "recommendations": [
            "Actionable advice 1",
            "Actionable advice 2"
          ]
        }
        """
        
        user_prompt = f"""
        Patient Profile:
        - Age: {data.get('age')}
        - Gender: {data.get('gender')}
        - Medical History: {data.get('medical_history', 'None reported')}
        
        Current Issue:
        - Symptoms: {data.get('symptoms')}
        - Duration: {data.get('duration')}
        - Severity (1-10): {data.get('severity')}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # Defaulting to faster/cheaper model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" }
            )
            
            result_json = response.choices[0].message.content
            return json.loads(result_json)
            
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return self._get_dummy_response()

    def _get_dummy_response(self):
        """Fallback response if API fails or no key is provided."""
        return {
            "conditions": [
                {"name": "Viral Infection", "match_percentage": 75},
                {"name": "Common Cold", "match_percentage": 60}
            ],
            "risk_level": "Low",
            "explanation": "Based on the reported symptoms, it appears to be a common viral infection. However, without an API key, this is a simulated response.",
            "recommendations": [
                "Rest and stay hydrated.",
                "Monitor your temperature.",
                "Consult a doctor if symptoms worsen after 3 days."
            ]
        }
