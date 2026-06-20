from app import create_app, db
from app.models import RiskPrediction
from app.services.pdf_service import PDFService
import traceback

app = create_app()
with app.app_context():
    try:
        prediction = RiskPrediction.query.filter_by(disease_type='comprehensive').order_by(RiskPrediction.id.desc()).first()
        if prediction:
            print(f"Found prediction {prediction.id}, generating PDF...")
            PDFService.generate_risk_prediction_pdf(prediction)
            print("PDF generation successful!")
        else:
            print("No comprehensive prediction found.")
    except Exception as e:
        print("PDF generation failed:")
        traceback.print_exc()
