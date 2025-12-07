"""
Fin Easy - Data Ingestion Layer
Handles importing transactions from various sources (bank, CSV, OCR, etc.)
"""

import pandas as pd
import csv
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from ocr_processor import OCRProcessor
from database import RawTransaction, Database
import os


class DataIngestion:
    """Data ingestion from multiple sources"""
    
    def __init__(self, db: Database, ocr_processor: Optional[OCRProcessor] = None):
        self.db = db
        self.ocr_processor = ocr_processor or OCRProcessor()
    
    def import_from_csv(self, csv_path: str, source: str = 'bank') -> List[Dict]:
        """
        Import transactions from CSV file
        Expected columns: date, amount, description (or similar)
        """
        transactions = []
        
        try:
            df = pd.read_csv(csv_path)
            
            # Normalize column names (case-insensitive)
            df.columns = df.columns.str.lower().str.strip()
            
            # Map common column names
            date_col = None
            amount_col = None
            desc_col = None
            
            for col in df.columns:
                if 'date' in col:
                    date_col = col
                elif 'amount' in col or 'amt' in col:
                    amount_col = col
                elif 'description' in col or 'desc' in col or 'memo' in col or 'details' in col:
                    desc_col = col
            
            if not date_col or not amount_col:
                raise ValueError("CSV must contain 'date' and 'amount' columns")
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_str = str(row[date_col])
                    if pd.isna(row[date_col]):
                        continue
                    
                    # Try different date formats
                    date_obj = None
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                    
                    if not date_obj:
                        continue
                    
                    # Parse amount
                    amount = float(row[amount_col])
                    
                    # Get description
                    description = str(row[desc_col]) if desc_col and not pd.isna(row[desc_col]) else ''
                    
                    transactions.append({
                        'source': source,
                        'transaction_date': date_obj,
                        'amount': amount,
                        'description': description,
                        'raw_data': row.to_dict()
                    })
                except Exception as e:
                    print(f"⚠️  Error parsing row: {e}")
                    continue
            
            print(f"✅ Imported {len(transactions)} transactions from {csv_path}")
            return transactions
        
        except Exception as e:
            print(f"❌ Error importing CSV {csv_path}: {e}")
            return []
    
    def import_from_excel(self, excel_path: str, source: str = 'bank', sheet_name: int = 0) -> List[Dict]:
        """Import transactions from Excel file"""
        transactions = []
        
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Same normalization as CSV
            df.columns = df.columns.str.lower().str.strip()
            
            date_col = None
            amount_col = None
            desc_col = None
            
            for col in df.columns:
                if 'date' in col:
                    date_col = col
                elif 'amount' in col or 'amt' in col:
                    amount_col = col
                elif 'description' in col or 'desc' in col or 'memo' in col:
                    desc_col = col
            
            if not date_col or not amount_col:
                raise ValueError("Excel must contain 'date' and 'amount' columns")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row[date_col])
                    if pd.isna(row[date_col]):
                        continue
                    
                    date_obj = None
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                    
                    if not date_obj:
                        continue
                    
                    amount = float(row[amount_col])
                    description = str(row[desc_col]) if desc_col and not pd.isna(row[desc_col]) else ''
                    
                    transactions.append({
                        'source': source,
                        'transaction_date': date_obj,
                        'amount': amount,
                        'description': description,
                        'raw_data': row.to_dict()
                    })
                except Exception as e:
                    continue
            
            print(f"✅ Imported {len(transactions)} transactions from {excel_path}")
            return transactions
        
        except Exception as e:
            print(f"❌ Error importing Excel {excel_path}: {e}")
            return []
    
    def import_from_image(self, image_path: str, source: str = 'receipt') -> Dict:
        """
        Import transaction from image using OCR
        Returns: Transaction data extracted from image
        """
        try:
            # Process image with OCR
            ocr_result = self.ocr_processor.process_document(image_path, document_type='image')
            
            if not ocr_result['success']:
                return None
            
            # Extract financial data
            financial_data = ocr_result['financial_data']
            extracted_text = ocr_result['extracted_text']
            
            # Try to extract key information
            amount = None
            if financial_data['amounts']:
                # Get the largest amount (likely the total)
                amounts_cleaned = []
                for amt_str in financial_data['amounts']:
                    # Remove currency symbols and commas
                    amt_clean = amt_str.replace('$', '').replace(',', '').replace('USD', '').strip()
                    try:
                        amounts_cleaned.append(float(amt_clean))
                    except:
                        continue
                
                if amounts_cleaned:
                    amount = max(amounts_cleaned)  # Usually the total is the largest
            
            # Extract date
            date_obj = None
            if financial_data['dates']:
                for date_str in financial_data['dates']:
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%B %d, %Y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                    if date_obj:
                        break
            
            # Extract vendor/description
            vendor = financial_data['vendor_names'][0] if financial_data['vendor_names'] else None
            description = vendor or extracted_text[:200]  # Use vendor or first 200 chars
            
            transaction = {
                'source': source,
                'transaction_date': date_obj or datetime.now().date(),
                'amount': amount,
                'description': description,
                'raw_data': {
                    'ocr_text': extracted_text,
                    'financial_data': financial_data,
                    'file_path': image_path
                }
            }
            
            print(f"✅ Extracted transaction from image: {image_path}")
            return transaction
        
        except Exception as e:
            print(f"❌ Error processing image {image_path}: {e}")
            return None
    
    def import_from_pdf(self, pdf_path: str, source: str = 'invoice') -> List[Dict]:
        """
        Import transactions from PDF (invoices, statements)
        """
        transactions = []
        
        try:
            # Process PDF with OCR
            ocr_result = self.ocr_processor.process_document(pdf_path, document_type='pdf')
            
            if not ocr_result['success']:
                return []
            
            financial_data = ocr_result['financial_data']
            extracted_text = ocr_result['extracted_text']
            
            # Extract invoice data
            amount = None
            if financial_data['amounts']:
                amounts_cleaned = []
                for amt_str in financial_data['amounts']:
                    amt_clean = amt_str.replace('$', '').replace(',', '').replace('USD', '').strip()
                    try:
                        amounts_cleaned.append(float(amt_clean))
                    except:
                        continue
                
                if amounts_cleaned:
                    amount = max(amounts_cleaned)
            
            date_obj = None
            if financial_data['dates']:
                for date_str in financial_data['dates']:
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                    if date_obj:
                        break
            
            vendor = financial_data['vendor_names'][0] if financial_data['vendor_names'] else None
            invoice_num = financial_data['invoice_numbers'][0] if financial_data['invoice_numbers'] else None
            
            description = f"Invoice {invoice_num} - {vendor}" if invoice_num and vendor else (vendor or extracted_text[:200])
            
            if amount:
                transactions.append({
                    'source': source,
                    'transaction_date': date_obj or datetime.now().date(),
                    'amount': amount,
                    'description': description,
                    'raw_data': {
                        'ocr_text': extracted_text,
                        'financial_data': financial_data,
                        'invoice_number': invoice_num,
                        'file_path': pdf_path
                    }
                })
            
            print(f"✅ Extracted {len(transactions)} transaction(s) from PDF: {pdf_path}")
            return transactions
        
        except Exception as e:
            print(f"❌ Error processing PDF {pdf_path}: {e}")
            return []
    
    def save_raw_transactions(self, transactions: List[Dict]) -> List[RawTransaction]:
        """Save raw transactions to database"""
        session = self.db.get_session()
        saved_transactions = []
        
        try:
            for trans_data in transactions:
                raw_trans = RawTransaction(
                    source=trans_data['source'],
                    transaction_date=trans_data['transaction_date'],
                    amount=trans_data['amount'],
                    description=trans_data.get('description', ''),
                    processed=False
                )
                session.add(raw_trans)
                saved_transactions.append(raw_trans)
            
            session.commit()
            print(f"✅ Saved {len(saved_transactions)} raw transactions to database")
            return saved_transactions
        
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving transactions: {e}")
            return []
        
        finally:
            session.close()

