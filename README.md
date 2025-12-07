# Fin Easy - Accounting Automation Bot

AI-powered accounting automation bot with full ledger and journal entries automation, OCR image analysis, and key account monitoring.

## 🎯 Features

- **Automated Journal Entry Generation**: AI-powered categorization and double-entry bookkeeping
- **OCR Image Processing**: Extract transactions from receipts, invoices, and bank statements using OCR
- **Key Account Monitoring**: Continuous validation and anomaly detection for critical accounts
- **Financial Reporting**: Generate income statements, balance sheets, trial balance, and more
- **Multi-Source Data Import**: CSV, Excel, PDF, and image file support
- **AI-Powered Intelligence**: Uses Ollama for transaction categorization and validation

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** (for image processing)
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
3. **Ollama** (for AI processing)
   - Install from [ollama.ai](https://ollama.ai)
   - Run: `ollama pull llama3.2` (or your preferred model)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/tuvisminds-design/fin-easy.git
cd fin-easy
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Initialize database**
```bash
python main.py init
```

## 📖 Usage

### Import Transactions

**From CSV:**
```bash
python main.py import transactions.csv --type csv --source bank
```

**From Excel:**
```bash
python main.py import transactions.xlsx --type excel --source bank
```

**From Image (OCR):**
```bash
python main.py import receipt.jpg --type image --source receipt
```

**From PDF:**
```bash
python main.py import invoice.pdf --type pdf --source invoice
```

### Process Transactions

Automatically generate journal entries from imported transactions:
```bash
python main.py process
```

Process limited number:
```bash
python main.py process --limit 10
```

### Monitor Accounts

Check all key accounts for accuracy and anomalies:
```bash
python main.py monitor
```

### Generate Reports

**Trial Balance:**
```bash
python main.py report trial
```

**Income Statement:**
```bash
python main.py report income --start-date 2024-01-01 --end-date 2024-12-31
```

**Balance Sheet:**
```bash
python main.py report balance --as-of 2024-12-31
```

## 🏗️ Architecture

```
Fin Easy Bot
├── Data Ingestion Layer
│   ├── CSV/Excel Import
│   ├── OCR Image Processing
│   └── PDF Extraction
├── AI Processing Engine (Ollama)
│   ├── Transaction Categorization
│   ├── Account Assignment
│   └── Anomaly Detection
├── Ledger Engine
│   ├── Double-Entry Validation
│   ├── Account Balance Management
│   └── Journal Entry Creation
├── Key Account Monitor
│   ├── Balance Verification
│   ├── Anomaly Detection
│   └── Compliance Checking
└── Reporting Engine
    ├── Income Statement
    ├── Balance Sheet
    └── Trial Balance
```

## 📊 Key Accounts Monitored

- **Cash** (1000)
- **Accounts Receivable** (1100)
- **Accounts Payable** (2000)
- **Inventory** (1200)
- **Sales Revenue** (4000)
- **Operating Expenses** (5100)

## 🔧 Configuration

Edit `.env` file:

```env
# Database
DATABASE_URL=sqlite:///fin_easy.db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Directories
DATA_DIR=./data
REPORTS_DIR=./reports
```

## 📝 Example Workflow

1. **Import bank statement:**
   ```bash
   python main.py import bank_statement.csv --type csv
   ```

2. **Process transactions:**
   ```bash
   python main.py process
   ```

3. **Monitor accounts:**
   ```bash
   python main.py monitor
   ```

4. **Generate reports:**
   ```bash
   python main.py report income
   python main.py report balance
   ```

## 🛠️ Development

### Project Structure

```
fin-easy/
├── main.py                 # CLI entry point
├── database.py             # Database models and schema
├── ai_engine.py            # AI processing (Ollama)
├── ocr_processor.py        # OCR image processing
├── data_ingestion.py       # Data import layer
├── ledger_engine.py         # Double-entry bookkeeping
├── journal_generator.py    # Automated journal entries
├── account_monitor.py      # Key account monitoring
├── reporting_engine.py     # Financial reporting
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🤖 AI Features

- **Transaction Categorization**: Automatically categorize transactions using AI
- **Account Assignment**: Smart account code assignment
- **Anomaly Detection**: Identify unusual transactions
- **Pattern Recognition**: Learn from historical data
- **Natural Language Processing**: Extract data from unstructured text

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Fin Easy** - Making accounting automation easy! 🚀


