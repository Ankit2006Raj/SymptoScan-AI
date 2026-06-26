from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')



@views_bp.route('/symptom-checker')
def symptom_checker():
    return render_template('pages/symptom_checker.html')

@views_bp.route('/risk-prediction')
def risk_prediction():
    return render_template('pages/risk_prediction.html')

@views_bp.route('/risk-prediction/diabetes')
def predict_diabetes():
    return render_template('pages/predict_diabetes.html')

@views_bp.route('/risk-prediction/heart')
def predict_heart():
    return render_template('pages/predict_heart.html')

@views_bp.route('/risk-prediction/kidney')
def predict_kidney():
    return render_template('pages/predict_kidney.html')

@views_bp.route('/risk-prediction/liver')
def predict_liver():
    return render_template('pages/predict_liver.html')

@views_bp.route('/risk-prediction/comprehensive')
def predict_comprehensive():
    return render_template('pages/predict_comprehensive.html')

@views_bp.route('/risk-prediction/respiratory')
def predict_respiratory():
    return render_template('pages/predict_respiratory.html')

@views_bp.route('/medical-report')
def medical_report():
    return render_template('pages/medical_report.html')

@views_bp.route('/ai-assistant')
def ai_assistant():
    return render_template('pages/ai_assistant.html')


@views_bp.route('/admin')
def admin_dashboard():
    return render_template('pages/admin.html')

@views_bp.route('/settings')
def settings():
    return render_template('pages/settings.html')

@views_bp.route('/about')
def about():
    return render_template('pages/about.html')

@views_bp.route('/recommendations')
def recommendations():
    return render_template('pages/recommendations.html')

@views_bp.route('/contact')
def contact():
    return render_template('pages/contact.html')

# Error Handlers
@views_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@views_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
