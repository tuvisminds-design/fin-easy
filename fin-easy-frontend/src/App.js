import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <main className="ml-64">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/import" element={<div className="p-8"><h1 className="text-2xl font-bold">Import Transactions</h1></div>} />
            <Route path="/transactions" element={<div className="p-8"><h1 className="text-2xl font-bold">Transactions</h1></div>} />
            <Route path="/reports" element={<div className="p-8"><h1 className="text-2xl font-bold">Financial Reports</h1></div>} />
            <Route path="/monitor" element={<div className="p-8"><h1 className="text-2xl font-bold">Account Monitor</h1></div>} />
            <Route path="/settings" element={<div className="p-8"><h1 className="text-2xl font-bold">Settings</h1></div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
