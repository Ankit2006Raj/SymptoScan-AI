from app import db
from datetime import datetime
import json

class RiskPrediction(db.Model):
    __tablename__ = 'risk_predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional for guests
    disease_type = db.Column(db.String(50), nullable=False) # e.g. 'Diabetes', 'Heart', 'Kidney', 'Liver'
    
    # Inputs (stored flexibly as JSON to accommodate different diseases)
    input_data = db.Column(db.Text, nullable=False) 
    
    # Outputs
    risk_score = db.Column(db.Float, nullable=False) # 0-100%
    risk_category = db.Column(db.String(50), nullable=False) # Low, Moderate, High
    factors = db.Column(db.Text, nullable=True) # JSON list of strings (contributing factors)
    recommendations = db.Column(db.Text, nullable=True) # JSON list of strings (preventive recommendations)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_data(self, inputs, factors, recommendations):
        self.input_data = json.dumps(inputs)
        self.factors = json.dumps(factors)
        self.recommendations = json.dumps(recommendations)
        
    def get_inputs(self):
        return json.loads(self.input_data) if self.input_data else {}
        
    def get_factors(self):
        return json.loads(self.factors) if self.factors else []
        
    def get_recommendations(self):
        return json.loads(self.recommendations) if self.recommendations else []

    def __repr__(self):
        return f'<RiskPrediction {self.disease_type} - {self.risk_score}%>'
