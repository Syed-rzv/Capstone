// FILE: src/App.jsx
// =============================================================================
import React from 'react';
import { FilterProvider } from './context/FilterContext';
import Dashboard from './components/Dashboard';

export default function App() {
  return (
    <FilterProvider>
      <Dashboard />
    </FilterProvider>
  );
}