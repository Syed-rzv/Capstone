// FILE: src/data/mockData.js
// =============================================================================
export const generateMockData = () => {
    const types = ['EMS', 'Fire', 'Traffic'];
    const townships = ['NEW HANOVER', 'HATFIELD TOWNSHIP', 'NORRISTOWN', 'LOWER POTTSGROVE'];
    const zipcodes = ['19525', '19446', '19401', '19464'];
    const genders = ['Male', 'Female', 'Other'];
    
    const data = [];
    const startDate = new Date('2015-01-01');
    const endDate = new Date('2015-12-31');
    
    for (let i = 0; i < 500; i++) {
      const randomDate = new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()));
      data.push({
        id: i + 1,
        timestamp: randomDate.toISOString(),
        emergency_type: types[Math.floor(Math.random() * types.length)],
        emergencyType: types[Math.floor(Math.random() * types.length)], // ADD THIS
        caller_age: Math.floor(Math.random() * 70) + 18,
        callerAge: Math.floor(Math.random() * 70) + 18, 
        caller_gender: genders[Math.floor(Math.random() * genders.length)],
        callerGender: genders[Math.floor(Math.random() * genders.length)], // ADD THIS
        latitude: 40.1 + Math.random() * 0.3,
        lat: 40.1 + Math.random() * 0.3,
        longitude: -75.6 + Math.random() * 0.3,
        lng: -75.6 + Math.random() * 0.3, 
        township: townships[Math.floor(Math.random() * townships.length)],
        district: townships[Math.floor(Math.random() * townships.length)], // ADD THIS
        zipcode: zipcodes[Math.floor(Math.random() * zipcodes.length)],
        emergency_title: `Emergency ${i + 1}`,
      });
    }
    return data;
  };
  