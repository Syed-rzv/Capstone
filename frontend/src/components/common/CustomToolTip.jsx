import React from 'react';

const CustomTooltip = ({ active, payload, label, chartType }) => {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload;

  // Different tooltip styles based on chart type
  if (chartType === 'timeline') {
    const percentAboveAvg = data.avgValue 
      ? (((data.count - data.avgValue) / data.avgValue) * 100).toFixed(1)
      : null;

    return (
      <div className="bg-gray-900 border border-green-500/30 rounded-lg p-4 shadow-xl min-w-[200px]">
        <p className="text-sm font-bold text-green-400 mb-2">{label}</p>
        <div className="space-y-1 text-sm">
          <p className="text-gray-300">
            📞 Calls: <span className="font-semibold text-white">{data.count}</span>
          </p>
          {data.avgValue && (
            <p className="text-gray-300">
              📊 Average: <span className="font-semibold text-white">{data.avgValue}</span>
            </p>
          )}
          {percentAboveAvg && (
            <p className={`font-semibold ${parseFloat(percentAboveAvg) > 0 ? 'text-orange-400' : 'text-blue-400'}`}>
              {parseFloat(percentAboveAvg) > 0 ? '↑' : '↓'} {Math.abs(percentAboveAvg)}% from avg
            </p>
          )}
          {data.isAnomaly && (
            <div className="mt-2 pt-2 border-t border-red-500/30">
              <p className="text-red-400 font-semibold flex items-center gap-1">
                ⚠️ Anomaly Detected
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Z-score: {data.zScore}σ
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default tooltip for other charts
  return (
    <div className="bg-gray-900 border border-green-500/30 rounded-lg p-3 shadow-xl">
      <p className="text-sm text-gray-300 mb-1">{label}</p>
      {payload.map((entry, index) => (
        <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
};

export default CustomTooltip;