import { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Upload, BarChart3, Image, History, Folders, Cpu, Menu, X } from 'lucide-react';
import '../styles/design-system.css';
import './Dashboard.css';

export default function Dashboard() {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const isActive = (path) => location.pathname === path;

    return (
        <div className="dashboard-layout">
            {/* Sidebar */}
            <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <div className="sidebar-brand">
                        <div className="brand-icon-small">
                            <Cpu size={18} />
                        </div>
                        <span className="brand-name">WagonAI</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <Link
                        to="/dashboard"
                        className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
                    >
                        <Upload size={20} />
                        <span>Upload</span>
                    </Link>

                    <Link
                        to="/dashboard/results"
                        className={`nav-link ${isActive('/dashboard/results') ? 'active' : ''}`}
                    >
                        <BarChart3 size={20} />
                        <span>Results</span>
                    </Link>

                    <Link
                        to="/dashboard/comparison"
                        className={`nav-link ${isActive('/dashboard/comparison') ? 'active' : ''}`}
                    >
                        <Image size={20} />
                        <span>Comparison</span>
                    </Link>

                    <Link
                        to="/dashboard/batch"
                        className={`nav-link ${isActive('/dashboard/batch') ? 'active' : ''}`}
                    >
                        <Folders size={20} />
                        <span>Batch Process</span>
                    </Link>

                    <Link
                        to="/dashboard/history"
                        className={`nav-link ${isActive('/dashboard/history') ? 'active' : ''}`}
                    >
                        <History size={20} />
                        <span>History</span>
                    </Link>
                </nav>

                <div className="sidebar-footer">
                    <div className="system-status">
                        <div className="status-indicator active"></div>
                        <div className="status-text">
                            <div className="status-title">System Online</div>
                            <div className="status-subtitle">NAFNet Ready</div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="dashboard-main">
                {/* Top Bar */}
                <header className="top-bar">
                    <button
                        className="menu-toggle"
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>

                    <div className="page-title">
                        Railway Wagon Detection Platform
                    </div>

                    <div className="top-bar-actions">
                        <div className="badge badge-success">
                            <span>33.7 dB PSNR</span>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="dashboard-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
