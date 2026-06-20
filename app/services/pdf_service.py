import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    BaseDocTemplate, PageTemplate, Frame, PageBreak, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.barcode import qr
from xml.sax.saxutils import escape

# Premium Medical Color Palette
BRAND_BLUE = colors.HexColor("#0f172a")     # Very Dark Blue/Slate
BRAND_PRIMARY = colors.HexColor("#2563eb")  # Vibrant Blue
BRAND_EMERALD = colors.HexColor("#059669")  # Health emerald
LIGHT_BLUE = colors.HexColor("#f0fdfa")     # Teal 50
LIGHT_EMERALD = colors.HexColor("#ecfdf5")
TEXT_DARK = colors.HexColor("#1e293b")
TEXT_MUTED = colors.HexColor("#64748b")
RED_FLAG = colors.HexColor("#dc2626")
LIGHT_RED = colors.HexColor("#fef2f2")
WHITE = colors.white
OFF_WHITE = colors.HexColor("#f8fafc")
BORDER_GRAY = colors.HexColor("#e2e8f0")
AMBER = colors.HexColor("#d97706")
LIGHT_AMBER = colors.HexColor("#fffbeb")

class RiskGauge(Flowable):
    def __init__(self, score, risk_level, width=200, height=140):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.score = score
        self.risk_level = risk_level
        
    def draw(self):
        canvas = self.canv
        cx, cy = self.width / 2.0, 30
        r = 75
        
        # Background arc
        canvas.setStrokeColor(BORDER_GRAY)
        canvas.setLineWidth(14)
        canvas.setLineCap(1) # Round caps
        canvas.arc(cx - r, cy - r, cx + r, cy + r, 0, 180)
        
        # Foreground arc
        if self.score >= 80: color = RED_FLAG
        elif self.score >= 40: color = AMBER
        else: color = BRAND_EMERALD
        
        canvas.setStrokeColor(color)
        angle = 180 * (self.score / 100.0)
        start_angle = 180 - angle
        canvas.arc(cx - r, cy - r, cx + r, cy + r, start_angle, angle)
        
        # Score Text
        canvas.setFillColor(TEXT_DARK)
        canvas.setFont("Helvetica-Bold", 38)
        canvas.drawCentredString(cx, cy + 15, str(self.score))
        
        # Out of 100
        canvas.setFillColor(TEXT_MUTED)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(cx, cy + 2, "RISK SCORE / 100")
        
        # Badge
        badge_w, badge_h = 100, 22
        canvas.setFillColor(color)
        canvas.roundRect(cx - badge_w/2.0, cy + 55, badge_w, badge_h, 11, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(cx, cy + 62, f"{self.risk_level.upper()} RISK")

class DiseaseChart(Flowable):
    def __init__(self, conditions, width=280, height=None):
        Flowable.__init__(self)
        self.width = width
        self.conditions = conditions
        self.bar_height = 28
        self.spacing = 16
        self.height = len(conditions) * (self.bar_height + self.spacing)
        
    def draw(self):
        canvas = self.canv
        y = self.height - self.bar_height
        
        for c in self.conditions:
            name = c.get('name', 'Unknown')
            conf = float(c.get('confidence_score') or c.get('match_percentage') or 0)
            
            if conf > 80: color = RED_FLAG
            elif conf > 50: color = AMBER
            else: color = BRAND_PRIMARY
            
            # Card Background
            canvas.setFillColor(WHITE)
            canvas.setStrokeColor(BORDER_GRAY)
            canvas.setLineWidth(1)
            canvas.roundRect(0, y-10, self.width, 38, 6, fill=1, stroke=1)
            
            # Text
            canvas.setFillColor(TEXT_DARK)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(10, y + 10, name[:35] + ("..." if len(name)>35 else ""))
            
            # Badge
            canvas.setFillColor(OFF_WHITE)
            canvas.roundRect(self.width - 70, y+8, 60, 16, 8, fill=1, stroke=0)
            canvas.setFillColor(TEXT_MUTED)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawCentredString(self.width - 40, y + 13, f"{conf}% Match")
            
            # Background bar
            bar_y = y - 2
            canvas.setFillColor(BORDER_GRAY)
            canvas.roundRect(10, bar_y, self.width - 20, 4, 2, fill=1, stroke=0)
            
            # Fill bar
            fill_w = (conf / 100.0) * (self.width - 20)
            if fill_w > 0:
                canvas.setFillColor(color)
                canvas.roundRect(10, bar_y, fill_w, 4, 2, fill=1, stroke=0)
                
            y -= (self.bar_height + self.spacing)

class SectionHeader(Flowable):
    def __init__(self, text, icon="■", color=BRAND_PRIMARY, width=500):
        Flowable.__init__(self)
        self.width = width
        self.height = 30
        self.text = text
        self.color = color
        self.icon = icon

    def draw(self):
        canvas = self.canv
        # Line
        canvas.setStrokeColor(BORDER_GRAY)
        canvas.setLineWidth(1)
        canvas.line(0, 5, self.width, 5)
        
        # Box
        canvas.setFillColor(self.color)
        canvas.roundRect(0, 5, 12, 12, 2, fill=1, stroke=0)
        
        canvas.setFillColor(TEXT_DARK)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(20, 7, self.text)

class PDFService:
    @staticmethod
    def _create_progress_bar(percentage, color, width=300, height=14):
        d = Drawing(width, height)
        d.add(Rect(0, 0, width, height, rx=7, ry=7, fillColor=BORDER_GRAY, strokeColor=None))
        fill_width = (percentage / 100.0) * width
        if fill_width > 0:
            d.add(Rect(0, 0, fill_width, height, rx=7, ry=7, fillColor=color, strokeColor=None))
        return d

    @staticmethod
    def _create_card(title, content_elements, bg_color=OFF_WHITE, border_color=BRAND_BLUE):
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CardTitle',
            parent=styles['Heading3'],
            textColor=border_color,
            fontSize=11,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            textTransform='uppercase'
        )
        cell_content = [Paragraph(title, title_style)] + content_elements
        t = Table([[cell_content]], colWidths=[500])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        return t

    @staticmethod
    def _get_base_styles():
        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle('Norm', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=TEXT_DARK, leading=14)
        bold_style = ParagraphStyle('BoldNorm', parent=normal_style, fontName='Helvetica-Bold')
        h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=BRAND_BLUE, spaceAfter=10, spaceBefore=10)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=BRAND_BLUE, spaceAfter=8, spaceBefore=8)
        list_style = ParagraphStyle('ListStyle', parent=normal_style, leftIndent=15, spaceAfter=6)
        return normal_style, bold_style, h1_style, h2_style, list_style

    @staticmethod
    def _draw_header_footer(canvas, doc, assessment_id, date_str):
        canvas.saveState()
        
        # Premium Header Band
        canvas.setFillColor(BRAND_BLUE)
        canvas.rect(0, letter[1] - 0.5*inch, letter[0], 0.5*inch, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(0.5*inch, letter[1] - 0.35*inch, "SymptoScan AI")
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(letter[0] - 0.5*inch, letter[1] - 0.35*inch, "Medical Intelligence Report")
        
        # Footer
        canvas.setStrokeColor(BORDER_GRAY)
        canvas.setLineWidth(1)
        canvas.line(0.5*inch, 1*inch, letter[0] - 0.5*inch, 1*inch)
        
        canvas.setFillColor(TEXT_MUTED)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(0.5*inch, 0.7*inch, "CONFIDENTIAL & PRELIMINARY")
        
        canvas.setFont("Helvetica", 7)
        disclaimer = "This report is generated by AI and does not constitute a medical diagnosis. Always consult a licensed healthcare professional."
        canvas.drawString(0.5*inch, 0.55*inch, disclaimer)
        
        canvas.drawRightString(letter[0] - 0.5*inch, 0.7*inch, f"ID: {assessment_id}  |  Date: {date_str}")
        canvas.drawRightString(letter[0] - 0.5*inch, 0.55*inch, f"Page {doc.page}")
        
        canvas.restoreState()
        
    @staticmethod
    def _draw_cover_page(canvas, doc, assessment_id, date_str):
        canvas.saveState()
        # Premium Cover Header with gradient simulation
        canvas.setFillColor(BRAND_BLUE)
        canvas.rect(0, letter[1] - 2.5*inch, letter[0], 2.5*inch, fill=1, stroke=0)
        
        # Subtle pattern/shapes
        canvas.setFillColor(colors.HexColor("#1e293b"))
        canvas.setFillAlpha(0.5)
        canvas.circle(letter[0], letter[1], 150, fill=1, stroke=0)
        canvas.circle(letter[0]-100, letter[1]-200, 50, fill=1, stroke=0)
        canvas.setFillAlpha(1.0)
        
        # Titles
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 34)
        canvas.drawString(0.5*inch, letter[1] - 1.2*inch, "Health Assessment Report")
        
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(0.5*inch, letter[1] - 1.5*inch, "POWERED BY SYMPTOSCAN CLINICAL INTELLIGENCE")
        
        # Badge
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.roundRect(0.5*inch, letter[1] - 2.2*inch, 120, 24, 12, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(0.5*inch + 60, letter[1] - 2.05*inch, f"ID: {assessment_id}")
        
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawString(0.5*inch + 135, letter[1] - 2.05*inch, f"Generated: {date_str}")
        
        # Footer
        PDFService._draw_header_footer(canvas, doc, assessment_id, date_str)
        canvas.restoreState()

    @staticmethod
    def generate_assessment_pdf(assessment):
        buffer = io.BytesIO()
        
        doc = BaseDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.8*inch,
            bottomMargin=1.2*inch
        )
        
        date_str = assessment.created_at.strftime('%b %d, %Y %H:%M')
        
        frame_cover = Frame(0.5*inch, 1.2*inch, letter[0]-1*inch, letter[1]-3.7*inch, id='cover', showBoundary=0)
        frame_normal = Frame(0.5*inch, 1.2*inch, letter[0]-1*inch, letter[1]-1.7*inch, id='normal', showBoundary=0)
        
        cover_template = PageTemplate(id='Cover', frames=[frame_cover], onPage=lambda c, d: PDFService._draw_cover_page(c, d, assessment.id, date_str))
        normal_template = PageTemplate(id='Normal', frames=[frame_normal], onPage=lambda c, d: PDFService._draw_header_footer(c, d, assessment.id, date_str))
        doc.addPageTemplates([cover_template, normal_template])

        normal_style, bold_style, h1_style, h2_style, list_style = PDFService._get_base_styles()
        elements = []
        
        # --- PAGE 1: EXECUTIVE DASHBOARD ---
        
        # 1. Patient Summary Grid
        elements.append(SectionHeader("Patient Profile", color=BRAND_PRIMARY))
        
        grid_data = [
            [Paragraph("<b>Age</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)), 
             Paragraph("<b>Gender</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)),
             Paragraph("<b>Duration</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)),
             Paragraph("<b>Severity</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9))],
            [Paragraph(str(assessment.age), bold_style), 
             Paragraph(escape(assessment.gender.title()), bold_style),
             Paragraph(escape(assessment.duration), bold_style),
             Paragraph(f"{assessment.severity} / 10", bold_style)]
        ]
        
        grid_table = Table(grid_data, colWidths=[125, 125, 125, 125])
        grid_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), OFF_WHITE),
            ('BOX', (0,0), (-1,-1), 1, BORDER_GRAY),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_GRAY),
            ('PADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(grid_table)
        elements.append(Spacer(1, 15))
        
        # 2. Symptoms Box
        symp_content = [
            Paragraph(f"<b>Reported Symptoms:</b> {escape(assessment.symptoms)}", normal_style),
            Spacer(1, 6),
            Paragraph(f"<b>Risk Factors / History:</b> {escape(assessment.medical_history) if assessment.medical_history else 'None reported'}", normal_style)
        ]
        elements.append(PDFService._create_card("Clinical Inputs", symp_content, bg_color=WHITE, border_color=BORDER_GRAY))
        elements.append(Spacer(1, 25))
        
        # 3. Two-Column Layout for Gauge and Conditions
        elements.append(SectionHeader("Assessment Results", color=BRAND_EMERALD))
        
        # Calculate derived score
        conditions = assessment.get_conditions()
        max_conf = 0
        if conditions:
            max_conf = float(conditions[0].get('confidence_score') or conditions[0].get('match_percentage') or 0)
        
        risk = assessment.risk_level.lower()
        if risk == 'low': base_score = 20 + (max_conf * 0.2)
        elif risk in ['high', 'severe']: base_score = 80 + (max_conf * 0.2)
        else: base_score = 40 + (max_conf * 0.4)
        score = min(100, int(round(base_score)))
        
        gauge = RiskGauge(score, assessment.risk_level)
        chart = DiseaseChart(conditions[:4]) # Show top 4
        
        two_col_data = [
            [gauge, chart]
        ]
        two_col_table = Table(two_col_data, colWidths=[200, 300])
        two_col_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (0,0), 0),
            ('RIGHTPADDING', (1,0), (1,0), 0),
        ]))
        elements.append(two_col_table)
        
        elements.append(PageBreak())
        
        # --- PAGE 2: ACTION PLAN ---
        
        # 1. Clinical Insights
        elements.append(SectionHeader("Clinical Insights", color=BRAND_PRIMARY))
        insight_content = [Paragraph(escape(assessment.explanation), normal_style)]
        elements.append(PDFService._create_card("AI Reasoning", insight_content, bg_color=LIGHT_BLUE, border_color=BRAND_PRIMARY))
        elements.append(Spacer(1, 20))
        
        # 2. Red Flags
        flags = assessment.get_red_flag_warnings()
        if flags:
            flag_content = []
            for f in flags:
                flag_content.append(Paragraph(f"<b>• {escape(f)}</b>", ParagraphStyle('rf', parent=normal_style, textColor=RED_FLAG)))
                flag_content.append(Spacer(1, 4))
            elements.append(PDFService._create_card("CRITICAL RED FLAG WARNINGS", flag_content, bg_color=LIGHT_RED, border_color=RED_FLAG))
            elements.append(Spacer(1, 20))
            
        # 3. Categorized Action Plan
        recs = assessment.get_recommendations()
        if recs:
            elements.append(SectionHeader("Personalized Action Plan", color=BRAND_EMERALD))
            
            consult_keywords = ['doctor', 'physician', 'hospital', 'emergency', 'medical attention', 'consult', 'evaluation', 'test', 'scan']
            consults = []
            home_care = []
            
            for r in recs:
                if any(k in r.lower() for k in consult_keywords):
                    consults.append(r)
                else:
                    home_care.append(r)
            
            if consults:
                c_content = [Paragraph(f"✓ {escape(r)}", normal_style) for r in consults]
                elements.append(PDFService._create_card("Professional Medical Care", c_content, bg_color=LIGHT_AMBER, border_color=AMBER))
                elements.append(Spacer(1, 15))
                
            if home_care:
                h_content = [Paragraph(f"✓ {escape(r)}", normal_style) for r in home_care]
                elements.append(PDFService._create_card("Home Care & Preventive Lifestyle", h_content, bg_color=LIGHT_EMERALD, border_color=BRAND_EMERALD))
                elements.append(Spacer(1, 20))
                
        # 4. Follow-up
        questions = assessment.get_follow_up_questions()
        if questions:
            elements.append(SectionHeader("Doctor Consultation Guide", color=TEXT_MUTED))
            q_content = [Paragraph(f"• {escape(q)}", normal_style) for q in questions]
            elements.append(PDFService._create_card("Questions to ask your Healthcare Provider", q_content, bg_color=WHITE, border_color=BORDER_GRAY))
            elements.append(Spacer(1, 25))
            
        # 5. Verification QR Code
        qr_code = qr.QrCodeWidget(f"https://symptoscan.ai/verify/{assessment.id}")
        qr_code.barLevel = 'Q'
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(60, 60, transform=[60./width,0,0,60./height,0,0])
        d.add(qr_code)
        
        qr_table = Table([[d, Paragraph("<b>Scan to verify authenticity</b><br/>This code links to the digital copy of this report in the SymptoScan portal.", ParagraphStyle('qr', parent=normal_style, textColor=TEXT_MUTED, fontSize=8))]], colWidths=[70, 400])
        qr_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(qr_table)
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    @staticmethod
    def generate_medical_report_pdf(report):
        # ... keeping existing simple layout for medical OCR reports for now
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        date_str = report.created_at.strftime('%Y-%m-%d')
        frame_normal = Frame(inch, inch, letter[0]-2*inch, letter[1]-2*inch, id='normal')
        normal_template = PageTemplate(id='Normal', frames=[frame_normal], onPage=lambda c, d: PDFService._draw_header_footer(c, d, report.id, date_str))
        doc.addPageTemplates([normal_template])
        elements = [Paragraph(f"Medical Report Analysis: {escape(report.filename)}", getSampleStyleSheet()['Heading1'])]
        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def generate_risk_prediction_pdf(prediction):
        buffer = io.BytesIO()
        doc = BaseDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.8*inch,
            bottomMargin=1.2*inch
        )
        date_str = prediction.created_at.strftime('%b %d, %Y %H:%M')
        
        frame_cover = Frame(0.5*inch, 1.2*inch, letter[0]-1*inch, letter[1]-3.7*inch, id='cover', showBoundary=0)
        frame_normal = Frame(0.5*inch, 1.2*inch, letter[0]-1*inch, letter[1]-1.7*inch, id='normal', showBoundary=0)
        
        cover_template = PageTemplate(id='Cover', frames=[frame_cover], onPage=lambda c, d: PDFService._draw_cover_page(c, d, prediction.id, date_str))
        normal_template = PageTemplate(id='Normal', frames=[frame_normal], onPage=lambda c, d: PDFService._draw_header_footer(c, d, prediction.id, date_str))
        doc.addPageTemplates([cover_template, normal_template])
        
        normal_style, bold_style, h1_style, h2_style, list_style = PDFService._get_base_styles()
        elements = []
        
        if prediction.disease_type == 'comprehensive':
            inputs = prediction.get_inputs()
            detailed = inputs.get('_detailed_results', {})
            factors = prediction.get_factors()
            recs = prediction.get_recommendations()
            
            elements.append(SectionHeader("Patient Biometrics", color=BRAND_PRIMARY))
            
            grid_data = [
                [Paragraph("<b>Age</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)), 
                 Paragraph("<b>Gender</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)),
                 Paragraph("<b>BMI</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9)),
                 Paragraph("<b>Blood Pressure</b>", ParagraphStyle('m', parent=normal_style, textColor=TEXT_MUTED, fontSize=9))],
                [Paragraph(str(inputs.get('age', 'N/A')), bold_style), 
                 Paragraph("N/A", bold_style),
                 Paragraph(str(inputs.get('bmi', 'N/A')), bold_style),
                 Paragraph(f"{inputs.get('systolic_bp', 'N/A')}/{inputs.get('blood_pressure', 'N/A')}", bold_style)]
            ]
            
            grid_table = Table(grid_data, colWidths=[125, 125, 125, 125])
            grid_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), OFF_WHITE),
                ('BOX', (0,0), (-1,-1), 1, BORDER_GRAY),
                ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_GRAY),
                ('PADDING', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(grid_table)
            elements.append(Spacer(1, 20))
            
            elements.append(SectionHeader("Overall Health Score", color=BRAND_EMERALD))
            gauge = RiskGauge(prediction.risk_score, prediction.risk_category)
            
            # Format conditions for DiseaseChart
            conditions = []
            for d_name, d_res in detailed.items():
                if 'risk_score' in d_res:
                    conditions.append({
                        'name': f"{d_name.capitalize()} Disease Risk",
                        'confidence_score': d_res['risk_score']
                    })
            conditions.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            chart = DiseaseChart(conditions)
            
            two_col_data = [[gauge, chart]]
            two_col_table = Table(two_col_data, colWidths=[200, 300])
            two_col_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (0,0), 0),
                ('RIGHTPADDING', (1,0), (1,0), 0),
            ]))
            elements.append(two_col_table)
            
            elements.append(PageBreak())
            
            elements.append(SectionHeader("Identified Risk Factors", color=AMBER))
            f_content = [Paragraph(f"• {escape(f)}", normal_style) for f in factors] if factors else [Paragraph("None identified.", normal_style)]
            elements.append(PDFService._create_card("Clinical Observations", f_content, bg_color=LIGHT_AMBER, border_color=AMBER))
            elements.append(Spacer(1, 20))
            
            elements.append(SectionHeader("Preventive Care Plan", color=BRAND_EMERALD))
            r_content = [Paragraph(f"✓ {escape(r)}", normal_style) for r in recs] if recs else [Paragraph("No specific recommendations.", normal_style)]
            elements.append(PDFService._create_card("Actionable Steps", r_content, bg_color=LIGHT_EMERALD, border_color=BRAND_EMERALD))
            
        else:
            # Fallback for single disease prediction
            elements.append(Paragraph(f"Risk Prediction: {escape(prediction.disease_type.title())}", h1_style))
            elements.append(Paragraph(f"Risk Score: {prediction.risk_score}% ({prediction.risk_category})", bold_style))
            
        doc.build(elements)
        return buffer.getvalue()
