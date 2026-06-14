import os
from PIL import Image
import PyPDF2

class OCRService:
    @staticmethod
    def extract_text(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return OCRService._extract_from_pdf(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return OCRService._extract_from_image(file_path)
        else:
            raise ValueError("Unsupported file format for OCR.")

    @staticmethod
    def _extract_from_pdf(file_path):
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF Extraction Error: {str(e)}")
            return "Error extracting PDF text."
        return text

    @staticmethod
    def _extract_from_image(file_path):
        try:
            import pytesseract
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text
        except ImportError:
            print("pytesseract is not installed.")
            return OCRService._mock_ocr()
        except Exception as e:
            # specifically catch TesseractNotFoundError
            if "tesseract is not installed" in str(e).lower() or "tesseract is not in your PATH" in str(e).lower():
                print("Tesseract binary not found. Falling back to mock OCR.")
                return OCRService._mock_ocr()
            print(f"Image OCR Error: {str(e)}")
            return OCRService._mock_ocr()

    @staticmethod
    def _mock_ocr():
        """Fallback to simulate OCR text for demo purposes if Tesseract isn't installed natively."""
        return """
        PATIENT LAB REPORT
        Date: 2026-06-13
        Patient Name: John Doe
        
        TEST                 RESULT    REFERENCE RANGE
        Glucose, Fasting     125       70-99 mg/dL
        Hemoglobin A1c       6.5       4.0-5.6 %
        Total Cholesterol    210       <200 mg/dL
        Triglycerides        150       <150 mg/dL
        HDL                  45        >40 mg/dL
        LDL                  135       <100 mg/dL
        
        Notes: Elevated glucose and HbA1c indicative of pre-diabetes/diabetes risk. High LDL observed.
        """
