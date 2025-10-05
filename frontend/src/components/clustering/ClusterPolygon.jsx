import { useEffect, useRef } from 'react';
import { Polygon, Popup, useMap } from 'react-leaflet';
import ClusterPopup from './ClusterPopup';

const ClusterPolygon = ({ cluster }) => {
  const map = useMap();
  const polygonRef = useRef(null);

  if (!cluster.polygon || cluster.polygon.length < 3) return null;

  const getSeverityColor = (score) => {
    if (score >= 8) return '#dc2626';
    if (score >= 6.5) return '#ea580c';
    if (score >= 5) return '#f59e0b';
    if (score >= 3.5) return '#eab308';
    return '#22c55e';
  };

  const getSeverityOpacity = (score) => {
    return Math.min(0.3 + (score / 10) * 0.4, 0.7);
  };

  const color = getSeverityColor(cluster.severity_score);
  const fillOpacity = getSeverityOpacity(cluster.severity_score);

  // Force re-render when toggled
  useEffect(() => {
    if (polygonRef.current && map) {
      map.invalidateSize();
    }
  }, [map]);

  return (
    <Polygon
      ref={polygonRef}
      positions={cluster.polygon}
      pathOptions={{
        color: color,
        weight: 2,
        fillColor: color,
        fillOpacity: fillOpacity,
      }}
      eventHandlers={{
        mouseover: (e) => {
          e.target.setStyle({ weight: 4, fillOpacity: fillOpacity + 0.2 });
        },
        mouseout: (e) => {
          e.target.setStyle({ weight: 2, fillOpacity: fillOpacity });
        },
      }}
    >
      <Popup maxWidth={350}>
        <ClusterPopup cluster={cluster} />
      </Popup>
    </Polygon>
  );
};

export default ClusterPolygon;