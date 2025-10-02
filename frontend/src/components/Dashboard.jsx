// FILE: src/components/Dashboard.jsx
// =============================================================================
import React, { useState, useMemo } from 'react';
import { Info, Phone, Users, Clock, Activity } from 'lucide-react';
import Sidebar from './layout/Sidebar';
import FiltersPanel from './filters/FiltersPanel';
import KPICard from './kpi/KPICard';
import TimelineChart from './charts/TimelineChart';
import TypePieChart from './charts/TypePieChart';
import AgeHistogram from './charts/AgeHistogram';
import GenderDonut from './charts/GenderDonut';
import MapView from './charts/MapView';
import { useFilters } from '../context/FilterContext';
import { generateMockData } from '../data/mockData';
import { filterData, calculateKPIs, aggregateTimelineData, aggregateTypeData, aggregateAgeData, aggregateGenderData } from '../utils/dataProcessing';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const mockData = useMemo(() => generateMockData(), []);
  const { filters } = useFilters();
  const filteredData = useMemo(() => filterData(mockData, filters), [mockData, filters]);
  const kpis = useMemo(() => calculateKPIs(filteredData), [filteredData]);
  const timelineData = useMemo(() => aggregateTimelineData(filteredData), [filteredData]);
  const typeData = useMemo(() => aggregateTypeData(filteredData), [filteredData]);
  const ageData = useMemo(() => aggregateAgeData(filteredData), [filteredData]);
  const genderData = useMemo(() => aggregateGenderData(filteredData), [filteredData]);
  const heatmapPoints = useMemo(() => {
    return filteredData.slice(0, 200).map((call) => ({ lat: call.latitude, lng: call.longitude, value: 1 }));
  }, [filteredData]);

  if (activeView !== 'dashboard') {
    return (
      <div className="flex h-screen bg-black">
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Info className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-green-500 mb-2">{activeView.charAt(0).toUpperCase() + activeView.slice(1)}</h2>
            <p className="text-gray-400">This section is under construction</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-black">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[1900px] mx-auto p-6 space-y-6">
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-green-500 mb-2 tracking-tight">CrisisLens</h1>
            <p className="text-gray-400 tracking-wider text-sm">Real-Time Emergency Analytics Dashboard</p>
          </div>
          <FiltersPanel mockData={mockData} />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard icon={Phone} label="Total Calls" value={kpis.totalCalls.toLocaleString()} gradient="bg-gradient-to-br from-green-500/5 to-green-600/10" />
            <KPICard icon={Activity} label="Most Common" value={kpis.mostCommonType} gradient="bg-gradient-to-br from-green-600/5 to-emerald-600/10" />
            <KPICard icon={Users} label="Average Age" value={kpis.avgAge} gradient="bg-gradient-to-br from-emerald-500/5 to-green-600/10" />
            <KPICard icon={Clock} label="Peak Hour" value={kpis.peakHour} gradient="bg-gradient-to-br from-emerald-600/5 to-green-500/10" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <TimelineChart data={timelineData} />
            <TypePieChart data={typeData} />
            <AgeHistogram data={ageData} />
            <GenderDonut data={genderData} />
          </div>
          <MapView filteredData={filteredData} heatmapPoints={heatmapPoints} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;