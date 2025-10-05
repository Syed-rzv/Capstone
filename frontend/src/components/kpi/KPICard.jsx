import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const KPICard = ({ title, value, icon: Icon, trend, trendUp, subtitle }) => {
  return (
    <div className="group bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-green-500/50 rounded-xl p-6 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/10 hover:-translate-y-1">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-green-500/10 rounded-lg group-hover:bg-green-500/20 transition-colors">
          <Icon className="w-6 h-6 text-green-500" />
        </div>
        
        {trend && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-bold ${
            trendUp 
              ? 'bg-green-500/10 text-green-400' 
              : 'bg-red-500/10 text-red-400'
          }`}>
            {trendUp ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {trend}
          </div>
        )}
      </div>

      {/* Content */}
      <div>
        <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
        <p className="text-3xl font-bold text-white mb-1 group-hover:text-green-400 transition-colors">
          {value}
        </p>
        {subtitle && (
          <p className="text-xs text-gray-500">{subtitle}</p>
        )}
      </div>

      {/* Animated bottom border */}
      <div className="mt-4 h-1 bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500"></div>
      </div>
    </div>
  );
};

export default KPICard;