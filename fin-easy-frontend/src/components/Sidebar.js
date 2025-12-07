import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Upload, FileText, BarChart3, TrendingUp, Settings, Calculator } from 'lucide-react';
import FinkoCharacter from './FinkoCharacter';

const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/import', icon: Upload, label: 'Import Transactions' },
    { path: '/transactions', icon: FileText, label: 'Transactions' },
    { path: '/reports', icon: BarChart3, label: 'Financial Reports' },
    { path: '/monitor', icon: TrendingUp, label: 'Account Monitor' },
    { path: '/settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-teal-600 to-teal-800 text-white shadow-2xl">
      <div className="flex flex-col h-full p-6">
        {/* FINKO Header */}
        <div className="flex flex-col items-center mb-8">
          <FinkoCharacter size="medium" animation="idle" />
          <h1 className="text-2xl font-bold mt-4 text-center">Fin Easy</h1>
          <p className="text-teal-200 text-sm mt-1">FINKO's Accounting Bot</p>
          <p className="text-teal-300 text-xs mt-2 italic">MICO's Cousin</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-white text-teal-700 shadow-lg transform scale-105'
                        : 'text-teal-100 hover:bg-teal-700 hover:text-white'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="mt-auto pt-4 border-t border-teal-500">
          <p className="text-xs text-teal-300 text-center">
            Powered by FINKO
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
