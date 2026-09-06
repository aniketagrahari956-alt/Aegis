import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { 
  Filter, 
  Search, 
  Clock, 
  Terminal, 
  User, 
  ArrowRight,
  Eye,
  Check,
  ShieldCheck,
  TrendingDown
} from 'lucide-react';

export default function AlertsFeed() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [status, setStatus] = useState('');
  const [severity, setSeverity] = useState('');
  const [source, setSource] = useState('');
  
  // Selection / Detail
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [assignedAnalyst, setAssignedAnalyst] = useState('');
  const [transitionStatus, setTransitionStatus] = useState('');

  const fetchAlerts = async () => {
    try {
      const params = {};
      if (status) params.status = status;
      if (severity) params.severity = severity;
      if (source) params.source = source;
      
      const response = await api.get('/alerts', { params });
      setAlerts(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load alert logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 4000);
    return () => clearInterval(interval);
  }, [status, severity, source]);

  const handleUpdateAlertStatus = async (alertId, newStatus) => {
    try {
      const response = await api.patch(`/alerts/${alertId}`, {
        status: newStatus,
        assigned_analyst: assignedAnalyst || undefined
      });
      // Update local state
      setAlerts(alerts.map(a => a.id === alertId ? response.data : a));
      setSelectedAlert(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to update alert state.');
    }
  };

  const handleOpenDetail = (alert) => {
    setSelectedAlert(alert);
    setAssignedAnalyst(alert.assigned_analyst || localStorage.getItem('email') || '');
    setTransitionStatus(alert.status);
  };

  return (
    <div className="space-y-6 text-white">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight">Security Alerts Feed</h1>
        <p className="text-slate-400 text-sm mt-1">Review, assign, and resolve security threats and anomalous flow alerts.</p>
      </div>

      {/* Filters Toolbar */}
      <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl flex flex-wrap gap-4 items-center">
        {/* Search Source IP */}
        <div className="relative flex-1 min-w-[200px]">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
            <Search className="w-4 h-4" />
          </span>
          <input
            id="search-input"
            type="text"
            placeholder="Search source IP..."
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-lg py-2 pl-9 pr-4 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Severity filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            id="severity-filter"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        {/* Status filter */}
        <div>
          <select
            id="status-filter"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Acknowledged">Acknowledged</option>
            <option value="Resolved">Resolved</option>
            <option value="False Positive">False Positive</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Main Table + Detail Panel Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Table List */}
        <div className={`bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden ${
          selectedAlert ? 'xl:col-span-2' : 'xl:col-span-3'
        }`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/20 text-slate-400 text-xs font-semibold uppercase tracking-wider border-b border-slate-800/80">
                  <th className="py-4 px-6">Timestamp</th>
                  <th className="py-4 px-6">Source IP</th>
                  <th className="py-4 px-6">Label</th>
                  <th className="py-4 px-6">Severity</th>
                  <th className="py-4 px-6">Confidence</th>
                  <th className="py-4 px-6">Status</th>
                  <th className="py-4 px-6"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-sm">
                {loading && alerts.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-slate-500">
                      Querying alert log base...
                    </td>
                  </tr>
                ) : alerts.length > 0 ? (
                  alerts.map((alert) => (
                    <tr 
                      key={alert.id} 
                      className={`hover:bg-slate-900/30 transition-colors cursor-pointer ${
                        selectedAlert?.id === alert.id ? 'bg-slate-900/40 border-l-2 border-l-blue-500' : ''
                      }`}
                      onClick={() => handleOpenDetail(alert)}
                    >
                      <td className="py-4 px-6 text-slate-400">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-4 px-6 font-mono font-medium text-slate-300">{alert.source_identifier}</td>
                      <td className="py-4 px-6">
                        <span className="flex items-center gap-1.5 uppercase font-medium">
                          <Terminal className="w-4 h-4 text-slate-500" />
                          {alert.predicted_label}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${
                          alert.severity === 'Critical' ? 'bg-red-500/10 border-red-500/20 text-red-500' :
                          alert.severity === 'High' ? 'bg-orange-500/10 border-orange-500/20 text-orange-500' :
                          alert.severity === 'Medium' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500' :
                          'bg-blue-500/10 border-blue-500/20 text-blue-500'
                        }`}>
                          {alert.severity}
                        </span>
                      </td>
                      <td className="py-4 px-6 font-mono text-slate-300">{(alert.confidence * 100).toFixed(1)}%</td>
                      <td className="py-4 px-6">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          alert.status === 'Open' ? 'bg-rose-500/10 text-rose-400' :
                          alert.status === 'Acknowledged' ? 'bg-amber-500/10 text-amber-400' :
                          alert.status === 'Resolved' ? 'bg-emerald-500/10 text-emerald-400' :
                          'bg-slate-500/10 text-slate-400'
                        }`}>
                          {alert.status}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button 
                          className="p-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-lg hover:text-white"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenDetail(alert);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-slate-500">
                      No matching threat alerts found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Panel */}
        {selectedAlert && (
          <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 space-y-6 h-fit relative">
            <button 
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
              onClick={() => setSelectedAlert(null)}
            >
              ✕
            </button>
            
            <div>
              <h3 className="text-lg font-bold">Alert Investigation</h3>
              <p className="text-slate-400 text-xs mt-1">Incident ID: #{selectedAlert.id}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm bg-slate-950/50 p-4 border border-slate-800/80 rounded-xl">
              <div>
                <span className="text-slate-500 text-xs block mb-1">Source Host</span>
                <span className="font-mono text-slate-200">{selectedAlert.source_identifier}</span>
              </div>
              <div>
                <span className="text-slate-500 text-xs block mb-1">Verdict</span>
                <span className="font-medium text-slate-200 uppercase">{selectedAlert.predicted_label}</span>
              </div>
              <div>
                <span className="text-slate-500 text-xs block mb-1">Severity Rating</span>
                <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${
                  selectedAlert.severity === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                  selectedAlert.severity === 'High' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                  selectedAlert.severity === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                  'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                }`}>{selectedAlert.severity}</span>
              </div>
              <div>
                <span className="text-slate-500 text-xs block mb-1">Detector Confidence</span>
                <span className="font-mono text-slate-200">{(selectedAlert.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-500 text-xs block mb-1">Unsupervised Anomaly Score</span>
                <span className="font-mono text-slate-200">{selectedAlert.anomaly_score.toFixed(4)}</span>
              </div>
            </div>

            {/* Triaging Action Panel */}
            <div className="space-y-4 border-t border-slate-800 pt-4">
              <h4 className="text-sm font-semibold">Triage & Actions</h4>
              
              <div>
                <label className="block text-slate-400 text-xs mb-1.5">Assigned Analyst</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                    <User className="w-4 h-4" />
                  </span>
                  <input
                    id="analyst-input"
                    type="text"
                    value={assignedAnalyst}
                    onChange={(e) => setAssignedAnalyst(e.target.value)}
                    placeholder="analyst@aegis.local"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-lg py-2 pl-9 pr-4 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 text-xs mb-2">Transition Status</label>
                <div className="flex flex-wrap gap-2">
                  {['Acknowledged', 'Resolved', 'False Positive'].map((statusOption) => (
                    <button
                      key={statusOption}
                      onClick={() => handleUpdateAlertStatus(selectedAlert.id, statusOption)}
                      className={`py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                        selectedAlert.status === statusOption
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      {selectedAlert.status === statusOption && <Check className="w-3.5 h-3.5" />}
                      {statusOption}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Raw JSON Features Inspector */}
            {selectedAlert.raw_features && (
              <div className="border-t border-slate-800 pt-4 space-y-2">
                <h4 className="text-sm font-semibold flex items-center gap-1.5">
                  <Terminal className="w-4 h-4 text-slate-400" />
                  Raw Flow Payload
                </h4>
                <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-[10px] font-mono h-48 overflow-y-auto text-slate-400 whitespace-pre-wrap">
                  {JSON.stringify(selectedAlert.raw_features, null, 2)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
