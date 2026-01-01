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
      <div className="min-h-screen bg-[#f2f3f3] flex flex-col font-sans">
        {/* AWS Style Global Header */}
        <header className="bg-[#232f3e] text-white h-14 flex items-center px-4 justify-between z-50 shadow-sm fixed w-full top-0 left-0">
          <div className="flex items-center gap-4">
            <div className="font-bold text-lg tracking-tight flex items-center gap-2">
              <div className="bg-[#FF9900] text-[#232f3e] p-1 rounded-sm font-bold text-xs leading-none"></div>
              <span>RailwayInspection<span className="font-normal text-gray-400">Console</span></span>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm text-gray-300">
            <div className="relative">
              <Search size={16} className="absolute left-2 top-1.5 text-gray-500" />
              <input type="text" placeholder="Search services..." className="pl-8 pr-4 py-1 bg-[#161e2d] border border-[#5d6b7b] rounded text-white placeholder-gray-500 focus:border-[#FF9900] outline-none text-sm w-64" />
            </div>
            <Bell size={18} className="hover:text-white cursor-pointer" />
            <HelpCircle size={18} className="hover:text-white cursor-pointer" />
            <div className="text-white font-bold cursor-pointer">Admin @ Adani</div>
          </div>
        </header>

        <div className="flex pt-14 h-screen">
          {/* AWS Style Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-300 flex flex-col fixed h-full z-40 overflow-y-auto pb-20">
            <div className="px-5 py-6">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">Service Navigation</h3>

              <nav className="space-y-1">
                <NavLink to="/" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <LayoutDashboard size={18} />
                  <span>Live Monitor</span>
                </NavLink>

                <NavLink to="/comparison" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <GitCompare size={18} />
                  <span>Frame Comparison</span>
                </NavLink>

                <NavLink to="/top-blur" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <AlertTriangle size={18} />
                  <span>Top Blur Events</span>
                </NavLink>

                <NavLink to="/analytics" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <BarChart size={18} />
                  <span>Analytics</span>
                </NavLink>

                <NavLink to="/history" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <History size={18} />
                  <span>History & Archives</span>
                </NavLink>

                <NavLink to="/reports" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                  <FileText size={18} />
                  <span>Reports</span>
                </NavLink>
              </nav>
            </div>

            <div className="mt-6 px-5 py-4 border-t border-gray-200">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">Configuration</h3>
              <NavLink to="/upload" className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium transition-colors ${isActive ? 'bg-[#f1f2f3] text-[#ec7211] border-l-4 border-[#ec7211]' : 'text-[#545b64] hover:text-[#16191f] hover:bg-[#fafafa] border-l-4 border-transparent'}`}>
                <Settings size={18} />
                <span>Setup & Upload</span>
              </NavLink>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 ml-64 p-8 overflow-y-auto bg-[#f2f3f3]">
            <Routes>
              <Route path="/" element={<SimulatedLiveDashboard />} />
              <Route path="/upload" element={
                <div className="max-w-4xl mx-auto">
                  <h2 className="text-2xl font-bold text-[#16191f] mb-6">System Configuration</h2>
                  <UploadSection />
                </div>
              } />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/comparison" element={<FrameComparison />} />
              <Route path="/top-blur" element={<TopBlurFrames />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
