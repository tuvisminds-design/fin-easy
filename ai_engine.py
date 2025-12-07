"""
Fin Easy - AI Processing Engine
Uses Ollama for transaction categorization, account assignment, and anomaly detection
"""

import ollama
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class AIEngine:
    """AI Engine using Ollama for accounting automation"""
    
    def __init__(self, model_name=None, base_url=None):
        self.model_name = model_name or os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.client = ollama.Client(host=self.base_url)
    
    def categorize_transaction(self, description: str, amount: float, date: str = None) -> Dict:
        """
        Categorize a transaction using AI
        Returns: {'category': str, 'account_type': str, 'account_code': str, 'confidence': float}
        """
        prompt = f"""Analyze this financial transaction and categorize it:

Transaction Description: {description}
Amount: {amount}
Date: {date or 'Not provided'}

Determine:
1. Transaction category (e.g., "Office Supplies", "Utilities", "Sales Revenue", "Bank Fee")
2. Account type (Asset, Liability, Equity, Revenue, Expense)
3. Suggested account code (from standard chart of accounts)

Respond in JSON format:
{{
    "category": "category name",
    "account_type": "Asset|Liability|Equity|Revenue|Expense",
    "account_code": "suggested code (e.g., 5100, 4000)",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                format='json'
            )
            
            result_text = response.get('response', '{}')
            # Extract JSON from response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"⚠️  AI categorization error: {e}")
            # Fallback to basic categorization
            return self._fallback_categorization(description, amount)
    
    def _fallback_categorization(self, description: str, amount: float) -> Dict:
        """Fallback categorization using keyword matching"""
        description_lower = description.lower()
        
        # Revenue indicators
        if any(word in description_lower for word in ['sale', 'revenue', 'income', 'payment received']):
            return {
                'category': 'Sales Revenue',
                'account_type': 'Revenue',
                'account_code': '4000',
                'confidence': 0.6,
                'reasoning': 'Keyword-based fallback'
            }
        
        # Expense indicators
        expense_keywords = {
            'rent': ('5300', 'Rent Expense'),
            'utility': ('5400', 'Utilities Expense'),
            'salary': ('5200', 'Salaries & Wages'),
            'marketing': ('5500', 'Marketing Expense'),
            'office': ('5100', 'Operating Expenses'),
            'supply': ('5100', 'Operating Expenses'),
        }
        
        for keyword, (code, category) in expense_keywords.items():
            if keyword in description_lower:
                return {
                    'category': category,
                    'account_type': 'Expense',
                    'account_code': code,
                    'confidence': 0.6,
                    'reasoning': 'Keyword-based fallback'
                }
        
        # Default
        return {
            'category': 'Uncategorized',
            'account_type': 'Expense',
            'account_code': '5100',
            'confidence': 0.3,
            'reasoning': 'Default fallback'
        }
    
    def detect_anomaly(self, transaction: Dict, historical_data: List[Dict] = None) -> Dict:
        """
        Detect anomalies in transactions
        Returns: {'is_anomaly': bool, 'anomaly_type': str, 'severity': str, 'reason': str}
        """
        prompt = f"""Analyze this transaction for anomalies:

Transaction: {json.dumps(transaction, indent=2)}
Historical Context: {len(historical_data) if historical_data else 0} similar transactions

Check for:
1. Unusual amount (compared to typical transactions)
2. Duplicate transactions
3. Suspicious patterns
4. Missing or incomplete information

Respond in JSON:
{{
    "is_anomaly": true/false,
    "anomaly_type": "amount|duplicate|pattern|missing",
    "severity": "low|medium|high",
    "reason": "explanation"
}}"""

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                format='json'
            )
            
            result_text = response.get('response', '{}')
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"⚠️  AI anomaly detection error: {e}")
            return {
                'is_anomaly': False,
                'anomaly_type': None,
                'severity': 'low',
                'reason': 'Error in analysis'
            }
    
    def extract_transaction_details(self, text: str) -> Dict:
        """
        Extract transaction details from unstructured text (e.g., from OCR)
        Returns: {'date': str, 'amount': float, 'description': str, 'vendor': str, etc.}
        """
        prompt = f"""Extract structured financial transaction data from this text:

{text}

Extract:
- Transaction date
- Amount (with currency if mentioned)
- Description/purpose
- Vendor/payee name
- Transaction type (payment, receipt, transfer, etc.)
- Account affected

Respond in JSON:
{{
    "date": "YYYY-MM-DD or null",
    "amount": number or null,
    "description": "string",
    "vendor": "string or null",
    "transaction_type": "payment|receipt|transfer|other",
    "account_hint": "suggested account"
}}"""

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                format='json'
            )
            
            result_text = response.get('response', '{}')
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"⚠️  AI extraction error: {e}")
            return {
                'date': None,
                'amount': None,
                'description': text[:200],
                'vendor': None,
                'transaction_type': 'other',
                'account_hint': None
            }
    
    def validate_account_balance(self, account_code: str, balance: float, transactions: List[Dict]) -> Dict:
        """
        Validate account balance using AI
        Returns: {'is_valid': bool, 'issues': List[str], 'recommendations': List[str]}
        """
        prompt = f"""Validate this account balance:

Account Code: {account_code}
Current Balance: {balance}
Recent Transactions: {len(transactions)} transactions

Check for:
1. Balance accuracy (does it match expected calculations?)
2. Unusual balance changes
3. Missing transactions
4. Accounting rule violations

Respond in JSON:
{{
    "is_valid": true/false,
    "issues": ["list of issues"],
    "recommendations": ["list of recommendations"]
}}"""

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                format='json'
            )
            
            result_text = response.get('response', '{}')
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            return result
        except Exception as e:
            print(f"⚠️  AI validation error: {e}")
            return {
                'is_valid': True,
                'issues': [],
                'recommendations': []
            }


