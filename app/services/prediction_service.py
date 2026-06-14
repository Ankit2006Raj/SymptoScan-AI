import random

class PredictionService:
    def __init__(self):
        pass

    def predict(self, disease_type, data):
        """
        Simulate a prediction model using basic clinical thresholds.
        In a real scenario, this would load a .pkl model and call model.predict_proba()
        """
        if disease_type == 'diabetes':
            return self._predict_diabetes(data)
        elif disease_type == 'heart':
            return self._predict_heart(data)
        elif disease_type == 'kidney':
            return self._predict_kidney(data)
        elif disease_type == 'liver':
            return self._predict_liver(data)
        elif disease_type == 'respiratory':
            return self._predict_respiratory(data)
        else:
            raise ValueError(f"Unknown disease type: {disease_type}")

    def _predict_diabetes(self, data):
        age = float(data.get('age', 30))
        bmi = float(data.get('bmi', 22))
        glucose = float(data.get('glucose', 100))
        hba1c = float(data.get('hba1c', 5.5))
        blood_pressure = float(data.get('blood_pressure', 80))
        family_history = data.get('family_history', 'no').lower()
        physical_activity = data.get('physical_activity', 'moderate').lower()
        diet_habits = data.get('diet_habits', 'average').lower()
        frequent_thirst = data.get('frequent_thirst', 'no').lower()
        frequent_urination = data.get('frequent_urination', 'no').lower()
        fatigue = data.get('fatigue', 'no').lower()
        
        risk_score = 5.0
        factors = []
        
        if glucose > 125:
            risk_score += 25
            factors.append("High fasting glucose level")
        elif glucose > 100:
            risk_score += 10
            factors.append("Elevated fasting glucose level (Pre-diabetes range)")
            
        if hba1c > 6.4:
            risk_score += 25
            factors.append("High HbA1c level")
        elif hba1c > 5.6:
            risk_score += 15
            factors.append("Elevated HbA1c level")

        if bmi > 30:
            risk_score += 15
            factors.append("Obesity (BMI > 30)")
        elif bmi > 25:
            risk_score += 5
            factors.append("Overweight (BMI > 25)")
            
        if age > 45:
            risk_score += 10
            factors.append("Age factor (> 45 years)")
            
        if blood_pressure > 90:
            risk_score += 5
            factors.append("High diastolic blood pressure")

        if family_history == 'yes':
            risk_score += 10
            factors.append("Family history of diabetes")

        if physical_activity == 'low':
            risk_score += 5
            factors.append("Low physical activity")

        if diet_habits == 'poor':
            risk_score += 5
            factors.append("Poor dietary habits")

        symptoms_count = sum(1 for s in [frequent_thirst, frequent_urination, fatigue] if s == 'yes')
        if symptoms_count > 0:
            risk_score += (symptoms_count * 5)
            factors.append(f"Presence of {symptoms_count} active symptoms")

        risk_score = min(99.9, risk_score + random.uniform(-2, 5))
        category = "Low" if risk_score < 35 else ("Moderate" if risk_score < 65 else "High")
            
        recs = [
            "Maintain a healthy diet rich in whole grains and vegetables.",
            "Engage in at least 150 minutes of moderate aerobic activity per week.",
            "Monitor blood sugar levels regularly if indicated."
        ]
        if category == 'High':
            recs.insert(0, "Consult an endocrinologist or primary care physician immediately.")
            
        return {"risk_score": round(risk_score, 1), "risk_category": category, "factors": factors, "recommendations": recs}

    def _predict_heart(self, data):
        age = float(data.get('age', 30))
        cholesterol = float(data.get('cholesterol', 180))
        systolic_bp = float(data.get('systolic_bp', 120))
        heart_rate = float(data.get('heart_rate', 70))
        smoking = data.get('smoking', 'no').lower()
        family_history = data.get('family_history', 'no').lower()
        chest_pain = data.get('chest_pain', 'no').lower()
        palpitations = data.get('palpitations', 'no').lower()
        shortness_of_breath = data.get('shortness_of_breath', 'no').lower()
        alcohol = data.get('alcohol_consumption', 'low').lower()
        diabetes_history = data.get('diabetes_history', 'no').lower()
        
        risk_score = 5.0
        factors = []
        
        if cholesterol > 240:
            risk_score += 20
            factors.append("High total cholesterol")
        elif cholesterol > 200:
            risk_score += 5
            factors.append("Borderline high cholesterol")
            
        if systolic_bp > 140:
            risk_score += 15
            factors.append("High systolic blood pressure (Hypertension)")
            
        if age > 55:
            risk_score += 10
            factors.append("Age factor (> 55 years)")
            
        if heart_rate > 100:
            risk_score += 5
            factors.append("Elevated resting heart rate")

        if smoking in ['yes', 'current']:
            risk_score += 15
            factors.append("Current smoker")

        if family_history == 'yes':
            risk_score += 10
            factors.append("Family history of heart disease")

        if diabetes_history == 'yes':
            risk_score += 10
            factors.append("History of diabetes")

        if alcohol in ['high', 'frequent']:
            risk_score += 5
            factors.append("High alcohol consumption")

        if chest_pain == 'yes':
            risk_score += 20
            factors.append("Recent episodes of chest pain")
        if palpitations == 'yes':
            risk_score += 10
            factors.append("Palpitations")
        if shortness_of_breath == 'yes':
            risk_score += 10
            factors.append("Shortness of breath")

        risk_score = min(99.9, risk_score + random.uniform(0, 5))
        category = "Low" if risk_score < 30 else ("Moderate" if risk_score < 60 else "High")
            
        recs = [
            "Reduce sodium intake and avoid trans fats.",
            "Engage in regular cardiovascular exercise."
        ]
        if smoking in ['yes', 'current']:
            recs.append("Enroll in a smoking cessation program.")
        if chest_pain == 'yes' or shortness_of_breath == 'yes':
            recs.insert(0, "URGENT: Consult a cardiologist regarding your active symptoms immediately.")
            
        return {"risk_score": round(risk_score, 1), "risk_category": category, "factors": factors, "recommendations": recs}

    def _predict_kidney(self, data):
        age = float(data.get('age', 30))
        creatinine = float(data.get('creatinine', 0.9))
        bun = float(data.get('bun', 15))
        egfr = float(data.get('egfr', 90))
        bp = float(data.get('blood_pressure', 80))
        diabetes = data.get('diabetes_history', 'no').lower()
        swelling = data.get('swelling_legs', 'no').lower()
        urination = data.get('frequent_urination', 'no').lower()
        kidney_history = data.get('kidney_disease_history', 'no').lower()
        
        risk_score = 5.0
        factors = []
        
        if creatinine > 1.2:
            risk_score += 25
            factors.append("Elevated serum creatinine")
        
        if bun > 20:
            risk_score += 15
            factors.append("Elevated BUN levels")

        if egfr < 60:
            risk_score += 30
            factors.append("Low eGFR (reduced kidney function)")
            
        if bp > 90:
            risk_score += 10
            factors.append("High blood pressure")
            
        if diabetes == 'yes':
            risk_score += 15
            factors.append("History of diabetes")

        if kidney_history == 'yes':
            risk_score += 15
            factors.append("Family history of kidney disease")

        if swelling == 'yes':
            risk_score += 10
            factors.append("Swelling in legs (edema)")

        if age > 60:
            risk_score += 10
            factors.append("Age factor (> 60 years)")
            
        risk_score = min(99.9, risk_score + random.uniform(0, 5))
        category = "Low" if risk_score < 30 else ("Moderate" if risk_score < 60 else "High")
        
        recs = ["Stay hydrated.", "Monitor blood pressure regularly.", "Avoid excessive use of NSAID pain relievers."]
        if egfr < 60:
            recs.insert(0, "Consult a nephrologist for comprehensive evaluation of kidney function.")
        return {"risk_score": round(risk_score, 1), "risk_category": category, "factors": factors, "recommendations": recs}

    def _predict_liver(self, data):
        age = float(data.get('age', 30))
        alcohol = data.get('alcohol_consumption', 'low').lower()
        sgpt = float(data.get('sgpt', 30)) # ALT
        sgot = float(data.get('sgot', 30)) # AST
        bilirubin = float(data.get('bilirubin', 1.0))
        fatty_liver = data.get('fatty_liver_history', 'no').lower()
        obesity = data.get('obesity', 'no').lower()
        hepatitis = data.get('hepatitis_history', 'no').lower()
        abd_pain = data.get('abdominal_pain', 'no').lower()
        jaundice = data.get('jaundice_symptoms', 'no').lower()
        
        risk_score = 5.0
        factors = []
        
        if sgpt > 40:
            risk_score += 20
            factors.append("Elevated ALT (SGPT) levels")
            
        if sgot > 40:
            risk_score += 15
            factors.append("Elevated AST (SGOT) levels")

        if bilirubin > 1.2:
            risk_score += 15
            factors.append("Elevated Bilirubin levels")
            
        if alcohol in ['high', 'frequent', 'yes']:
            risk_score += 25
            factors.append("High alcohol consumption")

        if fatty_liver == 'yes':
            risk_score += 15
            factors.append("History of fatty liver")

        if obesity == 'yes':
            risk_score += 10
            factors.append("Obesity")

        if hepatitis == 'yes':
            risk_score += 20
            factors.append("History of Hepatitis")

        if abd_pain == 'yes':
            risk_score += 10
            factors.append("Abdominal pain")

        if jaundice == 'yes':
            risk_score += 25
            factors.append("Jaundice symptoms")
            
        risk_score = min(99.9, risk_score + random.uniform(0, 5))
        category = "Low" if risk_score < 35 else ("Moderate" if risk_score < 65 else "High")
        
        recs = ["Maintain a healthy weight.", "Limit alcohol consumption.", "Get vaccinated against Hepatitis A and B."]
        if jaundice == 'yes' or bilirubin > 1.2:
            recs.insert(0, "URGENT: Consult a hepatologist regarding jaundice and elevated bilirubin.")
        return {"risk_score": round(risk_score, 1), "risk_category": category, "factors": factors, "recommendations": recs}

    def _predict_respiratory(self, data):
        age = float(data.get('age', 30))
        smoking = data.get('smoking', 'no').lower()
        cough = data.get('cough_duration', 'none').lower()
        wheezing = data.get('wheezing', 'no').lower()
        sob = data.get('shortness_of_breath', 'no').lower()
        chest_tightness = data.get('chest_tightness', 'no').lower()
        o2_sat = float(data.get('oxygen_saturation', 98))
        asthma = data.get('asthma_history', 'no').lower()
        copd = data.get('copd_history', 'no').lower()
        exposure = data.get('environmental_exposure', 'no').lower()

        risk_score = 5.0
        factors = []

        if smoking in ['yes', 'current']:
            risk_score += 25
            factors.append("Current smoker")
        elif smoking == 'former':
            risk_score += 10
            factors.append("Former smoker")

        if o2_sat < 95:
            risk_score += 20
            factors.append(f"Low oxygen saturation ({o2_sat}%)")

        if cough in ['chronic', 'more_than_3_weeks']:
            risk_score += 15
            factors.append("Chronic cough")

        if wheezing == 'yes':
            risk_score += 15
            factors.append("Wheezing")

        if sob == 'yes':
            risk_score += 20
            factors.append("Shortness of breath")

        if chest_tightness == 'yes':
            risk_score += 10
            factors.append("Chest tightness")

        if asthma == 'yes':
            risk_score += 10
            factors.append("History of Asthma")

        if copd == 'yes':
            risk_score += 20
            factors.append("History of COPD")

        if exposure == 'yes':
            risk_score += 10
            factors.append("High environmental/occupational exposure")

        risk_score = min(99.9, risk_score + random.uniform(0, 5))
        category = "Low" if risk_score < 30 else ("Moderate" if risk_score < 60 else "High")
        
        recs = ["Avoid smoking and secondhand smoke.", "Minimize exposure to air pollution and dust."]
        if o2_sat < 95 or sob == 'yes':
            recs.insert(0, "URGENT: Consult a pulmonologist regarding low oxygen levels or shortness of breath.")
        if smoking in ['yes', 'current']:
            recs.append("Enroll in a smoking cessation program.")

        return {"risk_score": round(risk_score, 1), "risk_category": category, "factors": factors, "recommendations": recs}
