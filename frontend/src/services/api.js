// =============================================================================
// FILE: src/services/api.js
// API Service Layer for CrisisLens Dashboard
// =============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Helper function for API calls with error handling
const fetchWithErrorHandling = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch ${endpoint}:`, error);
    throw error;
  }
};

// =============================================================================
// Emergency Calls API
// =============================================================================

export const api = {
  // Get all calls with optional filters and pagination
  getCalls: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.date) queryParams.append('date', params.date);
    if (params.type) queryParams.append('type', params.type);
    if (params.subtype) queryParams.append('subtype', params.subtype);
    if (params.township) queryParams.append('township', params.township);

    const queryString = queryParams.toString();
    const endpoint = `/calls${queryString ? `?${queryString}` : ''}`;
    
    return await fetchWithErrorHandling(endpoint);
  },

  // Get latest N calls
  getLatestCalls: async (limit = 10) => {
    return await fetchWithErrorHandling(`/calls/latest?limit=${limit}`);
  },

  // Submit a new emergency call
  ingestCall: async (callData) => {
    return await fetchWithErrorHandling('/calls', {
      method: 'POST',
      body: JSON.stringify(callData),
    });
  },

  // =============================================================================
  // Statistics API
  // =============================================================================

  // Get counts by emergency type and subtype
  getTypeCounts: async () => {
    return await fetchWithErrorHandling('/stats/counts');
  },

  // Get daily call statistics
  getDailyStats: async () => {
    return await fetchWithErrorHandling('/stats/daily');
  },

  // Get township-wise call counts
  getTownshipCounts: async () => {
    return await fetchWithErrorHandling('/stats/township');
  },
// Get district-wise call counts (alias for township)
  getDistrictCounts: async () => {
    return await fetchWithErrorHandling('/stats/township');
  },

  // =============================================================================
  // Forecast API
  // =============================================================================

  // Get forecast data with optional filters
  getForecast: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.latest) queryParams.append('latest', 'true');

    const queryString = queryParams.toString();
    const endpoint = `/forecast${queryString ? `?${queryString}` : ''}`;
    
    return await fetchWithErrorHandling(endpoint);
  },

  // =============================================================================
  // Health Check
  // =============================================================================

  // Check if API is available
  healthCheck: async () => {
    try {
      const response = await fetchWithErrorHandling('/');
      return { available: true, message: response.message };
    } catch (error) {
      return { available: false, error: error.message };
    }
  },
};

// =============================================================================
// Data Processing Utilities for API responses
// =============================================================================

export const processApiData = {
  // Transform API calls data to match dashboard format
  transformCallsData: (apiResponse) => {
    const calls = apiResponse.results || apiResponse;
    
    return calls.map(call => ({
      id: call.id,
      timestamp: new Date(call.timestamp),
      emergencyType: call.emergency_type,
      emergencySubtype: call.emergency_subtype,
      district: call.district || call.township,
      latitude: parseFloat(call.latitude),
      longitude: parseFloat(call.longitude),
      description: call.description,
      emergencyTitle: call.emergency_title,
      zipcode: call.zipcode,
      address: call.address,
      priorityFlag: call.priority_flag,
      callerGender: call.caller_gender,
      callerAge: parseInt(call.caller_age) || null,
      responseTime: call.response_time,
      source: call.source,
    }));
  },

  // Process type counts for pie chart
  transformTypeCounts: (apiResponse) => {
    return apiResponse.map(item => ({
      type: item.emergency_type,
      subtype: item.emergency_subtype,
      count: item.count,
    }));
  },

  // Process daily stats for timeline chart
  transformDailyStats: (apiResponse) => {
    return apiResponse.map(item => ({
      date: item.date,
      count: item.count,
    }));
  },

  // Process township counts
  transformTownshipCounts: (apiResponse) => {
    return apiResponse.map(item => ({
      township: item.township,
      count: item.count,
    }));
  },
  // Process district counts (alias for township)
  transformDistrictCounts: (apiResponse) => {
    return apiResponse.map(item => ({
      district: item.township || item.district,
      count: item.count,
    }));
  },
  
  // Process forecast data
  transformForecastData: (apiResponse) => {
    return apiResponse.map(item => ({
      forecastDate: item.forecast_date,
      township: item.township,
      emergencyType: item.emergency_type,
      emergencySubtype: item.emergency_subtype,
      predictedCalls: item.predicted_calls,
      lowerBound: item.lower_bound,
      upperBound: item.upper_bound,
      modelUsed: item.model_used,
      source: item.source,
      generatedAt: item.generated_at,
    }));
  },
};

export default api;