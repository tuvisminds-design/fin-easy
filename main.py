#!/usr/bin/env python3
"""
Fin Easy - Main Entry Point
Accounting Automation Bot with AI-powered ledger and journal automation
"""

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
import os

from database import Database
from ai_engine import AIEngine
from ocr_processor import OCRProcessor
from data_ingestion import DataIngestion
from ledger_engine import LedgerEngine
from journal_generator import JournalGenerator
from account_monitor import AccountMonitor
from reporting_engine import ReportingEngine


class FinEasyBot:
    """Main Fin Easy Bot"""
    
    def __init__(self):
        self.db = Database()
        self.ai_engine = AIEngine()
        self.ocr_processor = OCRProcessor()
        self.data_ingestion = DataIngestion(self.db, self.ocr_processor)
        self.ledger_engine = LedgerEngine(self.db)
        self.journal_generator = JournalGenerator(self.db, self.ai_engine, self.ledger_engine)
        self.account_monitor = AccountMonitor(self.db, self.ai_engine)
        self.reporting_engine = ReportingEngine(self.db, self.ledger_engine)
    
    def initialize(self):
        """Initialize database and default accounts"""
        print("🚀 Initializing Fin Easy...")
        self.db.create_tables()
        self.db.initialize_default_accounts()
        print("✅ Fin Easy initialized successfully!")
    
    def import_csv(self, csv_path: str, source: str = 'bank'):
        """Import transactions from CSV"""
        print(f"📥 Importing transactions from {csv_path}...")
        transactions = self.data_ingestion.import_from_csv(csv_path, source)
        if transactions:
            self.data_ingestion.save_raw_transactions(transactions)
            print(f"✅ Imported {len(transactions)} transactions")
        return transactions
    
    def import_excel(self, excel_path: str, source: str = 'bank'):
        """Import transactions from Excel"""
        print(f"📥 Importing transactions from {excel_path}...")
        transactions = self.data_ingestion.import_from_excel(excel_path, source)
        if transactions:
            self.data_ingestion.save_raw_transactions(transactions)
            print(f"✅ Imported {len(transactions)} transactions")
        return transactions
    
    def import_image(self, image_path: str, source: str = 'receipt'):
        """Import transaction from image using OCR"""
        print(f"📷 Processing image with OCR: {image_path}...")
        transaction = self.data_ingestion.import_from_image(image_path, source)
        if transaction:
            transactions = [transaction]
            self.data_ingestion.save_raw_transactions(transactions)
            print("✅ Transaction extracted from image")
        return transaction
    
    def import_pdf(self, pdf_path: str, source: str = 'invoice'):
        """Import transactions from PDF"""
        print(f"📄 Processing PDF: {pdf_path}...")
        transactions = self.data_ingestion.import_from_pdf(pdf_path, source)
        if transactions:
            self.data_ingestion.save_raw_transactions(transactions)
            print(f"✅ Extracted {len(transactions)} transaction(s) from PDF")
        return transactions
    
    def process_transactions(self, limit: int = None):
        """Process pending transactions and generate journal entries"""
        print("🔄 Processing pending transactions...")
        results = self.journal_generator.process_pending_transactions(limit)
        print(f"✅ Processed {len(results)} transactions")
        return results
    
    def monitor_accounts(self):
        """Monitor all key accounts"""
        print("🔍 Monitoring key accounts...")
        results = self.account_monitor.monitor_all_key_accounts()
        
        # Print summary
        for result in results:
            status_icon = "✅" if result.get('status') == 'pass' else "⚠️" if result.get('status') == 'warning' else "❌"
            check_type = result.get('check_type', 'unknown')
            account_code = result.get('account_code', 'N/A')
            print(f"{status_icon} {check_type.upper()} - Account {account_code}: {result.get('status', 'unknown')}")
        
        return results
    
    def generate_trial_balance(self):
        """Generate trial balance"""
        print("📊 Generating trial balance...")
        report = self.reporting_engine.generate_trial_balance()
        self._print_report(report)
        return report
    
    def generate_income_statement(self, start_date: date = None, end_date: date = None):
        """Generate income statement"""
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
        
        print(f"📊 Generating income statement ({start_date} to {end_date})...")
        report = self.reporting_engine.generate_income_statement(start_date, end_date)
        self._print_report(report)
        return report
    
    def generate_balance_sheet(self, as_of_date: date = None):
        """Generate balance sheet"""
        if not as_of_date:
            as_of_date = date.today()
        
        print(f"📊 Generating balance sheet (as of {as_of_date})...")
        report = self.reporting_engine.generate_balance_sheet(as_of_date)
        self._print_report(report)
        return report
    
    def _print_report(self, report: dict):
        """Print report in readable format"""
        print("\n" + "="*60)
        print(f"  {report.get('report_type', 'Report')}")
        print("="*60)
        
        if 'period' in report:
            print(f"Period: {report['period']}")
        if 'as_of_date' in report:
            print(f"As of: {report['as_of_date']}")
        
        # Print report-specific data
        if 'total_revenue' in report:
            print(f"\nTotal Revenue: ${report['total_revenue']:,.2f}")
            print(f"Total Expenses: ${report['total_expenses']:,.2f}")
            print(f"Net Income: ${report['net_income']:,.2f}")
        
        if 'total_assets' in report:
            print(f"\nTotal Assets: ${report['total_assets']:,.2f}")
            print(f"Total Liabilities: ${report['total_liabilities']:,.2f}")
            print(f"Total Equity: ${report['total_equity']:,.2f}")
            if 'is_balanced' in report:
                status = "✅ Balanced" if report['is_balanced'] else "❌ Not Balanced"
                print(f"Accounting Equation: {status}")
        
        if 'total_debits' in report:
            print(f"\nTotal Debits: ${report['total_debits']:,.2f}")
            print(f"Total Credits: ${report['total_credits']:,.2f}")
            if 'is_balanced' in report:
                status = "✅ Balanced" if report['is_balanced'] else "❌ Not Balanced"
                print(f"Trial Balance: {status}")
        
        print("="*60 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Fin Easy - Accounting Automation Bot')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize
    subparsers.add_parser('init', help='Initialize database and default accounts')
    
    # Import commands
    import_parser = subparsers.add_parser('import', help='Import transactions')
    import_parser.add_argument('file', help='File path to import')
    import_parser.add_argument('--type', choices=['csv', 'excel', 'image', 'pdf'], 
                             default='csv', help='File type')
    import_parser.add_argument('--source', default='bank', help='Transaction source')
    
    # Process
    process_parser = subparsers.add_parser('process', help='Process pending transactions')
    process_parser.add_argument('--limit', type=int, help='Limit number of transactions')
    
    # Monitor
    subparsers.add_parser('monitor', help='Monitor key accounts')
    
    # Reports
    report_parser = subparsers.add_parser('report', help='Generate financial reports')
    report_parser.add_argument('type', choices=['trial', 'income', 'balance'], 
                              help='Report type')
    report_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    report_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    report_parser.add_argument('--as-of', type=str, help='As of date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    bot = FinEasyBot()
    
    try:
        if args.command == 'init':
            bot.initialize()
        
        elif args.command == 'import':
            if args.type == 'csv':
                bot.import_csv(args.file, args.source)
            elif args.type == 'excel':
                bot.import_excel(args.file, args.source)
            elif args.type == 'image':
                bot.import_image(args.file, args.source)
            elif args.type == 'pdf':
                bot.import_pdf(args.file, args.source)
        
        elif args.command == 'process':
            bot.process_transactions(args.limit)
        
        elif args.command == 'monitor':
            bot.monitor_accounts()
        
        elif args.command == 'report':
            if args.type == 'trial':
                bot.generate_trial_balance()
            elif args.type == 'income':
                start = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
                end = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
                bot.generate_income_statement(start, end)
            elif args.type == 'balance':
                as_of = datetime.strptime(args.as_of, '%Y-%m-%d').date() if args.as_of else None
                bot.generate_balance_sheet(as_of)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

