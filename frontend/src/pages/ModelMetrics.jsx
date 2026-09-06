import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { ShieldCheck, Percent, Cpu, Activity, Info } from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Legend, 
  CartesianGrid 
} from 'recharts';

export default function ModelMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get('/model/metrics');
        setMetrics(response.data);
        setError('');
      } catch (err) {
        console.error(err);
        setError('Failed to fetch model metrics. Have you completed model training?');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
        <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mr-3"></div>
        Evaluating engine metrics...
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl max-w-xl mx-auto text-center space-y-4">
        <Info className="w-12 h-12 text-blue-500/40 mx-auto" />
        <h3 className="text-lg font-bold text-white">Model Metrics Unavailable</h3>
        <p className="text-slate-400 text-sm">{error || "Please run training first to build the XGBoost and Isolation Forest classifiers."}</p>
      </div>
    );
  }

  // Pre-calculate per-class bar chart data
  const classData = Object.keys(metrics.per_class).map((key) => ({
    name: key.toUpperCase(),
    Precision: (metrics.per_class[key].precision * 100).toFixed(1),
    Recall: (metrics.per_class[key].recall * 100).toFixed(1),
    F1: (metrics.per_class[key].f1_score * 100).toFixed(1)
  }));

  const classNames = ["NORMAL", "DOS", "PROBE", "R2L", "U2R"];

  return (
    <div className="space-y-8 text-white">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight">Detection Engine Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Detailed precision, recall, and false-positive scores for Aegis detection networks.</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Accuracy */}
        <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Ensemble Accuracy</span>
            <div className="p-2 bg-indigo-600/10 rounded-lg text-indigo-400"><Percent className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-indigo-400">
            {(metrics.accuracy * 100).toFixed(2)}%
          </h3>
          <p className="text-xs text-slate-500 mt-2">Overall correctly classified samples</p>
        </div>

        {/* ROC-AUC */}
        <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">ROC-AUC (Macro OVR)</span>
            <div className="p-2 bg-blue-600/10 rounded-lg text-blue-400"><ShieldCheck className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-blue-400">
            {metrics.roc_auc.toFixed(4)}
          </h3>
          <p className="text-xs text-slate-500 mt-2">Multi-class area under curve ratio</p>
        </div>

        {/* False Positive Rate */}
        <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">False Positive Rate (FPR)</span>
            <div className="p-2 bg-emerald-600/10 rounded-lg text-emerald-400"><Activity className="w-5 h-5" /></div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-emerald-400">
            {(metrics.fpr * 100).toFixed(3)}%
          </h3>
          <p className="text-xs text-slate-500 mt-2">Benign alerts mistakenly flagged as attack</p>
        </div>
      </div>

      {/* Per-Class Performance Bar Chart */}
      <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl">
        <h3 className="text-lg font-semibold mb-6">Per-Class Performance breakdown</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={classData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} unit="%" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }}
                labelStyle={{ color: '#ffffff' }}
              />
              <Legend />
              <Bar dataKey="Precision" fill="#3b82f6" radius={[2, 2, 0, 0]} />
              <Bar dataKey="Recall" fill="#f97316" radius={[2, 2, 0, 0]} />
              <Bar dataKey="F1" fill="#eab308" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confusion Matrix Table */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold">Confusion Matrix</h3>
          <p className="text-slate-400 text-xs mt-1">Cross-referencing true class values (rows) against engine predictions (columns).</p>
        </div>

        <div className="overflow-x-auto">
          <div className="min-w-[600px] flex flex-col items-center">
            {/* Headers */}
            <div className="grid grid-cols-6 gap-2 w-full text-center font-semibold text-xs text-slate-400 uppercase pb-2 border-b border-slate-800">
              <div>True \ Pred</div>
              {classNames.map(name => <div key={name}>{name}</div>)}
            </div>

            {/* Matrix Body */}
            <div className="w-full divide-y divide-slate-800/60 mt-2">
              {metrics.confusion_matrix.map((row, rIdx) => (
                <div key={rIdx} className="grid grid-cols-6 gap-2 w-full text-center items-center py-3 text-sm hover:bg-slate-900/30">
                  <div className="font-bold text-slate-400 uppercase text-xs text-left pl-2">{classNames[rIdx]}</div>
                  {row.map((val, cIdx) => (
                    <div 
                      key={cIdx} 
                      className={`py-2 rounded-lg font-mono transition-all ${
                        rIdx === cIdx 
                          ? 'bg-blue-600/10 text-blue-400 font-bold border border-blue-500/20' 
                          : val > 0 
                            ? 'bg-rose-500/5 text-rose-300/80 border border-rose-500/10' 
                            : 'text-slate-600'
                      }`}
                    >
                      {val}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
