import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class PDFService:
    @staticmethod
    def generate_medical_report_pdf(report):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Header
        elements.append(Paragraph("SymptoScan AI - Medical Report Analysis", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"File: {report.filename}", styles['Normal']))
        elements.append(Paragraph(f"Date: {report.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Analysis Content
        analysis = report.get_analysis()
        if analysis:
            elements.append(Paragraph("Executive Summary", styles['Heading2']))
            elements.append(Paragraph(analysis.get('summary', 'No summary available.'), styles['Normal']))
            elements.append(Spacer(1, 12))
            
            abnormal = analysis.get('abnormal_values', [])
            if abnormal:
                elements.append(Paragraph("Abnormal Values Detected", styles['Heading2']))
                data = [['Metric', 'Value', 'Range', 'Status']]
                for a in abnormal:
                    data.append([str(a.get('metric', '')), str(a.get('value', '')), str(a.get('range', '')), str(a.get('status', ''))])
                
                t = Table(data, colWidths=[150, 100, 100, 100])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 12),
                    ('BACKGROUND', (0,1), (-1,-1), colors.aliceblue),
                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                ]))
                elements.append(t)
                elements.append(Spacer(1, 12))
                
            recs = analysis.get('recommendations', [])
            if recs:
                elements.append(Paragraph("Recommendations", styles['Heading2']))
                for r in recs:
                    elements.append(Paragraph(f"• {r}", styles['Normal']))
        else:
            elements.append(Paragraph("No AI analysis data available for this report.", styles['Normal']))
            
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    @staticmethod
    def generate_risk_prediction_pdf(prediction):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Header
        elements.append(Paragraph(f"SymptoScan AI - {prediction.disease_type.title()} Risk Assessment", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Date: {prediction.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Details
        elements.append(Paragraph("Assessment Results", styles['Heading2']))
        elements.append(Paragraph(f"<b>Risk Score:</b> {prediction.risk_score}%", styles['Normal']))
        elements.append(Paragraph(f"<b>Risk Category:</b> {prediction.risk_category}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        result_data = prediction.get_results()
        if result_data:
            factors = result_data.get('factors', [])
            if factors:
                elements.append(Paragraph("Contributing Factors", styles['Heading3']))
                for f in factors:
                    elements.append(Paragraph(f"• {f}", styles['Normal']))
                elements.append(Spacer(1, 12))
                
            recs = result_data.get('recommendations', [])
            if recs:
                elements.append(Paragraph("Recommendations", styles['Heading3']))
                for r in recs:
                    elements.append(Paragraph(f"• {r}", styles['Normal']))
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
