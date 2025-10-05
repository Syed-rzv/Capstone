// =============================================================================
// FILE: src/hooks/useDashboardData.js
// Custom hook for fetching dashboard data with mock data fallback
// =============================================================================

import { useState, useEffect, useCallback } from 'react';
import api, { processApiData } from '../services/api';
import { generateMockData } from '../data/mockData';

 const useDashboardData = (filters = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMockData, setUsingMockData] = useState(false);
  const [apiAvailable, setApiAvailable] = useState(true);

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      const health = await api.healthCheck();
      setApiAvailable(health.available);
      
      if (!health.available) {
        console.warn('API unavailable, using mock data as fallback');
      }
    };
    
    checkApiHealth();
  }, []);

  // Fetch data from API or use mock data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (!apiAvailable) {
        // Use mock data if API is not available
        console.log('Using mock data (API unavailable)');
        const mockData = generateMockData();
        setData(mockData);
        setUsingMockData(true);
        setLoading(false);
        return;
      }

      // Try to fetch from API
      const response = await api.getCalls({
        limit: 1000, // Fetch more data for better visualization
        ...filters,
      });

      const transformedData = processApiData.transformCallsData(response);
      
      if (transformedData.length === 0) {
        console.warn('No data returned from API, using mock data');
        const mockData = generateMockData();
        setData(mockData);
        setUsingMockData(true);
      } else {
        setData(transformedData);
        setUsingMockData(false);
      }
    } catch (err) {
      console.error('Error fetching data from API:', err);
      console.log('Falling back to mock data');
      
      // Fallback to mock data on error
      const mockData = generateMockData();
      setData(mockData);
      setUsingMockData(true);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiAvailable, filters]);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps  
  }, [apiAvailable]);  // Only refetch if API availability changes

  return {
    data,
    loading,
    error,
    usingMockData,
    apiAvailable,
    refetch: fetchData,
  };
};

// =============================================================================
// Hook for statistics data
// =============================================================================

export const useStatsData = () => {
  const [stats, setStats] = useState({
    typeCounts: [],
    dailyStats: [],
    districtCounts: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const [typeCounts, dailyStats, districtCounts] = await Promise.all([
          api.getTypeCounts(),
          api.getDailyStats(),
          api.getDistrictCounts(),
        ]);

        setStats({
          typeCounts: processApiData.transformTypeCounts(typeCounts),
          dailyStats: processApiData.transformDailyStats(dailyStats),
          districtCounts: processApiData.transformDistrictCounts(districtCounts),
        });
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
};

// =============================================================================
// Hook for forecast data
// =============================================================================

export const useForecastData = (params = {}) => {
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchForecast = async () => {
      setLoading(true);
      try {
        const response = await api.getForecast(params);
        setForecast(processApiData.transformForecastData(response));
      } catch (err) {
        console.error('Error fetching forecast:', err);
        setError(err.message);
        setForecast([]);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [JSON.stringify(params)]);

  return { forecast, loading, error };
};

// =============================================================================
// Hook for submitting new emergency calls
// =============================================================================

export const useSubmitCall = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const submitCall = async (callData) => {
    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      const response = await api.ingestCall(callData);
      setSubmitSuccess(true);
      return response;
    } catch (err) {
      console.error('Error submitting call:', err);
      setSubmitError(err.message);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  return {
    submitCall,
    submitting,
    submitError,
    submitSuccess,
  };
};

export default useDashboardData;