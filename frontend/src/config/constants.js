export const API_CONFIG = {
    BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
    CALLS_LIMIT: {
      DASHBOARD: 50000,    // Dashboard default
      EXPORT: 100000,      // For data exports
      PREVIEW: 1000,       // For quick previews
      MAX: 200000,         // Absolute maximum
    },
  };