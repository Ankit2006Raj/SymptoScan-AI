import os
import json
from openai import OpenAI

class ReportAnalyzerService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _get_client(self):
        if not self.api_key: return None
        return OpenAI(api_key=self.api_key)

    def analyze_report(self, raw_text):
        client = self._get_client()
        if not client:
            return self._mock_analysis()

        system_prompt = """
        You are an expert Medical AI Analyst. I will provide raw OCR text extracted from a patient's lab report.
        Extract and return ONLY a valid JSON object matching this schema exactly:
        {
          "summary": "A 2-3 sentence overview of the patient's general health based on the report.",
          "abnormal_values": [
            { "metric": "Glucose", "value": "125", "range": "70-99", "status": "High" }
          ],
          "recommendations": [
            "Actionable advice 1",
            "Actionable advice 2"
          ]
        }
        Do not include any normal values in abnormal_values.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI Report Analysis Error: {str(e)}")
            return self._mock_analysis()

    def generate_chat_response(self, history):
        """
        history: array of dicts [{"role": "user", "content": "..."}]
        """
        client = self._get_client()
        if not client:
            return "I am a simulated AI Assistant because no OPENAI_API_KEY was provided. Please provide a key in `.env` to enable my true intelligence."

        system_prompt = """
        You are SymptoScan AI, a highly advanced, compassionate, and helpful medical assistant.
        Always advise users to seek professional medical help for serious symptoms.
        Keep answers concise, clear, and professional. Use markdown formatting.
        """
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Chat Error: {str(e)}")
            return "Sorry, I am having trouble connecting to my neural network right now."

    def _mock_analysis(self):
        return {
            "summary": "The patient's lab results show elevated fasting glucose and HbA1c levels, indicating a high risk for diabetes. Lipid panel also shows elevated LDL cholesterol.",
            "abnormal_values": [
                { "metric": "Glucose, Fasting", "value": "125", "range": "70-99", "status": "High" },
                { "metric": "Hemoglobin A1c", "value": "6.5", "range": "4.0-5.6", "status": "High" },
                { "metric": "Total Cholesterol", "value": "210", "range": "<200", "status": "High" },
                { "metric": "LDL", "value": "135", "range": "<100", "status": "High" }
            ],
            "recommendations": [
                "Consult with an endocrinologist regarding the elevated glucose and A1c.",
                "Adopt a diet low in simple carbohydrates and saturated fats.",
                "Incorporate at least 30 minutes of cardiovascular exercise daily."
            ]
        }
