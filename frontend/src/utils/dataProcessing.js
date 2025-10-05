// FILE: src/utils/dataProcessing.js
export const filterData = (data, filters) => {
  console.log("FILTER DEBUG - filters:", filters);
  console.log("FILTER DEBUG - data sample:", data[0]);
  
  return data.filter(item => {
    const itemDate = new Date(item.timestamp);
    const startDate = new Date(filters.dateRange.start);
    const endDate = new Date(filters.dateRange.end);

    const dateMatch = itemDate >= startDate && itemDate <= endDate;
    const typeMatch = filters.types.length === 0 || filters.types.includes(item.emergencyType);
    const townMatch = !filters.district || item.district === filters.district;
    const zipMatch = !filters.zipcode || item.zipcode === filters.zipcode;

    // Log only first item to avoid spam
    if (item.id === data[0].id) {
      console.log("FILTER DEBUG - first item check:", {
        dateMatch,
        typeMatch,
        townMatch,
        zipMatch,
        itemDate,
        startDate,
        endDate
      });
    }

    return dateMatch && typeMatch && townMatch && zipMatch;
  });
};

export const calculateKPIs = (data) => {
  if (data.length === 0) {
    return { totalCalls: 0, mostCommonType: '—', avgAge: '—', peakHour: '—' };
  }

  const totalCalls = data.length;
  const typeCounts = data.reduce((acc, curr) => {
    acc[curr.emergencyType] = (acc[curr.emergencyType] || 0) + 1; // Changed
    return acc;
  }, {});
  const mostCommonType = Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0][0];
  const avgAge = Math.round(data.reduce((sum, d) => sum + (d.callerAge || 0), 0) / data.length); // Changed
  const hours = data.map(d => new Date(d.timestamp).getHours());
  const hourCounts = hours.reduce((acc, h) => { acc[h] = (acc[h] || 0) + 1; return acc; }, {});
  const peak = Object.entries(hourCounts).sort((a, b) => b[1] - a[1])[0][0];
  const peakHour = `${String(peak).padStart(2, '0')}:00`;

  return { totalCalls, mostCommonType, avgAge, peakHour };
};

export const aggregateTimelineData = (data) => {
  const monthCounts = {};
  data.forEach(item => {
    const month = new Date(item.timestamp).toISOString().slice(0, 7);
    monthCounts[month] = (monthCounts[month] || 0) + 1;
  });
  return Object.entries(monthCounts)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([month, count]) => ({ month, count }));
};

export const aggregateTypeData = (data) => {
  const counts = {};
  data.forEach(item => { counts[item.emergencyType] = (counts[item.emergencyType] || 0) + 1; }); // Changed
  return Object.entries(counts).map(([type, count]) => ({ type, count }));
};

export const aggregateAgeData = (data) => {
  const bins = [
    { range: '18-25', min: 18, max: 25, count: 0 },
    { range: '26-35', min: 26, max: 35, count: 0 },
    { range: '36-45', min: 36, max: 45, count: 0 },
    { range: '46-55', min: 46, max: 55, count: 0 },
    { range: '56+', min: 56, max: 100, count: 0 }
  ];
  data.forEach(item => {
    const age = item.callerAge; // Changed
    if (age) {
      const bin = bins.find(b => age >= b.min && age <= b.max);
      if (bin) bin.count++;
    }
  });
  return bins;
};

export const aggregateGenderData = (data) => {
  const counts = {};
  data.forEach(item => { 
    const gender = item.callerGender; // Changed
    if (gender) counts[gender] = (counts[gender] || 0) + 1; 
  });
  return Object.entries(counts).map(([gender, count]) => ({ gender, count }));
};

export const detectAnomalies = (data, threshold = 2) => {
  const values = data.map(d => d.value);
  const mean = values.reduce((a, b) => a + b) / values.length;
  const stdDev = Math.sqrt(
    values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length
  );
  
  return data.map(item => ({
    ...item,
    isAnomaly: Math.abs(item.value - mean) > (threshold * stdDev),
    zScore: (item.value - mean) / stdDev
  }));
};

// Specialized version for timeline data (works with 'count' property)
export const detectTimelineAnomalies = (timelineData, threshold = 2) => {
  if (!timelineData || timelineData.length === 0) return [];
  
  const values = timelineData.map(d => d.count);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  
  return timelineData.map(item => ({
    ...item,
    isAnomaly: Math.abs(item.count - mean) > (threshold * stdDev),
    zScore: stdDev > 0 ? ((item.count - mean) / stdDev).toFixed(2) : 0,
    avgValue: Math.round(mean)
  }));
};