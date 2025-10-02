// FILE: src/components/charts/TimelineChart.jsx
// =============================================================================
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartCard from '../common/ChartCard';
import CustomTooltip from '../common/CustomToolTip';

const TimelineChart = ({ data }) => (
  <ChartCard title="Call Volume Over Time" className="lg:col-span-3">
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="month" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
        <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
        <Tooltip content={<CustomTooltip />} />
        <Line type="monotone" dataKey="count" stroke="#22c55e" strokeWidth={3}
          dot={{ fill: '#22c55e', r: 4 }} activeDot={{ r: 6 }} />
      </LineChart>
    </ResponsiveContainer>
  </ChartCard>
);

export default TimelineChart;