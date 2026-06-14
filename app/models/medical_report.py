from app import db
from datetime import datetime
import json

class MedicalReport(db.Model):
    __tablename__ = 'medical_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional for guests
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    
    raw_text = db.Column(db.Text, nullable=True)
    analysis_result = db.Column(db.Text, nullable=True) # Stored as JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_analysis(self, result_dict):
        self.analysis_result = json.dumps(result_dict)
        
    def get_analysis(self):
        return json.loads(self.analysis_result) if self.analysis_result else {}

    def __repr__(self):
        return f'<MedicalReport {self.filename}>'
