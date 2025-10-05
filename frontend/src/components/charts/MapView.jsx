import { useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useClusterData, useHeatmapData } from '../../hooks/useClusterData';
import HeatmapLayer from '../clustering/HeatmapLayer';
import ClusterPolygon from '../clustering/ClusterPolygon';
import MapControls from '../clustering/MapControls';

// Fix Leaflet default marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom outlier marker icon (yellow)
const outlierIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const MapView = ({ filteredData = [], heatmapPoints = [], initialCenter = [40.7128, -74.0060],  initialZoom = 11 }) => {
  const [layerSettings, setLayerSettings] = useState({
    showHeatmap: false,
    showClusters: true,
    showOutliers: false,
    timeRange: 'all',
    minSeverity: 0
  });

  // Fetch cluster data with filters
  const { clusters, outliers, loading: clusterLoading, error: clusterError } = useClusterData(
    layerSettings.timeRange,
    layerSettings.minSeverity > 0 ? layerSettings.minSeverity : null
  );

  // Fetch heatmap data
  const { heatmapData, loading: heatmapLoading } = useHeatmapData();

  // Filter clusters by severity if needed
  const filteredClusters = useMemo(() => {
    return clusters.filter(c => c.severity_score >= layerSettings.minSeverity);
  }, [clusters, layerSettings.minSeverity]);

  const handleLayerToggle = (newSettings) => {
    setLayerSettings(newSettings);
  };

  if (clusterError) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-600 font-semibold mb-2">Failed to load map data</p>
          <p className="text-sm text-gray-600">{clusterError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full style={{ minHeight: '600px' }}">
      {/* Loading Overlay */}
      {(clusterLoading || heatmapLoading) && (
        <div className="absolute inset-0 bg-white bg-opacity-75 z-[2000] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading cluster analysis...</p>
          </div>
        </div>
      )}

      {/* Map Controls */}
      <MapControls onLayerToggle={handleLayerToggle} activeFilters={layerSettings} />

      {/* Map Container */}
      <MapContainer
        center={initialCenter}
        zoom={initialZoom}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Heatmap Layer */}
        {layerSettings.showHeatmap && heatmapData.length > 0 && (
          <HeatmapLayer data={heatmapData} />
        )}

        {/* Cluster Polygons */}
        {layerSettings.showClusters && filteredClusters.map((cluster) => (
          <ClusterPolygon key={cluster.cluster_id} cluster={cluster} />
        ))}

        {/* Outlier Markers */}
        {layerSettings.showOutliers && outliers.map((outlier, idx) => (
          <Marker
            key={`outlier-${idx}`}
            position={[outlier.lat, outlier.lon]}
            icon={outlierIcon}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-bold text-sm text-gray-800 mb-2">
                  ⚠️ Isolated Call
                </h4>
                <div className="text-xs space-y-1">
                  <div>
                    <span className="text-gray-600">Type:</span>{' '}
                    <span className="font-semibold">{outlier.call_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Response:</span>{' '}
                    <span className="font-semibold">{outlier.response_time} min</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Time:</span>{' '}
                    <span className="font-semibold">
                      {new Date(outlier.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-orange-600">
                  This area may be underserved
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Stats Summary */}
      {!clusterLoading && (
        <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-3">
          <div className="text-xs space-y-1">
            <div className="font-semibold text-gray-800 mb-1">Quick Stats</div>
            <div className="text-gray-600">
              Clusters: <span className="font-semibold text-gray-900">{filteredClusters.length}</span>
            </div>
            {layerSettings.showOutliers && (
              <div className="text-gray-600">
                Outliers: <span className="font-semibold text-gray-900">{outliers.length}</span>
              </div>
            )}
            <div className="text-gray-600">
              Time: <span className="font-semibold text-gray-900 capitalize">{layerSettings.timeRange}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;