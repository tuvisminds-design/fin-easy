import React, { useState, useEffect } from 'react';
import { Upload, FileText, BarChart3, TrendingUp, DollarSign, AlertCircle } from 'lucide-react';
import FinkoCharacter from './FinkoCharacter';
import axios from 'axios';

const API_BASE = 'http://localhost:5001/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalTransactions: 0,
    pendingTransactions: 0,
    accountsMonitored: 6,
    lastReport: null
  });
  const [monitoringStatus, setMonitoringStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load initial stats
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // You can add API endpoints to get actual stats
      // For now, using placeholder data
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleMonitorAccounts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/monitor`);
      setMonitoringStatus(response.data);
    } catch (error) {
      console.error('Error monitoring accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Transactions',
      value: stats.totalTransactions,
      icon: FileText,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Pending Processing',
      value: stats.pendingTransactions,
      icon: AlertCircle,
      color: 'bg-yellow-500',
      change: '3 new'
    },
    {
      title: 'Accounts Monitored',
      value: stats.accountsMonitored,
      icon: TrendingUp,
      color: 'bg-green-500',
      change: 'All healthy'
    },
    {
      title: 'Total Balance',
      value: '$0.00',
      icon: DollarSign,
      color: 'bg-purple-500',
      change: 'Updated'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 mb-8">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">Welcome back! FINKO is here to help with your accounting.</p>
            </div>
            <FinkoCharacter size="large" animation="idle" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 pb-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                  <span className="text-sm text-green-600 font-semibold">{stat.change}</span>
                </div>
                <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Account Monitoring Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Account Monitoring</h2>
              <FinkoCharacter size="small" animation="calculating" />
            </div>
            <p className="text-gray-600 mb-4">
              FINKO continuously monitors your key accounts for accuracy and anomalies.
            </p>
            <button
              onClick={handleMonitorAccounts}
              disabled={loading}
              className="w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Monitoring...</span>
                </>
              ) : (
                <>
                  <TrendingUp size={20} />
                  <span>Run Account Check</span>
                </>
              )}
            </button>
            {monitoringStatus && (
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">{monitoringStatus.message}</p>
              </div>
            )}
          </div>

          {/* Quick Import Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Quick Import</h2>
              <FinkoCharacter size="small" animation="pointing" />
            </div>
            <p className="text-gray-600 mb-4">
              Import transactions from CSV, Excel, images, or PDFs. FINKO will process them automatically.
            </p>
            <div className="space-y-2">
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2">
                <Upload size={20} />
                <span>Import Transactions</span>
              </button>
            </div>
          </div>
        </div>

        {/* FINKO Message */}
        <div className="bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-start space-x-4">
            <FinkoCharacter size="medium" animation="celebrate" />
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2">Hello! I'm FINKO, MICO's Cousin!</h3>
              <p className="text-teal-100 mb-4">
                I'm here to help you automate your accounting tasks. I can import transactions, 
                generate journal entries, monitor your accounts, and create financial reports. 
                Let's get started!
              </p>
              <div className="flex space-x-3">
                <button className="bg-white text-teal-600 font-semibold py-2 px-4 rounded-lg hover:bg-teal-50 transition-colors">
                  Get Started
                </button>
                <button className="bg-teal-700 text-white font-semibold py-2 px-4 rounded-lg hover:bg-teal-800 transition-colors">
                  Learn More
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
