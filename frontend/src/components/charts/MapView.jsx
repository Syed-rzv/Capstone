// FILE: src/components/charts/MapView.jsx
// =============================================================================
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import { Layers } from 'lucide-react';
import L from 'leaflet';
import ChartCard from '../common/ChartCard';

const HeatmapOverlay = ({ points, visible }) => {
  const map = useMap();
  useEffect(() => {
    if (!map || !points.length || !visible) return;
    const heatmapLayer = L.layerGroup();
    points.forEach(point => {
      const circle = L.circleMarker([point.lat, point.lng], {
        radius: 10, fillColor: '#22c55e', color: 'transparent', fillOpacity: 0.2, weight: 0
      });
      circle.addTo(heatmapLayer);
    });
    heatmapLayer.addTo(map);
    return () => { map.removeLayer(heatmapLayer); };
  }, [map, points, visible]);
  return null;
};

const MapView = ({ filteredData, heatmapPoints }) => {
  const [showMarkers, setShowMarkers] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);

  return (
    <ChartCard title="Geographic Distribution">
      <div className="absolute top-6 right-6 z-[1000] bg-gray-800/95 backdrop-blur-sm border border-green-500/30 rounded-lg p-3 shadow-xl">
        <div className="flex items-center gap-2 mb-2">
          <Layers className="w-4 h-4 text-green-500" />
          <span className="text-xs font-semibold text-green-500 uppercase tracking-wider">Layers</span>
        </div>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer group">
            <input type="checkbox" checked={showMarkers} onChange={(e) => setShowMarkers(e.target.checked)}
              className="w-4 h-4 rounded border-green-500/25 bg-gray-700 text-green-500 focus:ring-green-500/50" />
            <span className="text-sm text-gray-400 group-hover:text-green-500 transition-colors">Markers</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer group">
            <input type="checkbox" checked={showHeatmap} onChange={(e) => setShowHeatmap(e.target.checked)}
              className="w-4 h-4 rounded border-green-500/25 bg-gray-700 text-green-500 focus:ring-green-500/50" />
            <span className="text-sm text-gray-400 group-hover:text-green-500 transition-colors">Heatmap</span>
          </label>
        </div>
      </div>
      <div className="h-96 w-full rounded-xl border border-green-500/10 overflow-hidden">
        <MapContainer center={[40.2, -75.4]} zoom={10} scrollWheelZoom={true} className="h-full w-full">
          <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>' />
          {showMarkers && (
            <MarkerClusterGroup chunkedLoading maxClusterRadius={40}>
              {filteredData.slice(0, 200).map((call) => (
                <Marker key={call.id} position={[call.latitude, call.longitude]}>
                  <Popup>
                    <div className="text-sm">
                      <strong>Type:</strong> {call.emergency_type}<br />
                      <strong>Age:</strong> {call.caller_age}<br />
                      <strong>Gender:</strong> {call.caller_gender}<br />
                      <strong>Township:</strong> {call.township}<br />
                      <strong>Zipcode:</strong> {call.zipcode}
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MarkerClusterGroup>
          )}
          {showHeatmap && <HeatmapOverlay points={heatmapPoints} visible={showHeatmap} />}
        </MapContainer>
      </div>
    </ChartCard>
  );
};

export default MapView;