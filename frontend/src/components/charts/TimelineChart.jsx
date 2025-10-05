import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot } from 'recharts';
import ChartCard from '../common/ChartCard';
import CustomTooltip from '../common/CustomTooltip';
import { detectTimelineAnomalies } from '../../utils/dataProcessing';

const TimelineChart = ({ data }) => {
  // Detect anomalies in the data
  const enrichedData = useMemo(() => {
    return detectTimelineAnomalies(data);
  }, [data]);

  // Extract only anomalous points for red markers
  const anomalyPoints = useMemo(() => {
    return enrichedData.filter(item => item.isAnomaly);
  }, [enrichedData]);

  return (
    <ChartCard title="Call Volume Over Time" className="lg:col-span-3">
      {/* Anomaly count indicator */}
      {anomalyPoints.length > 0 && (
        <div className="mb-3 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg inline-block">
          <span className="text-red-400 text-sm font-semibold">
            ⚠️ {anomalyPoints.length} anomal{anomalyPoints.length === 1 ? 'y' : 'ies'} detected
          </span>
        </div>
      )}
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={enrichedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis 
            dataKey="month" 
            stroke="#9ca3af" 
            tick={{ fill: '#9ca3af' }}
          />
          <YAxis 
            stroke="#9ca3af" 
            tick={{ fill: '#9ca3af' }}
          />
          <Tooltip content={<CustomTooltip chartType="timeline" />} />
          
          {/* Main line */}
          <Line
            type="monotone"
            dataKey="count"
            stroke="#22c55e"
            strokeWidth={3}
            dot={{ fill: '#22c55e', r: 4 }}
            activeDot={{ r: 6 }}
          />

          {/* Anomaly markers - red pulsing dots */}
          {anomalyPoints.map((point, idx) => (
            <ReferenceDot
              key={`anomaly-${idx}`}
              x={point.month}
              y={point.count}
              r={8}
              fill="#ef4444"
              stroke="#dc2626"
              strokeWidth={2}
              opacity={0.8}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};

export default TimelineChart;