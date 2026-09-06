import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { 
  ShieldAlert, 
  Activity, 
  Terminal, 
  Clock, 
  User, 
  AlertTriangle, 
  CheckCircle,
  AlertOctagon
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    try {
      const response = await api.get('/stats/overview');
      setStats(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to fetch dashboard metrics. Is the API server online?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Auto-refresh stats every 5 seconds to match simulator stream
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
        <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mr-3"></div>
        Loading security metrics...
      </div>
    );
  }

  // Pre-calculate data for charts
  const severityColors = {
    Critical: '#ef4444', // Red
    High: '#f97316',    // Orange
    Medium: '#eab308',  // Yellow
    Low: '#3b82f6',     // Blue
  };

  const severityData = stats ? Object.keys(stats.severity_distribution).map(key => ({
    name: key,
    value: stats.severity_distribution[key]
  })).filter(d => d.value > 0) : [];

  const labelData = stats ? Object.keys(stats.label_distribution).map(key => ({
    name: key.toUpperCase(),
    count: stats.label_distribution[key]
  })) : [];

  return (
    <div className="space-y-8 text-white">
      {/* Page Header */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Security Command Center</h1>
          <p className="text-slate-400 text-sm mt-1">Real-time intrusion detection and behavioral monitoring feed.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          Live Stream Replay Active
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm flex items-center gap-3">
          <AlertOctagon className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Scanned */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Total Scanned Events</span>
            <div className="p-2 bg-blue-600/10 rounded-lg text-blue-400"><Activity className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight">
            {stats?.total_scanned.toLocaleString() || 0}
          </h3>
          <p className="text-xs text-slate-500 mt-2">Incoming packet streams processed</p>
        </div>

        {/* Total Alerts */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Threat Alerts</span>
            <div className="p-2 bg-rose-600/10 rounded-lg text-rose-400"><ShieldAlert className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-rose-500">
            {stats?.total_alerts.toLocaleString() || 0}
          </h3>
          <p className="text-xs text-slate-500 mt-2">Intrusions & anomalies flagged</p>
        </div>

        {/* Critical Alerts */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Critical Incidents</span>
            <div className="p-2 bg-red-600/10 rounded-lg text-red-400"><AlertTriangle className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-red-500">
            {stats?.severity_distribution.Critical || 0}
          </h3>
          <p className="text-xs text-slate-500 mt-2">Require immediate investigation</p>
        </div>

        {/* Detection Accuracy (Fallback display) */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Threat Ratio</span>
            <div className="p-2 bg-emerald-600/10 rounded-lg text-emerald-400"><CheckCircle className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-emerald-400">
            {stats?.total_scanned > 0 
              ? ((stats.total_alerts / stats.total_scanned) * 100).toFixed(2)
              : '0.00'}%
          </h3>
          <p className="text-xs text-slate-500 mt-2">Percentage of packets labeled anomalous</p>
        </div>
      </div>

      {/* Visual Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Pie Chart */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl">
          <h3 className="text-lg font-semibold mb-6">Threat Severity Breakdown</h3>
          <div className="h-64 flex items-center justify-center">
            {severityData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={severityColors[entry.name]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }}
                    labelStyle={{ color: '#ffffff' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-sm">No alert severity records available.</div>
            )}
          </div>
        </div>

        {/* Attack Type Bar Chart */}
        <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl">
          <h3 className="text-lg font-semibold mb-6">Threat Vectors & Category Count</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={labelData.filter(d => d.name !== 'NORMAL')}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }}
                  labelStyle={{ color: '#ffffff' }}
                />
                <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Alerts List */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-slate-800/85">
          <h3 className="text-lg font-semibold">Active Threat Log</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/20 text-slate-400 text-xs font-semibold uppercase tracking-wider border-b border-slate-800/80">
                <th className="py-4 px-6">Timestamp</th>
                <th className="py-4 px-6">Source IP</th>
                <th className="py-4 px-6">Attack Vector</th>
                <th className="py-4 px-6">Severity</th>
                <th className="py-4 px-6">Confidence</th>
                <th className="py-4 px-6">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-sm">
              {stats?.recent_alerts && stats.recent_alerts.length > 0 ? (
                stats.recent_alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-slate-900/30 transition-colors">
                    <td className="py-4 px-6 text-slate-400 flex items-center gap-2">
                      <Clock className="w-4 h-4 text-slate-500" />
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-4 px-6 font-mono font-medium text-slate-300">{alert.source_identifier}</td>
                    <td className="py-4 px-6">
                      <span className="flex items-center gap-1.5">
                        <Terminal className="w-4 h-4 text-slate-500" />
                        {alert.predicted_label.toUpperCase()}
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
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-500">
                    No active threat logs detected. Pure benign traffic flow.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
