import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import SimulatedLiveDashboard from './pages/SimulatedLiveDashboard';
import AnalyticsPage from './pages/Analytics';
import ReportsPage from './pages/Reports';
import UploadSection from './components/UploadSection';
import { LayoutDashboard, Settings, Video, FileText, BarChart, AlertTriangle, GitCompare, Menu, Search, Bell, HelpCircle, History, Image, ChevronDown } from 'lucide-react';
import FrameComparison from './components/FrameComparison';
import TopBlurFrames from './pages/TopBlurFrames';
import HistoryPage from './pages/History';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white text-slate-900 font-sans relative overflow-hidden">

        {/* TOP NAVIGATION BAR */}
        <nav className="bg-white/95 backdrop-blur-xl border-b border-slate-200/60 shadow-sm sticky top-0 z-50">
          <div className="max-w-[1920px] mx-auto px-6">
            <div className="flex items-center justify-between h-16">

              {/* Brand */}
              <div className="flex items-center gap-4">
                <Link to="/" className="flex items-center gap-3 group">
                  <div className="w-10 h-10 rounded-xl overflow-hidden shadow-lg shadow-blue-600/20 group-hover:shadow-xl transition-shadow bg-white">
                    <img src="/vanguard-logo.svg" alt="Vanguard" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold text-lg text-slate-900 leading-none tracking-tight">Vanguard</span>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Enterprise Console</span>
                  </div>
                </Link>
              </div>

              {/* Main Navigation */}
              <div className="hidden md:flex items-center space-x-1">
                <NavLink
                  to="/"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <LayoutDashboard size={18} />
                  Live Monitor
                </NavLink>

                <NavLink
                  to="/comparison"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <GitCompare size={18} />
                  Frame Analysis
                </NavLink>

                <NavLink
                  to="/analytics"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <BarChart size={18} />
                  Analytics
                </NavLink>

                <NavLink
                  to="/history"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <History size={18} />
                  History
                </NavLink>

                <NavLink
                  to="/reports"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <FileText size={18} />
                  Reports
                </NavLink>

                <NavLink
                  to="/top-blur"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <Image size={18} />
                  Top Blur
                </NavLink>
              </div>

              {/* Right Side Actions */}
              <div className="flex items-center gap-4">

                {/* Search */}
                <div className="relative hidden sm:block">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input
                    type="text"
                    placeholder="Search wagons..."
                    className="bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-sm w-64 focus:w-80 transition-all duration-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 text-slate-900 placeholder-slate-400"
                  />
                </div>

                {/* Notifications */}
                <button className="p-2 rounded-lg hover:bg-slate-50 text-slate-500 hover:text-slate-700 transition-colors relative">
                  <Bell size={20} />
                  <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                {/* Help */}
                <button className="p-2 rounded-lg hover:bg-slate-50 text-slate-500 hover:text-slate-700 transition-colors">
                  <HelpCircle size={20} />
                </button>

                {/* User Menu */}
                <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center text-white text-sm font-bold">
                      AD
                    </div>
                    <div className="hidden sm:block">
                      <div className="text-sm font-medium text-slate-900">Admin User</div>
                      <div className="text-xs text-slate-500 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        Online
                      </div>
                    </div>
                    <ChevronDown size={16} className="text-slate-400" />
                  </div>
                </div>

                {/* Mobile Menu Button */}
                <button className="md:hidden p-2 rounded-lg hover:bg-slate-50 text-slate-500 hover:text-slate-700 transition-colors">
                  <Menu size={20} />
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1920px] mx-auto px-6 py-8">
            <Routes>
              <Route path="/" element={<SimulatedLiveDashboard />} />
              <Route path="/upload" element={
                <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
                  <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">System Configuration</h1>
                    <p className="text-slate-600">Manage video input sources, inference models, and threshold parameters.</p>
                  </div>
                  <UploadSection />
                </div>
              } />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/comparison" element={<FrameComparison />} />
              <Route path="/top-blur" element={<TopBlurFrames />} />
            </Routes>
          </div>
        </main>

        {/* Global Styles */}
        <style>{`
            @keyframes fade-in-up {
                0% { opacity: 0; transform: translateY(15px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in-up {
                animation: fade-in-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
        `}</style>
      </div>
    </Router>
  );
}

export default App;
