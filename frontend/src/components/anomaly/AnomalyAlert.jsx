import React from 'react';
import { AlertTriangle, TrendingUp } from 'lucide-react';

const AnomalyAlert = ({ anomalyCount, totalDataPoints }) => {
  if (anomalyCount === 0) return null;

  const percentage = ((anomalyCount / totalDataPoints) * 100).toFixed(1);

  return (
    <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-xl p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-red-500/20 rounded-lg">
          <AlertTriangle className="w-6 h-6 text-red-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-red-400 mb-1">
            Anomalies Detected
          </h3>
          <p className="text-gray-300 text-sm mb-2">
            Found <span className="font-bold text-white">{anomalyCount}</span> unusual spike
            {anomalyCount !== 1 ? 's' : ''} in call volume 
            <span className="text-gray-400"> ({percentage}% of data points)</span>
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <TrendingUp className="w-4 h-4" />
            <span>Points exceeding 2σ from the mean are flagged</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnomalyAlert;