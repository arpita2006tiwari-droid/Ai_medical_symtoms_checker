import os
from io import BytesIO
from pypdf import PdfReader
from fastapi import HTTPException

class ReportService:
    def extract_text(self, file_path: str, content_type: str) -> str:
        """
        Extracts text from medical reports. Supports digital PDFs.
        Returns a string of extracted text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")

        try:
            if content_type == "application/pdf":
                return self._extract_pdf_text(file_path)
            elif content_type in ["image/jpeg", "image/png", "image/webp"]:
                # We do not have local OCR setup (Tesseract), so we state it clearly
                return "[Image uploaded. Text extraction via OCR is not implemented natively. Please request AI summary to read the image.]"
            else:
                return "[Unsupported format for text extraction]"
        except Exception as e:
            print(f"Extraction error: {e}")
            return f"[Failed to extract text: {str(e)}]"

    def _extract_pdf_text(self, file_path: str) -> str:
        text_parts = []
        try:
            reader = PdfReader(file_path)
            
            if reader.is_encrypted:
                return "[Error: PDF is encrypted]"
                
            num_pages = len(reader.pages)
            if num_pages > 50:
                return "[Error: PDF exceeds maximum page limit of 50]"
                
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i+1} ---\n{page_text.strip()}")
            
            full_text = "\n\n".join(text_parts).strip()
            
            if not full_text:
                return "[No readable text found in PDF. It might be a scanned image without OCR.]"
                
            if len(full_text) > 100000:
                return full_text[:100000] + "\n\n[Text truncated due to length limits]"
                
            return full_text
            
        except Exception as e:
            raise Exception(f"PDF Parsing failed: {str(e)}")

report_service = ReportService()
