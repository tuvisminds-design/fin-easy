"""
Fin Easy - Moneycontrol.com Data Scraper
Scrapes public financial data from Moneycontrol for testing
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
import time
import re


class MoneyControlScraper:
    """Scraper for Moneycontrol.com financial data"""
    
    def __init__(self):
        self.base_url = "https://www.moneycontrol.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_company_financials(self, company_code: str) -> Dict:
        """
        Get financial data for a company
        company_code: Stock code (e.g., 'RELIANCE', 'TCS', 'INFY')
        """
        try:
            url = f"{self.base_url}/financials/{company_code}/balance-sheetVI/{company_code}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract balance sheet data
            financial_data = {
                'company_code': company_code,
                'scraped_date': date.today().isoformat(),
                'balance_sheet': self._extract_balance_sheet(soup),
                'income_statement': self._extract_income_statement(soup),
                'cash_flow': self._extract_cash_flow(soup)
            }
            
            return financial_data
        
        except Exception as e:
            print(f"❌ Error scraping {company_code}: {e}")
            return {}
    
    def _extract_balance_sheet(self, soup: BeautifulSoup) -> Dict:
        """Extract balance sheet data"""
        balance_sheet = {}
        
        try:
            # Look for balance sheet tables
            tables = soup.find_all('table', class_='mctable1')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        # Try to extract numeric values
                        values = []
                        for cell in cells[1:]:
                            text = cell.get_text(strip=True)
                            # Remove commas and convert to float
                            value = re.sub(r'[^\d.-]', '', text)
                            try:
                                values.append(float(value) if value else 0)
                            except:
                                values.append(0)
                        
                        if label and values:
                            balance_sheet[label] = values[0] if values else 0
        
        except Exception as e:
            print(f"⚠️  Error extracting balance sheet: {e}")
        
        return balance_sheet
    
    def _extract_income_statement(self, soup: BeautifulSoup) -> Dict:
        """Extract income statement data"""
        income_statement = {}
        
        try:
            # Similar to balance sheet extraction
            tables = soup.find_all('table', class_='mctable1')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        values = []
                        for cell in cells[1:]:
                            text = cell.get_text(strip=True)
                            value = re.sub(r'[^\d.-]', '', text)
                            try:
                                values.append(float(value) if value else 0)
                            except:
                                values.append(0)
                        
                        if label and values:
                            income_statement[label] = values[0] if values else 0
        
        except Exception as e:
            print(f"⚠️  Error extracting income statement: {e}")
        
        return income_statement
    
    def _extract_cash_flow(self, soup: BeautifulSoup) -> Dict:
        """Extract cash flow data"""
        cash_flow = {}
        
        try:
            # Similar extraction logic
            tables = soup.find_all('table', class_='mctable1')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        values = []
                        for cell in cells[1:]:
                            text = cell.get_text(strip=True)
                            value = re.sub(r'[^\d.-]', '', text)
                            try:
                                values.append(float(value) if value else 0)
                            except:
                                values.append(0)
                        
                        if label and values:
                            cash_flow[label] = values[0] if values else 0
        
        except Exception as e:
            print(f"⚠️  Error extracting cash flow: {e}")
        
        return cash_flow
    
    def create_test_transactions(self, company_code: str = 'RELIANCE') -> List[Dict]:
        """
        Create test transactions from scraped financial data
        Returns list of transactions in format suitable for Fin Easy
        """
        financial_data = self.get_company_financials(company_code)
        
        if not financial_data:
            # Return sample test data if scraping fails
            return self._get_sample_test_data()
        
        transactions = []
        
        # Convert balance sheet items to transactions
        balance_sheet = financial_data.get('balance_sheet', {})
        income_statement = financial_data.get('income_statement', {})
        
        # Create sample transactions based on financial data
        today = date.today()
        
        # Revenue transactions
        if 'Total Income' in income_statement:
            transactions.append({
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': abs(income_statement['Total Income']),
                'description': f'Revenue from {company_code} operations',
                'raw_data': {'type': 'revenue', 'source': 'income_statement'}
            })
        
        # Expense transactions
        if 'Total Expenses' in income_statement:
            transactions.append({
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': -abs(income_statement['Total Expenses']),
                'description': f'Operating expenses for {company_code}',
                'raw_data': {'type': 'expense', 'source': 'income_statement'}
            })
        
        # Asset transactions
        if 'Total Assets' in balance_sheet:
            transactions.append({
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': abs(balance_sheet['Total Assets']),
                'description': f'Total assets for {company_code}',
                'raw_data': {'type': 'asset', 'source': 'balance_sheet'}
            })
        
        # If no data extracted, return sample data
        if not transactions:
            return self._get_sample_test_data()
        
        return transactions
    
    def _get_sample_test_data(self) -> List[Dict]:
        """Generate sample test transactions"""
        today = date.today()
        
        return [
            {
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': 1000000.00,
                'description': 'Sample Revenue Transaction - Moneycontrol Test',
                'raw_data': {'type': 'revenue', 'source': 'test'}
            },
            {
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': -500000.00,
                'description': 'Sample Expense Transaction - Moneycontrol Test',
                'raw_data': {'type': 'expense', 'source': 'test'}
            },
            {
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': 250000.00,
                'description': 'Sample Asset Transaction - Moneycontrol Test',
                'raw_data': {'type': 'asset', 'source': 'test'}
            },
            {
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': -150000.00,
                'description': 'Sample Operating Expense - Moneycontrol Test',
                'raw_data': {'type': 'expense', 'source': 'test'}
            },
            {
                'source': 'moneycontrol',
                'transaction_date': today,
                'amount': 750000.00,
                'description': 'Sample Sales Revenue - Moneycontrol Test',
                'raw_data': {'type': 'revenue', 'source': 'test'}
            }
        ]
    
    def export_to_csv(self, transactions: List[Dict], filename: str = 'moneycontrol_transactions.csv') -> str:
        """Export transactions to CSV file"""
        df = pd.DataFrame(transactions)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(transactions)} transactions to {filename}")
        return filename

