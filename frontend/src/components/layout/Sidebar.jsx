// FILE: src/components/layout/Sidebar.jsx
// =============================================================================
import React from 'react';
import { Home, Upload, Filter, TrendingUp, Info, Activity } from 'lucide-react';

const Sidebar = ({ activeView, setActiveView }) => {
  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'upload', icon: Upload, label: 'Upload Data' },
    { id: 'filters', icon: Filter, label: 'Filters' },
    { id: 'visualizations', icon: TrendingUp, label: 'Visualizations' },
    { id: 'about', icon: Info, label: 'About' }
  ];

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-green-500" />
          <h1 className="text-xl font-bold text-green-500">CrisisLens</h1>
        </div>
        <p className="text-xs text-gray-400 mt-2">Emergency Analytics</p>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button key={item.id} onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}>
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;