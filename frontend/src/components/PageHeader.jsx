import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const PageHeader = ({ title, description, breadcrumbs = [] }) => {
  const location = useLocation();

  // Auto-generate breadcrumbs if not provided
  const defaultBreadcrumbs = [
    { label: 'Dashboard', path: '/', icon: Home }
  ];

  const currentBreadcrumbs = breadcrumbs.length > 0 ? breadcrumbs : defaultBreadcrumbs;

  return (
    <div className="mb-8">
      {/* Breadcrumbs */}
      <nav className="flex items-center space-x-2 text-sm text-slate-500 mb-4">
        {currentBreadcrumbs.map((crumb, index) => (
          <React.Fragment key={index}>
            {index > 0 && <ChevronRight size={16} className="text-slate-400" />}
            {crumb.path ? (
              <Link
                to={crumb.path}
                className="flex items-center gap-1 hover:text-slate-700 transition-colors"
              >
                {crumb.icon && <crumb.icon size={14} />}
                {crumb.label}
              </Link>
            ) : (
              <span className="flex items-center gap-1 text-slate-900 font-medium">
                {crumb.icon && <crumb.icon size={14} />}
                {crumb.label}
              </span>
            )}
          </React.Fragment>
        ))}
      </nav>

      {/* Page Title & Description */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">{title}</h1>
          {description && (
            <p className="text-slate-600 mt-2 text-lg">{description}</p>
          )}
        </div>

        {/* Optional actions area */}
        <div className="flex items-center gap-3">
          {/* Status indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium text-emerald-700">System Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PageHeader;