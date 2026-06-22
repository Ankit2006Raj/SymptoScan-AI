from app import db
from datetime import datetime
import json

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional for guest users
    
    # Inputs
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Integer, nullable=False) # 1-10 scale
    medical_history = db.Column(db.Text, nullable=True)
    
    # AI Outputs (stored as JSON strings)
    conditions = db.Column(db.Text, nullable=True) # JSON list of condition objects
    risk_level = db.Column(db.String(50), nullable=True) # Low, Moderate, High
    explanation = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True) # JSON list of strings
    red_flag_warnings = db.Column(db.Text, nullable=True) # JSON list of strings
    follow_up_questions = db.Column(db.Text, nullable=True) # JSON list of strings
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_ai_response(self, response_dict):
        """Helper to save the JSON response from OpenAI into the db fields"""
        self.conditions = json.dumps(response_dict.get('conditions', []))
        self.risk_level = response_dict.get('risk_level', 'Unknown')
        self.explanation = response_dict.get('explanation', '')
        self.recommendations = json.dumps(response_dict.get('recommendations', []))
        self.red_flag_warnings = json.dumps(response_dict.get('red_flag_warnings', []))
        self.follow_up_questions = json.dumps(response_dict.get('follow_up_questions', []))
        
    def get_conditions(self):
        return json.loads(self.conditions) if self.conditions else []
        
    def get_recommendations(self):
        return json.loads(self.recommendations) if self.recommendations else []
        
    def get_red_flag_warnings(self):
        return json.loads(self.red_flag_warnings) if self.red_flag_warnings else []
        
    def get_follow_up_questions(self):
        return json.loads(self.follow_up_questions) if self.follow_up_questions else []

    def __repr__(self):
        return f'<Assessment {self.id}>'
