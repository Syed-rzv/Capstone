// FILE: src/components/charts/AgeHistogram.jsx
// =============================================================================
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartCard from '../common/ChartCard';
import CustomTooltip from '../common/CustomToolTip';

const AgeHistogram = ({ data }) => (
  <ChartCard title="Age Distribution">
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="range" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
        <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" fill="#22c55e" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </ChartCard>
);

export default AgeHistogram;
