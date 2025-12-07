"""
Fin Easy - Reporting Engine
Generates financial statements, reports, and analytics
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from decimal import Decimal
from database import Database, Account
from ledger_engine import LedgerEngine
import json


class ReportingEngine:
    """Financial reporting engine"""
    
    def __init__(self, db: Database, ledger_engine: LedgerEngine):
        self.db = db
        self.ledger_engine = ledger_engine
    
    def generate_income_statement(self, start_date: date, end_date: date) -> Dict:
        """Generate Income Statement (Profit & Loss)"""
        session = self.db.get_session()
        
        try:
            # Get revenue accounts
            revenue_accounts = session.query(Account).filter_by(account_type='Revenue').all()
            # Get expense accounts
            expense_accounts = session.query(Account).filter_by(account_type='Expense').all()
            
            revenues = []
            total_revenue = Decimal(0)
            
            for account in revenue_accounts:
                # Calculate revenue for period (simplified - in production, sum transactions)
                revenue_amount = account.balance if account.balance > 0 else Decimal(0)
                if revenue_amount > 0:
                    revenues.append({
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'amount': float(revenue_amount)
                    })
                    total_revenue += revenue_amount
            
            expenses = []
            total_expenses = Decimal(0)
            
            for account in expense_accounts:
                expense_amount = account.balance if account.balance > 0 else Decimal(0)
                if expense_amount > 0:
                    expenses.append({
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'amount': float(expense_amount)
                    })
                    total_expenses += expense_amount
            
            net_income = total_revenue - total_expenses
            
            return {
                'report_type': 'Income Statement',
                'period': {
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                },
                'revenues': revenues,
                'total_revenue': float(total_revenue),
                'expenses': expenses,
                'total_expenses': float(total_expenses),
                'net_income': float(net_income),
                'generated_at': datetime.now().isoformat()
            }
        
        finally:
            session.close()
    
    def generate_balance_sheet(self, as_of_date: date) -> Dict:
        """Generate Balance Sheet"""
        session = self.db.get_session()
        
        try:
            # Assets
            asset_accounts = session.query(Account).filter_by(account_type='Asset').all()
            assets = []
            total_assets = Decimal(0)
            
            for account in asset_accounts:
                if account.balance != 0:
                    assets.append({
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'amount': float(account.balance)
                    })
                    total_assets += account.balance
            
            # Liabilities
            liability_accounts = session.query(Account).filter_by(account_type='Liability').all()
            liabilities = []
            total_liabilities = Decimal(0)
            
            for account in liability_accounts:
                if account.balance != 0:
                    liabilities.append({
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'amount': float(account.balance)
                    })
                    total_liabilities += account.balance
            
            # Equity
            equity_accounts = session.query(Account).filter_by(account_type='Equity').all()
            equity = []
            total_equity = Decimal(0)
            
            for account in equity_accounts:
                if account.balance != 0:
                    equity.append({
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'amount': float(account.balance)
                    })
                    total_equity += account.balance
            
            # Verify accounting equation
            equation_balance = total_assets - (total_liabilities + total_equity)
            
            return {
                'report_type': 'Balance Sheet',
                'as_of_date': str(as_of_date),
                'assets': assets,
                'total_assets': float(total_assets),
                'liabilities': liabilities,
                'total_liabilities': float(total_liabilities),
                'equity': equity,
                'total_equity': float(total_equity),
                'equation_balance': float(equation_balance),
                'is_balanced': abs(equation_balance) < Decimal('0.01'),
                'generated_at': datetime.now().isoformat()
            }
        
        finally:
            session.close()
    
    def generate_cash_flow_statement(self, start_date: date, end_date: date) -> Dict:
        """Generate Cash Flow Statement"""
        session = self.db.get_session()
        
        try:
            # Get cash account
            cash_account = session.query(Account).filter_by(account_code='1000').first()
            
            if not cash_account:
                return {'error': 'Cash account (1000) not found'}
            
            # Get cash transactions for period
            # Simplified - in production, would sum actual transactions
            cash_balance = cash_account.balance
            
            return {
                'report_type': 'Cash Flow Statement',
                'period': {
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                },
                'cash_balance': float(cash_balance),
                'generated_at': datetime.now().isoformat()
            }
        
        finally:
            session.close()
    
    def generate_trial_balance(self, as_of_date: date = None) -> Dict:
        """Generate Trial Balance"""
        trial_balance = self.ledger_engine.get_trial_balance(as_of_date)
        
        return {
            'report_type': 'Trial Balance',
            'as_of_date': str(as_of_date) if as_of_date else str(date.today()),
            'accounts': trial_balance[:-1],  # Exclude total row
            'total_debits': float(trial_balance[-1]['debit']),
            'total_credits': float(trial_balance[-1]['credit']),
            'is_balanced': trial_balance[-1]['debit'] == trial_balance[-1]['credit'],
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_account_analysis(self, account_code: str, start_date: date = None, 
                                  end_date: date = None) -> Dict:
        """Generate detailed account analysis"""
        ledger_entries = self.ledger_engine.get_general_ledger(
            account_code=account_code,
            start_date=start_date,
            end_date=end_date
        )
        
        session = self.db.get_session()
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                return {'error': f'Account {account_code} not found'}
            
            total_debits = sum(float(e['debit']) for e in ledger_entries)
            total_credits = sum(float(e['credit']) for e in ledger_entries)
            
            return {
                'report_type': 'Account Analysis',
                'account_code': account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'current_balance': float(account.balance),
                'period': {
                    'start_date': str(start_date) if start_date else None,
                    'end_date': str(end_date) if end_date else None
                },
                'transactions': ledger_entries,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'transaction_count': len(ledger_entries),
                'generated_at': datetime.now().isoformat()
            }
        finally:
            session.close()
    
    def export_report_to_json(self, report: Dict, filename: str = None) -> str:
        """Export report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{report['report_type'].lower().replace(' ', '_')}_{timestamp}.json"
        
        import os
        reports_dir = os.getenv('REPORTS_DIR', './reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Report exported to {filepath}")
        return filepath


