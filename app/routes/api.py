from flask import Blueprint, jsonify, request
from app.services.ai_service import AIService
from app.services.prediction_service import PredictionService
from app.models.assessment import Assessment
from app.models.risk_prediction import RiskPrediction
from app import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "SymptoScan AI API"})

@api_bp.route('/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    try:
        data = request.json
        if not data or not data.get('symptoms'):
            return jsonify({"error": "Symptoms are required"}), 400
            
        ai_service = AIService()
        ai_response = ai_service.analyze_symptoms(data)
        
        assessment = Assessment(
            age=data.get('age', 0),
            gender=data.get('gender', 'Unknown'),
            symptoms=data.get('symptoms'),
            duration=data.get('duration', 'Unknown'),
            severity=data.get('severity', 0),
            medical_history=data.get('medical_history', '')
        )
        assessment.set_ai_response(ai_response)
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({"success": True, "assessment_id": assessment.id, "results": ai_response})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in analyze_symptoms: {str(e)}")
        return jsonify({"error": "Failed to analyze symptoms"}), 500

@api_bp.route('/predict/<disease_type>', methods=['POST'])
def predict_disease(disease_type):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        service = PredictionService()

        if disease_type == 'comprehensive':
            res_diabetes = service.predict('diabetes', data)
            res_heart = service.predict('heart', data)
            res_kidney = service.predict('kidney', data)
            res_liver = service.predict('liver', data)
            res_respiratory = service.predict('respiratory', data)
            
            result = {
                "diabetes": res_diabetes,
                "heart": res_heart,
                "kidney": res_kidney,
                "liver": res_liver,
                "respiratory": res_respiratory
            }
            return jsonify({"success": True, "results": result})

        result = service.predict(disease_type, data)
        
        prediction = RiskPrediction(
            disease_type=disease_type,
            risk_score=result['risk_score'],
            risk_category=result['risk_category']
        )
        prediction.set_data(data, result['factors'], result['recommendations'])
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({"success": True, "prediction_id": prediction.id, "results": result})
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in predict_disease: {str(e)}")
        return jsonify({"error": "Prediction failed"}), 500

import os
from werkzeug.utils import secure_filename
from app.services.ocr_service import OCRService
from app.services.report_analyzer import ReportAnalyzerService
from app.models.medical_report import MedicalReport
from app.models.chat import ChatSession, ChatMessage

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'uploads')

@api_bp.route('/upload-report', methods=['POST'])
def upload_report():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            raw_text = OCRService.extract_text(file_path)
            
            analyzer = ReportAnalyzerService()
            analysis = analyzer.analyze_report(raw_text)
            
            report = MedicalReport(
                filename=filename,
                file_path=file_path,
                raw_text=raw_text
            )
            report.set_analysis(analysis)
            
            db.session.add(report)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "report_id": report.id,
                "analysis": analysis
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error processing report: {str(e)}")
            return jsonify({"error": "Failed to process report"}), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or not data.get('message'):
        return jsonify({"error": "Message is required"}), 400
        
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    try:
        if not session_id:
            session = ChatSession(title=user_message[:30] + "..." if len(user_message) > 30 else user_message)
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        else:
            session = ChatSession.query.get(session_id)
            if not session:
                return jsonify({"error": "Invalid session ID"}), 404
                
        user_msg_obj = ChatMessage(session_id=session_id, role='user', content=user_message)
        db.session.add(user_msg_obj)
        db.session.commit()
        
        # Build history
        history = [{"role": m.role, "content": m.content} for m in session.messages]
        
        analyzer = ReportAnalyzerService()
        bot_response = analyzer.generate_chat_response(history)
        
        bot_msg_obj = ChatMessage(session_id=session_id, role='assistant', content=bot_response)
        db.session.add(bot_msg_obj)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "response": bot_response
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat failed"}), 500

from flask import send_file
import io
from app.services.pdf_service import PDFService
from app.models.contact import ContactMessage
from app.models.risk_prediction import RiskPrediction
from app.models.assessment import Assessment

@api_bp.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    # In a real app, query by current_user.id. Since auth is mocked, query all or latest.
    try:
        reports = MedicalReport.query.order_by(MedicalReport.created_at.desc()).limit(5).all()
        predictions = RiskPrediction.query.order_by(RiskPrediction.created_at.desc()).limit(5).all()
        assessments = Assessment.query.order_by(Assessment.created_at.desc()).limit(5).all()
        
        timeline = []
        for r in reports:
            timeline.append({
                "type": "medical_report",
                "title": f"Report Analysis: {r.filename}",
                "date": r.created_at.strftime('%Y-%m-%d %H:%M'),
                "id": r.id
            })
        for p in predictions:
            timeline.append({
                "type": "risk_prediction",
                "title": f"{p.disease_type.title()} Risk Assessed",
                "date": p.created_at.strftime('%Y-%m-%d %H:%M'),
                "id": p.id,
                "score": p.risk_score
            })
        for a in assessments:
            timeline.append({
                "type": "symptom_assessment",
                "title": f"Symptom Check: {a.age}yo {a.gender}",
                "date": a.created_at.strftime('%Y-%m-%d %H:%M'),
                "id": a.id
            })
            
        # Sort by date descending
        timeline.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({"success": True, "timeline": timeline})
    except Exception as e:
        print(f"Dashboard Stats error: {str(e)}")
        return jsonify({"error": "Failed to fetch stats"}), 500

@api_bp.route('/export-report/<doc_type>/<int:doc_id>', methods=['GET'])
def export_report(doc_type, doc_id):
    try:
        pdf_bytes = None
        filename = "SymptoScan_Report.pdf"
        
        if doc_type == 'medical_report':
            report = MedicalReport.query.get_or_404(doc_id)
            pdf_bytes = PDFService.generate_medical_report_pdf(report)
            filename = f"Medical_Analysis_{report.filename}.pdf"
        elif doc_type == 'risk_prediction':
            prediction = RiskPrediction.query.get_or_404(doc_id)
            pdf_bytes = PDFService.generate_risk_prediction_pdf(prediction)
            filename = f"Risk_Assessment_{prediction.disease_type}.pdf"
        else:
            return jsonify({"error": "Invalid document type"}), 400
            
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Export error: {str(e)}")
        return jsonify({"error": "Failed to generate PDF"}), 500

@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.json
    try:
        msg = ContactMessage(
            name=data.get('name'),
            email=data.get('email'),
            subject=data.get('subject'),
            message=data.get('message')
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        print(f"Contact error: {str(e)}")
        return jsonify({"error": "Failed to submit message"}), 500
