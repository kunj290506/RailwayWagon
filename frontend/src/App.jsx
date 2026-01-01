import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import SimulatedLiveDashboard from './pages/SimulatedLiveDashboard';
import AnalyticsPage from './pages/Analytics';
import ReportsPage from './pages/Reports';
import UploadSection from './components/UploadSection'; // Keep old upload for setup

import { LayoutDashboard, Settings, Video, FileText, BarChart, AlertTriangle, GitCompare, Menu, Search, Bell, HelpCircle, History } from 'lucide-react';
import FrameComparison from './components/FrameComparison';
import TopBlurFrames from './pages/TopBlurFrames';
import HistoryPage from './pages/History';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-[#F3F4F6] font-sans text-gray-900">

        {/* Modern Sidebar (Fixed Left) */}
        <aside className="w-64 bg-white border-r border-gray-200 fixed h-full z-20 flex flex-col shadow-[2px_0_8px_-3px_rgba(0,0,0,0.05)]">
          {/* Logo Area */}
          <div className="h-16 flex items-center px-6 border-b border-gray-100">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-[#ec7211] rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
                A
              </div>
              <span className="font-bold text-lg tracking-tight text-gray-900">
                Adani<span className="text-gray-400 font-medium">Console</span>
              </span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-2">Main Platform</div>

            <NavLink to="/" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <LayoutDashboard size={18} />
              <span>Live Monitor</span>
            </NavLink>

            <NavLink to="/comparison" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <GitCompare size={18} />
              <span>Frame Comparison</span>
            </NavLink>

            <NavLink to="/top-blur" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <AlertTriangle size={18} />
              <span>Anomalies</span>
            </NavLink>

            <NavLink to="/analytics" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <BarChart size={18} />
              <span>Insights</span>
            </NavLink>

            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 mt-8 px-2">Data & Record</div>

            <NavLink to="/history" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <History size={18} />
              <span>Archives</span>
            </NavLink>

            <NavLink to="/reports" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <FileText size={18} />
              <span>Reports</span>
            </NavLink>

            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 mt-8 px-2">System</div>

            <NavLink to="/upload" className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive ? 'bg-orange-50 text-[#ec7211]' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
              <Settings size={18} />
              <span>Configuration</span>
            </NavLink>
          </nav>

          {/* User Profile Snippet */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <div className="w-8 h-8 rounded-full bg-[#232f3e] text-white flex items-center justify-center text-xs font-bold">
                AD
              </div>
              <div>
                <div className="text-sm font-bold text-gray-900">Admin User</div>
                <div className="text-xs text-gray-500">adani.ai</div>
              </div>
            </div>
          </div>
        </aside>

        {/* CSS to offset content for fixed sidebar */}
        <div className="flex-1 ml-64 flex flex-col min-h-screen">

          {/* Top Navbar (Clean White) */}
          <header className="h-16 bg-white border-b border-gray-200 sticky top-0 z-10 px-8 flex items-center justify-between shadow-sm">

            {/* Search / Breadcrumb */}
            <div className="flex items-center gap-4 w-96">
              <Search size={18} className="text-gray-400" />
              <input
                type="text"
                placeholder="Search wagons, batches, or alerts..."
                className="w-full bg-transparent border-none text-sm focus:outline-none text-gray-700 placeholder-gray-400"
              />
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-1.5 px-3 py-1 bg-green-50 border border-green-200 rounded-full">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs font-bold text-green-700">System Online</span>
              </div>
              <div className="w-px h-6 bg-gray-200"></div>
              <Bell size={20} className="text-gray-400 hover:text-gray-600 cursor-pointer" />
              <HelpCircle size={20} className="text-gray-400 hover:text-gray-600 cursor-pointer" />
            </div>
          </header>

          {/* Main Scrollable Content */}
          <main className="flex-1 p-8 overflow-y-auto">
            <div className="max-w-[1920px] mx-auto animate-fade-in">
              <Routes>
                <Route path="/" element={<SimulatedLiveDashboard />} />
                <Route path="/upload" element={
                  <div className="max-w-4xl mx-auto">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">System Configuration</h2>
                    <p className="text-gray-500 mb-8">Configure input sources and processing parameters.</p>
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
        </div>

      </div>
    </Router>
  );
}

export default App;
