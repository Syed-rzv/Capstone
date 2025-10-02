// FILE: src/components/common/ChartCard.jsx
// =============================================================================
import React from 'react';

const ChartCard = ({ title, children, className = "" }) => (
  <div className={`bg-gray-900/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 hover:border-green-500/40 transition-all ${className}`}>
    <h3 className="text-lg font-semibold text-green-500 mb-4">{title}</h3>
    {children}
  </div>
);

export default ChartCard;