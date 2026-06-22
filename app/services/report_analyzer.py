import re
import random

class ReportAnalyzerService:
    def __init__(self):
        # Basic reference ranges for heuristic OCR parsing
        self.reference_ranges = {
            "glucose": {"min": 70.0, "max": 99.0, "name": "Fasting Glucose"},
            "hba1c": {"min": 4.0, "max": 5.6, "name": "Hemoglobin A1c"},
            "cholesterol": {"min": 0.0, "max": 200.0, "name": "Total Cholesterol"},
            "ldl": {"min": 0.0, "max": 100.0, "name": "LDL Cholesterol"},
            "hdl": {"min": 40.0, "max": 60.0, "name": "HDL Cholesterol", "higher_is_better": True},
            "triglycerides": {"min": 0.0, "max": 150.0, "name": "Triglycerides"},
            "hemoglobin": {"min": 12.0, "max": 15.5, "name": "Hemoglobin"},
            "platelets": {"min": 150.0, "max": 450.0, "name": "Platelets"},
            "wbc": {"min": 4.5, "max": 11.0, "name": "White Blood Cells"},
        }

    def analyze_report(self, raw_text):
        """
        Parses OCR text using regex heuristics to find abnormal values.
        """
        abnormal_values = []
        recommendations = set()
        
        # Lowercase for easier matching
        text_lower = raw_text.lower()
        
        # Look for numbers near keywords
        for key, ref in self.reference_ranges.items():
            # Simple regex to find the keyword followed by a number
            pattern = rf"{key}[^\d]*?(\d+(\.\d+)?)"
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    val = float(match.group(1))
                    status = "Normal"
                    
                    if ref.get("higher_is_better"):
                        if val < ref["min"]:
                            status = "Low"
                    else:
                        if val > ref["max"]:
                            status = "High"
                        elif val < ref["min"]:
                            status = "Low"
                            
                    if status != "Normal":
                        abnormal_values.append({
                            "metric": ref["name"],
                            "value": str(val),
                            "range": f'{ref["min"]}-{ref["max"]}',
                            "status": status
                        })
                        
                        if key in ["glucose", "hba1c"]:
                            recommendations.add("Consult with an endocrinologist regarding blood sugar levels.")
                            recommendations.add("Adopt a diet low in simple carbohydrates.")
                        elif key in ["cholesterol", "ldl", "triglycerides"]:
                            recommendations.add("Incorporate cardiovascular exercise daily.")
                            recommendations.add("Reduce intake of saturated fats.")
                        elif key == "hemoglobin" and status == "Low":
                            recommendations.add("Consider iron-rich foods or consult a doctor about potential anemia.")
                            
                except ValueError:
                    continue
                    
        # Filter to unique abnormal values (in case of multiple matches, just take first)
        seen = set()
        unique_abnormal = []
        for a in abnormal_values:
            if a["metric"] not in seen:
                seen.add(a["metric"])
                unique_abnormal.append(a)

        # Generate summary
        if unique_abnormal:
            metrics_str = ", ".join([a["metric"] for a in unique_abnormal])
            summary = f"The patient's lab results show abnormal values for {metrics_str}. These require medical review."
        else:
            summary = "No explicitly abnormal values could be extracted from the report. Please review manually with a doctor."
            
        if not recommendations:
            recommendations.add("Maintain a balanced diet and regular check-ups.")

        return {
            "summary": summary,
            "abnormal_values": unique_abnormal,
            "recommendations": list(recommendations)
        }

    def generate_chat_response(self, history):
        """
        Since OpenAI is removed, provide a static fallback/heuristic chatbot.
        history: array of dicts [{"role": "user", "content": "..."}]
        """
        if not history:
            return "Hello! How can I assist you with your health today?"
            
        last_message = history[-1].get("content", "").lower()
        
        if "fever" in last_message:
            return "If you have a high or persistent fever, it's important to stay hydrated, rest, and monitor your temperature. If it exceeds 103°F (39.4°C) or lasts more than 3 days, please see a doctor."
        elif "pain" in last_message:
            return "Pain can be caused by many factors. If the pain is severe, sudden, or in your chest/abdomen, please seek immediate emergency medical care."
        elif "hello" in last_message or "hi" in last_message:
            return "Hello! I am SymptoScan AI, operating entirely on local intelligence. How can I help you today?"
        elif "thank" in last_message:
            return "You're very welcome! Let me know if you need any further assistance."
        else:
            return "I am operating in a fully localized mode without a generative AI backend. While I cannot chat dynamically, you can use the Symptom Checker or Report Scanner for programmatic medical analysis. If you are experiencing a medical emergency, please dial 911 immediately."
