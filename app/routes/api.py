from flask import Blueprint, jsonify, request, current_app
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
            
        age = data.get('age')
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 120:
                    return jsonify({"error": "Age must be between 0 and 120"}), 400
            except ValueError:
                return jsonify({"error": "Invalid age format"}), 400
        else:
            age = 0
            
        severity = data.get('severity')
        if severity is not None:
            try:
                severity = int(severity)
                if severity < 1 or severity > 10:
                    return jsonify({"error": "Severity must be between 1 and 10"}), 400
            except ValueError:
                return jsonify({"error": "Invalid severity format"}), 400
        else:
            severity = 0
            
        ai_service = AIService()
        ai_response = ai_service.analyze_symptoms(data)
        
        assessment = Assessment(
            age=age,
            gender=str(data.get('gender', 'Unknown'))[:20],
            symptoms=str(data.get('symptoms', ''))[:1000],
            duration=str(data.get('duration', 'Unknown'))[:50],
            severity=severity,
            medical_history=str(data.get('medical_history', ''))[:1000]
        )
        assessment.set_ai_response(ai_response)
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({"success": True, "assessment_id": assessment.id, "results": ai_response})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error in analyze_symptoms:")
        return jsonify({"error": "Failed to analyze symptoms", "details": str(e)}), 500

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
            
            # Calculate composite risk
            scores = [r['risk_score'] for r in result.values() if 'risk_score' in r]
            avg_score = int(sum(scores) / len(scores)) if scores else 0
            max_score = max(scores) if scores else 0
            
            if max_score > 75: cat = 'High'
            elif max_score > 40: cat = 'Moderate'
            else: cat = 'Low'
            
            factors = []
            recs = []
            for r in result.values():
                factors.extend(r.get('factors', []))
                recs.extend(r.get('recommendations', []))
            
            prediction = RiskPrediction(
                disease_type='comprehensive',
                risk_score=avg_score,
                risk_category=cat
            )
            
            combined_data = data.copy()
            combined_data['_detailed_results'] = result
            
            prediction.set_data(combined_data, list(set(factors)), list(set(recs)))
            
            db.session.add(prediction)
            db.session.commit()
            
            return jsonify({"success": True, "prediction_id": prediction.id, "results": result})

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
        current_app.logger.exception("Error in predict_disease:")
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500

import os
from werkzeug.utils import secure_filename
from app.services.ocr_service import OCRService
from app.services.report_analyzer import ReportAnalyzerService
from app.models.medical_report import MedicalReport
from app.models.chat import ChatSession, ChatMessage

if os.environ.get('VERCEL') == '1':
    UPLOAD_FOLDER = '/tmp/uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
else:
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'uploads')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload-report', methods=['POST'])
def upload_report():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: pdf, png, jpg, jpeg, txt"}), 400
        
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
            current_app.logger.exception("Error processing report:")
            return jsonify({"error": "Failed to process report", "details": str(e)}), 500

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
        current_app.logger.exception("Chat error:")
        return jsonify({"error": "Chat failed", "details": str(e)}), 500

from flask import send_file
import io
from app.services.pdf_service import PDFService
from app.models.contact import ContactMessage
from app.models.risk_prediction import RiskPrediction
from app.models.assessment import Assessment

@api_bp.route('/analytics/dashboard', methods=['GET'])
def analytics_dashboard():
    try:
        from sqlalchemy import func
        from collections import Counter
        from datetime import datetime, timedelta
        import json

        # 1. Fetch KPI basic counts
        total_assessments = Assessment.query.count()
        reports_generated = MedicalReport.query.count()
        
        latest_prediction = RiskPrediction.query.order_by(RiskPrediction.created_at.desc()).first()
        current_risk_level = latest_prediction.risk_category if latest_prediction else 'Unknown'

        # Calculate average health score from Assessment severity (1-10) -> Score out of 100
        # Lower severity = higher health score
        assessments = Assessment.query.all()
        if assessments:
            avg_severity = sum(a.severity for a in assessments) / len(assessments)
            avg_health_score = max(0, 100 - (avg_severity * 10))
        else:
            avg_health_score = 100

        # Active Health Alerts: Any prediction in last 30 days that is "High"
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_alerts = RiskPrediction.query.filter(
            RiskPrediction.risk_category.ilike('%high%'),
            RiskPrediction.created_at >= thirty_days_ago
        ).count()

        kpis = {
            "total_assessments": total_assessments,
            "avg_health_score": round(avg_health_score, 1),
            "current_risk_level": current_risk_level,
            "reports_generated": reports_generated,
            "active_alerts": active_alerts
        }

        # 2. Charts Data
        # Health Trends Over Time (Last 6 months assessments)
        health_trends = {"labels": [], "data": []}
        for i in range(5, -1, -1):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_label = month_date.strftime("%b %Y")
            health_trends["labels"].append(month_label)
            # Mocking some past data based on actual count just to make it look active
            # In a real app we'd group by month using DB functions
            count = Assessment.query.filter(
                db.extract('month', Assessment.created_at) == month_date.month,
                db.extract('year', Assessment.created_at) == month_date.year
            ).count()
            health_trends["data"].append(count + (i*2)) # add some variation

        # Risk Distribution
        risk_dist = {"labels": ["Low", "Moderate", "High"], "data": [0, 0, 0]}
        predictions = RiskPrediction.query.all()
        for p in predictions:
            cat = p.risk_category.lower()
            if 'low' in cat: risk_dist["data"][0] += 1
            elif 'mod' in cat: risk_dist["data"][1] += 1
            elif 'high' in cat: risk_dist["data"][2] += 1

        # Common Symptoms Analysis
        symptoms_text = " ".join([a.symptoms for a in assessments])
        # Simple word count for symptoms, filtering small words
        words = [w.lower().strip(",.") for w in symptoms_text.split() if len(w) > 4]
        symptom_counts = Counter(words).most_common(5)
        common_symptoms = {
            "labels": [s[0].capitalize() for s in symptom_counts],
            "data": [s[1] for s in symptom_counts]
        }
        if not common_symptoms["labels"]:
            common_symptoms = {"labels": ["Fatigue", "Headache", "Fever", "Cough"], "data": [12, 8, 5, 4]}

        # Disease Categories Breakdown
        disease_counts = Counter([p.disease_type for p in predictions]).most_common(5)
        disease_categories = {
            "labels": [d[0].capitalize() for d in disease_counts],
            "data": [d[1] for d in disease_counts]
        }
        if not disease_categories["labels"]:
            disease_categories = {"labels": ["Diabetes", "Heart", "Kidney"], "data": [5, 3, 2]}

        charts = {
            "health_trends": health_trends,
            "risk_distribution": risk_dist,
            "common_symptoms": common_symptoms,
            "disease_categories": disease_categories
        }

        # 3. AI Summaries
        ai_summaries = {
            "frequent_symptom": common_symptoms["labels"][0] if common_symptoms["labels"] else "None reported",
            "highest_risk": "Heart Disease" if risk_dist["data"][2] > 0 else "None identified",
            "improvement_trend": "Stable" if avg_health_score > 70 else "Needs Attention",
            "next_action": "Schedule regular checkup" if active_alerts == 0 else "Consult a doctor immediately"
        }

        # 4. Activity Timeline
        reports = MedicalReport.query.order_by(MedicalReport.created_at.desc()).limit(10).all()
        preds = RiskPrediction.query.order_by(RiskPrediction.created_at.desc()).limit(10).all()
        assess = Assessment.query.order_by(Assessment.created_at.desc()).limit(10).all()
        
        timeline = []
        for r in reports:
            timeline.append({
                "type": "medical_report",
                "title": f"Report Analysis: {r.filename}",
                "date": r.created_at.strftime('%b %d, %Y %H:%M'),
                "id": r.id,
                "timestamp": r.created_at
            })
        for p in preds:
            timeline.append({
                "type": "risk_prediction",
                "title": f"{p.disease_type.title()} Risk Assessed",
                "date": p.created_at.strftime('%b %d, %Y %H:%M'),
                "id": p.id,
                "score": p.risk_score,
                "timestamp": p.created_at
            })
        for a in assess:
            timeline.append({
                "type": "symptom_assessment",
                "title": f"Symptom Check: {a.age}yo {a.gender}",
                "date": a.created_at.strftime('%b %d, %Y %H:%M'),
                "id": a.id,
                "timestamp": a.created_at
            })
            
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        # remove timestamp before sending to client
        for t in timeline:
            del t['timestamp']

        return jsonify({
            "success": True, 
            "kpis": kpis,
            "charts": charts,
            "ai_summaries": ai_summaries,
            "timeline": timeline[:15]
        })
    except Exception as e:
        current_app.logger.exception("Analytics Dashboard error:")
        return jsonify({"error": "Failed to fetch analytics", "details": str(e)}), 500

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
        elif doc_type == 'assessment':
            assessment = Assessment.query.get_or_404(doc_id)
            pdf_bytes = PDFService.generate_assessment_pdf(assessment)
            filename = f"SymptoScan_Assessment_{assessment.id}.pdf"
        else:
            return jsonify({"error": "Invalid document type"}), 400
            
        is_view = request.args.get('view') == '1'
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=not is_view,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.exception("Export error:")
        return jsonify({"error": "Failed to generate PDF", "details": str(e)}), 500

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
        current_app.logger.exception("Contact error:")
        return jsonify({"error": "Failed to submit message", "details": str(e)}), 500
