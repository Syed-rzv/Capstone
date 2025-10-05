import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000';

export const useClusterData = (timeRange = 'all', minSeverity = null) => {
  const [clusters, setClusters] = useState([]);
  const [outliers, setOutliers] = useState([]);
  const [temporalAnalysis, setTemporalAnalysis] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClusters = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (timeRange !== 'all') params.append('time_range', timeRange);
        if (minSeverity) params.append('min_severity', minSeverity);

        const response = await fetch(
          `${API_BASE_URL}/clusters?${params.toString()}`
        );

        if (!response.ok) throw new Error('Failed to fetch cluster data');

        const data = await response.json();
        
        setClusters(data.clusters || []);
        setOutliers(data.outliers || []);
        setTemporalAnalysis(data.temporal_analysis || []);
        setSummary(data.summary || null);
      } catch (err) {
        setError(err.message);
        console.error('Cluster data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClusters();
  }, [timeRange, minSeverity]);

  return { clusters, outliers, temporalAnalysis, summary, loading, error };
};

export const useHeatmapData = () => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHeatmap = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/clusters/heatmap-data`);
        if (!response.ok) throw new Error('Failed to fetch heatmap data');

        const data = await response.json();
        setHeatmapData(data.data || []);
      } catch (err) {
        setError(err.message);
        console.error('Heatmap data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmap();
  }, []);

  return { heatmapData, loading, error };
};