"""
Fin Easy - Journal Entry Generator
Automatically generates journal entries from raw transactions using AI
"""

from datetime import date
from typing import Dict, List, Optional
from database import Database, RawTransaction, Account
from ai_engine import AIEngine
from ledger_engine import LedgerEngine


class JournalGenerator:
    """Automated journal entry generator"""
    
    def __init__(self, db: Database, ai_engine: AIEngine, ledger_engine: LedgerEngine):
        self.db = db
        self.ai_engine = ai_engine
        self.ledger_engine = ledger_engine
    
    def generate_entry_from_transaction(self, raw_transaction: RawTransaction) -> Optional[Dict]:
        """
        Generate journal entry from a raw transaction
        Returns: Journal entry data or None if failed
        """
        session = self.db.get_session()
        
        try:
            # Use AI to categorize transaction
            ai_result = self.ai_engine.categorize_transaction(
                description=raw_transaction.description or '',
                amount=float(raw_transaction.amount),
                date=str(raw_transaction.transaction_date)
            )
            
            # Get account
            account_code = ai_result.get('account_code', '5100')  # Default to Operating Expenses
            account = session.query(Account).filter_by(account_code=account_code).first()
            
            if not account:
                print(f"⚠️  Account {account_code} not found, using default")
                account = session.query(Account).filter_by(account_code='5100').first()
            
            # Determine debit/credit based on transaction type
            transactions = []
            
            if raw_transaction.amount > 0:
                # Positive amount - could be revenue or expense
                if account.account_type == 'Revenue':
                    # Revenue: Credit Revenue, Debit Cash
                    cash_account = session.query(Account).filter_by(account_code='1000').first()
                    if cash_account:
                        transactions = [
                            {
                                'account_code': '1000',  # Cash
                                'debit': float(raw_transaction.amount),
                                'credit': 0,
                                'description': f"Payment received: {raw_transaction.description}"
                            },
                            {
                                'account_code': account_code,
                                'debit': 0,
                                'credit': float(raw_transaction.amount),
                                'description': raw_transaction.description
                            }
                        ]
                else:
                    # Expense: Debit Expense, Credit Cash
                    cash_account = session.query(Account).filter_by(account_code='1000').first()
                    if cash_account:
                        transactions = [
                            {
                                'account_code': account_code,
                                'debit': float(raw_transaction.amount),
                                'credit': 0,
                                'description': raw_transaction.description
                            },
                            {
                                'account_code': '1000',  # Cash
                                'debit': 0,
                                'credit': float(raw_transaction.amount),
                                'description': f"Payment: {raw_transaction.description}"
                            }
                        ]
            else:
                # Negative amount (withdrawal/payment)
                amount = abs(raw_transaction.amount)
                transactions = [
                    {
                        'account_code': account_code,
                        'debit': amount,
                        'credit': 0,
                        'description': raw_transaction.description
                    },
                    {
                        'account_code': '1000',  # Cash
                        'debit': 0,
                        'credit': amount,
                        'description': f"Payment: {raw_transaction.description}"
                    }
                ]
            
            if not transactions:
                return None
            
            # Create journal entry
            description = f"{ai_result.get('category', 'Transaction')}: {raw_transaction.description}"
            journal_entry = self.ledger_engine.create_journal_entry(
                entry_date=raw_transaction.transaction_date,
                description=description,
                transactions=transactions,
                reference=f"Auto-generated from {raw_transaction.source}"
            )
            
            # Mark raw transaction as processed
            raw_transaction.processed = True
            raw_transaction.journal_entry_id = journal_entry.id
            raw_transaction.account_id = account.id
            raw_transaction.category = ai_result.get('category', 'Uncategorized')
            session.add(raw_transaction)
            session.commit()
            
            return {
                'journal_entry': journal_entry,
                'ai_categorization': ai_result,
                'transactions': transactions
            }
        
        except Exception as e:
            session.rollback()
            print(f"❌ Error generating journal entry: {e}")
            return None
        
        finally:
            session.close()
    
    def process_pending_transactions(self, limit: int = None) -> List[Dict]:
        """Process all pending raw transactions"""
        session = self.db.get_session()
        
        try:
            query = session.query(RawTransaction).filter_by(processed=False)
            if limit:
                query = query.limit(limit)
            
            raw_transactions = query.all()
            results = []
            
            for raw_trans in raw_transactions:
                result = self.generate_entry_from_transaction(raw_trans)
                if result:
                    results.append(result)
            
            print(f"✅ Processed {len(results)} transactions")
            return results
        
        finally:
            session.close()
    
    def generate_adjusting_entry(self, entry_date: date, description: str, 
                                account_code: str, amount: float, 
                                entry_type: str = 'debit') -> Dict:
        """
        Generate adjusting journal entry
        entry_type: 'debit' or 'credit'
        """
        session = self.db.get_session()
        
        try:
            account = session.query(Account).filter_by(account_code=account_code).first()
            if not account:
                raise ValueError(f"Account not found: {account_code}")
            
            # Determine offset account based on account type
            if account.account_type in ['Asset', 'Expense']:
                # Use Retained Earnings or appropriate offset
                offset_account_code = '3100'  # Retained Earnings
            else:
                offset_account_code = '1000'  # Cash (or appropriate)
            
            transactions = []
            
            if entry_type == 'debit':
                transactions = [
                    {
                        'account_code': account_code,
                        'debit': amount,
                        'credit': 0,
                        'description': description
                    },
                    {
                        'account_code': offset_account_code,
                        'debit': 0,
                        'credit': amount,
                        'description': f"Adjustment: {description}"
                    }
                ]
            else:  # credit
                transactions = [
                    {
                        'account_code': account_code,
                        'debit': 0,
                        'credit': amount,
                        'description': description
                    },
                    {
                        'account_code': offset_account_code,
                        'debit': amount,
                        'credit': 0,
                        'description': f"Adjustment: {description}"
                    }
                ]
            
            journal_entry = self.ledger_engine.create_journal_entry(
                entry_date=entry_date,
                description=description,
                transactions=transactions,
                reference="Adjusting Entry"
            )
            
            return {
                'journal_entry': journal_entry,
                'transactions': transactions
            }
        
        finally:
            session.close()

