import React, { useState, createContext, useContext, useMemo, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {Home, Upload, Filter, TrendingUp, Info, Calendar, MapPin, Users, Phone, Clock, Activity} from 'lucide-react';

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import './markercluster.css';

import L from 'leaflet';
import h337 from 'heatmap.js';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadowUrl from 'leaflet/dist/images/marker-shadow.png';

// Set default Leaflet marker icon (Vite/ESM-compatible)
const DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl: iconShadowUrl,
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  iconSize: [25, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl: iconShadowUrl,
});


// Mock Data Generator
const generateMockData = () => {
  const types = ['EMS', 'Fire', 'Traffic'];
  const townships = ['NEW HANOVER', 'HATFIELD TOWNSHIP', 'NORRISTOWN', 'LOWER POTTSGROVE'];
  const zipcodes = ['19525', '19446', '19401', '19464'];
  const genders = ['Male', 'Female', 'Other'];
  const sampleData = [
    { id: 1, latitude: 40.2979, longitude: -75.5813, description: 'Fire: GAS-ODOR/LEAK' },
    { id: 2, latitude: 40.2581, longitude: -75.2647, description: 'EMS: BACK PAINS/INJURY' },
    { id: 3, latitude: 40.1212, longitude: -75.352, description: 'EMS: CARDIAC EMERGENCY' },
    { id: 4, latitude: 40.3454, longitude: -75.1521, description: 'EMS: BREATHING PROBLEMS' },
    { id: 5, latitude: 40.2111, longitude: -75.4442, description: 'EMS: FALL/INJURY' },
    { id: 6, latitude: 40.1892, longitude: -75.5123, description: 'Fire: SMOKE/ODOR' },
    { id: 7, latitude: 40.2333, longitude: -75.3888, description: 'EMS: HEART ATTACK' },
    { id: 8, latitude: 40.1555, longitude: -75.2999, description: 'EMS: CHEST PAINS/INJURY' },
    { id: 9, latitude: 40.2777, longitude: -75.6222, description: 'Fire: ELECTRICITY/ODOR' },
    { id: 10, latitude: 40.1988, longitude: -75.3333, description: 'EMS: DIABETIC EMERGENCY' },
  ];
  
  const data = [];
  const startDate = new Date('2015-01-01');
  const endDate = new Date('2015-12-31');
  
  for (let i = 0; i < 500; i++) {
    const randomDate = new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()));
    data.push({
      id: i + 1,
      timestamp: randomDate.toISOString(),
      emergency_type: types[Math.floor(Math.random() * types.length)],
      caller_age: Math.floor(Math.random() * 70) + 18,
      caller_gender: genders[Math.floor(Math.random() * genders.length)],
      latitude: 40.1 + Math.random() * 0.3,
      longitude: -75.6 + Math.random() * 0.3,
      township: townships[Math.floor(Math.random() * townships.length)],
      zipcode: zipcodes[Math.floor(Math.random() * zipcodes.length)],
      emergency_title: `Emergency ${i + 1}`,
    });
  }
  return data;
};

// Filter Context
const FilterContext = createContext();

const FilterProvider = ({ children }) => {
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

const useFilters = () => useContext(FilterContext);

const HeatmapOverlay = ({ points }) => {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    // Create a div for heatmap
    const container = L.DomUtil.create('div');
    const cfg = {
      radius: 25,
      maxOpacity: 0.8,
      scaleRadius: true,
      useLocalExtrema: false,
      latField: 'lat',
      lngField: 'lng',
      valueField: 'value',
    };
    const heatmapInstance = h337.create({ container, ...cfg });

    const data = {
      max: Math.max(...points.map(p => p.value)),
      data: points.map(p => ({ lat: p.lat, lng: p.lng, value: p.value })),
    };
    heatmapInstance.setData(data);

    const canvasOverlay = L.imageOverlay(heatmapInstance.getDataURL(), map.getBounds()).addTo(map);

    const updateOverlay = () => {
      canvasOverlay.setBounds(map.getBounds());
      canvasOverlay.setUrl(heatmapInstance.getDataURL());
    };

    map.on('moveend zoomend', updateOverlay);

    return () => {
      map.off('moveend zoomend', updateOverlay);
      map.removeLayer(canvasOverlay);
    };
  }, [map, points]);

  return null;
};

// Sidebar Component
const Sidebar = ({ activeView, setActiveView }) => {
  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'upload', icon: Upload, label: 'Upload Data' },
    { id: 'filters', icon: Filter, label: 'Filters' },
    { id: 'visualizations', icon: TrendingUp, label: 'Visualizations' },
    { id: 'about', icon: Info, label: 'About' }
  ];

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-green-500" />
          <h1 className="text-xl font-bold text-green-500">CrisisLens</h1>
        </div>
        <p className="text-xs text-gray-400 mt-2">Emergency Analytics</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive 
                  ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};

// Filters Panel Component
const FiltersPanel = ({ mockData }) => {
  const { filters, setFilters } = useFilters();
  
  const uniqueTypes = [...new Set(mockData.map(d => d.emergency_type))];
  const uniqueTownships = [...new Set(mockData.map(d => d.township))].sort();
  const uniqueZipcodes = [...new Set(mockData.map(d => d.zipcode))].sort();

  const handleTypeToggle = (type) => {
    setFilters(prev => ({
      ...prev,
      types: prev.types.includes(type)
        ? prev.types.filter(t => t !== type)
        : [...prev.types, type]
    }));
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Date Range */}
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <Calendar className="w-4 h-4" />
            Date Range
          </label>
          <div className="space-y-2">
            <input
              type="date"
              value={filters.dateRange.start}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, start: e.target.value }
              }))}
              className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            />
            <input
              type="date"
              value={filters.dateRange.end}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, end: e.target.value }
              }))}
              className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            />
          </div>
        </div>

        {/* Emergency Type */}
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <Activity className="w-4 h-4" />
            Emergency Type
          </label>
          <div className="space-y-2">
            {uniqueTypes.map(type => (
              <label key={type} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={filters.types.includes(type)}
                  onChange={() => handleTypeToggle(type)}
                  className="w-4 h-4 rounded border-green-500/25 bg-gray-800 text-green-500 focus:ring-green-500/50"
                />
                <span className="text-sm text-gray-400 group-hover:text-green-500 transition-colors">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Township */}
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <MapPin className="w-4 h-4" />
            Township
          </label>
          <select
            value={filters.township}
            onChange={(e) => setFilters(prev => ({ ...prev, township: e.target.value }))}
            className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50"
          >
            <option value="">All Townships</option>
            {uniqueTownships.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        {/* Zipcode */}
        <div>
          <label className="flex items-center gap-2 text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">
            <MapPin className="w-4 h-4" />
            Zipcode
          </label>
          <select
            value={filters.zipcode}
            onChange={(e) => setFilters(prev => ({ ...prev, zipcode: e.target.value }))}
            className="w-full bg-gray-800 border border-green-500/25 rounded-lg px-3 py-2 text-sm text-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50"
          >
            <option value="">All Zipcodes</option>
            {uniqueZipcodes.map(z => (
              <option key={z} value={z}>{z}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

// KPI Card Component
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

// Chart Card Wrapper
const ChartCard = ({ title, children, className = "" }) => (
  <div className={`bg-gray-900/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 hover:border-green-500/40 transition-all ${className}`}>
    <h3 className="text-lg font-semibold text-green-500 mb-4">{title}</h3>
    {children}
  </div>
);

// Custom Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-900 border border-green-500/30 rounded-lg p-3 shadow-xl">
        <p className="text-sm text-gray-300 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Main Dashboard Component
const Dashboard = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const mockData = useMemo(() => generateMockData(), []);
  const { filters } = useFilters();

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    return mockData.filter(item => {
      const itemDate = new Date(item.timestamp);
      const startDate = new Date(filters.dateRange.start);
      const endDate = new Date(filters.dateRange.end);

      const dateMatch = itemDate >= startDate && itemDate <= endDate;
      const typeMatch = filters.types.length === 0 || filters.types.includes(item.emergency_type);
      const townMatch = !filters.township || item.township === filters.township;
      const zipMatch = !filters.zipcode || item.zipcode === filters.zipcode;

      return dateMatch && typeMatch && townMatch && zipMatch;
    });
  }, [mockData, filters]);

  // Heatmap Points
  const heatmapPoints = useMemo(() => {
    return mockData.map((call) => ({
    lat: call.latitude,
    lng: call.longitude,
    intensity: 1,
  }));
  }, [mockData]);

  // Calculate KPIs
  const totalCalls = filteredData.length;
  const topType = filteredData.length > 0
    ? filteredData.reduce((acc, curr) => {
        acc[curr.emergency_type] = (acc[curr.emergency_type] || 0) + 1;
        return acc;
      }, {})
    : {};
  const mostCommonType = Object.keys(topType).length > 0
    ? Object.entries(topType).sort((a, b) => b[1] - a[1])[0][0]
    : '—';

  const avgAge = filteredData.length > 0
    ? Math.round(filteredData.reduce((sum, d) => sum + d.caller_age, 0) / filteredData.length)
    : '—';

  const peakHour = filteredData.length > 0
    ? (() => {
        const hours = filteredData.map(d => new Date(d.timestamp).getHours());
        const hourCounts = hours.reduce((acc, h) => {
          acc[h] = (acc[h] || 0) + 1;
          return acc;
        }, {});
        const peak = Object.entries(hourCounts).sort((a, b) => b[1] - a[1])[0][0];
        return `${String(peak).padStart(2, '0')}:00`;
      })()
    : '—';

  // Timeline data (monthly aggregation)
  const timelineData = useMemo(() => {
    const monthCounts = {};
    filteredData.forEach(item => {
      const month = new Date(item.timestamp).toISOString().slice(0, 7);
      monthCounts[month] = (monthCounts[month] || 0) + 1;
    });
    return Object.entries(monthCounts)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([month, count]) => ({ month, count }));
  }, [filteredData]);

  // Type breakdown data
  const typeData = useMemo(() => {
    const counts = {};
    filteredData.forEach(item => {
      counts[item.emergency_type] = (counts[item.emergency_type] || 0) + 1;
    });
    return Object.entries(counts).map(([type, count]) => ({ type, count }));
  }, [filteredData]);

  // Age distribution data
  const ageData = useMemo(() => {
    const bins = [
      { range: '18-25', min: 18, max: 25, count: 0 },
      { range: '26-35', min: 26, max: 35, count: 0 },
      { range: '36-45', min: 36, max: 45, count: 0 },
      { range: '46-55', min: 46, max: 55, count: 0 },
      { range: '56+', min: 56, max: 100, count: 0 }
    ];

    filteredData.forEach(item => {
      const bin = bins.find(b => item.caller_age >= b.min && item.caller_age <= b.max);
      if (bin) bin.count++;
    });

    return bins;
  }, [filteredData]);

  // Gender distribution data
  const genderData = useMemo(() => {
    const counts = {};
    filteredData.forEach(item => {
      counts[item.caller_gender] = (counts[item.caller_gender] || 0) + 1;
    });
    return Object.entries(counts).map(([gender, count]) => ({ gender, count }));
  }, [filteredData]);

  const COLORS = ['#22c55e', '#15803d', '#86efac', '#166534'];

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
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-green-500 mb-2 tracking-tight">
              CrisisLens
            </h1>
            <p className="text-gray-400 tracking-wider text-sm">Real-Time Emergency Analytics Dashboard</p>
          </div>

          {/* Filters */}
          <FiltersPanel mockData={mockData} />

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              icon={Phone}
              label="Total Calls"
              value={totalCalls.toLocaleString()}
              gradient="bg-gradient-to-br from-green-500/5 to-green-600/10"
            />
            <KPICard
              icon={Activity}
              label="Most Common"
              value={mostCommonType}
              gradient="bg-gradient-to-br from-green-600/5 to-emerald-600/10"
            />
            <KPICard
              icon={Users}
              label="Average Age"
              value={avgAge}
              gradient="bg-gradient-to-br from-emerald-500/5 to-green-600/10"
            />
            <KPICard
              icon={Clock}
              label="Peak Hour"
              value={peakHour}
              gradient="bg-gradient-to-br from-emerald-600/5 to-green-500/10"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Timeline Chart - Full Width */}
            <ChartCard title="Call Volume Over Time" className="lg:col-span-3">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="month" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#22c55e"
                    strokeWidth={3}
                    dot={{ fill: '#22c55e', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Type Pie Chart */}
            <ChartCard title="Emergency Type Breakdown">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="count"
                    label={(entry) => entry.type}
                  >
                    {typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Age Distribution */}
            <ChartCard title="Age Distribution">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ageData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="range" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#22c55e" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Gender Distribution */}
            <ChartCard title="Gender Distribution">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={genderData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="count"
                    label={(entry) => entry.gender}
                  >
                    {genderData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Map Placeholder */}
          <ChartCard title="Geographic Distribution">
            <div className="h-96 w-full rounded-xl border border-green-500/10 overflow-hidden">
              <MapContainer
                center={[40.0, -75.0]} // approximate center
                zoom={10}
                scrollWheelZoom={true}
                className="h-full w-full"
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                   attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
                />

                {/* Marker Clusters */}
                <MarkerClusterGroup chunkedLoading maxClusterRadius={40}>
                  {filteredData.slice(0, 200).map((call) => (
                    <Marker key={call.id} position={[call.latitude, call.longitude]}>
                      <Popup>
                        <div className="text-sm">
                          <strong>Type:</strong> {call.emergency_type}
                          <br />
                          <strong>Age:</strong> {call.caller_age}
                          <br />
                          <strong>Gender:</strong> {call.caller_gender}
                          <br />
                          <strong>Township:</strong> {call.township}
                          <br />
                          <strong>Zipcode:</strong> {call.zipcode}
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MarkerClusterGroup>

                {/* Heatmap Overlay */}
                <HeatmapOverlay points = {heatmapPoints} />
              </MapContainer>
            </div>
          </ChartCard>
        </div>
      </div>
    </div>
  );
};

// Main App Component
export default function App() {
  return (
    <FilterProvider>
      <Dashboard />
    </FilterProvider>
  );
}
