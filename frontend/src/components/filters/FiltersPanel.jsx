// FILE: src/components/filters/FiltersPanel.jsx
// =============================================================================
import React from 'react';
import { Calendar, Activity, MapPin } from 'lucide-react';
import { useFilters } from '../../context/FilterContext';

const FiltersPanel = ({ mockData }) => {
  const { filters, setFilters } = useFilters();
  const uniqueTypes = [...new Set(mockData.map(d => d.emergency_type))];
  const uniqueTownships = [...new Set(mockData.map(d => d.township))].sort();
  const uniqueZipcodes = [...new Set(mockData.map(d => d.zipcode))].sort();

  const handleTypeToggle = (type) => {
    setFilters(prev => ({
      ...prev,
      types: prev.types.includes(type) ? prev.types.filter(t => t !== type) : [...prev.types, type]
    }));
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <Calendar className="w-4 h-4" />Date Range
          </label>
          <div className="space-y-2">
            <input type="date" value={filters.dateRange.start}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: { ...prev.dateRange, start: e.target.value }}))}
              className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50" />
            <input type="date" value={filters.dateRange.end}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: { ...prev.dateRange, end: e.target.value }}))}
              className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50" />
          </div>
        </div>
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <Activity className="w-4 h-4" />Emergency Type
          </label>
          <div className="space-y-2">
            {uniqueTypes.map(type => (
              <label key={type} className="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" checked={filters.types.includes(type)} onChange={() => handleTypeToggle(type)}
                  className="w-4 h-4 rounded border-green-500/25 bg-gray-800 text-green-500 focus:ring-green-500/50" />
                <span className="text-sm text-gray-400 group-hover:text-green-500 transition-colors">{type}</span>
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <MapPin className="w-4 h-4" />Township
          </label>
          <select value={filters.township} onChange={(e) => setFilters(prev => ({ ...prev, township: e.target.value }))}
            className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50">
            <option value="">All Townships</option>
            {uniqueTownships.map(t => (<option key={t} value={t}>{t}</option>))}
          </select>
        </div>
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <MapPin className="w-4 h-4" />Zipcode
          </label>
          <select value={filters.zipcode} onChange={(e) => setFilters(prev => ({ ...prev, zipcode: e.target.value }))}
            className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50">
            <option value="">All Zipcodes</option>
            {uniqueZipcodes.map(z => (<option key={z} value={z}>{z}</option>))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default FiltersPanel;