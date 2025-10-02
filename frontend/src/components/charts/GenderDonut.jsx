// FILE: src/components/charts/GenderDonut.jsx
// =============================================================================
import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import ChartCard from '../common/ChartCard';
import CustomTooltip from '../common/CustomToolTip';

const COLORS = ['#22c55e', '#15803d', '#86efac', '#166534'];

const GenderDonut = ({ data }) => (
  <ChartCard title="Gender Distribution">
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={70} outerRadius={100}
          paddingAngle={5} dataKey="count" label={(entry) => entry.gender}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  </ChartCard>
);

export default GenderDonut;