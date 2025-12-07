"""
Fin Easy - Ledger Engine
Handles double-entry bookkeeping, account balances, and ledger maintenance
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List, Optional
from database import Database, Account, JournalEntry, TransactionLine, RawTransaction
from sqlalchemy import func


class LedgerEngine:
    """Ledger engine for double-entry bookkeeping"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_journal_entry(self, entry_date: date, description: str, 
                           transactions: List[Dict], reference: str = None) -> JournalEntry:
        """
        Create a journal entry with double-entry validation
        transactions: List of {'account_code': str, 'debit': float, 'credit': float, 'description': str}
        """
        session = self.db.get_session()
        
        try:
            # Validate double-entry (debits = credits)
            total_debits = sum(Decimal(str(t.get('debit', 0))) for t in transactions)
            total_credits = sum(Decimal(str(t.get('credit', 0))) for t in transactions)
            
            if total_debits != total_credits:
                raise ValueError(f"Double-entry validation failed: Debits ({total_debits}) != Credits ({total_credits})")
            
            # Generate entry number
            entry_number = self._generate_entry_number(entry_date)
            
            # Create journal entry
            journal_entry = JournalEntry(
                entry_date=entry_date,
                entry_number=entry_number,
                description=description,
                reference=reference
            )
            session.add(journal_entry)
            session.flush()  # Get the ID
            
            # Create transaction lines
            for trans in transactions:
                account_code = trans.get('account_code')
                account = session.query(Account).filter_by(account_code=account_code).first()
                
                if not account:
                    raise ValueError(f"Account not found: {account_code}")
                
                transaction_line = TransactionLine(
                    journal_entry_id=journal_entry.id,
                    account_id=account.id,
                    debit_amount=Decimal(str(trans.get('debit', 0))),
                    credit_amount=Decimal(str(trans.get('credit', 0))),
                    description=trans.get('description', '')
                )
                session.add(transaction_line)
                
                # Update account balance
                self._update_account_balance(account, transaction_line, session)
            
            session.commit()
            print(f"✅ Created journal entry {entry_number}")
            return journal_entry
        
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating journal entry: {e}")
            raise
        
        finally:
            session.close()
    
    def _update_account_balance(self, account: Account, transaction_line: TransactionLine, session):
        """Update account balance based on transaction"""
        # Asset and Expense accounts: Debit increases, Credit decreases
        # Liability, Equity, Revenue accounts: Credit increases, Debit decreases
        
        balance_change = Decimal(0)
        
        if account.account_type in ['Asset', 'Expense']:
            balance_change = transaction_line.debit_amount - transaction_line.credit_amount
        elif account.account_type in ['Liability', 'Equity', 'Revenue']:
            balance_change = transaction_line.credit_amount - transaction_line.debit_amount
        
        account.balance += balance_change
        session.add(account)
    
    def _generate_entry_number(self, entry_date: date) -> str:
        """Generate unique journal entry number"""
        session = self.db.get_session()
        
        try:
            # Format: JE-YYYYMMDD-XXX
            date_str = entry_date.strftime('%Y%m%d')
            
            # Count entries for this date
            count = session.query(JournalEntry).filter(
                JournalEntry.entry_date == entry_date
            ).count()
            
            entry_number = f"JE-{date_str}-{count + 1:03d}"
            return entry_number
        
        finally:
            session.close()
    
    def get_account_balance(self, account_code: str, as_of_date: date = None) -> Decimal:
        """Get account balance as of a specific date"""
        session = self.db.get_session()
        
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                return Decimal(0)
            
            if as_of_date:
                # Calculate balance up to specific date
                # This would require summing all transactions up to that date
                # For simplicity, using current balance
                # In production, you'd want to calculate from transactions
                pass
            
            return account.balance
        
        finally:
            session.close()
    
    def get_trial_balance(self, as_of_date: date = None) -> List[Dict]:
        """Generate trial balance"""
        session = self.db.get_session()
        
        try:
            accounts = session.query(Account).all()
            trial_balance = []
            
            total_debits = Decimal(0)
            total_credits = Decimal(0)
            
            for account in accounts:
                if account.balance == 0:
                    continue
                
                if account.account_type in ['Asset', 'Expense']:
                    debit = account.balance if account.balance > 0 else Decimal(0)
                    credit = -account.balance if account.balance < 0 else Decimal(0)
                else:  # Liability, Equity, Revenue
                    credit = account.balance if account.balance > 0 else Decimal(0)
                    debit = -account.balance if account.balance < 0 else Decimal(0)
                
                trial_balance.append({
                    'account_code': account.account_code,
                    'account_name': account.account_name,
                    'debit': debit,
                    'credit': credit
                })
                
                total_debits += debit
                total_credits += credit
            
            # Add totals row
            trial_balance.append({
                'account_code': 'TOTAL',
                'account_name': '',
                'debit': total_debits,
                'credit': total_credits
            })
            
            return trial_balance
        
        finally:
            session.close()
    
    def get_general_ledger(self, account_code: str = None, start_date: date = None, 
                          end_date: date = None) -> List[Dict]:
        """Get general ledger entries"""
        session = self.db.get_session()
        
        try:
            query = session.query(TransactionLine, JournalEntry, Account).join(
                JournalEntry
            ).join(Account)
            
            if account_code:
                account = session.query(Account).filter_by(account_code=account_code).first()
                if account:
                    query = query.filter(TransactionLine.account_id == account.id)
            
            if start_date:
                query = query.filter(JournalEntry.entry_date >= start_date)
            
            if end_date:
                query = query.filter(JournalEntry.entry_date <= end_date)
            
            query = query.order_by(JournalEntry.entry_date, JournalEntry.entry_number)
            
            ledger_entries = []
            for trans_line, journal_entry, account in query.all():
                ledger_entries.append({
                    'date': journal_entry.entry_date,
                    'entry_number': journal_entry.entry_number,
                    'account_code': account.account_code,
                    'account_name': account.account_name,
                    'description': trans_line.description or journal_entry.description,
                    'debit': trans_line.debit_amount,
                    'credit': trans_line.credit_amount,
                    'reference': journal_entry.reference
                })
            
            return ledger_entries
        
        finally:
            session.close()


