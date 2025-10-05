import React, { useState } from 'react';
import { Calendar, Filter, X, Save, Star, Trash2, Sparkles } from 'lucide-react';
import { useFilters } from '../../context/FilterContext';

const FiltersPanel = () => {
  const { filters, setFilters, savedPresets, savePreset, loadPreset, deletePreset } = useFilters();
  const [showPresetModal, setShowPresetModal] = useState(false);
  const [newPresetName, setNewPresetName] = useState('');
  const [activePreset, setActivePreset] = useState(null);

  const emergencyTypes = ['EMS', 'Fire', 'Traffic'];

  const handleTypeToggle = (type) => {
    setFilters(prev => ({
      ...prev,
      types: prev.types.includes(type)
        ? prev.types.filter(t => t !== type)
        : [...prev.types, type]
    }));
    setActivePreset(null); // Clear active preset when manually changing filters
  };

  const handleSavePreset = () => {
    if (newPresetName.trim()) {
      savePreset(newPresetName.trim(), filters);
      setNewPresetName('');
      setShowPresetModal(false);
    }
  };

  const handleLoadPreset = (preset) => {
    loadPreset(preset);
    setActivePreset(preset.name);
  };

  const handleClearFilters = () => {
    setFilters({
      dateRange: { start: '2000-01-01', end: '2030-12-31' },
      types: [],
      district: '',
      zipcode: ''
    });
    setActivePreset(null);
  };

  const isFiltersActive = filters.types.length > 0 || filters.district || filters.zipcode;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/20 rounded-lg">
            <Filter className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-green-500">Advanced Filters</h3>
            <p className="text-xs text-gray-400">Refine your data analysis</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Save Current Filters */}
          <button
            onClick={() => setShowPresetModal(true)}
            className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 text-blue-400 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Preset
          </button>
          
          {/* Clear Filters */}
          {isFiltersActive && (
            <button
              onClick={handleClearFilters}
              className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Saved Presets */}
      {savedPresets.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Star className="w-4 h-4 text-yellow-500" />
            <h4 className="text-sm font-semibold text-gray-300">Saved Presets</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {savedPresets.map((preset, idx) => (
              <div
                key={idx}
                className={`group relative px-4 py-2 rounded-lg border transition-all cursor-pointer ${
                  activePreset === preset.name
                    ? 'bg-green-500/20 border-green-500/50 text-green-400'
                    : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-green-500/30'
                }`}
              >
                <button
                  onClick={() => handleLoadPreset(preset)}
                  className="flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span className="text-sm font-medium">{preset.name}</span>
                </button>
                
                {/* Delete Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deletePreset(preset.name);
                    if (activePreset === preset.name) setActivePreset(null);
                  }}
                  className="absolute -top-2 -right-2 p-1 bg-red-500 hover:bg-red-600 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3 text-white" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Date Range */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-green-500" />
            Date Range
          </label>
          <div className="space-y-2">
            <input
              type="date"
              value={filters.dateRange.start}
              onChange={(e) => {
                setFilters(prev => ({
                  ...prev,
                  dateRange: { ...prev.dateRange, start: e.target.value }
                }));
                setActivePreset(null);
              }}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:border-green-500 focus:outline-none"
            />
            <input
              type="date"
              value={filters.dateRange.end}
              onChange={(e) => {
                setFilters(prev => ({
                  ...prev,
                  dateRange: { ...prev.dateRange, end: e.target.value }
                }));
                setActivePreset(null);
              }}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:border-green-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Emergency Types */}
        <div className="lg:col-span-2">
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Emergency Type
          </label>
          <div className="flex gap-3">
            {emergencyTypes.map(type => (
              <label
                key={type}
                className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg cursor-pointer group hover:border-green-500/50 transition-all"
              >
                <input
                  type="checkbox"
                  checked={filters.types.includes(type)}
                  onChange={() => handleTypeToggle(type)}
                  className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-green-500 focus:ring-green-500 focus:ring-offset-0 cursor-pointer"
                />
                <span className="text-sm font-medium text-gray-300 group-hover:text-green-400 transition-colors">
                  {type}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* District Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            District
          </label>
          <input
            type="text"
            value={filters.district}
            onChange={(e) => {
              setFilters(prev => ({ ...prev, district: e.target.value }));
              setActivePreset(null);
            }}
            placeholder="Enter district name"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 placeholder-gray-500 focus:border-green-500 focus:outline-none"
          />
        </div>

        {/* Zipcode Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Zipcode
          </label>
          <input
            type="text"
            value={filters.zipcode}
            onChange={(e) => {
              setFilters(prev => ({ ...prev, zipcode: e.target.value }));
              setActivePreset(null);
            }}
            placeholder="Enter zipcode"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 placeholder-gray-500 focus:border-green-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Active Filters Summary */}
      {isFiltersActive && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">Active filters:</span>
            {filters.types.length > 0 && (
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-semibold">
                {filters.types.length} type{filters.types.length > 1 ? 's' : ''}
              </span>
            )}
            {filters.district && (
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-semibold">
                District: {filters.district}
              </span>
            )}
            {filters.zipcode && (
              <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs font-semibold">
                Zip: {filters.zipcode}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Save Preset Modal */}
      {showPresetModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <h3 className="text-xl font-bold text-green-500 mb-4">Save Filter Preset</h3>
            <p className="text-gray-400 text-sm mb-4">
              Give this filter combination a name for quick access later.
            </p>
            <input
              type="text"
              value={newPresetName}
              onChange={(e) => setNewPresetName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSavePreset()}
              placeholder="e.g., High Priority Calls"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-300 placeholder-gray-500 focus:border-green-500 focus:outline-none mb-4"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={handleSavePreset}
                className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors"
              >
                Save Preset
              </button>
              <button
                onClick={() => {
                  setShowPresetModal(false);
                  setNewPresetName('');
                }}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 rounded-lg font-semibold transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FiltersPanel;