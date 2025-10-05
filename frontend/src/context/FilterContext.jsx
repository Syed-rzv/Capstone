import React, { createContext, useContext, useState, useCallback } from 'react';

const FilterContext = createContext();

export const useFilters = () => useContext(FilterContext);

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    dateRange: {
      start: '2000-01-01',
      end: '2030-12-31'
    },
    types: [],
    district: '',
    zipcode: ''
  });

  // ============ NEW: Saved Presets State ============
  const [savedPresets, setSavedPresets] = useState([
    {
      name: "High Priority",
      filters: { types: ['Fire', 'EMS'], dateRange: { start: '2000-01-01', end: '2030-12-31' } }
    },
    {
      name: "Traffic Only",
      filters: { types: ['Traffic'], dateRange: { start: '2000-01-01', end: '2030-12-31' } }
    }
  ]);

  const setDynamicDateRange = useCallback((data) => {
    if (!data || data.length === 0) return;
    
    const dates = data.map(item => new Date(item.timestamp));
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));
    
    setFilters(prev => ({
      ...prev,
      dateRange: {
        start: minDate.toISOString().split('T')[0],
        end: maxDate.toISOString().split('T')[0]
      }
    }));
  }, []);

  // ============ NEW: Preset Functions ============
  const savePreset = useCallback((name, currentFilters) => {
    setSavedPresets(prev => [...prev, { name, filters: currentFilters }]);
  }, []);

  const loadPreset = useCallback((preset) => {
    setFilters(preset.filters);
  }, []);

  const deletePreset = useCallback((presetName) => {
    setSavedPresets(prev => prev.filter(p => p.name !== presetName));
  }, []);

  return (
    <FilterContext.Provider value={{ 
      filters, 
      setFilters, 
      setDynamicDateRange,
      savedPresets,
      savePreset,
      loadPreset,
      deletePreset
    }}>
      {children}
    </FilterContext.Provider>
  );
};