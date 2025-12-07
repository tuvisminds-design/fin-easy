const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const multer = require('multer');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads
const upload = multer({ 
  dest: 'uploads/',
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Fin Easy Python script path
const FIN_EASY_PATH = path.join(__dirname, '..', 'fin-easy');
const PYTHON_CMD = process.platform === 'win32' ? 'python' : 'python3';

// Helper function to run Python commands
function runPythonCommand(args, callback) {
  const pythonProcess = spawn(PYTHON_CMD, args, {
    cwd: FIN_EASY_PATH,
    shell: true,
    env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' }
  });

  let stdout = '';
  let stderr = '';

  pythonProcess.stdout.on('data', (data) => {
    stdout += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    stderr += data.toString();
  });

  pythonProcess.on('close', (code) => {
    callback(code === 0 ? null : new Error(stderr || `Process exited with code ${code}`), stdout, stderr);
  });
}

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Fin Easy API is running' });
});

// Initialize database
app.post('/api/init', (req, res) => {
  runPythonCommand(['main.py', 'init'], (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Database initialized', output: stdout });
  });
});

// Import transactions from CSV
app.post('/api/import/csv', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const source = req.body.source || 'bank';
  const filePath = req.file.path;

  runPythonCommand(['main.py', 'import', filePath, '--type', 'csv', '--source', source], (error, stdout, stderr) => {
    // Clean up uploaded file
    fs.unlink(filePath, () => {});

    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Transactions imported', output: stdout });
  });
});

// Import transactions from Excel
app.post('/api/import/excel', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const source = req.body.source || 'bank';
  const filePath = req.file.path;

  runPythonCommand(['main.py', 'import', filePath, '--type', 'excel', '--source', source], (error, stdout, stderr) => {
    fs.unlink(filePath, () => {});

    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Transactions imported', output: stdout });
  });
});

// Import from image (OCR)
app.post('/api/import/image', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const source = req.body.source || 'receipt';
  const filePath = req.file.path;

  runPythonCommand(['main.py', 'import', filePath, '--type', 'image', '--source', source], (error, stdout, stderr) => {
    fs.unlink(filePath, () => {});

    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Transaction extracted from image', output: stdout });
  });
});

// Import from PDF
app.post('/api/import/pdf', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const source = req.body.source || 'invoice';
  const filePath = req.file.path;

  runPythonCommand(['main.py', 'import', filePath, '--type', 'pdf', '--source', source], (error, stdout, stderr) => {
    fs.unlink(filePath, () => {});

    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Transactions extracted from PDF', output: stdout });
  });
});

// Process pending transactions
app.post('/api/process', (req, res) => {
  const limit = req.body.limit || null;
  const args = ['main.py', 'process'];
  if (limit) {
    args.push('--limit', limit.toString());
  }

  runPythonCommand(args, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Transactions processed', output: stdout });
  });
});

// Monitor accounts
app.get('/api/monitor', (req, res) => {
  runPythonCommand(['main.py', 'monitor'], (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, message: 'Accounts monitored', output: stdout });
  });
});

// Generate trial balance
app.get('/api/report/trial', (req, res) => {
  runPythonCommand(['main.py', 'report', 'trial'], (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, report: stdout });
  });
});

// Generate income statement
app.get('/api/report/income', (req, res) => {
  const args = ['main.py', 'report', 'income'];
  if (req.query.start_date) {
    args.push('--start-date', req.query.start_date);
  }
  if (req.query.end_date) {
    args.push('--end-date', req.query.end_date);
  }

  runPythonCommand(args, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, report: stdout });
  });
});

// Generate balance sheet
app.get('/api/report/balance', (req, res) => {
  const args = ['main.py', 'report', 'balance'];
  if (req.query.as_of) {
    args.push('--as-of', req.query.as_of);
  }

  runPythonCommand(args, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ success: true, report: stdout });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ Fin Easy Backend API running on port ${PORT}`);
  console.log(`📡 API available at http://localhost:${PORT}/api`);
});

