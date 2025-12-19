import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, FileText, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';

const CompanyCard = ({ company }) => {
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  return (
    <Link to={`/company/${encodeURIComponent(company.name)}`}>
      <div className="bg-white dark:bg-infynd-card-dark rounded-xl p-6 shadow-bento hover:shadow-bento-hover transition-all duration-300 border border-slate-100 dark:border-slate-700 group h-full">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2 flex items-center group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {company.name}
              <ExternalLink size={16} className="ml-2 text-slate-400 dark:text-slate-500" />
            </h3>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center text-slate-600 dark:text-slate-400">
            <FileText size={18} className="mr-2 text-primary-500" />
            <span className="text-sm">
              <span className="font-semibold text-slate-900 dark:text-slate-200">{company.totalSources || 0}</span> {(company.totalSources === 1) ? 'source' : 'sources'}
            </span>
          </div>

          <div className="flex items-center text-slate-600 dark:text-slate-400">
            <Calendar size={18} className="mr-2 text-infynd-success" />
            <span className="text-sm">
              Updated: <span className="font-medium text-slate-800 dark:text-slate-300">{formatDate(company.lastUpdated)}</span>
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
          <button className="text-primary-600 dark:text-primary-400 font-medium text-sm flex items-center group-hover:translate-x-1 transition-transform">
            View Details →
          </button>
        </div>
      </div>
    </Link>
  );
};

export default CompanyCard;
