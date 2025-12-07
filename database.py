"""
Fin Easy - Database Models and Schema
Handles all database operations for accounts, transactions, and journal entries
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from decimal import Decimal as PyDecimal
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Account(Base):
    """Chart of Accounts"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    account_code = Column(String(50), unique=True, nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    balance = Column(Numeric(15, 2), default=0.00)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    parent = relationship('Account', remote_side=[id], backref='children')
    transaction_lines = relationship('TransactionLine', back_populates='account')
    
    def __repr__(self):
        return f"<Account(code={self.account_code}, name={self.account_name}, type={self.account_type})>"


class JournalEntry(Base):
    """Journal Entries"""
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, nullable=False)
    entry_number = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    reference = Column(String(200))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    transaction_lines = relationship('TransactionLine', back_populates='journal_entry', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<JournalEntry(number={self.entry_number}, date={self.entry_date})>"


class TransactionLine(Base):
    """Transaction Lines (Double-Entry)"""
    __tablename__ = 'transaction_lines'
    
    id = Column(Integer, primary_key=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    debit_amount = Column(Numeric(15, 2), default=0.00)
    credit_amount = Column(Numeric(15, 2), default=0.00)
    description = Column(Text)
    
    # Relationships
    journal_entry = relationship('JournalEntry', back_populates='transaction_lines')
    account = relationship('Account', back_populates='transaction_lines')
    
    def __repr__(self):
        return f"<TransactionLine(account={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"


class RawTransaction(Base):
    """Raw Transactions from external sources"""
    __tablename__ = 'raw_transactions'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # 'bank', 'credit_card', 'manual', etc.
    transaction_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # AI-determined
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)  # AI-assigned
    processed = Column(Boolean, default=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    account = relationship('Account')
    journal_entry = relationship('JournalEntry')
    
    def __repr__(self):
        return f"<RawTransaction(source={self.source}, date={self.transaction_date}, amount={self.amount})>"


class AccountCheck(Base):
    """Key Account Checks and Validations"""
    __tablename__ = 'account_checks'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    check_date = Column(Date, nullable=False)
    check_type = Column(String(50), nullable=False)  # 'balance', 'anomaly', 'reconciliation'
    status = Column(String(20), nullable=False)  # 'pass', 'fail', 'warning'
    details = Column(Text)  # JSON with check results
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    account = relationship('Account')
    
    def __repr__(self):
        return f"<AccountCheck(account={self.account_id}, type={self.check_type}, status={self.status})>"


class Database:
    """Database connection and session management"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///fin_easy.db')
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created successfully")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def initialize_default_accounts(self):
        """Initialize default chart of accounts"""
        session = self.get_session()
        try:
            # Check if accounts already exist
            if session.query(Account).count() > 0:
                print("ℹ️  Chart of accounts already initialized")
                return
            
            # Default accounts
            default_accounts = [
                # Assets
                {'code': '1000', 'name': 'Cash', 'type': 'Asset'},
                {'code': '1100', 'name': 'Accounts Receivable', 'type': 'Asset'},
                {'code': '1200', 'name': 'Inventory', 'type': 'Asset'},
                {'code': '1300', 'name': 'Prepaid Expenses', 'type': 'Asset'},
                {'code': '1400', 'name': 'Property, Plant & Equipment', 'type': 'Asset'},
                
                # Liabilities
                {'code': '2000', 'name': 'Accounts Payable', 'type': 'Liability'},
                {'code': '2100', 'name': 'Accrued Expenses', 'type': 'Liability'},
                {'code': '2200', 'name': 'Short-term Debt', 'type': 'Liability'},
                {'code': '2300', 'name': 'Long-term Debt', 'type': 'Liability'},
                
                # Equity
                {'code': '3000', 'name': 'Owner\'s Equity', 'type': 'Equity'},
                {'code': '3100', 'name': 'Retained Earnings', 'type': 'Equity'},
                
                # Revenue
                {'code': '4000', 'name': 'Sales Revenue', 'type': 'Revenue'},
                {'code': '4100', 'name': 'Service Revenue', 'type': 'Revenue'},
                {'code': '4200', 'name': 'Other Income', 'type': 'Revenue'},
                
                # Expenses
                {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'Expense'},
                {'code': '5100', 'name': 'Operating Expenses', 'type': 'Expense'},
                {'code': '5200', 'name': 'Salaries & Wages', 'type': 'Expense'},
                {'code': '5300', 'name': 'Rent Expense', 'type': 'Expense'},
                {'code': '5400', 'name': 'Utilities Expense', 'type': 'Expense'},
                {'code': '5500', 'name': 'Marketing Expense', 'type': 'Expense'},
                {'code': '5600', 'name': 'Depreciation Expense', 'type': 'Expense'},
            ]
            
            for acc_data in default_accounts:
                account = Account(
                    account_code=acc_data['code'],
                    account_name=acc_data['name'],
                    account_type=acc_data['type']
                )
                session.add(account)
            
            session.commit()
            print(f"✅ Initialized {len(default_accounts)} default accounts")
        except Exception as e:
            session.rollback()
            print(f"❌ Error initializing accounts: {e}")
        finally:
            session.close()


