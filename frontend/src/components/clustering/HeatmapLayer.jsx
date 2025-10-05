import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

const HeatmapLayer = ({ data, intensity = 0.6, radius = 25, blur = 15 }) => {
  const map = useMap();
  const heatLayerRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0) return;
    if (!map || !map._loaded) return;

    // Remove existing layer if any
    if (heatLayerRef.current && map.hasLayer(heatLayerRef.current)) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    const timer = setTimeout(() => {
      try {
        heatLayerRef.current = L.heatLayer(data, {
          radius: radius,
          blur: blur,
          maxZoom: 17,
          max: 1.0,
          gradient: {
            0.0: '#3b82f6',
            0.3: '#22c55e',
            0.5: '#eab308',
            0.7: '#f97316',
            1.0: '#ef4444'
          }
        }).addTo(map);
      } catch (error) {
        console.error('Heatmap rendering error:', error);
      }
    }, 100);

    return () => {
      clearTimeout(timer);
      if (heatLayerRef.current && map.hasLayer(heatLayerRef.current)) {
        map.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }
    };
  }, [map, data, radius, blur]);

  return null;
};

export default HeatmapLayer;