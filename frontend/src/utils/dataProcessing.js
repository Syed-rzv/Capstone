// FILE: src/utils/dataProcessing.js
// =============================================================================
export const filterData = (data, filters) => {
    return data.filter(item => {
      const itemDate = new Date(item.timestamp);
      const startDate = new Date(filters.dateRange.start);
      const endDate = new Date(filters.dateRange.end);
  
      const dateMatch = itemDate >= startDate && itemDate <= endDate;
      const typeMatch = filters.types.length === 0 || filters.types.includes(item.emergency_type);
      const townMatch = !filters.township || item.township === filters.township;
      const zipMatch = !filters.zipcode || item.zipcode === filters.zipcode;
  
      return dateMatch && typeMatch && townMatch && zipMatch;
    });
  };
  
  export const calculateKPIs = (data) => {
    if (data.length === 0) {
      return { totalCalls: 0, mostCommonType: '—', avgAge: '—', peakHour: '—' };
    }
  
    const totalCalls = data.length;
    const typeCounts = data.reduce((acc, curr) => {
      acc[curr.emergency_type] = (acc[curr.emergency_type] || 0) + 1;
      return acc;
    }, {});
    const mostCommonType = Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0][0];
    const avgAge = Math.round(data.reduce((sum, d) => sum + d.caller_age, 0) / data.length);
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
    data.forEach(item => { counts[item.emergency_type] = (counts[item.emergency_type] || 0) + 1; });
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
      const bin = bins.find(b => item.caller_age >= b.min && item.caller_age <= b.max);
      if (bin) bin.count++;
    });
    return bins;
  };
  
  export const aggregateGenderData = (data) => {
    const counts = {};
    data.forEach(item => { counts[item.caller_gender] = (counts[item.caller_gender] || 0) + 1; });
    return Object.entries(counts).map(([gender, count]) => ({ gender, count }));
  };
  