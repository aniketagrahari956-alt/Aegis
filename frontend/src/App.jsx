import React, { useState, useEffect } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AlertsFeed from './pages/AlertsFeed';
import ModelMetrics from './pages/ModelMetrics';
import { 
  Shield, 
  LayoutDashboard, 
  BellRing, 
  BarChart3, 
  LogOut, 
  User, 
  Settings 
} from 'lucide-react';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('');

  useEffect(() => {
    if (token) {
      setEmail(localStorage.getItem('email') || 'analyst@aegis.local');
      setRole(localStorage.getItem('role') || 'analyst');
    }
  }, [token]);

  const handleLoginSuccess = () => {
    setToken(localStorage.getItem('token'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('email');
    setToken(null);
    setActiveTab('dashboard');
  };

  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'alerts':
        return <AlertsFeed />;
      case 'model':
        return <ModelMetrics />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Glow Effects */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900/60 backdrop-blur-md border-r border-slate-800 flex flex-col relative z-10">
        {/* Brand Logo Header */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-blue-600/10 border border-blue-500/20 rounded-lg text-blue-400">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-tight text-white">AEGIS THREAT</h1>
            <span className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">Operations</span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-1.5">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full py-3 px-4 rounded-xl text-sm font-medium flex items-center gap-3 transition-all ${
              activeTab === 'dashboard'
                ? 'bg-blue-600/15 border border-blue-500/20 text-blue-400'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40 border border-transparent'
            }`}
          >
            <LayoutDashboard className="w-5 h-5" />
            Command Center
          </button>

          <button
            id="alerts-tab-btn"
            onClick={() => setActiveTab('alerts')}
            className={`w-full py-3 px-4 rounded-xl text-sm font-medium flex items-center gap-3 transition-all ${
              activeTab === 'alerts'
                ? 'bg-blue-600/15 border border-blue-500/20 text-blue-400'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40 border border-transparent'
            }`}
          >
            <BellRing className="w-5 h-5" />
            Alerts Feed
          </button>

          <button
            id="model-tab-btn"
            onClick={() => setActiveTab('model')}
            className={`w-full py-3 px-4 rounded-xl text-sm font-medium flex items-center gap-3 transition-all ${
              activeTab === 'model'
                ? 'bg-blue-600/15 border border-blue-500/20 text-blue-400'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40 border border-transparent'
            }`}
          >
            <BarChart3 className="w-5 h-5" />
            Model Metrics
          </button>
        </nav>

        {/* User profile footer info */}
        <div className="p-4 border-t border-slate-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <User className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-slate-200 truncate">{email}</p>
              <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">{role}</span>
            </div>
          </div>

          <button
            id="logout-btn"
            onClick={handleLogout}
            className="w-full py-2 px-3 border border-slate-850 bg-slate-950/60 hover:bg-slate-900 text-xs font-medium text-slate-400 hover:text-rose-400 hover:border-rose-500/20 rounded-lg flex items-center justify-center gap-2 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
            Logout Console
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        <div className="flex-1 overflow-y-auto p-8 max-w-7xl w-full mx-auto">
          {renderActiveView()}
        </div>
      </main>
    </div>
  );
}
