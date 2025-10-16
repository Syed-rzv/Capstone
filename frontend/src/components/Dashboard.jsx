import React, { useState, useMemo } from 'react';
import { Home, TrendingUp, Info } from 'lucide-react';
import { useFilters } from '../context/FilterContext';
import useDashboardData from '../hooks/useDashboardData';
import Sidebar from './layout/Sidebar';
import FiltersPanel from './filters/FiltersPanel';
import KPICard from './kpi/KPICard';
import TimelineChart from './charts/TimelineChart';
import TypePieChart from './charts/TypePieChart';
import AgeHistogram from './charts/AgeHistogram';
import GenderDonut from './charts/GenderDonut';
import MapView from './charts/MapView';
import AnomalyAlert from './anomaly/AnomalyAlert';
import SubmitCall from '../pages/SubmitCall';

import { 
  filterData, 
  calculateKPIs, 
  aggregateTimelineData, 
  aggregateTypeData, 
  aggregateAgeData, 
  aggregateGenderData,
  detectTimelineAnomalies 
} from '../utils/dataProcessing';
import AnimatedBackground from './layout/AnimatedBackground';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const { data: rawData, loading, error, refetch, usingMockData } = useDashboardData();
  const { filters } = useFilters();

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    if (!rawData || rawData.length === 0) return [];
    return filterData(rawData, filters);
  }, [rawData, filters]);

  // Calculate KPIs
  const kpis = useMemo(() => calculateKPIs(filteredData), [filteredData]);

  // Aggregate data for charts
  const timelineData = useMemo(() => aggregateTimelineData(filteredData), [filteredData]);
  const typeData = useMemo(() => aggregateTypeData(filteredData), [filteredData]);
  const ageData = useMemo(() => aggregateAgeData(filteredData), [filteredData]);
  const genderData = useMemo(() => aggregateGenderData(filteredData), [filteredData]);

  // Detect anomalies for the alert component
  const { anomalyCount, totalDataPoints } = useMemo(() => {
    const enrichedTimeline = detectTimelineAnomalies(timelineData);
    return {
      anomalyCount: enrichedTimeline.filter(d => d.isAnomaly).length,
      totalDataPoints: timelineData.length
    };
  }, [timelineData]);

  // Prepare heatmap points for map
  const heatmapPoints = useMemo(() => {
    return filteredData.map(item => ({
      lat: item.lat,
      lng: item.lng,
      intensity: 1
    }));
  }, [filteredData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400 text-lg">Loading emergency data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-400 mb-2">Error Loading Data</h2>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  // Handle non-dashboard views
  if (activeView === 'submit') {
    return (
      <div className="min-h-screen bg-gray-950">
        <AnimatedBackground />
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <div className="ml-64 min-h-screen">
          <SubmitCall />
        </div>
      </div>
    );
  }

  if (activeView !== 'dashboard') {
    return (
      <div className="min-h-screen bg-gray-950">
        <AnimatedBackground />
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <div className="ml-64 min-h-screen flex items-center justify-center">
          <div className="text-center">
            <Info className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-green-500 mb-2">
              {activeView.charAt(0).toUpperCase() + activeView.slice(1)}
            </h2>
            <p className="text-gray-400">This section is under construction</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <AnimatedBackground />
      {/* Sidebar */}
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      {/* Main Content */}
      <div className="ml-64 min-h-screen">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <div className = "flex-1">
                <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">
                  CrisisLens Dashboard
                </h1>
                <p className="text-gray-400 mt-1">
                  Real-time emergency call analytics and insights
                </p>
              </div>
              <div className="flex items-center gap-3">
                {/* Data Summary Badge */}
                <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-green-400 font-semibold">
                      {filteredData.length.toLocaleString()} calls loaded
                    </span>
                  </div>
                </div>
                {/* Info Button */}
                <button className="p-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg transition-colors">
                  <Info className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>
          </div>

          {/* Filters Panel */}
          <FiltersPanel />

          {/* Anomaly Alert */}
          <AnomalyAlert 
            anomalyCount={anomalyCount} 
            totalDataPoints={totalDataPoints} 
          />

          {/* Refresh Controls */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
              <button
                onClick={refetch}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                {loading ? 'Refreshing...' : 'Refresh Now'}
              </button>
              <span className="text-sm text-gray-400">
                {usingMockData ? '⚠️ Using mock data' : '✅ Live data connected'} • Auto-refresh: 1min (when idle)
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Total Calls: {filteredData.length.toLocaleString()}
            </div>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <KPICard
              title="Total Calls"
              value={kpis.totalCalls.toLocaleString()}
              icon={Home}
              trend="+12.5%"
              trendUp={true}
            />
            <KPICard
              title="Most Common Type"
              value={kpis.mostCommonType}
              icon={TrendingUp}
              subtitle="Emergency Category"
            />
            <KPICard
              title="Average Age"
              value={kpis.avgAge}
              icon={Info}
              subtitle="Caller Demographics"
            />
            <KPICard
              title="Peak Hour"
              value={kpis.peakHour}
              icon={TrendingUp}
              subtitle="Highest Activity"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Timeline Chart - Full Width */}
            <TimelineChart data={timelineData} />

            {/* Type Pie Chart */}
            <TypePieChart data={typeData} />

            {/* Age Distribution */}
            <AgeHistogram data={ageData} />

            {/* Gender Distribution */}
            <GenderDonut data={genderData} />

            {/* Map View - Full Width */}
            <div className="lg:col-span-3 h-[600px]">
              <MapView filteredData={filteredData} heatmapPoints={heatmapPoints} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;