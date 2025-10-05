import { useState } from 'react';

const MapControls = ({ onLayerToggle, activeFilters = {} }) => {
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showClusters, setShowClusters] = useState(true);
  const [showOutliers, setShowOutliers] = useState(false);
  const [timeRange, setTimeRange] = useState('all');
  const [minSeverity, setMinSeverity] = useState(0);

  const handleToggle = (layer, value) => {
    const updates = { showHeatmap, showClusters, showOutliers, timeRange, minSeverity };
    
    switch(layer) {
      case 'heatmap':
        setShowHeatmap(value);
        updates.showHeatmap = value;
        break;
      case 'clusters':
        setShowClusters(value);
        updates.showClusters = value;
        break;
      case 'outliers':
        setShowOutliers(value);
        updates.showOutliers = value;
        break;
      case 'timeRange':
        setTimeRange(value);
        updates.timeRange = value;
        break;
      case 'severity':
        setMinSeverity(value);
        updates.minSeverity = value;
        break;
      default:
        break;
    }
    
    onLayerToggle(updates);
  };

  return (
    <div className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-lg p-4 w-72">
      {/* Header */}
      <div className="mb-3 pb-2 border-b border-gray-200">
        <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2">
          🗺️ Map Layers
        </h3>
      </div>

      {/* Layer Toggles */}
      <div className="space-y-3">
        {/* Heatmap Toggle */}
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm text-gray-700 flex items-center gap-2">
            🔥 Heatmap
          </span>
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(e) => handleToggle('heatmap', e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
        </label>

        {/* Clusters Toggle */}
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm text-gray-700 flex items-center gap-2">
            📍 Cluster Zones
          </span>
          <input
            type="checkbox"
            checked={showClusters}
            onChange={(e) => handleToggle('clusters', e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
        </label>

        {/* Outliers Toggle */}
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm text-gray-700 flex items-center gap-2">
            ⚠️ Outliers
          </span>
          <input
            type="checkbox"
            checked={showOutliers}
            onChange={(e) => handleToggle('outliers', e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
        </label>
      </div>

      {/* Filters */}
      <div className="mt-4 pt-3 border-t border-gray-200 space-y-3">
        {/* Time Range Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Time Period
          </label>
          <select
            value={timeRange}
            onChange={(e) => handleToggle('timeRange', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Day</option>
            <option value="day">Daytime (6AM-6PM)</option>
            <option value="night">Nighttime (6PM-6AM)</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Min Severity: {minSeverity}/10
          </label>
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={minSeverity}
            onChange={(e) => handleToggle('severity', parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>All</span>
            <span>Critical Only</span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="text-xs font-medium text-gray-600 mb-2">Severity Scale</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-600"></div>
            <span className="text-xs text-gray-600">Critical (8-10)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-600"></div>
            <span className="text-xs text-gray-600">High (6.5-8)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-500"></div>
            <span className="text-xs text-gray-600">Medium (5-6.5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-500"></div>
            <span className="text-xs text-gray-600">Moderate (3.5-5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500"></div>
            <span className="text-xs text-gray-600">Low (&lt;3.5)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapControls;