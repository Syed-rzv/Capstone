const ClusterPopup = ({ cluster }) => {
    const getSeverityLabel = (score) => {
      if (score >= 8) return { label: 'CRITICAL', color: 'text-red-600 font-bold' };
      if (score >= 6.5) return { label: 'HIGH', color: 'text-orange-600 font-semibold' };
      if (score >= 5) return { label: 'MEDIUM', color: 'text-amber-600 font-medium' };
      if (score >= 3.5) return { label: 'MODERATE', color: 'text-yellow-600' };
      return { label: 'LOW', color: 'text-green-600' };
    };
  
    const severity = getSeverityLabel(cluster.severity_score);
    const isPeakHour = cluster.peak_hour >= 17 && cluster.peak_hour <= 22;
  
    return (
      <div className="p-2 min-w-[280px]">
        {/* Header */}
        <div className="mb-3 pb-2 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-800">
            Cluster #{cluster.cluster_id}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-sm ${severity.color}`}>
              {severity.label}
            </span>
            <span className="text-xs text-gray-500">
              Severity: {cluster.severity_score}/10
            </span>
          </div>
        </div>
  
        {/* Statistics Grid */}
        <div className="space-y-2 text-sm">
          {/* Call Volume */}
          <div className="flex justify-between items-center">
            <span className="text-gray-600">📞 Total Calls:</span>
            <span className="font-semibold text-gray-900">{cluster.call_count}</span>
          </div>
  
          {/* Primary Type */}
          <div className="flex justify-between items-center">
            <span className="text-gray-600">🚨 Primary Type:</span>
            <span className="font-semibold text-gray-900">
              {cluster.primary_type}
            </span>
          </div>
          <div className="text-xs text-gray-500 text-right -mt-1">
            {cluster.primary_type_pct}% of calls
          </div>
  
          {/* Peak Hour */}
          <div className="flex justify-between items-center">
            <span className="text-gray-600">⏰ Peak Hour:</span>
            <span className="font-semibold text-gray-900">
              {cluster.peak_hour}:00 {isPeakHour && '🔥'}
            </span>
          </div>
  
          {/* Response Time */}
          <div className="flex justify-between items-center">
            <span className="text-gray-600">⏱️ Avg Response:</span>
            <span className={`font-semibold ${
              cluster.response_diff_pct > 10 ? 'text-red-600' :
              cluster.response_diff_pct < -10 ? 'text-green-600' :
              'text-gray-900'
            }`}>
              {cluster.avg_response_time} min
            </span>
          </div>
          <div className={`text-xs text-right -mt-1 ${
            cluster.response_diff_pct > 0 ? 'text-red-500' : 'text-green-500'
          }`}>
            {cluster.response_diff_pct > 0 ? '+' : ''}{cluster.response_diff_pct}% 
            {cluster.response_diff_pct > 0 ? ' slower' : ' faster'} than city avg
          </div>
        </div>
  
        {/* Action Indicator */}
        {cluster.severity_score >= 7 && (
          <div className="mt-3 pt-2 border-t border-gray-200">
            <div className="text-xs text-orange-600 font-medium">
              ⚠️ High-priority area - consider resource reallocation
            </div>
          </div>
        )}
      </div>
    );
  };
  
  export default ClusterPopup;