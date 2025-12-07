#!/usr/bin/env python3
"""
Test script for Moneycontrol scraper and Fin Easy integration
"""

from moneycontrol_scraper import MoneyControlScraper
from data_ingestion import DataIngestion
from database import Database
from journal_generator import JournalGenerator
from ai_engine import AIEngine
from ledger_engine import LedgerEngine
from reporting_engine import ReportingEngine


def test_moneycontrol_integration():
    """Test Moneycontrol scraper with Fin Easy"""
    print("="*60)
    print("  Fin Easy - Moneycontrol Integration Test")
    print("="*60)
    
    # Initialize components
    db = Database()
    ai_engine = AIEngine()
    ledger_engine = LedgerEngine(db)
    journal_generator = JournalGenerator(db, ai_engine, ledger_engine)
    data_ingestion = DataIngestion(db)
    reporting_engine = ReportingEngine(db, ledger_engine)
    
    # Initialize scraper
    scraper = MoneyControlScraper()
    
    print("\n1. Scraping Moneycontrol data...")
    transactions = scraper.create_test_transactions('RELIANCE')
    print(f"   ✅ Generated {len(transactions)} test transactions")
    
    # Export to CSV
    csv_file = scraper.export_to_csv(transactions, 'moneycontrol_test.csv')
    print(f"   ✅ Exported to {csv_file}")
    
    print("\n2. Importing transactions to Fin Easy...")
    imported = data_ingestion.save_raw_transactions(transactions)
    print(f"   ✅ Imported {len(imported)} transactions")
    
    print("\n3. Processing transactions (generating journal entries)...")
    results = journal_generator.process_pending_transactions()
    print(f"   ✅ Processed {len(results)} transactions")
    
    print("\n4. Generating Trial Balance...")
    trial_balance = reporting_engine.generate_trial_balance()
    print(f"   ✅ Trial Balance generated")
    print(f"   Total Debits: ${trial_balance['total_debits']:,.2f}")
    print(f"   Total Credits: ${trial_balance['total_credits']:,.2f}")
    print(f"   Balanced: {'✅ Yes' if trial_balance['is_balanced'] else '❌ No'}")
    
    print("\n5. Generating Income Statement...")
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    income_stmt = reporting_engine.generate_income_statement(start_date, end_date)
    print(f"   ✅ Income Statement generated")
    if 'total_revenue' in income_stmt:
        print(f"   Total Revenue: ${income_stmt['total_revenue']:,.2f}")
        print(f"   Total Expenses: ${income_stmt['total_expenses']:,.2f}")
        print(f"   Net Income: ${income_stmt['net_income']:,.2f}")
    
    print("\n6. Generating Balance Sheet...")
    balance_sheet = reporting_engine.generate_balance_sheet(end_date)
    print(f"   ✅ Balance Sheet generated")
    if 'total_assets' in balance_sheet:
        print(f"   Total Assets: ${balance_sheet['total_assets']:,.2f}")
        print(f"   Total Liabilities: ${balance_sheet['total_liabilities']:,.2f}")
        print(f"   Total Equity: ${balance_sheet['total_equity']:,.2f}")
        print(f"   Balanced: {'✅ Yes' if balance_sheet['is_balanced'] else '❌ No'}")
    
    print("\n" + "="*60)
    print("  ✅ Moneycontrol Integration Test Complete!")
    print("="*60)
    
    return {
        'transactions': len(transactions),
        'processed': len(results),
        'trial_balance': trial_balance,
        'income_statement': income_stmt,
        'balance_sheet': balance_sheet
    }


if __name__ == '__main__':
    test_moneycontrol_integration()

