"""
Fin Easy - OCR Processor for Image Analysis
Handles OCR extraction from images, PDFs, and scanned documents
"""

import pytesseract
from PIL import Image
import pdfplumber
import cv2
import numpy as np
from typing import Dict, List, Optional
import os
import re
from datetime import datetime


class OCRProcessor:
    """OCR processor for extracting text from images and PDFs"""
    
    def __init__(self, tesseract_cmd=None):
        """
        Initialize OCR processor
        tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt':  # Windows
            # Common Windows installation path
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def extract_text_from_image(self, image_path: str, preprocess: bool = True) -> str:
        """
        Extract text from an image file
        """
        try:
            if preprocess:
                processed_img = self.preprocess_image(image_path)
                # Convert numpy array to PIL Image
                pil_image = Image.fromarray(processed_img)
            else:
                pil_image = Image.open(image_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image, lang='eng')
            return text.strip()
        except Exception as e:
            print(f"❌ OCR error for {image_path}: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = True) -> Dict[str, str]:
        """
        Extract text from PDF
        Returns: {'text': str, 'pages': List[str]}
        """
        all_text = []
        pages_text = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Try to extract text directly (for text-based PDFs)
                    page_text = page.extract_text()
                    
                    # If no text found and OCR is enabled, use OCR
                    if (not page_text or len(page_text.strip()) < 10) and use_ocr:
                        # Convert PDF page to image
                        page_image = page.to_image(resolution=300)
                        pil_image = page_image.original
                        
                        # Extract text using OCR
                        page_text = pytesseract.image_to_string(pil_image, lang='eng')
                    
                    if page_text:
                        all_text.append(page_text)
                        pages_text.append(f"--- Page {page_num} ---\n{page_text}")
            
            return {
                'text': '\n\n'.join(all_text),
                'pages': pages_text,
                'total_pages': len(pages_text)
            }
        except Exception as e:
            print(f"❌ PDF extraction error for {pdf_path}: {e}")
            return {'text': '', 'pages': [], 'total_pages': 0}
    
    def extract_financial_data(self, text: str) -> Dict:
        """
        Extract structured financial data from OCR text
        Uses pattern matching to find amounts, dates, account numbers, etc.
        """
        data = {
            'amounts': [],
            'dates': [],
            'account_numbers': [],
            'vendor_names': [],
            'invoice_numbers': [],
            'raw_text': text
        }
        
        # Extract amounts (currency formats)
        amount_patterns = [
            r'\$[\d,]+\.?\d*',  # $1,234.56
            r'[\d,]+\.\d{2}',   # 1234.56
            r'USD\s*[\d,]+\.?\d*',  # USD 1234.56
            r'[\d,]+\.\d{2}\s*(?:USD|EUR|GBP)',  # 1234.56 USD
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['amounts'].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # January 1, 2024
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['dates'].extend(matches)
        
        # Extract invoice/account numbers
        invoice_patterns = [
            r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'INV[-/]?([A-Z0-9-]+)',
            r'Account\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'ACC[-/]?([A-Z0-9-]+)',
        ]
        
        for pattern in invoice_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['invoice_numbers'].extend(matches)
        
        # Extract vendor/company names (common patterns)
        vendor_patterns = [
            r'Bill\s+To:?\s*([A-Z][A-Za-z\s&,.-]+)',
            r'From:?\s*([A-Z][A-Za-z\s&,.-]+)',
            r'Vendor:?\s*([A-Z][A-Za-z\s&,.-]+)',
            r'Company:?\s*([A-Z][A-Za-z\s&,.-]+)',
        ]
        
        for pattern in vendor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['vendor_names'].extend([m.strip() for m in matches])
        
        return data
    
    def process_document(self, file_path: str, document_type: str = 'auto') -> Dict:
        """
        Process a document (image or PDF) and extract financial data
        Returns: Complete extracted data with OCR text and structured fields
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        result = {
            'file_path': file_path,
            'document_type': document_type,
            'extracted_text': '',
            'financial_data': {},
            'processing_date': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            if file_ext == '.pdf':
                # Process PDF
                pdf_result = self.extract_text_from_pdf(file_path)
                result['extracted_text'] = pdf_result['text']
                result['pages'] = pdf_result['pages']
                result['total_pages'] = pdf_result['total_pages']
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                # Process image
                result['extracted_text'] = self.extract_text_from_image(file_path)
                result['pages'] = [result['extracted_text']]
                result['total_pages'] = 1
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Extract structured financial data
            if result['extracted_text']:
                result['financial_data'] = self.extract_financial_data(result['extracted_text'])
                result['success'] = True
            else:
                result['error'] = 'No text extracted from document'
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            print(f"❌ Error processing {file_path}: {e}")
        
        return result
    
    def batch_process(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple documents in batch
        """
        results = []
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append(result)
        return results


