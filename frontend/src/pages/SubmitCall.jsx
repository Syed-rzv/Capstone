import { useState } from 'react';
import api from '../services/api';

export default function SubmitCall() {
  const [formData, setFormData] = useState({
    timestamp: new Date().toISOString(),
    description: '',
    latitude: '',
    longitude: '',
    district: '',
    gender: '',
    age: '',
    caller_name: '',
    caller_number: ''
  });
  
  const [address, setAddress] = useState('');
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Geocode address to coordinates
  const geocodeAddress = async () => {
    if (!address.trim()) {
      setSubmitStatus({
        type: 'error',
        message: 'Please enter an address'
      });
      return;
    }
    
    setIsGeocoding(true);
    setSubmitStatus(null);
    
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1&countrycodes=us`,
        {
          headers: {
            'User-Agent': 'CrisisLens-Emergency-Analytics/1.0'
          }
        }
      );
      
      const data = await response.json();
      
      if (data && data.length > 0) {
        setFormData({
          ...formData,
          latitude: parseFloat(data[0].lat),
          longitude: parseFloat(data[0].lon),
          district: data[0].display_name.split(',')[0] // Extract first part as district
        });
        setSubmitStatus({
          type: 'success',
          message: `✅ Location found: ${data[0].display_name}`
        });
      } else {
        setSubmitStatus({
          type: 'error',
          message: '❌ Address not found. Try: "123 Main St, New York, NY" format'
        });
      }
    } catch (error) {
      setSubmitStatus({
        type: 'error',
        message: `Geocoding error: ${error.message}`
      });
    } finally {
      setIsGeocoding(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if coordinates are populated
    if (!formData.latitude || !formData.longitude) {
      setSubmitStatus({
        type: 'error',
        message: 'Please geocode an address first or enter coordinates manually'
      });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await api.ingestCall(formData);
      setSubmitStatus({ 
        type: 'success', 
        message: `✅ Call ingested successfully! ID: ${response.raw_id}. Processing in background...` 
      });
      
      // Reset form
      setFormData({
        timestamp: new Date().toISOString().slice(0, 16),
        description: '',
        latitude: '',
        longitude: '',
        district: '',
        gender: '',
        age: '',
        caller_name: '',
        caller_number: ''
      });
      setAddress('');
    } catch (error) {
      setSubmitStatus({ 
        type: 'error', 
        message: `Failed to submit call: ${error.message}` 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-green-500 mb-2">Submit Emergency Call</h1>
        <p className="text-gray-400 mb-6">Enter call details for processing and classification</p>
        
        {submitStatus && (
          <div className={`p-4 mb-6 rounded-lg border ${
            submitStatus.type === 'success' 
              ? 'bg-green-500/10 border-green-500/30 text-green-400' 
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            {submitStatus.message}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Address Geocoding Section */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-green-400 mb-4">📍 Location Lookup</h2>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Enter Address
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), geocodeAddress())}
                    className="flex-1 bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                    placeholder="e.g., 123 Main St, New York, NY 10001"
                  />
                  <button
                    type="button"
                    onClick={geocodeAddress}
                    disabled={isGeocoding}
                    className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:bg-gray-600"
                  >
                    {isGeocoding ? 'Finding...' : 'Find Location'}
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  💡 Powered by OpenStreetMap - Free & open-source geocoding
                </p>
              </div>
              
              {/* Show coordinates after geocoding */}
              {formData.latitude && formData.longitude && (
                <div className="bg-green-500/10 border border-green-500/30 rounded p-3">
                  <p className="text-sm text-green-400">
                    📌 Coordinates: {formData.latitude}, {formData.longitude}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* OR Manual Entry */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-400 mb-4">Or Enter Manually</h2>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Latitude
                </label>
                <input
                  type="number"
                  step="0.000001"
                  value={formData.latitude}
                  onChange={(e) => setFormData({...formData, latitude: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="40.7128"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Longitude
                </label>
                <input
                  type="number"
                  step="0.000001"
                  value={formData.longitude}
                  onChange={(e) => setFormData({...formData, longitude: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="-74.0060"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  District
                </label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({...formData, district: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="Manhattan"
                />
              </div>
            </div>
          </div>

          {/* Call Information */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold text-green-400 mb-4">📞 Call Details</h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Timestamp
              </label>
              <input
                type="datetime-local"
                value={formData.timestamp.slice(0, 16)}
                onChange={(e) => setFormData({...formData, timestamp: new Date(e.target.value).toISOString()})}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Call Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                rows="4"
                placeholder="e.g., Male caller reporting chest pain and difficulty breathing..."
                required
              />
            </div>
          </div>

          {/* Caller Information */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold text-green-400 mb-4">👤 Caller Information</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Gender *
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({...formData, gender: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  required
                >
                  <option value="">Select...</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Age *
                </label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({...formData, age: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="30"
                  required
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Caller Name (Optional)
                </label>
                <input
                  type="text"
                  value={formData.caller_name}
                  onChange={(e) => setFormData({...formData, caller_name: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="John Doe"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Caller Number (Optional)
                </label>
                <input
                  type="tel"
                  value={formData.caller_number}
                  onChange={(e) => setFormData({...formData, caller_number: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  placeholder="+1-555-0123"
                />
              </div>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting || !formData.latitude || !formData.longitude}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 rounded-lg transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Emergency Call'}
          </button>
        </form>
      </div>
    </div>
  );
}