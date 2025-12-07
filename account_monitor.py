"""
Fin Easy - Key Account Monitor
Continuous monitoring and validation of key accounts with anomaly detection
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
from database import Database, Account, AccountCheck, TransactionLine, JournalEntry
from ai_engine import AIEngine
from sqlalchemy import func, and_


class AccountMonitor:
    """Monitor key accounts for accuracy, anomalies, and compliance"""
    
    KEY_ACCOUNTS = {
        'Cash': '1000',
        'Accounts Receivable': '1100',
        'Accounts Payable': '2000',
        'Inventory': '1200',
        'Sales Revenue': '4000',
        'Operating Expenses': '5100'
    }
    
    def __init__(self, db: Database, ai_engine: AIEngine):
        self.db = db
        self.ai_engine = ai_engine
    
    def check_account_balance(self, account_code: str) -> Dict:
        """Check if account balance is accurate"""
        session = self.db.get_session()
        
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                return {'status': 'error', 'message': f'Account {account_code} not found'}
            
            # Calculate balance from transactions
            calculated_balance = self._calculate_balance_from_transactions(account.id, session)
            
            # Compare with stored balance
            balance_match = abs(account.balance - calculated_balance) < Decimal('0.01')
            
            result = {
                'account_code': account_code,
                'account_name': account.account_name,
                'stored_balance': float(account.balance),
                'calculated_balance': float(calculated_balance),
                'difference': float(account.balance - calculated_balance),
                'status': 'pass' if balance_match else 'fail',
                'check_type': 'balance',
                'check_date': date.today()
            }
            
            # Save check result
            self._save_check_result(account.id, result, session)
            
            return result
        
        finally:
            session.close()
    
    def _calculate_balance_from_transactions(self, account_id: int, session) -> Decimal:
        """Calculate account balance from all transactions"""
        # Get all transaction lines for this account
        transaction_lines = session.query(TransactionLine).filter_by(account_id=account_id).all()
        
        account = session.query(Account).filter_by(id=account_id).first()
        if not account:
            return Decimal(0)
        
        balance = Decimal(0)
        
        for trans_line in transaction_lines:
            if account.account_type in ['Asset', 'Expense']:
                balance += trans_line.debit_amount - trans_line.credit_amount
            else:  # Liability, Equity, Revenue
                balance += trans_line.credit_amount - trans_line.debit_amount
        
        return balance
    
    def detect_anomalies(self, account_code: str, days: int = 30) -> Dict:
        """Detect anomalies in account activity"""
        session = self.db.get_session()
        
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                return {'status': 'error', 'message': f'Account {account_code} not found'}
            
            # Get recent transactions
            start_date = date.today() - timedelta(days=days)
            transactions = session.query(TransactionLine, JournalEntry).join(
                JournalEntry
            ).filter(
                and_(
                    TransactionLine.account_id == account.id,
                    JournalEntry.entry_date >= start_date
                )
            ).all()
            
            # Analyze transactions
            amounts = [float(abs(t[0].debit_amount - t[0].credit_amount)) for t in transactions]
            
            if not amounts:
                return {
                    'account_code': account_code,
                    'status': 'pass',
                    'anomalies': [],
                    'message': 'No recent transactions'
                }
            
            # Statistical analysis
            import statistics
            mean_amount = statistics.mean(amounts) if amounts else 0
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            anomalies = []
            
            # Check for unusual amounts (outside 2 standard deviations)
            for trans_line, journal_entry in transactions:
                amount = float(abs(trans_line.debit_amount - trans_line.credit_amount))
                if std_amount > 0:
                    z_score = (amount - mean_amount) / std_amount if std_amount > 0 else 0
                    if abs(z_score) > 2:
                        anomalies.append({
                            'date': journal_entry.entry_date,
                            'entry_number': journal_entry.entry_number,
                            'amount': amount,
                            'z_score': z_score,
                            'type': 'unusual_amount',
                            'description': trans_line.description
                        })
            
            # Check for duplicate transactions
            seen = {}
            for trans_line, journal_entry in transactions:
                key = (float(trans_line.debit_amount), float(trans_line.credit_amount), 
                       journal_entry.entry_date)
                if key in seen:
                    anomalies.append({
                        'date': journal_entry.entry_date,
                        'entry_number': journal_entry.entry_number,
                        'type': 'duplicate',
                        'description': 'Possible duplicate transaction',
                        'original_entry': seen[key]
                    })
                else:
                    seen[key] = journal_entry.entry_number
            
            result = {
                'account_code': account_code,
                'account_name': account.account_name,
                'status': 'warning' if anomalies else 'pass',
                'anomalies': anomalies,
                'total_transactions': len(transactions),
                'mean_amount': mean_amount,
                'std_amount': std_amount,
                'check_type': 'anomaly',
                'check_date': date.today()
            }
            
            # Save check result
            self._save_check_result(account.id, result, session)
            
            return result
        
        finally:
            session.close()
    
    def check_double_entry_balance(self) -> Dict:
        """Verify that all journal entries balance (debits = credits)"""
        session = self.db.get_session()
        
        try:
            # Get all journal entries
            journal_entries = session.query(JournalEntry).all()
            
            unbalanced_entries = []
            
            for journal_entry in journal_entries:
                transaction_lines = session.query(TransactionLine).filter_by(
                    journal_entry_id=journal_entry.id
                ).all()
                
                total_debits = sum(t.debit_amount for t in transaction_lines)
                total_credits = sum(t.credit_amount for t in transaction_lines)
                
                if total_debits != total_credits:
                    unbalanced_entries.append({
                        'entry_number': journal_entry.entry_number,
                        'date': journal_entry.entry_date,
                        'debits': float(total_debits),
                        'credits': float(total_credits),
                        'difference': float(total_debits - total_credits)
                    })
            
            result = {
                'status': 'pass' if not unbalanced_entries else 'fail',
                'total_entries': len(journal_entries),
                'unbalanced_entries': unbalanced_entries,
                'check_type': 'double_entry',
                'check_date': date.today()
            }
            
            return result
        
        finally:
            session.close()
    
    def monitor_all_key_accounts(self) -> List[Dict]:
        """Monitor all key accounts"""
        results = []
        
        for account_name, account_code in self.KEY_ACCOUNTS.items():
            print(f"🔍 Checking {account_name} ({account_code})...")
            
            # Balance check
            balance_result = self.check_account_balance(account_code)
            results.append(balance_result)
            
            # Anomaly detection
            anomaly_result = self.detect_anomalies(account_code)
            results.append(anomaly_result)
        
        # Double-entry validation
        double_entry_result = self.check_double_entry_balance()
        results.append(double_entry_result)
        
        return results
    
    def _save_check_result(self, account_id: int, result: Dict, session):
        """Save account check result to database"""
        check = AccountCheck(
            account_id=account_id,
            check_date=result.get('check_date', date.today()),
            check_type=result.get('check_type', 'unknown'),
            status=result.get('status', 'unknown'),
            details=str(result)
        )
        session.add(check)
        session.commit()
    
    def get_check_history(self, account_code: str, limit: int = 10) -> List[Dict]:
        """Get check history for an account"""
        session = self.db.get_session()
        
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                return []
            
            checks = session.query(AccountCheck).filter_by(
                account_id=account.id
            ).order_by(AccountCheck.check_date.desc()).limit(limit).all()
            
            return [{
                'check_date': check.check_date,
                'check_type': check.check_type,
                'status': check.status,
                'details': check.details
            } for check in checks]
        
        finally:
            session.close()

