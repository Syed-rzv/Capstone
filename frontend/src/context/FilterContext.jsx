// FILE: src/context/FilterContext.jsx
// =============================================================================
import React, { createContext, useContext, useState } from 'react';

const FilterContext = createContext();

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    dateRange: { start: '2015-01-01', end: '2015-12-31' },
    types: [],
    township: '',
    zipcode: ''
  });

  return (
    <FilterContext.Provider value={{ filters, setFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => useContext(FilterContext);