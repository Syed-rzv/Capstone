// FILE: src/components/kpi/KPICard.jsx
// =============================================================================
import React from 'react';

const KPICard = ({ icon: Icon, label, value, gradient }) => (
  <div className={`relative overflow-hidden rounded-2xl border border-green-500/20 p-6 transition-all hover:scale-105 hover:border-green-500/40 ${gradient}`}>
    <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/5 rounded-full -mr-16 -mt-16" />
    <div className="relative">
      <Icon className="w-8 h-8 text-green-500 mb-3" />
      <div className="text-3xl font-bold text-green-500 mb-1">{value}</div>
      <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">{label}</div>
    </div>
  </div>
);

export default KPICard;


